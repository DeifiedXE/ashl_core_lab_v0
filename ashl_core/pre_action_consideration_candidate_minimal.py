"""Pre-action consideration candidates from bounded memory tendency deltas."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .runtime_action_tendency_memory_influence_ab_minimal import CANDIDATE_ACTIONS
from .runtime_tendency_memory_influence_multi_scenario_check_minimal import (
    build_runtime_tendency_multi_scenario_result,
)


COMMAND = "run-pre-action-consideration-candidate-minimal-check"
FLOW = "pre_action_consideration_candidate_minimal_v0"

EXPECTED_MAPPING = {
    "obstacle_retry_failed_same_state": ("obstacle_retry_failed", "check_before_retry"),
    "costly_retry_same_state": ("costly_retry_failed", "slow_down_or_reduce_cost"),
    "unclear_failure_same_state": ("unclear_failure_repeated", "ask_for_help"),
}

REQUIRED_FIELDS = {
    "pre_action_candidate_result_id",
    "source_multi_scenario_result_id",
    "candidate_count",
    "candidates",
    "aggregate_result",
    "human_summary",
    "blocked_flags",
}

REQUIRED_AGGREGATE_FIELDS = {
    "all_candidates_from_exact_key_scenarios",
    "all_candidates_from_positive_delta",
    "all_candidates_pre_action_only",
    "all_candidates_not_final_action",
    "safe_to_continue_to_pre_action_gate_check",
}

REQUIRED_HUMAN_SUMMARY = {
    "what_was_built",
    "what_candidates_mean",
    "what_is_blocked",
    "plain_result",
}

REQUIRED_BLOCKED_FLAGS = {
    "production_action_selection",
    "final_action_created",
    "action_selected",
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


def build_pre_action_consideration_candidates(
    multi_scenario_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = multi_scenario_result or build_runtime_tendency_multi_scenario_result()
    candidates = [
        candidate
        for scenario in source.get("scenario_results", [])
        for candidate in [_candidate_from_scenario(scenario)]
        if candidate is not None
    ]
    return {
        "pre_action_candidate_result_id": "pre_action_consideration_candidate_demo_001",
        "source_multi_scenario_result_id": source.get(
            "multi_scenario_result_id",
            "runtime_tendency_memory_influence_multi_scenario_demo_001",
        ),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "aggregate_result": {
            "all_candidates_from_exact_key_scenarios": True,
            "all_candidates_from_positive_delta": True,
            "all_candidates_pre_action_only": True,
            "all_candidates_not_final_action": True,
            "safe_to_continue_to_pre_action_gate_check": True,
        },
        "human_summary": {
            "what_was_built": "Runtime tendency deltas were converted into pre-action consideration candidates.",
            "what_candidates_mean": "A candidate means an action deserves consideration before selection, not that it should be executed.",
            "what_is_blocked": "Final action selection, action execution, direct commands, persistent policy, and generalized behavior remain blocked.",
            "plain_result": "The system can now name which actions are worth pre-action consideration from bounded runtime tendency memory influence.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_pre_action_consideration_candidate_result(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)
    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if record.get("candidate_count") != 3:
        errors.append("candidate_count_not_three")

    candidates = record.get("candidates")
    if not isinstance(candidates, list):
        errors.append("candidates_missing_or_not_list")
        candidates = []
    if len(candidates) != 3:
        errors.append("candidates_length_not_three")

    candidate_validations = [_validate_candidate(candidate) for candidate in candidates]
    for validation in candidate_validations:
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
        "pre_action_candidate_result_id": record.get("pre_action_candidate_result_id"),
        "valid": not errors,
        "error_codes": errors,
        "candidate_count": len(candidates),
        "positive_delta_candidate_count": sum(1 for result in candidate_validations if result["positive_delta"]),
        "pre_action_only_candidate_count": sum(1 for result in candidate_validations if result["pre_action_only"]),
        "not_final_action_candidate_count": sum(
            1 for result in candidate_validations if result["not_final_action"]
        ),
        "exact_key_candidate_count": sum(1 for result in candidate_validations if result["exact_key_valid"]),
        "obstacle_candidate_pass_count": _candidate_pass_count(
            candidate_validations,
            "obstacle_retry_failed_same_state",
        ),
        "costly_retry_candidate_pass_count": _candidate_pass_count(
            candidate_validations,
            "costly_retry_same_state",
        ),
        "unclear_failure_candidate_pass_count": _candidate_pass_count(
            candidate_validations,
            "unclear_failure_same_state",
        ),
        **_blocked_flag_values(blocked_flags),
    }


def run_pre_action_consideration_candidate_minimal_check() -> dict[str, Any]:
    valid_result = build_pre_action_consideration_candidates()
    records = [
        valid_result,
        *_invalid_demo_records(valid_result),
    ]
    validation_results = [validate_pre_action_consideration_candidate_result(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "pre_action_consideration_candidate_results": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "Largest positive runtime tendency deltas become pre-action consideration candidates.",
            "Candidates are not selected actions and do not create final_action.",
            "No production action selection, execution, direct command, semantic/fuzzy matching, persistent policy, predictor mutation, or proof of learning is added.",
        ],
    }


def _candidate_from_scenario(scenario: dict[str, Any]) -> dict[str, Any] | None:
    if scenario.get("runtime_tendency_changed") is not True:
        return None
    deltas = scenario.get("score_deltas", {})
    positive_actions = [
        (action, _round(delta))
        for action, delta in deltas.items()
        if action in CANDIDATE_ACTIONS and isinstance(delta, (int, float)) and _round(delta) > 0.0
    ]
    if not positive_actions:
        return None
    considered_action, delta = max(positive_actions, key=lambda item: item[1])
    off_score = scenario["memory_off_scores"][considered_action]
    on_score = scenario["memory_on_scores"][considered_action]
    return {
        "candidate_id": f"pre_action_candidate_{scenario['exact_key']}_001",
        "scenario_id": scenario["scenario_id"],
        "exact_key": scenario["exact_key"],
        "considered_action": considered_action,
        "consideration_source": "largest_positive_runtime_tendency_delta",
        "baseline_score": _round(off_score),
        "memory_influenced_score": _round(on_score),
        "delta": delta,
        "reason": f"Memory influence increased {considered_action} tendency in this controlled scenario.",
        "pre_action_only": True,
        "selected_as_final_action": False,
    }


def _validate_candidate(candidate: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(candidate, dict):
        return _candidate_validation_result("", "", "", False, False, False, False, errors + ["candidate_not_dict"])

    if not isinstance(candidate.get("candidate_id"), str) or not candidate.get("candidate_id"):
        errors.append("candidate_id_empty_or_not_string")

    scenario_id = candidate.get("scenario_id")
    exact_key = candidate.get("exact_key")
    expected = EXPECTED_MAPPING.get(scenario_id)
    scenario_valid = expected is not None
    if not scenario_valid:
        errors.append("unknown_scenario_id")

    exact_key_valid = exact_key in {value[0] for value in EXPECTED_MAPPING.values()}
    if not exact_key_valid:
        errors.append("unknown_exact_key")
    if expected is not None and exact_key != expected[0]:
        errors.append("scenario_exact_key_mismatch")

    action = candidate.get("considered_action")
    action_valid = action in CANDIDATE_ACTIONS
    if not action_valid:
        errors.append("unknown_considered_action")
    if expected is not None and action_valid and action != expected[1]:
        errors.append(f"{scenario_id}_wrong_considered_action")

    if candidate.get("consideration_source") != "largest_positive_runtime_tendency_delta":
        errors.append("consideration_source_not_largest_positive_runtime_tendency_delta")

    baseline = candidate.get("baseline_score")
    memory_score = candidate.get("memory_influenced_score")
    delta = candidate.get("delta")
    positive_delta = False
    if not _valid_score(baseline):
        errors.append("baseline_score_out_of_range_or_not_number")
    if not _valid_score(memory_score):
        errors.append("memory_influenced_score_out_of_range_or_not_number")
    if not isinstance(delta, (int, float)):
        errors.append("delta_not_number")
    else:
        positive_delta = _round(delta) > 0.0
        if not positive_delta:
            errors.append("delta_not_positive")
        if _round(delta) > 0.10:
            errors.append("delta_too_high")
    if _valid_score(baseline) and _valid_score(memory_score) and isinstance(delta, (int, float)):
        if _round(memory_score - baseline) != _round(delta):
            errors.append("delta_mismatch")

    if not isinstance(candidate.get("reason"), str) or not candidate.get("reason"):
        errors.append("reason_empty_or_not_string")

    pre_action_only = candidate.get("pre_action_only") is True
    if not pre_action_only:
        errors.append("pre_action_only_not_true")

    not_final_action = candidate.get("selected_as_final_action") is False
    if not not_final_action:
        errors.append("selected_as_final_action_not_false")

    candidate_pass = bool(
        scenario_valid
        and exact_key_valid
        and action_valid
        and expected is not None
        and action == expected[1]
        and positive_delta
        and isinstance(delta, (int, float))
        and _round(delta) <= 0.10
        and pre_action_only
        and not_final_action
        and not errors
    )
    return _candidate_validation_result(
        str(scenario_id or ""),
        str(exact_key or ""),
        str(action or ""),
        exact_key_valid,
        positive_delta,
        pre_action_only,
        not_final_action,
        errors,
        candidate_pass=candidate_pass,
    )


def _candidate_validation_result(
    scenario_id: str,
    exact_key: str,
    considered_action: str,
    exact_key_valid: bool,
    positive_delta: bool,
    pre_action_only: bool,
    not_final_action: bool,
    errors: list[str],
    candidate_pass: bool = False,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "exact_key": exact_key,
        "considered_action": considered_action,
        "exact_key_valid": exact_key_valid,
        "positive_delta": positive_delta,
        "pre_action_only": pre_action_only,
        "not_final_action": not_final_action,
        "candidate_pass": candidate_pass,
        "error_codes": errors,
    }


def _valid_score(value: Any) -> bool:
    return isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0


def _round(value: float) -> float:
    return round(float(value), 2)


def _candidate_pass_count(candidate_validations: list[dict[str, Any]], scenario_id: str) -> int:
    return sum(
        1 for result in candidate_validations if result["scenario_id"] == scenario_id and result["candidate_pass"]
    )


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _invalid_demo_records(valid_result: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    candidate_count_wrong = _copy_case(valid_result, "candidate_count_wrong")
    candidate_count_wrong["candidate_count"] = 2
    records.append(candidate_count_wrong)

    missing_candidate = _copy_case(valid_result, "missing_candidate")
    missing_candidate["candidates"] = missing_candidate["candidates"][:2]
    records.append(missing_candidate)

    unknown_scenario = _copy_case(valid_result, "unknown_scenario")
    unknown_scenario["candidates"][0]["scenario_id"] = "unknown_scenario"
    records.append(unknown_scenario)

    unknown_exact_key = _copy_case(valid_result, "unknown_exact_key")
    unknown_exact_key["candidates"][0]["exact_key"] = "semantic_guess"
    records.append(unknown_exact_key)

    unknown_action = _copy_case(valid_result, "unknown_action")
    unknown_action["candidates"][0]["considered_action"] = "teleport"
    records.append(unknown_action)

    wrong_obstacle_mapping = _copy_case(valid_result, "wrong_obstacle_mapping")
    wrong_obstacle_mapping["candidates"][0]["considered_action"] = "ask_for_help"
    records.append(wrong_obstacle_mapping)

    wrong_costly_mapping = _copy_case(valid_result, "wrong_costly_mapping")
    wrong_costly_mapping["candidates"][1]["considered_action"] = "check_before_retry"
    records.append(wrong_costly_mapping)

    wrong_unclear_mapping = _copy_case(valid_result, "wrong_unclear_mapping")
    wrong_unclear_mapping["candidates"][2]["considered_action"] = "check_before_retry"
    records.append(wrong_unclear_mapping)

    negative_delta = _copy_case(valid_result, "negative_delta")
    negative_delta["candidates"][0]["delta"] = -0.01
    records.append(negative_delta)

    zero_delta = _copy_case(valid_result, "zero_delta")
    zero_delta["candidates"][0]["delta"] = 0.00
    zero_delta["candidates"][0]["memory_influenced_score"] = zero_delta["candidates"][0]["baseline_score"]
    records.append(zero_delta)

    delta_too_high = _copy_case(valid_result, "delta_too_high")
    delta_too_high["candidates"][0]["delta"] = 0.11
    delta_too_high["candidates"][0]["memory_influenced_score"] = 0.61
    records.append(delta_too_high)

    wrong_source = _copy_case(valid_result, "wrong_source")
    wrong_source["candidates"][0]["consideration_source"] = "manual_selection"
    records.append(wrong_source)

    pre_action_false = _copy_case(valid_result, "pre_action_false")
    pre_action_false["candidates"][0]["pre_action_only"] = False
    records.append(pre_action_false)

    selected_final = _copy_case(valid_result, "selected_final")
    selected_final["candidates"][0]["selected_as_final_action"] = True
    records.append(selected_final)

    aggregate_cases = [
        "all_candidates_from_exact_key_scenarios",
        "all_candidates_from_positive_delta",
        "all_candidates_pre_action_only",
        "all_candidates_not_final_action",
        "safe_to_continue_to_pre_action_gate_check",
    ]
    for field in aggregate_cases:
        invalid = _copy_case(valid_result, f"{field}_false")
        invalid["aggregate_result"][field] = False
        records.append(invalid)

    empty_meaning = _copy_case(valid_result, "empty_what_candidates_mean")
    empty_meaning["human_summary"]["what_candidates_mean"] = ""
    records.append(empty_meaning)

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
    copied["pre_action_candidate_result_id"] = f"{record['pre_action_candidate_result_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    valid_result = valid_results[0] if valid_results else {}
    summary: dict[str, int | bool] = {
        "pre_action_candidate_result_count": len(validation_results),
        "valid_pre_action_candidate_result_count": len(valid_results),
        "invalid_pre_action_candidate_result_count": sum(1 for result in validation_results if not result["valid"]),
        "candidate_count": int(valid_result.get("candidate_count", 0)),
        "positive_delta_candidate_count": int(valid_result.get("positive_delta_candidate_count", 0)),
        "pre_action_only_candidate_count": int(valid_result.get("pre_action_only_candidate_count", 0)),
        "not_final_action_candidate_count": int(valid_result.get("not_final_action_candidate_count", 0)),
        "exact_key_candidate_count": int(valid_result.get("exact_key_candidate_count", 0)),
        "obstacle_candidate_pass_count": int(valid_result.get("obstacle_candidate_pass_count", 0)),
        "costly_retry_candidate_pass_count": int(valid_result.get("costly_retry_candidate_pass_count", 0)),
        "unclear_failure_candidate_pass_count": int(valid_result.get("unclear_failure_candidate_pass_count", 0)),
        "candidate_count_violation_blocked_count": _count_errors(
            validation_results,
            {"candidate_count_not_three", "candidates_length_not_three"},
        ),
        "unknown_scenario_blocked_count": _count_error(validation_results, "unknown_scenario_id"),
        "unknown_exact_key_blocked_count": _count_error(validation_results, "unknown_exact_key"),
        "wrong_mapping_blocked_count": _count_errors_ending(validation_results, "_wrong_considered_action"),
        "non_positive_delta_blocked_count": _count_error(validation_results, "delta_not_positive"),
        "delta_too_high_blocked_count": _count_error(validation_results, "delta_too_high"),
        "pre_action_only_false_blocked_count": _count_error(validation_results, "pre_action_only_not_true"),
        "selected_as_final_action_blocked_count": _count_error(
            validation_results,
            "selected_as_final_action_not_false",
        ),
        "wrong_consideration_source_blocked_count": _count_error(
            validation_results,
            "consideration_source_not_largest_positive_runtime_tendency_delta",
        ),
        "aggregate_exact_key_false_blocked_count": _count_error(
            validation_results,
            "all_candidates_from_exact_key_scenarios_not_true",
        ),
        "aggregate_positive_delta_false_blocked_count": _count_error(
            validation_results,
            "all_candidates_from_positive_delta_not_true",
        ),
        "aggregate_pre_action_only_false_blocked_count": _count_error(
            validation_results,
            "all_candidates_pre_action_only_not_true",
        ),
        "aggregate_not_final_action_false_blocked_count": _count_error(
            validation_results,
            "all_candidates_not_final_action_not_true",
        ),
        "safe_to_continue_false_blocked_count": _count_error(
            validation_results,
            "safe_to_continue_to_pre_action_gate_check_not_true",
        ),
        "empty_what_candidates_mean_blocked_count": _count_error(
            validation_results,
            "what_candidates_mean_empty_or_not_string",
        ),
        "empty_plain_result_blocked_count": _count_error(validation_results, "plain_result_empty_or_not_string"),
        "production_action_selection_blocked_count": _count_error(
            validation_results,
            "production_action_selection_enabled",
        ),
        "final_action_created_blocked_count": _count_error(validation_results, "final_action_created_enabled"),
        "action_selected_blocked_count": _count_error(validation_results, "action_selected_enabled"),
        "action_executed_blocked_count": _count_error(validation_results, "action_executed_enabled"),
        "direct_action_command_blocked_count": _count_error(validation_results, "direct_action_command_enabled"),
        "real_navigation_changed_blocked_count": _count_error(validation_results, "real_navigation_changed_enabled"),
        "ui_behavior_changed_blocked_count": _count_error(validation_results, "ui_behavior_changed_enabled"),
        "persistent_policy_written_blocked_count": _count_error(
            validation_results,
            "persistent_policy_written_enabled",
        ),
        "general_behavior_changed_blocked_count": _count_error(
            validation_results,
            "general_behavior_changed_enabled",
        ),
        "semantic_or_fuzzy_match_used_blocked_count": _count_error(
            validation_results,
            "semantic_or_fuzzy_match_used_enabled",
        ),
        "exploration_blocked_count": _count_error(validation_results, "exploration_blocked_enabled"),
        "curiosity_overridden_blocked_count": _count_error(validation_results, "curiosity_overridden_enabled"),
        "mentor_override_blocked_count": _count_error(validation_results, "mentor_override_blocked_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(validation_results, "new_retention_written_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
    }
    summary["all_pre_action_consideration_candidate_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["pre_action_candidate_result_count"] == 40
        and summary["valid_pre_action_candidate_result_count"] == 1
        and summary["invalid_pre_action_candidate_result_count"] == 39
        and summary["candidate_count"] == 3
        and summary["positive_delta_candidate_count"] == 3
        and summary["pre_action_only_candidate_count"] == 3
        and summary["not_final_action_candidate_count"] == 3
        and summary["exact_key_candidate_count"] == 3
        and summary["obstacle_candidate_pass_count"] == 1
        and summary["costly_retry_candidate_pass_count"] == 1
        and summary["unclear_failure_candidate_pass_count"] == 1
        and summary["candidate_count_violation_blocked_count"] == 2
        and summary["unknown_scenario_blocked_count"] == 1
        and summary["unknown_exact_key_blocked_count"] == 1
        and summary["wrong_mapping_blocked_count"] == 3
        and summary["non_positive_delta_blocked_count"] == 2
        and summary["delta_too_high_blocked_count"] == 1
        and summary["pre_action_only_false_blocked_count"] == 1
        and summary["selected_as_final_action_blocked_count"] == 1
        and summary["wrong_consideration_source_blocked_count"] == 1
        and summary["aggregate_exact_key_false_blocked_count"] == 1
        and summary["aggregate_positive_delta_false_blocked_count"] == 1
        and summary["aggregate_pre_action_only_false_blocked_count"] == 1
        and summary["aggregate_not_final_action_false_blocked_count"] == 1
        and summary["safe_to_continue_false_blocked_count"] == 1
        and summary["empty_what_candidates_mean_blocked_count"] == 1
        and summary["empty_plain_result_blocked_count"] == 1
        and summary["production_action_selection_blocked_count"] == 1
        and summary["final_action_created_blocked_count"] == 1
        and summary["action_selected_blocked_count"] == 1
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
        "pre_action_consideration_candidate_layer_enabled": True,
        "candidate_count": summary["candidate_count"],
        "positive_delta_candidate_count": summary["positive_delta_candidate_count"],
        "pre_action_only_candidate_count": summary["pre_action_only_candidate_count"],
        "not_final_action_candidate_count": summary["not_final_action_candidate_count"],
        "exact_key_candidate_count": summary["exact_key_candidate_count"],
        "production_action_selection_added": False,
        "final_action_creation_added": False,
        "action_selection_added": False,
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


def _count_errors(validation_results: list[dict[str, Any]], error_codes: set[str]) -> int:
    return sum(1 for result in validation_results if any(error in result["error_codes"] for error in error_codes))


def _count_errors_ending(validation_results: list[dict[str, Any]], suffix: str) -> int:
    return sum(1 for result in validation_results for error in result["error_codes"] if error.endswith(suffix))
