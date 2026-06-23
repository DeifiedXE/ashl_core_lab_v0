"""Approval boundary from arbitration selected_action to future final_action."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_selected_action_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_selected_action_record,
    run_sandbox_candidate_ordering_arbitration_selected_action_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_selected_action_record,
)


COMMAND = "run-sandbox-candidate-ordering-arbitration-final-action-approval-boundary-minimal-check"
FLOW = "sandbox_candidate_ordering_arbitration_final_action_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingArbitrationFinalActionApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b141"
BOUNDARY_INDEX_AFTER = "2026-06-09-b142"

REQUIRED_TOP_LEVEL_FIELDS = {
    "final_action_approval_boundary_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_sandbox_selected_action",
    "final_action_approval_boundary",
    "human_summary",
    "blocked_flags",
}

BLOCKED_FLAGS = {
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


def build_sandbox_candidate_ordering_arbitration_final_action_approval_boundary_record(
    sandbox_selected_action_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(sandbox_selected_action_record)
        if sandbox_selected_action_record is not None
        else build_sandbox_candidate_ordering_arbitration_selected_action_record()
    )
    validation = validate_sandbox_candidate_ordering_arbitration_selected_action_record(source)
    if not validation["valid"]:
        raise ValueError("sandbox_selected_action_record must validate before final_action approval boundary")

    source_summary = _source_summary(source)
    selected_action = source_summary["selected_action"]
    scenario = source_summary["scenario_id"]
    return {
        "final_action_approval_boundary_id": (
            f"sandbox_candidate_ordering_arbitration_final_action_approval_boundary_{scenario}_demo_001"
        ),
        "record_type": "sandbox_candidate_ordering_arbitration_final_action_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_sandbox_selected_action": source_summary,
        "final_action_approval_boundary": {
            "future_final_action_allowed": True,
            "allowed_next_package": "Sandbox Candidate Ordering Arbitration Final Action Minimal v0",
            "candidate_for_future_final_action": selected_action,
            "candidate_source": "sandbox_candidate_ordering_arbitration_selected_action",
            "final_action_scope": "sandbox_only",
            "final_action_created_in_this_package": False,
            "direct_command_created": False,
            "sandbox_execution_created": False,
            "execution_allowed_in_this_package": False,
            "future_direct_command_requires_separate_boundary": True,
            "future_execution_requires_separate_boundary": True,
            "future_memory_write_requires_separate_boundary": True,
            "future_retention_requires_separate_boundary": True,
            "future_predictor_influence_requires_separate_boundary": True,
            "future_production_promotion_requires_separate_boundary": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "human_summary": {
            "what_was_opened": f"Sandbox selected_action {selected_action} may enter a future final_action package.",
            "what_it_allows": "A future package may create a sandbox-only final_action from this arbitration-selected action.",
            "what_is_blocked": "This package creates no final_action, direct command, execution, persistence, memory write, predictor use, direct feed, production behavior, or proof claims.",
            "plain_result": "The arbitration selected_action can approach final_action, but no final action is created yet.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_final_action_approval_boundary_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "sandbox_candidate_ordering_arbitration_final_action_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_sandbox_selected_action"), errors, "source_sandbox_selected_action")
    boundary = _as_dict(record.get("final_action_approval_boundary"), errors, "final_action_approval_boundary")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_boundary(boundary, source, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action": source.get("selected_action"),
        "future_final_action_allowed": boundary.get("future_final_action_allowed") is True,
        "final_action_creation_blocked": boundary.get("final_action_created_in_this_package") is False
        and blocked.get("final_action_created") is False,
        "direct_command_blocked": boundary.get("direct_command_created") is False
        and blocked.get("direct_command_created") is False,
        "execution_blocked": boundary.get("sandbox_execution_created") is False
        and boundary.get("execution_allowed_in_this_package") is False
        and blocked.get("sandbox_execution_created") is False,
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


def run_sandbox_candidate_ordering_arbitration_final_action_approval_boundary_minimal_check() -> dict[str, Any]:
    source_records = run_sandbox_candidate_ordering_arbitration_selected_action_minimal_check()["valid_records"]
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_final_action_approval_boundary_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_final_action_approval_boundary_record(record)
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
            "boundary_reason": "Opens an approval boundary for future sandbox-only final_action from arbitration selected_action.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Arbitration selected_action can now reach a future sandbox final_action approval boundary.",
            "what_changed": "Sandbox selected_action records may become future final_action candidates.",
            "what_is_blocked": "No final_action, direct command, execution, persistence, predictor use, direct feed, production behavior, or proof claims are created.",
            "plain_result": "The arbitration action line has a checked gate before final_action creation.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    selected = source["sandbox_selected_action"]
    source_boundary = source["source_selected_action_approval_boundary"]
    return {
        "source_selected_action_record_id": source["selected_action_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": selected["scenario_id"],
        "approved_purpose": selected["approved_purpose"],
        "candidate_family": selected["candidate_family"],
        "selected_action": selected["selected_action"],
        "selected_action_created": selected["selected_action_created"],
        "selected_action_scope": selected["selected_action_scope"],
        "selected_action_source": selected["selected_action_source"],
        "source_final_action_created": selected["final_action_created"],
        "source_direct_command_created": selected["direct_command_created"],
        "source_sandbox_execution_created": selected["sandbox_execution_created"],
        "source_execution_allowed_in_source_package": selected["execution_allowed_in_this_package"],
        "source_future_final_action_requires_separate_boundary": selected[
            "future_final_action_requires_separate_boundary"
        ],
        "source_rollback_available": selected["rollback_available"],
        "source_audit_recorded": selected["audit_recorded"],
        "source_candidate_for_future_selected_action": source_boundary["candidate_for_future_selected_action"],
        "source_arbitration_rules_preserved": selected["arbitration_rules_preserved"]
        and source_boundary["arbitration_rules_preserved"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("selected_action_created") is not True:
        errors.append("source_selected_action_created_not_true")
    if source.get("selected_action_scope") != "sandbox_only":
        errors.append("source_selected_action_scope_not_sandbox_only")
    if source.get("selected_action_source") != "arbitration_checked_selected_action_approval_boundary":
        errors.append("source_selected_action_source_not_expected")
    if source.get("selected_action") != source.get("source_candidate_for_future_selected_action"):
        errors.append("source_selected_action_not_from_approved_candidate")
    if source.get("source_arbitration_rules_preserved") is not True:
        errors.append("source_arbitration_rules_preserved_not_true")
    for field in (
        "source_final_action_created",
        "source_direct_command_created",
        "source_sandbox_execution_created",
        "source_execution_allowed_in_source_package",
    ):
        if source.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in (
        "source_future_final_action_requires_separate_boundary",
        "source_rollback_available",
        "source_audit_recorded",
    ):
        if source.get(field) is not True:
            errors.append(f"{field}_not_true")


def _validate_boundary(boundary: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "future_final_action_allowed": True,
        "allowed_next_package": "Sandbox Candidate Ordering Arbitration Final Action Minimal v0",
        "candidate_for_future_final_action": source.get("selected_action"),
        "candidate_source": "sandbox_candidate_ordering_arbitration_selected_action",
        "final_action_scope": "sandbox_only",
        "final_action_created_in_this_package": False,
        "direct_command_created": False,
        "sandbox_execution_created": False,
        "execution_allowed_in_this_package": False,
        "future_direct_command_requires_separate_boundary": True,
        "future_execution_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    for field, value in expected.items():
        if boundary.get(field) != value:
            errors.append(f"final_action_approval_boundary_{field}_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_opened", "what_it_allows", "what_is_blocked", "plain_result"):
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked_flags(blocked: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(flag for flag in BLOCKED_FLAGS if flag not in blocked)
    errors.extend(f"missing_blocked_flag:{flag}" for flag in missing)
    extra = sorted(flag for flag in blocked if flag not in BLOCKED_FLAGS)
    errors.extend(f"unexpected_blocked_flag:{flag}" for flag in extra)
    for flag in BLOCKED_FLAGS:
        if blocked.get(flag) is not False:
            errors.append(f"blocked_flags_{flag}_not_false")


def _invalid_records(first: dict[str, Any], second: dict[str, Any], third: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["final_action_approval_boundary_id"] = (
            f"{record['final_action_approval_boundary_id']}_invalid_{label}"
        )
        invalids.append(record)

    mutate(first, "bad_record_type", ("record_type",), "sandbox_final_action_boundary")
    mutate(first, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(first, "source_not_validated", ("source_sandbox_selected_action", "source_validated"), False)
    mutate(first, "source_selected_action_not_created", ("source_sandbox_selected_action", "selected_action_created"), False)
    mutate(first, "source_wrong_scope", ("source_sandbox_selected_action", "selected_action_scope"), "production")
    mutate(first, "source_wrong_candidate", ("source_sandbox_selected_action", "selected_action"), "wait_or_observe")
    mutate(first, "source_rules_not_preserved", ("source_sandbox_selected_action", "source_arbitration_rules_preserved"), False)
    mutate(first, "wrong_future_candidate", ("final_action_approval_boundary", "candidate_for_future_final_action"), "wait_or_observe")
    mutate(first, "future_not_allowed", ("final_action_approval_boundary", "future_final_action_allowed"), False)
    mutate(first, "wrong_scope", ("final_action_approval_boundary", "final_action_scope"), "production")
    mutate(first, "final_action_created", ("final_action_approval_boundary", "final_action_created_in_this_package"), True)
    mutate(first, "direct_command", ("final_action_approval_boundary", "direct_command_created"), True)
    mutate(first, "execution", ("final_action_approval_boundary", "sandbox_execution_created"), True)
    mutate(first, "execution_allowed", ("final_action_approval_boundary", "execution_allowed_in_this_package"), True)
    mutate(first, "future_direct_boundary_missing", ("final_action_approval_boundary", "future_direct_command_requires_separate_boundary"), False)
    mutate(first, "future_execution_boundary_missing", ("final_action_approval_boundary", "future_execution_requires_separate_boundary"), False)
    mutate(second, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(second, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(second, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(second, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(second, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(second, "direct_feed", ("blocked_flags", "direct_tendency_feed"), True)
    mutate(third, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(third, "raw_sum", ("blocked_flags", "raw_weighted_sum_used"), True)
    mutate(third, "purpose_changed", ("blocked_flags", "purpose_changed_by_tendency"), True)
    mutate(third, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "final_action_approval_boundary_result_count": len(validation_results),
        "valid_final_action_approval_boundary_count": len(valid),
        "invalid_final_action_approval_boundary_count": len(validation_results) - len(valid),
        "future_final_action_allowed_count": sum(1 for result in valid if result["future_final_action_allowed"]),
        "reach_front_item_final_action_candidate_count": sum(
            1 for result in valid if result["selected_action"] == "reach_front_item"
        ),
        "wait_or_observe_final_action_candidate_count": sum(
            1 for result in valid if result["selected_action"] == "wait_or_observe"
        ),
        "observe_or_alternative_probe_final_action_candidate_count": sum(
            1 for result in valid if result["selected_action"] == "observe_or_alternative_probe"
        ),
        "final_action_creation_blocked_count": sum(
            1 for result in valid if result["final_action_creation_blocked"]
        ),
        "direct_command_blocked_count": sum(1 for result in valid if result["direct_command_blocked"]),
        "execution_blocked_count": sum(1 for result in valid if result["execution_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["final_action_approval_boundary_result_count"] == 29
        and summary["valid_final_action_approval_boundary_count"] == 3
        and summary["invalid_final_action_approval_boundary_count"] == 26
        and summary["future_final_action_allowed_count"] == 3
        and summary["reach_front_item_final_action_candidate_count"] == 1
        and summary["wait_or_observe_final_action_candidate_count"] == 1
        and summary["observe_or_alternative_probe_final_action_candidate_count"] == 1
        and summary["final_action_creation_blocked_count"] == 3
        and summary["direct_command_blocked_count"] == 3
        and summary["execution_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
