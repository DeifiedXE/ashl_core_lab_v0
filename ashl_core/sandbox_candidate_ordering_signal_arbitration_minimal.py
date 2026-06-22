"""Arbitrate sandbox candidate-ordering signals without creating actions."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-sandbox-candidate-ordering-signal-arbitration-minimal-check"
FLOW = "sandbox_candidate_ordering_signal_arbitration_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingSignalArbitration-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b138"
BOUNDARY_INDEX_AFTER = "2026-06-09-b139"

SIGNAL_AUTHORITY_ORDER = [
    "approved_purpose_scope",
    "safety_boundary",
    "affordance_feasibility_gate",
    "approved_purpose_feedback_reorder",
    "tendency_tie_break_or_small_nudge",
]

ALLOWED_PURPOSES = {
    "approach_or_reach_item",
    "resolve_mismatch",
    "support_user_comfort",
}

SCENARIOS = {
    "item_reachable_feedback_prioritizes_reach": {
        "approved_purpose": "approach_or_reach_item",
        "candidate_family": "positive_item_interaction_candidates",
        "candidate_actions_before_arbitration": [
            "wait_or_observe",
            "reach_front_item",
            "step_toward_item",
            "fallback_stop_and_report",
        ],
        "candidate_actions_after_arbitration": [
            "reach_front_item",
            "step_toward_item",
            "wait_or_observe",
            "fallback_stop_and_report",
        ],
        "affordance_signal": {
            "front_symbol": "i",
            "candidate_checked": "reach_front_item",
            "affordance_confidence": 0.93,
            "affordance_available": True,
            "affordance_role": "feasibility_gate",
        },
        "feedback_signal": {
            "feedback_type": "positive_item_contact_feedback",
            "feedback_scope_matches_purpose": True,
            "feedback_rank_delta": -2,
            "feedback_role": "same_purpose_reorder",
        },
        "tendency_signal": {
            "tendency_source": "bounded_same_session_context",
            "tendency_score": 0.54,
            "tendency_delta": 0.04,
            "tendency_role": "tie_break_or_small_nudge",
        },
        "primary_ranked_action": "reach_front_item",
        "arbitration_reason": "purpose_allows_reach_and_affordance_available_feedback_prioritizes_reach",
    },
    "item_not_afforded_blocks_feedback_priority": {
        "approved_purpose": "approach_or_reach_item",
        "candidate_family": "positive_item_interaction_candidates",
        "candidate_actions_before_arbitration": [
            "reach_front_item",
            "wait_or_observe",
            "fallback_stop_and_report",
        ],
        "candidate_actions_after_arbitration": [
            "wait_or_observe",
            "fallback_stop_and_report",
        ],
        "affordance_signal": {
            "front_symbol": "w",
            "candidate_checked": "reach_front_item",
            "affordance_confidence": 0.08,
            "affordance_available": False,
            "affordance_role": "feasibility_gate",
        },
        "feedback_signal": {
            "feedback_type": "positive_item_contact_feedback",
            "feedback_scope_matches_purpose": True,
            "feedback_rank_delta": -2,
            "feedback_role": "same_purpose_reorder",
        },
        "tendency_signal": {
            "tendency_source": "bounded_same_session_context",
            "tendency_score": 0.57,
            "tendency_delta": 0.07,
            "tendency_role": "tie_break_or_small_nudge",
        },
        "primary_ranked_action": "wait_or_observe",
        "arbitration_reason": "affordance_gate_blocks_unavailable_reach_despite_feedback_or_tendency",
    },
    "mismatch_feedback_outranks_retry_tendency": {
        "approved_purpose": "resolve_mismatch",
        "candidate_family": "verification_or_observation_candidates",
        "candidate_actions_before_arbitration": [
            "retry_same_action_without_check",
            "check_before_retry",
            "observe_or_alternative_probe",
            "fallback_stop_and_report",
        ],
        "candidate_actions_after_arbitration": [
            "observe_or_alternative_probe",
            "check_before_retry",
            "fallback_stop_and_report",
            "retry_same_action_without_check",
        ],
        "affordance_signal": {
            "front_symbol": "unknown_or_mismatch",
            "candidate_checked": "observe_or_alternative_probe",
            "affordance_confidence": 0.74,
            "affordance_available": True,
            "affordance_role": "feasibility_gate",
        },
        "feedback_signal": {
            "feedback_type": "mismatch_resolution_observation_feedback",
            "feedback_scope_matches_purpose": True,
            "feedback_rank_delta": -2,
            "feedback_role": "same_purpose_reorder",
        },
        "tendency_signal": {
            "tendency_source": "bounded_retry_pressure",
            "tendency_score": 0.58,
            "tendency_delta": 0.08,
            "tendency_role": "tie_break_or_small_nudge",
        },
        "primary_ranked_action": "observe_or_alternative_probe",
        "arbitration_reason": "same_purpose_feedback_prioritizes_observation_over_retry_tendency",
    },
}

BLOCKED_FLAGS = {
    "purpose_created_from_affordance",
    "purpose_created_from_feedback",
    "purpose_created_from_tendency",
    "purpose_changed_by_affordance",
    "purpose_changed_by_feedback",
    "purpose_changed_by_tendency",
    "raw_weighted_sum_used",
    "affordance_used_as_desire",
    "feedback_cross_purpose_applied",
    "tendency_overrode_purpose",
    "tendency_overrode_affordance_gate",
    "action_intent_created",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "sandbox_execution_created",
    "runtime_behavior_changed",
    "feedback_persisted",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "production_behavior_changed",
    "proof_of_learning_claim",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "arbitration_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "signal_authority_order",
    "source_signals",
    "arbitration_result",
    "rollback_preview",
    "human_summary",
    "blocked_flags",
}


def build_sandbox_candidate_ordering_signal_arbitration_record(
    scenario_id: str = "item_reachable_feedback_prioritizes_reach",
) -> dict[str, Any]:
    if scenario_id not in SCENARIOS:
        raise ValueError(f"unsupported arbitration scenario: {scenario_id}")
    scenario = deepcopy(SCENARIOS[scenario_id])
    after = scenario["candidate_actions_after_arbitration"]
    return {
        "arbitration_record_id": f"sandbox_candidate_ordering_signal_arbitration_{scenario_id}_demo_001",
        "record_type": "sandbox_candidate_ordering_signal_arbitration_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "signal_authority_order": list(SIGNAL_AUTHORITY_ORDER),
        "source_signals": {
            "approved_purpose": scenario["approved_purpose"],
            "candidate_family": scenario["candidate_family"],
            "affordance_signal": scenario["affordance_signal"],
            "approved_purpose_feedback_signal": scenario["feedback_signal"],
            "tendency_signal": scenario["tendency_signal"],
            "same_purpose_scope_required": True,
            "purpose_created_by_signals": False,
            "raw_weighted_sum_used": False,
        },
        "arbitration_result": {
            "scenario_id": scenario_id,
            "candidate_actions_before_arbitration": scenario["candidate_actions_before_arbitration"],
            "candidate_actions_after_arbitration": after,
            "primary_ranked_action": scenario["primary_ranked_action"],
            "purpose_scope_preserved": True,
            "affordance_gate_applied": True,
            "feedback_applied_only_within_purpose": True,
            "tendency_used_only_as_tie_break_or_small_nudge": True,
            "candidate_ordering_is_sandbox_only": True,
            "candidate_ordering_is_advisory": True,
            "action_intent_created": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "sandbox_execution_created": False,
            "arbitration_reason": scenario["arbitration_reason"],
        },
        "rollback_preview": {
            "rollback_available": True,
            "candidate_actions_restored": list(scenario["candidate_actions_before_arbitration"]),
            "dirty_state_after_rollback": False,
            "persistent_update_performed": False,
        },
        "human_summary": {
            "what_was_arbitrated": "Approved purpose, affordance confidence, approved-purpose feedback, and tendency signals were ordered by authority.",
            "authority_order": "Purpose sets scope; safety and affordance gate feasibility; same-purpose feedback adjusts order; tendency only nudges or breaks ties.",
            "what_changed": "A sandbox-only advisory arbitration record can explain why a candidate order is valid.",
            "what_is_blocked": "Signals cannot create purpose, use raw weighted sums, create actions, execute, persist, write memory, mutate predictors, directly feed endocrine/tendency systems, or prove learning.",
            "plain_result": "The ordering signals now have a checked priority rule instead of being blindly added together.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_signal_arbitration_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "sandbox_candidate_ordering_signal_arbitration_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    if record.get("signal_authority_order") != SIGNAL_AUTHORITY_ORDER:
        errors.append("signal_authority_order_not_expected")

    source = _as_dict(record.get("source_signals"), errors, "source_signals")
    result = _as_dict(record.get("arbitration_result"), errors, "arbitration_result")
    rollback = _as_dict(record.get("rollback_preview"), errors, "rollback_preview")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_result(result, source, errors)
    _validate_rollback(rollback, result, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": result.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "primary_ranked_action": result.get("primary_ranked_action"),
        "purpose_scope_preserved": result.get("purpose_scope_preserved") is True,
        "affordance_gate_applied": result.get("affordance_gate_applied") is True,
        "feedback_within_purpose_checked": result.get("feedback_applied_only_within_purpose") is True,
        "tendency_limited_checked": result.get("tendency_used_only_as_tie_break_or_small_nudge") is True,
        "raw_weighted_sum_blocked": source.get("raw_weighted_sum_used") is False
        and blocked.get("raw_weighted_sum_used") is False,
        "purpose_creation_blocked": source.get("purpose_created_by_signals") is False
        and blocked.get("purpose_created_from_affordance") is False
        and blocked.get("purpose_created_from_feedback") is False
        and blocked.get("purpose_created_from_tendency") is False,
        "action_creation_blocked": result.get("action_intent_created") is False
        and result.get("selected_action_created") is False
        and result.get("final_action_created") is False
        and result.get("direct_command_created") is False
        and result.get("sandbox_execution_created") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False,
        "predictor_use_blocked": blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False,
        "direct_feed_blocked": blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
        "rollback_available": rollback.get("rollback_available") is True
        and rollback.get("dirty_state_after_rollback") is False,
    }


def run_sandbox_candidate_ordering_signal_arbitration_minimal_check() -> dict[str, Any]:
    valid_records = [
        build_sandbox_candidate_ordering_signal_arbitration_record(scenario_id)
        for scenario_id in SCENARIOS
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_signal_arbitration_record(record)
        for record in records
    ]
    valid_results = [result for result in validation_results if result["valid"]]
    summary = _summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Defines checked signal authority for sandbox candidate ordering arbitration.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A sandbox candidate ordering signal arbitration boundary was added.",
            "what_changed": "Approved purpose, affordance confidence, same-purpose feedback, and tendency now have a checked priority order.",
            "plain_result": "Purpose answers what to do, affordance answers whether it is possible, feedback answers what worked in this purpose, and tendency only nudges eligible candidates.",
        },
        "valid_human_summaries": [record["human_summary"] for record in valid_records],
        "valid_result_keys": [sorted(result.keys()) for result in valid_results],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    purpose = source.get("approved_purpose")
    if purpose not in ALLOWED_PURPOSES:
        errors.append("approved_purpose_not_allowed")
    if not isinstance(source.get("candidate_family"), str) or not source.get("candidate_family"):
        errors.append("candidate_family_empty")
    if source.get("same_purpose_scope_required") is not True:
        errors.append("same_purpose_scope_required_not_true")
    if source.get("purpose_created_by_signals") is not False:
        errors.append("purpose_created_by_signals_not_false")
    if source.get("raw_weighted_sum_used") is not False:
        errors.append("raw_weighted_sum_used_not_false")

    affordance = _as_dict(source.get("affordance_signal"), errors, "affordance_signal")
    feedback = _as_dict(
        source.get("approved_purpose_feedback_signal"),
        errors,
        "approved_purpose_feedback_signal",
    )
    tendency = _as_dict(source.get("tendency_signal"), errors, "tendency_signal")

    confidence = affordance.get("affordance_confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        errors.append("affordance_confidence_not_bounded")
    if affordance.get("affordance_role") != "feasibility_gate":
        errors.append("affordance_role_not_feasibility_gate")
    if not isinstance(affordance.get("affordance_available"), bool):
        errors.append("affordance_available_not_bool")

    if feedback.get("feedback_scope_matches_purpose") is not True:
        errors.append("feedback_scope_matches_purpose_not_true")
    if feedback.get("feedback_role") != "same_purpose_reorder":
        errors.append("feedback_role_not_same_purpose_reorder")

    tendency_delta = tendency.get("tendency_delta")
    if not isinstance(tendency_delta, (int, float)) or abs(tendency_delta) > 0.10:
        errors.append("tendency_delta_not_bounded")
    if tendency.get("tendency_role") != "tie_break_or_small_nudge":
        errors.append("tendency_role_not_limited")


def _validate_result(result: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    scenario_id = result.get("scenario_id")
    expected = SCENARIOS.get(scenario_id)
    if expected is None:
        errors.append("scenario_id_not_supported")
        return
    if source.get("approved_purpose") != expected["approved_purpose"]:
        errors.append("source_purpose_mismatch")
    if source.get("candidate_family") != expected["candidate_family"]:
        errors.append("source_candidate_family_mismatch")
    if result.get("candidate_actions_before_arbitration") != expected["candidate_actions_before_arbitration"]:
        errors.append("candidate_actions_before_arbitration_not_expected")
    if result.get("candidate_actions_after_arbitration") != expected["candidate_actions_after_arbitration"]:
        errors.append("candidate_actions_after_arbitration_not_expected")
    if result.get("primary_ranked_action") != expected["primary_ranked_action"]:
        errors.append("primary_ranked_action_not_expected")
    after = result.get("candidate_actions_after_arbitration")
    if isinstance(after, list) and after and after[0] != result.get("primary_ranked_action"):
        errors.append("primary_ranked_action_not_first")
    for field in (
        "purpose_scope_preserved",
        "affordance_gate_applied",
        "feedback_applied_only_within_purpose",
        "tendency_used_only_as_tie_break_or_small_nudge",
        "candidate_ordering_is_sandbox_only",
        "candidate_ordering_is_advisory",
    ):
        if result.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in (
        "action_intent_created",
        "selected_action_created",
        "final_action_created",
        "direct_command_created",
        "sandbox_execution_created",
    ):
        if result.get(field) is not False:
            errors.append(f"{field}_not_false")
    if not isinstance(result.get("arbitration_reason"), str) or not result.get("arbitration_reason"):
        errors.append("arbitration_reason_empty")


def _validate_rollback(rollback: dict[str, Any], result: dict[str, Any], errors: list[str]) -> None:
    if rollback.get("rollback_available") is not True:
        errors.append("rollback_available_not_true")
    if rollback.get("candidate_actions_restored") != result.get("candidate_actions_before_arbitration"):
        errors.append("candidate_actions_restored_not_before_order")
    if rollback.get("dirty_state_after_rollback") is not False:
        errors.append("dirty_state_after_rollback_not_false")
    if rollback.get("persistent_update_performed") is not False:
        errors.append("persistent_update_performed_not_false")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    for field in (
        "what_was_arbitrated",
        "authority_order",
        "what_changed",
        "what_is_blocked",
        "plain_result",
    ):
        if not isinstance(human.get(field), str) or not human.get(field):
            errors.append(f"{field}_empty")


def _validate_blocked(blocked: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(flag for flag in BLOCKED_FLAGS if flag not in blocked)
    errors.extend(f"missing_blocked_flag:{flag}" for flag in missing)
    extra = sorted(flag for flag in blocked if flag not in BLOCKED_FLAGS)
    errors.extend(f"unexpected_blocked_flag:{flag}" for flag in extra)
    for flag in BLOCKED_FLAGS:
        if blocked.get(flag) is not False:
            errors.append(f"{flag}_not_false")


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "arbitration_result_count": len(validation_results),
        "valid_arbitration_result_count": len(valid),
        "invalid_arbitration_result_count": len(validation_results) - len(valid),
        "purpose_scope_preserved_count": sum(1 for result in valid if result["purpose_scope_preserved"]),
        "affordance_gate_applied_count": sum(1 for result in valid if result["affordance_gate_applied"]),
        "feedback_within_purpose_checked_count": sum(
            1 for result in valid if result["feedback_within_purpose_checked"]
        ),
        "tendency_limited_checked_count": sum(1 for result in valid if result["tendency_limited_checked"]),
        "raw_weighted_sum_blocked_count": sum(1 for result in valid if result["raw_weighted_sum_blocked"]),
        "purpose_creation_blocked_count": sum(1 for result in valid if result["purpose_creation_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "rollback_available_count": sum(1 for result in valid if result["rollback_available"]),
        "affordance_blocks_unavailable_feedback_count": sum(
            1 for result in valid if result["scenario_id"] == "item_not_afforded_blocks_feedback_priority"
        ),
        "feedback_outranks_tendency_count": sum(
            1 for result in valid if result["scenario_id"] == "mismatch_feedback_outranks_retry_tendency"
        ),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["arbitration_result_count"] == 36
        and summary["valid_arbitration_result_count"] == 3
        and summary["invalid_arbitration_result_count"] == 33
        and summary["purpose_scope_preserved_count"] == 3
        and summary["affordance_gate_applied_count"] == 3
        and summary["feedback_within_purpose_checked_count"] == 3
        and summary["tendency_limited_checked_count"] == 3
        and summary["raw_weighted_sum_blocked_count"] == 3
        and summary["purpose_creation_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["rollback_available_count"] == 3
        and summary["affordance_blocks_unavailable_feedback_count"] == 1
        and summary["feedback_outranks_tendency_count"] == 1
    )


def _invalid_records(first: dict[str, Any], second: dict[str, Any], third: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def with_change(base: dict[str, Any], path: tuple[str, ...], value: Any) -> dict[str, Any]:
        record = deepcopy(base)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        return record

    cases.append(with_change(first, ("record_type",), "wrong"))
    cases.append(with_change(first, ("boundary_index_before",), "2026-06-09-b137"))
    cases.append(with_change(first, ("boundary_index_after",), "2026-06-09-b138"))
    cases.append(with_change(first, ("boundary_change_required",), False))
    cases.append(with_change(first, ("signal_authority_order",), list(reversed(SIGNAL_AUTHORITY_ORDER))))
    cases.append(with_change(first, ("source_signals", "approved_purpose"), "unsupported_purpose"))
    cases.append(with_change(first, ("source_signals", "same_purpose_scope_required"), False))
    cases.append(with_change(first, ("source_signals", "purpose_created_by_signals"), True))
    cases.append(with_change(first, ("source_signals", "raw_weighted_sum_used"), True))
    cases.append(with_change(first, ("source_signals", "affordance_signal", "affordance_confidence"), 1.2))
    cases.append(with_change(first, ("source_signals", "affordance_signal", "affordance_role"), "desire_score"))
    cases.append(with_change(first, ("source_signals", "approved_purpose_feedback_signal", "feedback_scope_matches_purpose"), False))
    cases.append(with_change(first, ("source_signals", "approved_purpose_feedback_signal", "feedback_role"), "global_reward"))
    cases.append(with_change(first, ("source_signals", "tendency_signal", "tendency_delta"), 0.25))
    cases.append(with_change(first, ("source_signals", "tendency_signal", "tendency_role"), "purpose_driver"))
    cases.append(with_change(second, ("arbitration_result", "candidate_actions_after_arbitration"), ["reach_front_item", "wait_or_observe"]))
    cases.append(with_change(third, ("arbitration_result", "primary_ranked_action"), "retry_same_action_without_check"))
    cases.append(with_change(first, ("arbitration_result", "purpose_scope_preserved"), False))
    cases.append(with_change(first, ("arbitration_result", "affordance_gate_applied"), False))
    cases.append(with_change(first, ("arbitration_result", "feedback_applied_only_within_purpose"), False))
    cases.append(with_change(first, ("arbitration_result", "tendency_used_only_as_tie_break_or_small_nudge"), False))
    cases.append(with_change(first, ("arbitration_result", "candidate_ordering_is_sandbox_only"), False))
    cases.append(with_change(first, ("arbitration_result", "candidate_ordering_is_advisory"), False))
    cases.append(with_change(first, ("arbitration_result", "action_intent_created"), True))
    cases.append(with_change(first, ("arbitration_result", "selected_action_created"), True))
    cases.append(with_change(first, ("arbitration_result", "final_action_created"), True))
    cases.append(with_change(first, ("arbitration_result", "direct_command_created"), True))
    cases.append(with_change(first, ("rollback_preview", "candidate_actions_restored"), []))
    cases.append(with_change(first, ("human_summary", "plain_result"), ""))
    cases.append(with_change(first, ("blocked_flags", "raw_weighted_sum_used"), True))
    cases.append(with_change(first, ("blocked_flags", "tendency_overrode_purpose"), True))
    cases.append(with_change(first, ("blocked_flags", "memory_write"), True))
    cases.append(with_change(first, ("blocked_flags", "predictor_modified"), True))
    return cases


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_not_dict")
        return {}
    return value
