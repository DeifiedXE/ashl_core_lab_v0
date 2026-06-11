"""Controlled runtime action tendency memory influence A/B check."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-runtime-action-tendency-memory-influence-ab-minimal-check"
FLOW = "runtime_action_tendency_memory_influence_ab_minimal_v0"
SCENARIO_ID = "obstacle_retry_failed_same_state"

DEMO_STATE = {
    "situation": "obstacle_ahead",
    "prior_failure_exact_key": "obstacle_retry_failed",
}

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

EXPECTED_DELTAS = {
    "retry_same_action": -0.05,
    "check_before_retry": 0.10,
    "ask_for_help": 0.00,
    "slow_down_or_reduce_cost": 0.00,
}

REQUIRED_FIELDS = {
    "ab_result_id",
    "scenario_id",
    "same_runner_used",
    "same_state_used",
    "same_candidate_actions_used",
    "memory_off_result",
    "memory_on_result",
    "score_deltas",
    "runtime_tendency_changed",
    "behavior_boundary",
    "human_summary",
    "blocked_flags",
}

REQUIRED_BEHAVIOR_BOUNDARY = {
    "runtime_tendency_scores_changed",
    "final_action_selected",
    "action_executed",
    "direct_command_created",
    "real_behavior_changed",
}

REQUIRED_BLOCKED_FLAGS = {
    "final_action_created",
    "action_executed",
    "direct_action_command",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_policy_written",
    "general_behavior_changed",
    "exploration_blocked",
    "curiosity_overridden",
    "mentor_override_blocked",
    "lesson_applied",
    "memory_write",
    "new_retention_written",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_runtime_action_tendency_scores(
    state: dict[str, Any],
    candidate_actions: list[str],
    memory_influence_enabled: bool,
    memory_signal: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the deterministic tendency scorer used for both A and B."""

    scores = {action: _score_for_action(action) for action in candidate_actions}
    if memory_influence_enabled and _valid_memory_signal_for_state(memory_signal, state):
        for action, delta in memory_signal.get("influence", {}).items():
            if action in scores:
                scores[action] = _round_score(scores[action] + float(delta))

    return {
        "memory_influence_enabled": bool(memory_influence_enabled),
        "scores": {action: _round_score(scores[action]) for action in candidate_actions},
    }


def build_runtime_action_tendency_memory_influence_ab_result() -> dict[str, Any]:
    state = deepcopy(DEMO_STATE)
    candidate_actions = list(CANDIDATE_ACTIONS)
    memory_signal = _memory_signal()
    memory_off_result = build_runtime_action_tendency_scores(
        state,
        candidate_actions,
        memory_influence_enabled=False,
        memory_signal=memory_signal,
    )
    memory_on_result = build_runtime_action_tendency_scores(
        state,
        candidate_actions,
        memory_influence_enabled=True,
        memory_signal=memory_signal,
    )
    score_deltas = _score_deltas(memory_off_result["scores"], memory_on_result["scores"])
    runtime_tendency_changed = any(delta != 0.0 for delta in score_deltas.values())

    return {
        "ab_result_id": "runtime_action_tendency_memory_influence_ab_demo_001",
        "scenario_id": SCENARIO_ID,
        "same_runner_used": True,
        "same_state_used": True,
        "same_candidate_actions_used": True,
        "memory_off_result": memory_off_result,
        "memory_on_result": memory_on_result,
        "score_deltas": score_deltas,
        "runtime_tendency_changed": runtime_tendency_changed,
        "behavior_boundary": {
            "runtime_tendency_scores_changed": runtime_tendency_changed,
            "final_action_selected": False,
            "action_executed": False,
            "direct_command_created": False,
            "real_behavior_changed": False,
        },
        "human_summary": {
            "memory_off": "Without memory influence, retry_same_action and check_before_retry both scored 0.50.",
            "memory_on": "With valid memory influence, check_before_retry scored 0.60 and retry_same_action scored 0.45.",
            "what_changed": "The controlled runtime tendency runner produced different scores with memory enabled.",
            "plain_result": "Retained memory changed runtime action tendency scores in this controlled A/B runner, but no action was selected or executed.",
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_runtime_action_tendency_memory_influence_ab_result(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if record.get("scenario_id") != SCENARIO_ID:
        errors.append("scenario_id_mismatch")
    if record.get("same_runner_used") is not True:
        errors.append("same_runner_used_not_true")
    if record.get("same_state_used") is not True:
        errors.append("same_state_used_not_true")
    if record.get("same_candidate_actions_used") is not True:
        errors.append("same_candidate_actions_used_not_true")

    memory_off = record.get("memory_off_result")
    if not isinstance(memory_off, dict):
        errors.append("memory_off_result_missing_or_not_dict")
        memory_off = {}
    if memory_off.get("memory_influence_enabled") is not False:
        errors.append("memory_off_influence_enabled_not_false")

    memory_on = record.get("memory_on_result")
    if not isinstance(memory_on, dict):
        errors.append("memory_on_result_missing_or_not_dict")
        memory_on = {}
    if memory_on.get("memory_influence_enabled") is not True:
        errors.append("memory_on_influence_enabled_not_true")

    off_scores = memory_off.get("scores")
    if not isinstance(off_scores, dict):
        errors.append("memory_off_scores_missing_or_not_dict")
        off_scores = {}
    on_scores = memory_on.get("scores")
    if not isinstance(on_scores, dict):
        errors.append("memory_on_scores_missing_or_not_dict")
        on_scores = {}

    for prefix, scores in (("memory_off", off_scores), ("memory_on", on_scores)):
        _validate_scores(prefix, scores, errors)

    score_deltas = record.get("score_deltas")
    if not isinstance(score_deltas, dict):
        errors.append("score_deltas_missing_or_not_dict")
        score_deltas = {}

    deltas_valid = True
    for action in CANDIDATE_ACTIONS:
        delta = score_deltas.get(action)
        if not isinstance(delta, (int, float)):
            errors.append(f"{action}_delta_not_number")
            deltas_valid = False
            continue
        expected_delta = _delta_from_scores(off_scores, on_scores, action)
        if expected_delta is not None and _round_delta(float(delta)) != expected_delta:
            errors.append(f"{action}_delta_mismatch")
            deltas_valid = False
        if _round_delta(float(delta)) != EXPECTED_DELTAS[action]:
            errors.append(f"{action}_delta_unexpected")
            deltas_valid = False

    runtime_tendency_changed = record.get("runtime_tendency_changed")
    expected_changed = _expected_runtime_tendency_changed(score_deltas) if deltas_valid else None
    if not isinstance(runtime_tendency_changed, bool):
        errors.append("runtime_tendency_changed_not_bool")
    elif expected_changed is not None and runtime_tendency_changed is not expected_changed:
        errors.append("runtime_tendency_changed_mismatch")
    elif runtime_tendency_changed is not True:
        errors.append("runtime_tendency_changed_not_true")

    behavior_boundary = record.get("behavior_boundary")
    if not isinstance(behavior_boundary, dict):
        errors.append("behavior_boundary_missing_or_not_dict")
        behavior_boundary = {}
    for field in sorted(REQUIRED_BEHAVIOR_BOUNDARY):
        if field not in behavior_boundary:
            errors.append(f"missing_behavior_boundary:{field}")
    if behavior_boundary.get("runtime_tendency_scores_changed") is not True:
        errors.append("runtime_tendency_scores_changed_not_true")
    if behavior_boundary.get("final_action_selected") is not False:
        errors.append("final_action_selected_enabled")
    if behavior_boundary.get("action_executed") is not False:
        errors.append("action_executed_enabled")
    if behavior_boundary.get("direct_command_created") is not False:
        errors.append("direct_command_created_enabled")
    if behavior_boundary.get("real_behavior_changed") is not False:
        errors.append("real_behavior_changed_enabled")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    for field in ("memory_off", "memory_on", "what_changed", "plain_result"):
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
        "ab_result_id": record.get("ab_result_id"),
        "valid": not errors,
        "error_codes": errors,
        "runtime_tendency_changed": runtime_tendency_changed is True,
        "same_runner_used": record.get("same_runner_used") is True,
        "same_state_used": record.get("same_state_used") is True,
        "same_candidate_actions_used": record.get("same_candidate_actions_used") is True,
        "memory_off_enabled": memory_off.get("memory_influence_enabled") is True,
        "memory_on_enabled": memory_on.get("memory_influence_enabled") is True,
        **_behavior_boundary_values(behavior_boundary),
        **_blocked_flag_values(blocked_flags),
    }


def run_runtime_action_tendency_memory_influence_ab_minimal_check() -> dict[str, Any]:
    valid_result = build_runtime_action_tendency_memory_influence_ab_result()
    records = [
        valid_result,
        *_invalid_demo_records(valid_result),
    ]
    validation_results = [
        validate_runtime_action_tendency_memory_influence_ab_result(record) for record in records
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "runtime_action_tendency_memory_influence_ab_results": records,
        "valid_human_summaries": [
            record["human_summary"]
            for record, validation in zip(records, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "The same deterministic runtime tendency runner is used for memory_off and memory_on.",
            "Memory influence changes tendency scores only; no final action is selected or executed.",
            "No direct command, real navigation, UI behavior change, persistent policy, lesson application, memory write, new retention, predictor mutation, or proof of learning is added.",
        ],
    }


def _memory_signal() -> dict[str, Any]:
    return {
        "memory_signal_id": "retained_memory_signal_obstacle_retry_failed_001",
        "exact_key": "obstacle_retry_failed",
        "source": "retained_experience_exact_key_lookup",
        "valid": True,
        "target_action_tendency": "check_before_retry",
        "influence": {
            "check_before_retry": 0.10,
            "retry_same_action": -0.05,
        },
        "blocked_flags": {
            "semantic_or_fuzzy_match": False,
            "memory_write": False,
            "new_retention_written": False,
        },
    }


def _valid_memory_signal_for_state(memory_signal: dict[str, Any] | None, state: dict[str, Any]) -> bool:
    if not isinstance(memory_signal, dict):
        return False
    blocked_flags = memory_signal.get("blocked_flags")
    if not isinstance(blocked_flags, dict) or any(blocked_flags.values()):
        return False
    return (
        memory_signal.get("valid") is True
        and memory_signal.get("source") == "retained_experience_exact_key_lookup"
        and memory_signal.get("exact_key") == state.get("prior_failure_exact_key")
        and isinstance(memory_signal.get("influence"), dict)
    )


def _score_for_action(action: str) -> float:
    return BASELINE_SCORES.get(action, 0.0)


def _round_score(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 2)


def _round_delta(value: float) -> float:
    return round(float(value), 2)


def _score_deltas(off_scores: dict[str, float], on_scores: dict[str, float]) -> dict[str, float]:
    return {
        action: _round_delta(on_scores[action] - off_scores[action])
        for action in CANDIDATE_ACTIONS
    }


def _delta_from_scores(off_scores: dict[str, Any], on_scores: dict[str, Any], action: str) -> float | None:
    off_score = off_scores.get(action)
    on_score = on_scores.get(action)
    if not isinstance(off_score, (int, float)) or not isinstance(on_score, (int, float)):
        return None
    return _round_delta(float(on_score) - float(off_score))


def _expected_runtime_tendency_changed(score_deltas: dict[str, Any]) -> bool | None:
    deltas: list[float] = []
    for action in CANDIDATE_ACTIONS:
        delta = score_deltas.get(action)
        if not isinstance(delta, (int, float)):
            return None
        deltas.append(_round_delta(float(delta)))
    return any(delta != 0.0 for delta in deltas)


def _validate_scores(prefix: str, scores: dict[str, Any], errors: list[str]) -> None:
    for action in CANDIDATE_ACTIONS:
        score = scores.get(action)
        if not isinstance(score, (int, float)):
            errors.append(f"{prefix}_{action}_score_not_number")
        elif score < 0.0 or score > 1.0:
            errors.append(f"{prefix}_{action}_score_out_of_range")


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _invalid_demo_records(valid_result: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    same_runner_false = _copy_case(valid_result, "same_runner_false")
    same_runner_false["same_runner_used"] = False
    records.append(same_runner_false)

    same_state_false = _copy_case(valid_result, "same_state_false")
    same_state_false["same_state_used"] = False
    records.append(same_state_false)

    same_candidates_false = _copy_case(valid_result, "same_candidate_actions_false")
    same_candidates_false["same_candidate_actions_used"] = False
    records.append(same_candidates_false)

    memory_off_enabled = _copy_case(valid_result, "memory_off_enabled")
    memory_off_enabled["memory_off_result"]["memory_influence_enabled"] = True
    records.append(memory_off_enabled)

    memory_on_disabled = _copy_case(valid_result, "memory_on_disabled")
    memory_on_disabled["memory_on_result"]["memory_influence_enabled"] = False
    records.append(memory_on_disabled)

    wrong_check_delta = _copy_case(valid_result, "wrong_check_before_retry_delta")
    wrong_check_delta["score_deltas"]["check_before_retry"] = 0.09
    records.append(wrong_check_delta)

    wrong_retry_delta = _copy_case(valid_result, "wrong_retry_same_action_delta")
    wrong_retry_delta["score_deltas"]["retry_same_action"] = -0.04
    records.append(wrong_retry_delta)

    changed_false = _copy_case(valid_result, "runtime_tendency_changed_false")
    changed_false["runtime_tendency_changed"] = False
    records.append(changed_false)

    final_action_selected = _copy_case(valid_result, "final_action_selected")
    final_action_selected["behavior_boundary"]["final_action_selected"] = True
    records.append(final_action_selected)

    action_executed = _copy_case(valid_result, "action_executed")
    action_executed["behavior_boundary"]["action_executed"] = True
    records.append(action_executed)

    direct_command = _copy_case(valid_result, "direct_command_created")
    direct_command["behavior_boundary"]["direct_command_created"] = True
    records.append(direct_command)

    real_behavior_changed = _copy_case(valid_result, "real_behavior_changed")
    real_behavior_changed["behavior_boundary"]["real_behavior_changed"] = True
    records.append(real_behavior_changed)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_result, flag)
        flagged["blocked_flags"][flag] = True
        records.append(flagged)

    return records


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["ab_result_id"] = f"{record['ab_result_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "runtime_tendency_ab_result_count": len(validation_results),
        "valid_runtime_tendency_ab_result_count": len(valid_results),
        "invalid_runtime_tendency_ab_result_count": sum(1 for result in validation_results if not result["valid"]),
        "runtime_tendency_changed_count": sum(1 for result in valid_results if result["runtime_tendency_changed"]),
        "same_runner_violation_blocked_count": _count_error(validation_results, "same_runner_used_not_true"),
        "same_state_violation_blocked_count": _count_error(validation_results, "same_state_used_not_true"),
        "same_candidate_actions_violation_blocked_count": _count_error(
            validation_results, "same_candidate_actions_used_not_true"
        ),
        "memory_off_enabled_violation_blocked_count": _count_error(
            validation_results, "memory_off_influence_enabled_not_false"
        ),
        "memory_on_disabled_violation_blocked_count": _count_error(
            validation_results, "memory_on_influence_enabled_not_true"
        ),
        "wrong_check_before_retry_delta_blocked_count": _count_error(
            validation_results, "check_before_retry_delta_unexpected"
        ),
        "wrong_retry_same_action_delta_blocked_count": _count_error(
            validation_results, "retry_same_action_delta_unexpected"
        ),
        "runtime_tendency_changed_false_blocked_count": _count_error(
            validation_results, "runtime_tendency_changed_mismatch"
        ),
        "final_action_selected_blocked_count": _count_error(validation_results, "final_action_selected_enabled"),
        "action_executed_blocked_count": _count_error(validation_results, "action_executed_enabled"),
        "direct_command_created_blocked_count": _count_error(validation_results, "direct_command_created_enabled"),
        "real_behavior_changed_blocked_count": _count_error(validation_results, "real_behavior_changed_enabled"),
        "final_action_created_blocked_count": _count_error(validation_results, "final_action_created_enabled"),
        "direct_action_command_blocked_count": _count_error(validation_results, "direct_action_command_enabled"),
        "real_navigation_changed_blocked_count": _count_error(validation_results, "real_navigation_changed_enabled"),
        "ui_behavior_changed_blocked_count": _count_error(validation_results, "ui_behavior_changed_enabled"),
        "persistent_policy_written_blocked_count": _count_error(
            validation_results, "persistent_policy_written_enabled"
        ),
        "general_behavior_changed_blocked_count": _count_error(
            validation_results, "general_behavior_changed_enabled"
        ),
        "exploration_blocked_count": _count_error(validation_results, "exploration_blocked_enabled"),
        "curiosity_overridden_blocked_count": _count_error(validation_results, "curiosity_overridden_enabled"),
        "mentor_override_blocked_count": _count_error(validation_results, "mentor_override_blocked_enabled"),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(validation_results, "new_retention_written_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
        "final_action_created_count": _count_valid_flag(valid_results, "final_action_created"),
        "action_executed_count": _count_valid_flag(valid_results, "action_executed"),
        "direct_action_command_count": _count_valid_flag(valid_results, "direct_action_command"),
        "real_navigation_changed_count": _count_valid_flag(valid_results, "real_navigation_changed"),
        "ui_behavior_changed_count": _count_valid_flag(valid_results, "ui_behavior_changed"),
        "persistent_policy_written_count": _count_valid_flag(valid_results, "persistent_policy_written"),
        "general_behavior_changed_count": _count_valid_flag(valid_results, "general_behavior_changed"),
        "exploration_blocked_valid_count": _count_valid_flag(valid_results, "exploration_blocked"),
        "curiosity_overridden_count": _count_valid_flag(valid_results, "curiosity_overridden"),
        "mentor_override_blocked_valid_count": _count_valid_flag(valid_results, "mentor_override_blocked"),
        "lesson_applied_count": _count_valid_flag(valid_results, "lesson_applied"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "new_retention_written_count": _count_valid_flag(valid_results, "new_retention_written"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_runtime_action_tendency_memory_influence_ab_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["runtime_tendency_ab_result_count"] == 28
        and summary["valid_runtime_tendency_ab_result_count"] == 1
        and summary["invalid_runtime_tendency_ab_result_count"] == 27
        and summary["runtime_tendency_changed_count"] == 1
        and summary["same_runner_violation_blocked_count"] == 1
        and summary["same_state_violation_blocked_count"] == 1
        and summary["same_candidate_actions_violation_blocked_count"] == 1
        and summary["memory_off_enabled_violation_blocked_count"] == 1
        and summary["memory_on_disabled_violation_blocked_count"] == 1
        and summary["wrong_check_before_retry_delta_blocked_count"] == 1
        and summary["wrong_retry_same_action_delta_blocked_count"] == 1
        and summary["runtime_tendency_changed_false_blocked_count"] == 1
        and summary["final_action_selected_blocked_count"] == 1
        and summary["action_executed_blocked_count"] == 2
        and summary["direct_command_created_blocked_count"] == 1
        and summary["real_behavior_changed_blocked_count"] == 1
        and summary["final_action_created_blocked_count"] == 1
        and summary["direct_action_command_blocked_count"] == 1
        and summary["real_navigation_changed_blocked_count"] == 1
        and summary["ui_behavior_changed_blocked_count"] == 1
        and summary["persistent_policy_written_blocked_count"] == 1
        and summary["general_behavior_changed_blocked_count"] == 1
        and summary["exploration_blocked_count"] == 1
        and summary["curiosity_overridden_blocked_count"] == 1
        and summary["mentor_override_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["new_retention_written_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["final_action_created_count"] == 0
        and summary["action_executed_count"] == 0
        and summary["direct_action_command_count"] == 0
        and summary["real_navigation_changed_count"] == 0
        and summary["ui_behavior_changed_count"] == 0
        and summary["persistent_policy_written_count"] == 0
        and summary["general_behavior_changed_count"] == 0
        and summary["exploration_blocked_valid_count"] == 0
        and summary["curiosity_overridden_count"] == 0
        and summary["mentor_override_blocked_valid_count"] == 0
        and summary["lesson_applied_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["new_retention_written_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int | str]:
    return {
        "runtime_action_tendency_memory_influence_ab_minimal_enabled": True,
        "same_runner_used": True,
        "same_state_used": True,
        "same_candidate_actions_used": True,
        "memory_influence_changes_runtime_tendency_scores": True,
        "runtime_tendency_scores_only": True,
        "final_action_creation_added": False,
        "action_execution_added": False,
        "direct_action_command_added": False,
        "real_navigation_change_added": False,
        "ui_behavior_change_added": False,
        "persistent_policy_write_added": False,
        "general_behavior_change_added": False,
        "exploration_blocking_added": False,
        "curiosity_override_added": False,
        "mentor_override_blocking_added": False,
        "lesson_application_added": False,
        "memory_write_added": False,
        "new_retention_write_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "valid_runtime_tendency_ab_result_count": summary["valid_runtime_tendency_ab_result_count"],
        "runtime_tendency_changed_count": summary["runtime_tendency_changed_count"],
        "final_action_created_count": summary["final_action_created_count"],
        "action_executed_count": summary["action_executed_count"],
        "direct_action_command_count": summary["direct_action_command_count"],
        "real_navigation_changed_count": summary["real_navigation_changed_count"],
        "ui_behavior_changed_count": summary["ui_behavior_changed_count"],
        "persistent_policy_written_count": summary["persistent_policy_written_count"],
        "general_behavior_changed_count": summary["general_behavior_changed_count"],
        "memory_write_count": summary["memory_write_count"],
        "new_retention_written_count": summary["new_retention_written_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _behavior_boundary_values(behavior_boundary: dict[str, Any]) -> dict[str, bool]:
    return {
        "final_action_selected": behavior_boundary.get("final_action_selected") is True,
        "action_executed_boundary": behavior_boundary.get("action_executed") is True,
        "direct_command_created": behavior_boundary.get("direct_command_created") is True,
        "real_behavior_changed": behavior_boundary.get("real_behavior_changed") is True,
    }


def _blocked_flag_values(blocked_flags: dict[str, Any]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
