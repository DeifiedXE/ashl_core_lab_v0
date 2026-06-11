"""Controlled multi-scenario check for runtime tendency memory influence."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .runtime_action_tendency_memory_influence_ab_minimal import (
    CANDIDATE_ACTIONS,
    build_runtime_action_tendency_scores,
)


COMMAND = "run-runtime-tendency-memory-influence-multi-scenario-check-minimal-check"
FLOW = "runtime_tendency_memory_influence_multi_scenario_check_minimal_v0"

ALLOWED_EXACT_KEYS = {
    "obstacle_retry_failed",
    "costly_retry_failed",
    "unclear_failure_repeated",
}

EXPECTED_DELTAS = {
    "obstacle_retry_failed": {
        "retry_same_action": -0.05,
        "check_before_retry": 0.10,
        "ask_for_help": 0.00,
        "slow_down_or_reduce_cost": 0.00,
    },
    "costly_retry_failed": {
        "retry_same_action": -0.05,
        "check_before_retry": 0.00,
        "ask_for_help": 0.00,
        "slow_down_or_reduce_cost": 0.10,
    },
    "unclear_failure_repeated": {
        "retry_same_action": -0.05,
        "check_before_retry": 0.00,
        "ask_for_help": 0.10,
        "slow_down_or_reduce_cost": 0.00,
    },
}

REQUIRED_FIELDS = {
    "multi_scenario_result_id",
    "scenario_count",
    "same_candidate_actions_used",
    "scenario_results",
    "aggregate_result",
    "human_summary",
    "blocked_flags",
}

REQUIRED_AGGREGATE_FIELDS = {
    "all_scenarios_changed",
    "all_scenarios_within_delta_limit",
    "all_scenarios_exact_key_only",
    "all_scenarios_rollback_ready",
    "all_scenarios_mentor_override_ready",
    "safe_to_continue_to_pre_action_consideration_design",
}

REQUIRED_HUMAN_SUMMARY = {
    "what_was_tested",
    "what_changed",
    "safety_result",
    "plain_result",
}

REQUIRED_BLOCKED_FLAGS = {
    "production_action_selection",
    "final_action_created",
    "action_executed",
    "direct_action_command",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_policy_written",
    "general_behavior_changed",
    "semantic_or_fuzzy_match_used",
    "exploration_blocked",
    "curiosity_overridden",
    "mentor_override_blocked",
    "lesson_applied",
    "memory_write",
    "new_retention_written",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_runtime_tendency_multi_scenario_result() -> dict[str, Any]:
    scenario_results = [_build_scenario_result(scenario) for scenario in _scenario_fixtures()]
    return {
        "multi_scenario_result_id": "runtime_tendency_memory_influence_multi_scenario_demo_001",
        "scenario_count": 3,
        "same_candidate_actions_used": True,
        "scenario_results": scenario_results,
        "aggregate_result": {
            "all_scenarios_changed": True,
            "all_scenarios_within_delta_limit": True,
            "all_scenarios_exact_key_only": True,
            "all_scenarios_rollback_ready": True,
            "all_scenarios_mentor_override_ready": True,
            "safe_to_continue_to_pre_action_consideration_design": True,
        },
        "human_summary": {
            "what_was_tested": "Runtime tendency memory influence was tested across three controlled scenarios.",
            "what_changed": "Each scenario changed a different bounded action tendency while reducing retry_same_action.",
            "safety_result": "All scenarios stayed within max_absolute_delta <= 0.10 and remained rollback/mentor-override ready.",
            "plain_result": "Memory influence is not only an obstacle-only single-case artifact, but it is still limited to controlled runtime tendency scores.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_runtime_tendency_multi_scenario_result(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if record.get("scenario_count") != 3:
        errors.append("scenario_count_not_three")
    if record.get("same_candidate_actions_used") is not True:
        errors.append("same_candidate_actions_used_not_true")

    scenario_results = record.get("scenario_results")
    if not isinstance(scenario_results, list):
        errors.append("scenario_results_missing_or_not_list")
        scenario_results = []
    if len(scenario_results) != 3:
        errors.append("scenario_results_length_not_three")

    scenario_validations = [_validate_scenario_result(scenario) for scenario in scenario_results]
    for validation in scenario_validations:
        errors.extend(validation["error_codes"])

    aggregate = record.get("aggregate_result")
    if not isinstance(aggregate, dict):
        errors.append("aggregate_result_missing_or_not_dict")
        aggregate = {}
    for field in sorted(REQUIRED_AGGREGATE_FIELDS):
        if field not in aggregate:
            errors.append(f"missing_aggregate_field:{field}")
        elif aggregate.get(field) is not True:
            errors.append(f"{field}_not_true")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        if not isinstance(human_summary.get(field), str) or not human_summary.get(field):
            errors.append(f"{field}_empty_or_not_string")

    blocked_flags = record.get("blocked_flags")
    if not isinstance(blocked_flags, dict):
        errors.append("blocked_flags_missing_or_not_dict")
        blocked_flags = {}
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "multi_scenario_result_id": record.get("multi_scenario_result_id"),
        "valid": not errors,
        "error_codes": errors,
        "scenario_count": len(scenario_results),
        "changed_scenario_count": sum(1 for result in scenario_validations if result["runtime_tendency_changed"]),
        "within_delta_limit_scenario_count": sum(
            1 for result in scenario_validations if result["within_delta_limit"]
        ),
        "rollback_ready_scenario_count": sum(1 for result in scenario_validations if result["rollback_ready"]),
        "mentor_override_ready_scenario_count": sum(
            1 for result in scenario_validations if result["mentor_override_ready"]
        ),
        "exact_key_only_scenario_count": sum(1 for result in scenario_validations if result["exact_key_only"]),
        "obstacle_scenario_pass_count": _scenario_pass_count(scenario_validations, "obstacle_retry_failed"),
        "costly_retry_scenario_pass_count": _scenario_pass_count(scenario_validations, "costly_retry_failed"),
        "unclear_failure_scenario_pass_count": _scenario_pass_count(
            scenario_validations, "unclear_failure_repeated"
        ),
        **_blocked_flag_values(blocked_flags),
    }


def run_runtime_tendency_memory_influence_multi_scenario_check_minimal_check() -> dict[str, Any]:
    valid_result = build_runtime_tendency_multi_scenario_result()
    records = [
        valid_result,
        *_invalid_demo_records(valid_result),
    ]
    validation_results = [validate_runtime_tendency_multi_scenario_result(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "runtime_tendency_memory_influence_multi_scenario_results": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Three controlled exact-key scenarios are checked with the same candidate action set.",
            "Memory influence changes bounded runtime tendency scores only.",
            "No production action selection, final action, execution, direct command, semantic/fuzzy matching, persistent policy, predictor mutation, or proof of learning is added.",
        ],
    }


def _build_scenario_result(scenario: dict[str, Any]) -> dict[str, Any]:
    memory_signal = {
        "memory_signal_id": f"retained_memory_signal_{scenario['exact_key']}_001",
        "exact_key": scenario["exact_key"],
        "source": "retained_experience_exact_key_lookup",
        "valid": True,
        "target_action_tendency": scenario["target_action_tendency"],
        "influence": scenario["influence"],
        "blocked_flags": {
            "semantic_or_fuzzy_match": False,
            "memory_write": False,
            "new_retention_written": False,
        },
    }
    memory_off = build_runtime_action_tendency_scores(
        deepcopy(scenario["state"]),
        list(CANDIDATE_ACTIONS),
        memory_influence_enabled=False,
        memory_signal=memory_signal,
    )
    memory_on = build_runtime_action_tendency_scores(
        deepcopy(scenario["state"]),
        list(CANDIDATE_ACTIONS),
        memory_influence_enabled=True,
        memory_signal=memory_signal,
    )
    score_deltas = _score_deltas(memory_off["scores"], memory_on["scores"])
    return {
        "scenario_id": scenario["scenario_id"],
        "exact_key": scenario["exact_key"],
        "memory_off_scores": memory_off["scores"],
        "memory_on_scores": memory_on["scores"],
        "score_deltas": score_deltas,
        "runtime_tendency_changed": any(delta != 0.0 for delta in score_deltas.values()),
        "max_absolute_delta": max(abs(delta) for delta in score_deltas.values()),
        "rollback_ready": True,
        "mentor_override_ready": True,
    }


def _validate_scenario_result(scenario: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(scenario, dict):
        return _scenario_validation_result("", "", False, False, False, False, errors + ["scenario_not_dict"])

    scenario_id = scenario.get("scenario_id")
    if not isinstance(scenario_id, str) or not scenario_id:
        errors.append("scenario_id_empty_or_not_string")

    exact_key = scenario.get("exact_key")
    exact_key_only = exact_key in ALLOWED_EXACT_KEYS
    if not exact_key_only:
        errors.append("unknown_exact_key")

    off_scores = _scores("memory_off_scores", scenario.get("memory_off_scores"), errors)
    on_scores = _scores("memory_on_scores", scenario.get("memory_on_scores"), errors)
    deltas = _scores("score_deltas", scenario.get("score_deltas"), errors, allow_negative=True)

    deltas_valid = True
    expected = EXPECTED_DELTAS.get(exact_key)
    for action in CANDIDATE_ACTIONS:
        off = off_scores.get(action)
        on = on_scores.get(action)
        delta = deltas.get(action)
        if isinstance(off, (int, float)) and isinstance(on, (int, float)) and isinstance(delta, (int, float)):
            calculated = _round(on - off)
            if _round(delta) != calculated:
                errors.append(f"{exact_key or 'unknown'}_{action}_delta_mismatch")
                deltas_valid = False
            if expected is not None and _round(delta) != expected[action]:
                errors.append(f"{exact_key}_{action}_delta_unexpected")
                deltas_valid = False
    runtime_tendency_changed = scenario.get("runtime_tendency_changed") is True
    if not runtime_tendency_changed:
        errors.append("runtime_tendency_changed_not_true")

    max_absolute_delta = scenario.get("max_absolute_delta")
    within_delta_limit = isinstance(max_absolute_delta, (int, float)) and float(max_absolute_delta) <= 0.10
    if not isinstance(max_absolute_delta, (int, float)):
        errors.append("max_absolute_delta_not_number")
    elif float(max_absolute_delta) > 0.10:
        errors.append("max_absolute_delta_too_high")

    rollback_ready = scenario.get("rollback_ready") is True
    if not rollback_ready:
        errors.append("rollback_ready_not_true")
    mentor_override_ready = scenario.get("mentor_override_ready") is True
    if not mentor_override_ready:
        errors.append("mentor_override_ready_not_true")

    expected_scenario_pass = bool(
        exact_key_only
        and deltas_valid
        and runtime_tendency_changed
        and within_delta_limit
        and rollback_ready
        and mentor_override_ready
    )
    return _scenario_validation_result(
        str(scenario_id or ""),
        str(exact_key or ""),
        exact_key_only,
        runtime_tendency_changed,
        within_delta_limit,
        rollback_ready,
        errors,
        mentor_override_ready=mentor_override_ready,
        scenario_pass=expected_scenario_pass,
    )


def _scenario_validation_result(
    scenario_id: str,
    exact_key: str,
    exact_key_only: bool,
    runtime_tendency_changed: bool,
    within_delta_limit: bool,
    rollback_ready: bool,
    errors: list[str],
    mentor_override_ready: bool = False,
    scenario_pass: bool = False,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "exact_key": exact_key,
        "exact_key_only": exact_key_only,
        "runtime_tendency_changed": runtime_tendency_changed,
        "within_delta_limit": within_delta_limit,
        "rollback_ready": rollback_ready,
        "mentor_override_ready": mentor_override_ready,
        "scenario_pass": scenario_pass,
        "error_codes": errors,
    }


def _scores(
    field: str,
    scores: Any,
    errors: list[str],
    allow_negative: bool = False,
) -> dict[str, Any]:
    if not isinstance(scores, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    for action in CANDIDATE_ACTIONS:
        score = scores.get(action)
        if not isinstance(score, (int, float)):
            errors.append(f"{field}_{action}_not_number")
        elif not allow_negative and (score < 0.0 or score > 1.0):
            errors.append(f"{field}_{action}_out_of_range")
    return scores


def _scenario_pass_count(scenario_validations: list[dict[str, Any]], exact_key: str) -> int:
    return sum(1 for result in scenario_validations if result["exact_key"] == exact_key and result["scenario_pass"])


def _scenario_fixtures() -> list[dict[str, Any]]:
    return [
        {
            "scenario_id": "obstacle_retry_failed_same_state",
            "exact_key": "obstacle_retry_failed",
            "state": {
                "situation": "obstacle_ahead",
                "prior_failure_exact_key": "obstacle_retry_failed",
            },
            "target_action_tendency": "check_before_retry",
            "influence": {"check_before_retry": 0.10, "retry_same_action": -0.05},
        },
        {
            "scenario_id": "costly_retry_same_state",
            "exact_key": "costly_retry_failed",
            "state": {
                "situation": "retry_cost_high",
                "prior_failure_exact_key": "costly_retry_failed",
            },
            "target_action_tendency": "slow_down_or_reduce_cost",
            "influence": {"slow_down_or_reduce_cost": 0.10, "retry_same_action": -0.05},
        },
        {
            "scenario_id": "unclear_failure_same_state",
            "exact_key": "unclear_failure_repeated",
            "state": {
                "situation": "failure_reason_unclear",
                "prior_failure_exact_key": "unclear_failure_repeated",
            },
            "target_action_tendency": "ask_for_help",
            "influence": {"ask_for_help": 0.10, "retry_same_action": -0.05},
        },
    ]


def _score_deltas(off_scores: dict[str, Any], on_scores: dict[str, Any]) -> dict[str, float]:
    return {action: _round(on_scores[action] - off_scores[action]) for action in CANDIDATE_ACTIONS}


def _round(value: float) -> float:
    return round(float(value), 2)


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _invalid_demo_records(valid_result: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    scenario_count_wrong = _copy_case(valid_result, "scenario_count_wrong")
    scenario_count_wrong["scenario_count"] = 2
    records.append(scenario_count_wrong)

    same_candidates_false = _copy_case(valid_result, "same_candidate_actions_false")
    same_candidates_false["same_candidate_actions_used"] = False
    records.append(same_candidates_false)

    missing_scenario = _copy_case(valid_result, "missing_scenario")
    missing_scenario["scenario_results"] = missing_scenario["scenario_results"][:2]
    records.append(missing_scenario)

    unknown_exact_key = _copy_case(valid_result, "unknown_exact_key")
    unknown_exact_key["scenario_results"][0]["exact_key"] = "semantic_guess"
    records.append(unknown_exact_key)

    wrong_obstacle_delta = _copy_case(valid_result, "wrong_obstacle_delta")
    wrong_obstacle_delta["scenario_results"][0]["score_deltas"]["check_before_retry"] = 0.09
    records.append(wrong_obstacle_delta)

    wrong_costly_delta = _copy_case(valid_result, "wrong_costly_delta")
    wrong_costly_delta["scenario_results"][1]["score_deltas"]["slow_down_or_reduce_cost"] = 0.09
    records.append(wrong_costly_delta)

    wrong_unclear_delta = _copy_case(valid_result, "wrong_unclear_delta")
    wrong_unclear_delta["scenario_results"][2]["score_deltas"]["ask_for_help"] = 0.09
    records.append(wrong_unclear_delta)

    max_delta_high = _copy_case(valid_result, "max_delta_high")
    max_delta_high["scenario_results"][0]["max_absolute_delta"] = 0.11
    records.append(max_delta_high)

    rollback_false = _copy_case(valid_result, "rollback_false")
    rollback_false["scenario_results"][0]["rollback_ready"] = False
    records.append(rollback_false)

    mentor_override_false = _copy_case(valid_result, "mentor_override_false")
    mentor_override_false["scenario_results"][0]["mentor_override_ready"] = False
    records.append(mentor_override_false)

    aggregate_cases = [
        "all_scenarios_changed",
        "all_scenarios_within_delta_limit",
        "all_scenarios_exact_key_only",
        "all_scenarios_rollback_ready",
        "all_scenarios_mentor_override_ready",
        "safe_to_continue_to_pre_action_consideration_design",
    ]
    for field in aggregate_cases:
        invalid = _copy_case(valid_result, f"{field}_false")
        invalid["aggregate_result"][field] = False
        records.append(invalid)

    empty_what_changed = _copy_case(valid_result, "empty_what_changed")
    empty_what_changed["human_summary"]["what_changed"] = ""
    records.append(empty_what_changed)

    empty_plain_result = _copy_case(valid_result, "empty_plain_result")
    empty_plain_result["human_summary"]["plain_result"] = ""
    records.append(empty_plain_result)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_result, flag)
        flagged["blocked_flags"][flag] = True
        records.append(flagged)

    return records


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["multi_scenario_result_id"] = f"{record['multi_scenario_result_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    valid_result = valid_results[0] if valid_results else {}
    summary: dict[str, int | bool] = {
        "multi_scenario_result_count": len(validation_results),
        "valid_multi_scenario_result_count": len(valid_results),
        "invalid_multi_scenario_result_count": sum(1 for result in validation_results if not result["valid"]),
        "scenario_count": int(valid_result.get("scenario_count", 0)),
        "changed_scenario_count": int(valid_result.get("changed_scenario_count", 0)),
        "within_delta_limit_scenario_count": int(valid_result.get("within_delta_limit_scenario_count", 0)),
        "rollback_ready_scenario_count": int(valid_result.get("rollback_ready_scenario_count", 0)),
        "mentor_override_ready_scenario_count": int(valid_result.get("mentor_override_ready_scenario_count", 0)),
        "exact_key_only_scenario_count": int(valid_result.get("exact_key_only_scenario_count", 0)),
        "obstacle_scenario_pass_count": int(valid_result.get("obstacle_scenario_pass_count", 0)),
        "costly_retry_scenario_pass_count": int(valid_result.get("costly_retry_scenario_pass_count", 0)),
        "unclear_failure_scenario_pass_count": int(valid_result.get("unclear_failure_scenario_pass_count", 0)),
        "max_absolute_delta_violation_blocked_count": _count_error(validation_results, "max_absolute_delta_too_high"),
        "unknown_exact_key_blocked_count": _count_error(validation_results, "unknown_exact_key"),
        "wrong_delta_blocked_count": _count_errors_ending(validation_results, "_delta_unexpected"),
        "rollback_ready_false_blocked_count": _count_error(validation_results, "rollback_ready_not_true"),
        "mentor_override_ready_false_blocked_count": _count_error(
            validation_results, "mentor_override_ready_not_true"
        ),
        "aggregate_changed_false_blocked_count": _count_error(
            validation_results, "all_scenarios_changed_not_true"
        ),
        "aggregate_delta_limit_false_blocked_count": _count_error(
            validation_results, "all_scenarios_within_delta_limit_not_true"
        ),
        "aggregate_exact_key_false_blocked_count": _count_error(
            validation_results, "all_scenarios_exact_key_only_not_true"
        ),
        "aggregate_rollback_false_blocked_count": _count_error(
            validation_results, "all_scenarios_rollback_ready_not_true"
        ),
        "aggregate_mentor_override_false_blocked_count": _count_error(
            validation_results, "all_scenarios_mentor_override_ready_not_true"
        ),
        "safe_to_continue_false_blocked_count": _count_error(
            validation_results, "safe_to_continue_to_pre_action_consideration_design_not_true"
        ),
        "production_action_selection_blocked_count": _count_error(
            validation_results, "production_action_selection_enabled"
        ),
        "final_action_created_blocked_count": _count_error(validation_results, "final_action_created_enabled"),
        "action_executed_blocked_count": _count_error(validation_results, "action_executed_enabled"),
        "direct_action_command_blocked_count": _count_error(validation_results, "direct_action_command_enabled"),
        "real_navigation_changed_blocked_count": _count_error(validation_results, "real_navigation_changed_enabled"),
        "ui_behavior_changed_blocked_count": _count_error(validation_results, "ui_behavior_changed_enabled"),
        "persistent_policy_written_blocked_count": _count_error(
            validation_results, "persistent_policy_written_enabled"
        ),
        "general_behavior_changed_blocked_count": _count_error(
            validation_results, "general_behavior_changed_enabled"
        ),
        "semantic_or_fuzzy_match_used_blocked_count": _count_error(
            validation_results, "semantic_or_fuzzy_match_used_enabled"
        ),
        "exploration_blocked_count": _count_error(validation_results, "exploration_blocked_enabled"),
        "curiosity_overridden_blocked_count": _count_error(validation_results, "curiosity_overridden_enabled"),
        "mentor_override_blocked_count": _count_error(validation_results, "mentor_override_blocked_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(validation_results, "new_retention_written_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
        "scenario_count_not_three_blocked_count": _count_error(validation_results, "scenario_count_not_three"),
        "same_candidate_actions_false_blocked_count": _count_error(
            validation_results, "same_candidate_actions_used_not_true"
        ),
        "missing_scenario_blocked_count": _count_error(validation_results, "scenario_results_length_not_three"),
        "empty_what_changed_blocked_count": _count_error(validation_results, "what_changed_empty_or_not_string"),
        "empty_plain_result_blocked_count": _count_error(validation_results, "plain_result_empty_or_not_string"),
    }
    summary["all_runtime_tendency_memory_influence_multi_scenario_check_minimal_checks_passed"] = _all_checks_passed(
        summary
    )
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["multi_scenario_result_count"] == 36
        and summary["valid_multi_scenario_result_count"] == 1
        and summary["invalid_multi_scenario_result_count"] == 35
        and summary["scenario_count"] == 3
        and summary["changed_scenario_count"] == 3
        and summary["within_delta_limit_scenario_count"] == 3
        and summary["rollback_ready_scenario_count"] == 3
        and summary["mentor_override_ready_scenario_count"] == 3
        and summary["exact_key_only_scenario_count"] == 3
        and summary["obstacle_scenario_pass_count"] == 1
        and summary["costly_retry_scenario_pass_count"] == 1
        and summary["unclear_failure_scenario_pass_count"] == 1
        and summary["scenario_count_not_three_blocked_count"] == 1
        and summary["same_candidate_actions_false_blocked_count"] == 1
        and summary["missing_scenario_blocked_count"] == 1
        and summary["max_absolute_delta_violation_blocked_count"] == 1
        and summary["unknown_exact_key_blocked_count"] == 1
        and summary["wrong_delta_blocked_count"] == 3
        and summary["rollback_ready_false_blocked_count"] == 1
        and summary["mentor_override_ready_false_blocked_count"] == 1
        and summary["aggregate_changed_false_blocked_count"] == 1
        and summary["aggregate_delta_limit_false_blocked_count"] == 1
        and summary["aggregate_exact_key_false_blocked_count"] == 1
        and summary["aggregate_rollback_false_blocked_count"] == 1
        and summary["aggregate_mentor_override_false_blocked_count"] == 1
        and summary["safe_to_continue_false_blocked_count"] == 1
        and summary["empty_what_changed_blocked_count"] == 1
        and summary["empty_plain_result_blocked_count"] == 1
        and summary["production_action_selection_blocked_count"] == 1
        and summary["final_action_created_blocked_count"] == 1
        and summary["action_executed_blocked_count"] == 1
        and summary["direct_action_command_blocked_count"] == 1
        and summary["real_navigation_changed_blocked_count"] == 1
        and summary["ui_behavior_changed_blocked_count"] == 1
        and summary["persistent_policy_written_blocked_count"] == 1
        and summary["general_behavior_changed_blocked_count"] == 1
        and summary["semantic_or_fuzzy_match_used_blocked_count"] == 1
        and summary["exploration_blocked_count"] == 1
        and summary["curiosity_overridden_blocked_count"] == 1
        and summary["mentor_override_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["new_retention_written_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "runtime_tendency_memory_influence_multi_scenario_check_enabled": True,
        "scenario_count": summary["scenario_count"],
        "changed_scenario_count": summary["changed_scenario_count"],
        "within_delta_limit_scenario_count": summary["within_delta_limit_scenario_count"],
        "rollback_ready_scenario_count": summary["rollback_ready_scenario_count"],
        "mentor_override_ready_scenario_count": summary["mentor_override_ready_scenario_count"],
        "exact_key_only_scenario_count": summary["exact_key_only_scenario_count"],
        "runtime_tendency_scores_only": True,
        "production_action_selection_added": False,
        "final_action_creation_added": False,
        "action_execution_added": False,
        "direct_action_command_added": False,
        "semantic_or_fuzzy_matching_added": False,
        "persistent_policy_write_added": False,
        "general_behavior_change_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "top_level_field_count": len(REQUIRED_FIELDS),
    }


def _blocked_flag_values(blocked_flags: dict[str, Any]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_errors_ending(validation_results: list[dict[str, Any]], suffix: str) -> int:
    return sum(1 for result in validation_results for error in result["error_codes"] if error.endswith(suffix))
