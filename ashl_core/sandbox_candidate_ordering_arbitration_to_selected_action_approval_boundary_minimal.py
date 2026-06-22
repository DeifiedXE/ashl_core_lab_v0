"""Approval boundary from arbitration-checked ordering to future sandbox selected_action."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_signal_arbitration_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_signal_arbitration_record,
    run_sandbox_candidate_ordering_signal_arbitration_minimal_check,
    validate_sandbox_candidate_ordering_signal_arbitration_record,
)


COMMAND = "run-sandbox-candidate-ordering-arbitration-to-selected-action-approval-boundary-minimal-check"
FLOW = "sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingArbitrationToSelectedActionApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b139"
BOUNDARY_INDEX_AFTER = "2026-06-09-b140"

REQUIRED_TOP_LEVEL_FIELDS = {
    "approval_boundary_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_signal_arbitration",
    "selected_action_approval_boundary",
    "human_summary",
    "blocked_flags",
}

BLOCKED_FLAGS = {
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "sandbox_execution_created",
    "runtime_behavior_changed",
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


def build_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_record(
    signal_arbitration_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(signal_arbitration_record)
        if signal_arbitration_record is not None
        else build_sandbox_candidate_ordering_signal_arbitration_record()
    )
    validation = validate_sandbox_candidate_ordering_signal_arbitration_record(source)
    if not validation["valid"]:
        raise ValueError("signal_arbitration_record must validate before selected_action approval boundary")

    source_summary = _source_summary(source)
    candidate = source_summary["top_ranked_candidate"]
    scenario = source_summary["scenario_id"]
    return {
        "approval_boundary_id": (
            "sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_"
            f"{scenario}_demo_001"
        ),
        "record_type": "sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_signal_arbitration": source_summary,
        "selected_action_approval_boundary": {
            "future_selected_action_allowed": True,
            "allowed_next_package": "Sandbox Candidate Ordering Arbitration Selected Action Minimal v0",
            "candidate_for_future_selected_action": candidate,
            "candidate_source": "top_ranked_arbitration_checked_sandbox_ordering",
            "selected_action_scope": "sandbox_only",
            "selected_action_created_in_this_package": False,
            "final_action_created": False,
            "direct_command_created": False,
            "sandbox_execution_created": False,
            "execution_allowed_in_this_package": False,
            "future_final_action_requires_separate_boundary": True,
            "future_direct_command_requires_separate_boundary": True,
            "future_execution_requires_separate_boundary": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "human_summary": {
            "what_was_opened": "A future sandbox selected_action approval boundary was opened from arbitration-checked candidate ordering.",
            "what_it_allows": f"A future package may create a sandbox selected_action for {candidate}.",
            "what_is_blocked": "This package does not create selected_action, final_action, direct command, execution, persistence, memory write, predictor use, direct endocrine/tendency feed, production behavior, or proof claims.",
            "plain_result": "Arbitration-checked ordering may approach selected_action, but no action is selected yet.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_signal_arbitration"), errors, "source_signal_arbitration")
    boundary = _as_dict(record.get("selected_action_approval_boundary"), errors, "selected_action_approval_boundary")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_boundary(boundary, source, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "candidate_for_future_selected_action": boundary.get("candidate_for_future_selected_action"),
        "future_selected_action_allowed": boundary.get("future_selected_action_allowed") is True,
        "selected_action_creation_blocked": boundary.get("selected_action_created_in_this_package") is False
        and blocked.get("selected_action_created") is False,
        "final_action_blocked": boundary.get("final_action_created") is False
        and blocked.get("final_action_created") is False,
        "direct_command_blocked": boundary.get("direct_command_created") is False
        and blocked.get("direct_command_created") is False,
        "execution_blocked": boundary.get("sandbox_execution_created") is False
        and boundary.get("execution_allowed_in_this_package") is False
        and blocked.get("sandbox_execution_created") is False,
        "arbitration_rules_preserved": source.get("purpose_scope_preserved") is True
        and source.get("affordance_gate_applied") is True
        and source.get("feedback_within_purpose_checked") is True
        and source.get("tendency_limited_checked") is True
        and source.get("raw_weighted_sum_used") is False,
        "purpose_creation_blocked": blocked.get("purpose_created_from_affordance") is False
        and blocked.get("purpose_created_from_feedback") is False
        and blocked.get("purpose_created_from_tendency") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False,
        "predictor_use_blocked": blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False,
        "direct_feed_blocked": blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
    }


def run_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_minimal_check() -> dict[str, Any]:
    source_records = run_sandbox_candidate_ordering_signal_arbitration_minimal_check()["valid_records"]
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_to_selected_action_approval_boundary_record(record)
        for record in records
    ]
    valid_results = [result for result in validation_results if result["valid"]]
    summary = _summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Opens a selected_action approval boundary from arbitration-checked sandbox candidate ordering.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Arbitration-checked ordering can now reach a future sandbox selected_action approval boundary.",
            "what_changed": "Top-ranked arbitration-checked advisory candidates may become future selected_action candidates.",
            "plain_result": "The signal-arbitrated action line has a checked gate before selected_action creation.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    result = source["arbitration_result"]
    signals = source["source_signals"]
    return {
        "source_arbitration_record_id": source["arbitration_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": result["scenario_id"],
        "approved_purpose": signals["approved_purpose"],
        "candidate_family": signals["candidate_family"],
        "candidate_actions_after_arbitration": list(result["candidate_actions_after_arbitration"]),
        "top_ranked_candidate": result["primary_ranked_action"],
        "purpose_scope_preserved": result["purpose_scope_preserved"],
        "affordance_gate_applied": result["affordance_gate_applied"],
        "feedback_within_purpose_checked": result["feedback_applied_only_within_purpose"],
        "tendency_limited_checked": result["tendency_used_only_as_tie_break_or_small_nudge"],
        "raw_weighted_sum_used": signals["raw_weighted_sum_used"],
        "source_action_intent_created": result["action_intent_created"],
        "source_selected_action_created": result["selected_action_created"],
        "source_final_action_created": result["final_action_created"],
        "source_direct_command_created": result["direct_command_created"],
        "source_sandbox_execution_created": result["sandbox_execution_created"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    actions = source.get("candidate_actions_after_arbitration")
    if not isinstance(actions, list) or not actions:
        errors.append("candidate_actions_after_arbitration_empty")
    if source.get("top_ranked_candidate") != (actions[0] if isinstance(actions, list) and actions else None):
        errors.append("top_ranked_candidate_not_first")
    for field in (
        "purpose_scope_preserved",
        "affordance_gate_applied",
        "feedback_within_purpose_checked",
        "tendency_limited_checked",
    ):
        if source.get(field) is not True:
            errors.append(f"source_{field}_not_true")
    if source.get("raw_weighted_sum_used") is not False:
        errors.append("source_raw_weighted_sum_used_not_false")
    for field in (
        "source_action_intent_created",
        "source_selected_action_created",
        "source_final_action_created",
        "source_direct_command_created",
        "source_sandbox_execution_created",
    ):
        if source.get(field) is not False:
            errors.append(f"{field}_not_false")


def _validate_boundary(boundary: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "future_selected_action_allowed": True,
        "allowed_next_package": "Sandbox Candidate Ordering Arbitration Selected Action Minimal v0",
        "candidate_for_future_selected_action": source.get("top_ranked_candidate"),
        "candidate_source": "top_ranked_arbitration_checked_sandbox_ordering",
        "selected_action_scope": "sandbox_only",
        "selected_action_created_in_this_package": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_execution_created": False,
        "execution_allowed_in_this_package": False,
        "future_final_action_requires_separate_boundary": True,
        "future_direct_command_requires_separate_boundary": True,
        "future_execution_requires_separate_boundary": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    for field, value in expected.items():
        if boundary.get(field) != value:
            errors.append(f"selected_action_approval_boundary_{field}_not_expected")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_opened", "what_it_allows", "what_is_blocked", "plain_result"):
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
        "selected_action_approval_boundary_result_count": len(validation_results),
        "valid_selected_action_approval_boundary_count": len(valid),
        "invalid_selected_action_approval_boundary_count": len(validation_results) - len(valid),
        "future_selected_action_allowed_count": sum(1 for result in valid if result["future_selected_action_allowed"]),
        "selected_action_creation_blocked_count": sum(
            1 for result in valid if result["selected_action_creation_blocked"]
        ),
        "final_action_blocked_count": sum(1 for result in valid if result["final_action_blocked"]),
        "direct_command_blocked_count": sum(1 for result in valid if result["direct_command_blocked"]),
        "execution_blocked_count": sum(1 for result in valid if result["execution_blocked"]),
        "arbitration_rules_preserved_count": sum(1 for result in valid if result["arbitration_rules_preserved"]),
        "purpose_creation_blocked_count": sum(1 for result in valid if result["purpose_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["selected_action_approval_boundary_result_count"] == 31
        and summary["valid_selected_action_approval_boundary_count"] == 3
        and summary["invalid_selected_action_approval_boundary_count"] == 28
        and summary["future_selected_action_allowed_count"] == 3
        and summary["selected_action_creation_blocked_count"] == 3
        and summary["final_action_blocked_count"] == 3
        and summary["direct_command_blocked_count"] == 3
        and summary["execution_blocked_count"] == 3
        and summary["arbitration_rules_preserved_count"] == 3
        and summary["purpose_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
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
    cases.append(with_change(first, ("boundary_index_before",), "2026-06-09-b138"))
    cases.append(with_change(first, ("boundary_index_after",), "2026-06-09-b139"))
    cases.append(with_change(first, ("boundary_change_required",), False))
    cases.append(with_change(first, ("source_signal_arbitration", "source_validated"), False))
    cases.append(with_change(first, ("source_signal_arbitration", "source_boundary_index"), "2026-06-09-b138"))
    cases.append(with_change(first, ("source_signal_arbitration", "candidate_actions_after_arbitration"), []))
    cases.append(with_change(first, ("source_signal_arbitration", "top_ranked_candidate"), "wrong"))
    cases.append(with_change(first, ("source_signal_arbitration", "purpose_scope_preserved"), False))
    cases.append(with_change(first, ("source_signal_arbitration", "affordance_gate_applied"), False))
    cases.append(with_change(first, ("source_signal_arbitration", "feedback_within_purpose_checked"), False))
    cases.append(with_change(first, ("source_signal_arbitration", "tendency_limited_checked"), False))
    cases.append(with_change(first, ("source_signal_arbitration", "raw_weighted_sum_used"), True))
    cases.append(with_change(first, ("source_signal_arbitration", "source_action_intent_created"), True))
    cases.append(with_change(first, ("source_signal_arbitration", "source_selected_action_created"), True))
    cases.append(with_change(first, ("selected_action_approval_boundary", "future_selected_action_allowed"), False))
    cases.append(with_change(first, ("selected_action_approval_boundary", "candidate_for_future_selected_action"), "wrong"))
    cases.append(with_change(second, ("selected_action_approval_boundary", "selected_action_scope"), "production"))
    cases.append(with_change(first, ("selected_action_approval_boundary", "selected_action_created_in_this_package"), True))
    cases.append(with_change(first, ("selected_action_approval_boundary", "final_action_created"), True))
    cases.append(with_change(first, ("selected_action_approval_boundary", "direct_command_created"), True))
    cases.append(with_change(first, ("selected_action_approval_boundary", "sandbox_execution_created"), True))
    cases.append(with_change(first, ("selected_action_approval_boundary", "execution_allowed_in_this_package"), True))
    cases.append(with_change(first, ("selected_action_approval_boundary", "rollback_available"), False))
    cases.append(with_change(first, ("human_summary", "plain_result"), ""))
    cases.append(with_change(first, ("blocked_flags", "selected_action_created"), True))
    cases.append(with_change(third, ("blocked_flags", "memory_write"), True))
    cases.append(with_change(first, ("blocked_flags", "proof_of_learning_claim"), True))
    return cases


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_not_dict")
        return {}
    return value
