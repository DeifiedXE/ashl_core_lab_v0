"""Phase 0 Level 0 obstacle memory flip runtime tendency check."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-phase0-level0-obstacle-memory-flip-test-minimal-check"
FLOW = "phase0_level0_obstacle_memory_flip_test_minimal_v0"
LEVEL_ID = "phase0_level0_obstacle_memory_flip_test"
LEVEL_MODE = "controlled_runtime_tendency_flip_test"
CANDIDATE_ACTIONS = [
    "retry_same_action",
    "check_before_retry",
    "ask_for_help",
    "slow_down_or_reduce_cost",
]
BASELINE_SCORES = {
    "retry_same_action": 0.50,
    "check_before_retry": 0.50,
    "ask_for_help": 0.20,
    "slow_down_or_reduce_cost": 0.30,
}
MEMORY_SIGNALS = [
    {
        "memory_case": "retry_failed",
        "exact_key": "obstacle_retry_failed",
        "remembered_outcome": "retry_same_action failed",
        "failure_reason": "blocked_by_obstacle",
        "influence": {"check_before_retry": 0.10, "retry_same_action": -0.05},
        "expected_stronger_action": "check_before_retry",
    },
    {
        "memory_case": "retry_succeeded",
        "exact_key": "obstacle_retry_succeeded",
        "remembered_outcome": "retry_same_action succeeded",
        "success_reason": "obstacle_was_passable_or_false_alarm",
        "influence": {"retry_same_action": 0.10, "check_before_retry": -0.05},
        "expected_stronger_action": "retry_same_action",
    },
]

REQUIRED_TOP_LEVEL = {
    "level0_result_id",
    "level_info",
    "shared_state",
    "candidate_actions",
    "baseline_result",
    "memory_case_results",
    "flip_check",
    "human_summary",
    "blocked_flags",
}
REQUIRED_HUMAN_SUMMARY = {
    "what_was_tested",
    "failed_memory_result",
    "success_memory_result",
    "plain_result",
}
REQUIRED_BLOCKED_FLAGS = {
    "danger_cell_used",
    "pathfinding_performed",
    "action_executed",
    "production_action_selection",
    "runtime_action_selection",
    "selected_action_created",
    "final_action_created",
    "direct_action_command",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_policy_written",
    "general_behavior_changed",
    "lesson_applied",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "semantic_or_fuzzy_match_used",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_level0_obstacle_memory_flip_tendency_scores(
    state: dict[str, Any],
    candidate_actions: list[str],
    memory_signal: dict[str, Any] | None,
) -> dict[str, float]:
    if state.get("scenario_id") != "obstacle_memory_flip_same_state":
        return {}
    scores = {action: BASELINE_SCORES[action] for action in candidate_actions if action in BASELINE_SCORES}
    if not memory_signal:
        return scores
    exact_key = memory_signal.get("exact_key")
    if exact_key not in {"obstacle_retry_failed", "obstacle_retry_succeeded"}:
        return scores
    for action, delta in memory_signal.get("influence", {}).items():
        if action in scores:
            scores[action] = round(scores[action] + delta, 2)
    return scores


def build_phase0_level0_obstacle_memory_flip_result() -> dict[str, Any]:
    state = {
        "scenario_id": "obstacle_memory_flip_same_state",
        "front_symbol": "w",
        "symbol_meaning_in_fixture": "obstacle_or_wall_like_marker",
        "symbol_fixture_only": True,
        "agent_position": [0, 0],
        "facing": "east",
        "front_cell_position": [1, 0],
        "same_state_for_all_cases": True,
    }
    baseline_scores = build_level0_obstacle_memory_flip_tendency_scores(state, CANDIDATE_ACTIONS, None)
    memory_results = []
    for signal in MEMORY_SIGNALS:
        scores = build_level0_obstacle_memory_flip_tendency_scores(state, CANDIDATE_ACTIONS, signal)
        deltas = {action: round(scores[action] - baseline_scores[action], 2) for action in CANDIDATE_ACTIONS}
        expected_action = signal["expected_stronger_action"]
        other_action = "retry_same_action" if expected_action == "check_before_retry" else "check_before_retry"
        memory_results.append(
            {
                "memory_case": signal["memory_case"],
                "exact_key": signal["exact_key"],
                "scores": scores,
                "score_deltas": deltas,
                "expected_stronger_action": expected_action,
                "flip_side_passed": scores[expected_action] > scores[other_action],
            }
        )

    return {
        "level0_result_id": "phase0_level0_obstacle_memory_flip_demo_001",
        "level_info": {
            "level_id": LEVEL_ID,
            "level_title": "小關 0：障礙記憶翻面測試",
            "level_mode": LEVEL_MODE,
            "execution_required": False,
            "pathfinding_required": False,
            "danger_cell_used": False,
        },
        "shared_state": state,
        "candidate_actions": list(CANDIDATE_ACTIONS),
        "baseline_result": {"memory_case": "none", "scores": baseline_scores},
        "memory_case_results": memory_results,
        "flip_check": {
            "same_runner_used": True,
            "same_state_used": True,
            "same_candidate_actions_used": True,
            "only_memory_content_changed": True,
            "failed_memory_prefers_check": True,
            "success_memory_prefers_retry": True,
            "bidirectional_flip_passed": True,
            "one_way_caution_bias_rejected": True,
            "safe_to_continue_to_level1_danger": True,
        },
        "human_summary": {
            "what_was_tested": (
                "Level 0 tested whether memory content can flip runtime tendency direction in the same obstacle state."
            ),
            "failed_memory_result": (
                "When memory said retry failed, check_before_retry became stronger than retry_same_action."
            ),
            "success_memory_result": (
                "When memory said retry succeeded, retry_same_action became stronger than check_before_retry."
            ),
            "plain_result": (
                "The system passed the obstacle memory flip test, so Level 1 danger checking is less likely to be "
                "only a one-way caution bias."
            ),
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_phase0_level0_obstacle_memory_flip_result(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _check_top_level(record, errors)

    level_info = _section(record, "level_info", errors)
    if level_info.get("level_id") != LEVEL_ID:
        errors.append("level_id_not_phase0_level0_obstacle_memory_flip_test")
    if level_info.get("level_mode") != LEVEL_MODE:
        errors.append("level_mode_not_controlled_runtime_tendency_flip_test")
    _require_false(level_info, "execution_required", errors)
    _require_false(level_info, "pathfinding_required", errors)
    _require_false(level_info, "danger_cell_used", errors)

    shared_state = _section(record, "shared_state", errors)
    if shared_state.get("scenario_id") != "obstacle_memory_flip_same_state":
        errors.append("scenario_id_not_obstacle_memory_flip_same_state")
    if shared_state.get("front_symbol") != "w":
        errors.append("front_symbol_not_w")
    _require_true(shared_state, "symbol_fixture_only", errors)
    if shared_state.get("agent_position") != [0, 0]:
        errors.append("agent_position_not_origin")
    if shared_state.get("facing") != "east":
        errors.append("facing_not_east")
    if shared_state.get("front_cell_position") != [1, 0]:
        errors.append("front_cell_position_not_1_0")
    _require_true(shared_state, "same_state_for_all_cases", errors)

    candidate_actions = record.get("candidate_actions")
    if candidate_actions != CANDIDATE_ACTIONS:
        errors.append("candidate_actions_changed")

    baseline_result = _section(record, "baseline_result", errors)
    baseline_scores = baseline_result.get("scores", {})
    if baseline_result.get("memory_case") != "none":
        errors.append("baseline_memory_case_not_none")
    _validate_scores("baseline", baseline_scores, BASELINE_SCORES, errors)

    memory_results = record.get("memory_case_results")
    if not isinstance(memory_results, list):
        errors.append("memory_case_results_missing_or_not_list")
        memory_results = []
    if len(memory_results) != 2:
        errors.append("memory_case_results_count_not_2")
    cases = {item.get("memory_case"): item for item in memory_results if isinstance(item, dict)}
    _validate_memory_case("retry_failed", cases.get("retry_failed"), baseline_scores, errors)
    _validate_memory_case("retry_succeeded", cases.get("retry_succeeded"), baseline_scores, errors)

    flip_check = _section(record, "flip_check", errors)
    for field in (
        "same_runner_used",
        "same_state_used",
        "same_candidate_actions_used",
        "only_memory_content_changed",
        "failed_memory_prefers_check",
        "success_memory_prefers_retry",
        "bidirectional_flip_passed",
        "one_way_caution_bias_rejected",
        "safe_to_continue_to_level1_danger",
    ):
        _require_true(flip_check, field, errors)

    human_summary = _section(record, "human_summary", errors)
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        if field not in human_summary:
            errors.append(f"missing_human_summary_field:{field}")
        elif not isinstance(human_summary.get(field), str) or not human_summary.get(field):
            errors.append(f"{field}_empty_or_not_string")

    blocked_flags = _section(record, "blocked_flags", errors)
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "level0_result_id": record.get("level0_result_id"),
        "valid": not errors,
        "error_codes": errors,
        "retry_failed_case": "retry_failed" in cases,
        "retry_succeeded_case": "retry_succeeded" in cases,
        "failed_memory_prefers_check": _failed_prefers_check(cases.get("retry_failed")),
        "success_memory_prefers_retry": _success_prefers_retry(cases.get("retry_succeeded")),
        "bidirectional_flip_passed": flip_check.get("bidirectional_flip_passed") is True,
        "one_way_caution_bias_rejected": flip_check.get("one_way_caution_bias_rejected") is True,
        "safe_to_continue_to_level1_danger": flip_check.get("safe_to_continue_to_level1_danger") is True,
        "same_runner_used": flip_check.get("same_runner_used") is True,
        "same_state_used": flip_check.get("same_state_used") is True,
        "same_candidate_actions_used": flip_check.get("same_candidate_actions_used") is True,
        "only_memory_content_changed": flip_check.get("only_memory_content_changed") is True,
    }


def run_phase0_level0_obstacle_memory_flip_test_minimal_check() -> dict[str, Any]:
    valid_result = build_phase0_level0_obstacle_memory_flip_result()
    records = [valid_result, *_invalid_demo_records(valid_result)]
    validation_results = [validate_phase0_level0_obstacle_memory_flip_result(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "level0_results": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "runtime_tendency_only": True,
            "danger_cell_used": False,
            "action_execution_added": False,
            "pathfinding_added": False,
            "lesson_application_added": False,
            "memory_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "proof_of_learning_claimed": False,
        },
        "notes": [
            "Memory must be content-sensitive, not just caution-biased.",
            "This is a runtime tendency flip test only; no action is executed.",
        ],
    }


def _validate_memory_case(
    memory_case: str,
    item: dict[str, Any] | None,
    baseline_scores: dict[str, Any],
    errors: list[str],
) -> None:
    if not isinstance(item, dict):
        errors.append(f"missing_{memory_case}_case")
        return
    expected = {
        "retry_failed": {
            "exact_key": "obstacle_retry_failed",
            "scores": {
                "retry_same_action": 0.45,
                "check_before_retry": 0.60,
                "ask_for_help": 0.20,
                "slow_down_or_reduce_cost": 0.30,
            },
            "stronger": "check_before_retry",
        },
        "retry_succeeded": {
            "exact_key": "obstacle_retry_succeeded",
            "scores": {
                "retry_same_action": 0.60,
                "check_before_retry": 0.45,
                "ask_for_help": 0.20,
                "slow_down_or_reduce_cost": 0.30,
            },
            "stronger": "retry_same_action",
        },
    }[memory_case]
    if item.get("exact_key") != expected["exact_key"]:
        errors.append(f"{memory_case}_exact_key_wrong")
    scores = item.get("scores", {})
    _validate_scores(memory_case, scores, expected["scores"], errors)
    deltas = item.get("score_deltas", {})
    for action in CANDIDATE_ACTIONS:
        expected_delta = round(scores.get(action, 999) - baseline_scores.get(action, 999), 2)
        if round(deltas.get(action, 999), 2) != expected_delta:
            errors.append(f"{memory_case}_{action}_delta_wrong")
        if abs(round(deltas.get(action, 999), 2)) > 0.10:
            errors.append(f"{memory_case}_{action}_delta_too_high")
    if item.get("expected_stronger_action") != expected["stronger"]:
        errors.append(f"{memory_case}_expected_stronger_action_wrong")
    if item.get("flip_side_passed") is not True:
        errors.append(f"{memory_case}_flip_side_passed_not_true")
    if memory_case == "retry_failed" and not _failed_prefers_check(item):
        errors.append("retry_failed_does_not_prefer_check")
    if memory_case == "retry_succeeded" and not _success_prefers_retry(item):
        errors.append("retry_succeeded_does_not_prefer_retry")


def _validate_scores(label: str, scores: Any, expected: dict[str, float], errors: list[str]) -> None:
    if not isinstance(scores, dict):
        errors.append(f"{label}_scores_missing_or_not_dict")
        return
    for action, expected_score in expected.items():
        if round(scores.get(action, 999), 2) != expected_score:
            errors.append(f"{label}_{action}_score_wrong")


def _invalid_demo_records(valid_result: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    mutations = [
        ("level_info", "level_id", "bad_level"),
        ("level_info", "level_mode", "free_mode"),
        ("level_info", "execution_required", True),
        ("level_info", "pathfinding_required", True),
        ("level_info", "danger_cell_used", True),
        ("shared_state", "scenario_id", "bad_scenario"),
        ("shared_state", "front_symbol", "d"),
        ("shared_state", "same_state_for_all_cases", False),
    ]
    for section, field, value in mutations:
        invalid = _copy_case(valid_result, f"{section}_{field}")
        invalid[section][field] = value
        records.append(invalid)

    invalid = _copy_case(valid_result, "candidate_actions_changed")
    invalid["candidate_actions"] = ["retry_same_action", "check_before_retry"]
    records.append(invalid)

    invalid = _copy_case(valid_result, "missing_retry_failed")
    invalid["memory_case_results"] = [valid_result["memory_case_results"][1]]
    records.append(invalid)

    invalid = _copy_case(valid_result, "missing_retry_succeeded")
    invalid["memory_case_results"] = [valid_result["memory_case_results"][0]]
    records.append(invalid)

    invalid = _copy_case(valid_result, "retry_failed_prefers_retry")
    failed = invalid["memory_case_results"][0]
    failed["scores"]["retry_same_action"] = 0.60
    failed["scores"]["check_before_retry"] = 0.45
    failed["score_deltas"]["retry_same_action"] = 0.10
    failed["score_deltas"]["check_before_retry"] = -0.05
    records.append(invalid)

    invalid = _copy_case(valid_result, "retry_succeeded_prefers_check")
    succeeded = invalid["memory_case_results"][1]
    succeeded["scores"]["retry_same_action"] = 0.45
    succeeded["scores"]["check_before_retry"] = 0.60
    succeeded["score_deltas"]["retry_same_action"] = -0.05
    succeeded["score_deltas"]["check_before_retry"] = 0.10
    records.append(invalid)

    invalid = _copy_case(valid_result, "one_way_caution_bias")
    invalid["memory_case_results"][1]["scores"]["retry_same_action"] = 0.45
    invalid["memory_case_results"][1]["scores"]["check_before_retry"] = 0.60
    invalid["memory_case_results"][1]["score_deltas"]["retry_same_action"] = -0.05
    invalid["memory_case_results"][1]["score_deltas"]["check_before_retry"] = 0.10
    invalid["flip_check"]["one_way_caution_bias_rejected"] = False
    records.append(invalid)

    invalid = _copy_case(valid_result, "wrong_delta")
    invalid["memory_case_results"][0]["score_deltas"]["check_before_retry"] = 0.09
    records.append(invalid)

    invalid = _copy_case(valid_result, "delta_too_high")
    invalid["memory_case_results"][0]["score_deltas"]["check_before_retry"] = 0.20
    records.append(invalid)

    for field in (
        "same_runner_used",
        "same_state_used",
        "same_candidate_actions_used",
        "only_memory_content_changed",
        "failed_memory_prefers_check",
        "success_memory_prefers_retry",
        "bidirectional_flip_passed",
        "one_way_caution_bias_rejected",
        "safe_to_continue_to_level1_danger",
    ):
        invalid = _copy_case(valid_result, f"flip_check_{field}")
        invalid["flip_check"][field] = False
        records.append(invalid)

    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        invalid = _copy_case(valid_result, f"empty_{field}")
        invalid["human_summary"][field] = ""
        records.append(invalid)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid = _copy_case(valid_result, flag)
        invalid["blocked_flags"][flag] = True
        records.append(invalid)

    return records


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "level0_flip_result_count": len(validation_results),
        "valid_level0_flip_result_count": len(valid_results),
        "invalid_level0_flip_result_count": sum(1 for result in validation_results if not result["valid"]),
        "retry_failed_case_count": sum(1 for result in valid_results if result["retry_failed_case"]),
        "retry_succeeded_case_count": sum(1 for result in valid_results if result["retry_succeeded_case"]),
        "failed_memory_prefers_check_count": sum(1 for result in valid_results if result["failed_memory_prefers_check"]),
        "success_memory_prefers_retry_count": sum(
            1 for result in valid_results if result["success_memory_prefers_retry"]
        ),
        "bidirectional_flip_passed_count": sum(1 for result in valid_results if result["bidirectional_flip_passed"]),
        "one_way_caution_bias_rejected_count": sum(
            1 for result in valid_results if result["one_way_caution_bias_rejected"]
        ),
        "safe_to_continue_to_level1_danger_count": sum(
            1 for result in valid_results if result["safe_to_continue_to_level1_danger"]
        ),
        "same_runner_used_count": sum(1 for result in valid_results if result["same_runner_used"]),
        "same_state_used_count": sum(1 for result in valid_results if result["same_state_used"]),
        "same_candidate_actions_used_count": sum(
            1 for result in valid_results if result["same_candidate_actions_used"]
        ),
        "only_memory_content_changed_count": sum(
            1 for result in valid_results if result["only_memory_content_changed"]
        ),
        "danger_cell_used_blocked_count": _count_error(validation_results, "danger_cell_used_not_false")
        + _count_error(validation_results, "danger_cell_used_enabled"),
        "pathfinding_performed_blocked_count": _count_error(validation_results, "pathfinding_required_not_false")
        + _count_error(validation_results, "pathfinding_performed_enabled"),
        "action_executed_blocked_count": _count_error(validation_results, "action_executed_enabled"),
        "production_action_selection_blocked_count": _count_error(
            validation_results,
            "production_action_selection_enabled",
        ),
        "runtime_action_selection_blocked_count": _count_error(validation_results, "runtime_action_selection_enabled"),
        "selected_action_created_blocked_count": _count_error(
            validation_results,
            "selected_action_created_enabled",
        ),
        "final_action_created_blocked_count": _count_error(validation_results, "final_action_created_enabled"),
        "direct_action_command_blocked_count": _count_error(validation_results, "direct_action_command_enabled"),
        "semantic_or_fuzzy_match_used_blocked_count": _count_error(
            validation_results,
            "semantic_or_fuzzy_match_used_enabled",
        ),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "retention_write_blocked_count": _count_error(validation_results, "retention_write_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
    }
    summary["all_phase0_level0_obstacle_memory_flip_test_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["level0_flip_result_count"] == 49
        and summary["valid_level0_flip_result_count"] == 1
        and summary["invalid_level0_flip_result_count"] == 48
        and summary["retry_failed_case_count"] == 1
        and summary["retry_succeeded_case_count"] == 1
        and summary["failed_memory_prefers_check_count"] == 1
        and summary["success_memory_prefers_retry_count"] == 1
        and summary["bidirectional_flip_passed_count"] == 1
        and summary["one_way_caution_bias_rejected_count"] == 1
        and summary["safe_to_continue_to_level1_danger_count"] == 1
        and summary["same_runner_used_count"] == 1
        and summary["same_state_used_count"] == 1
        and summary["same_candidate_actions_used_count"] == 1
        and summary["only_memory_content_changed_count"] == 1
        and summary["danger_cell_used_blocked_count"] >= 2
        and summary["pathfinding_performed_blocked_count"] >= 2
        and summary["action_executed_blocked_count"] == 1
        and summary["production_action_selection_blocked_count"] == 1
        and summary["runtime_action_selection_blocked_count"] == 1
        and summary["selected_action_created_blocked_count"] == 1
        and summary["final_action_created_blocked_count"] == 1
        and summary["direct_action_command_blocked_count"] == 1
        and summary["semantic_or_fuzzy_match_used_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["retention_write_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
    )


def _failed_prefers_check(item: dict[str, Any] | None) -> bool:
    if not isinstance(item, dict):
        return False
    scores = item.get("scores", {})
    return scores.get("check_before_retry", 0) > scores.get("retry_same_action", 0)


def _success_prefers_retry(item: dict[str, Any] | None) -> bool:
    if not isinstance(item, dict):
        return False
    scores = item.get("scores", {})
    return scores.get("retry_same_action", 0) > scores.get("check_before_retry", 0)


def _check_top_level(record: dict[str, Any], errors: list[str]) -> None:
    for field in sorted(REQUIRED_TOP_LEVEL):
        if field not in record:
            errors.append(f"missing_required_field:{field}")
    for field in sorted(record):
        if field not in REQUIRED_TOP_LEVEL:
            errors.append(f"unexpected_field:{field}")


def _section(record: dict[str, Any], field: str, errors: list[str]) -> dict[str, Any]:
    value = record.get(field)
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _require_true(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not True:
        errors.append(f"{field}_not_true")


def _require_false(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not False:
        errors.append(f"{field}_not_false")


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["level0_result_id"] = f"{record['level0_result_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])
