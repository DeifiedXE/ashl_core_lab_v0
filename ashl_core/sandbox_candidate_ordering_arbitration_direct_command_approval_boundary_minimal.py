"""Approval boundary from arbitration final_action to future direct command."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_final_action_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_final_action_record,
    run_sandbox_candidate_ordering_arbitration_final_action_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_final_action_record,
)


COMMAND = "run-sandbox-candidate-ordering-arbitration-direct-command-approval-boundary-minimal-check"
FLOW = "sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingArbitrationDirectCommandApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b143"
BOUNDARY_INDEX_AFTER = "2026-06-09-b144"

REQUIRED_TOP_LEVEL_FIELDS = {
    "direct_command_approval_boundary_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_sandbox_final_action",
    "direct_command_approval_boundary",
    "human_summary",
    "blocked_flags",
}

BLOCKED_FLAGS = {
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


def build_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_record(
    sandbox_final_action_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(sandbox_final_action_record)
        if sandbox_final_action_record is not None
        else build_sandbox_candidate_ordering_arbitration_final_action_record()
    )
    validation = validate_sandbox_candidate_ordering_arbitration_final_action_record(source)
    if not validation["valid"]:
        raise ValueError("sandbox_final_action_record must validate before direct command approval boundary")

    source_summary = _source_summary(source)
    final_action = source_summary["final_action"]
    scenario = source_summary["scenario_id"]
    direct_command = f"sandbox.arbitration.{final_action}"
    return {
        "direct_command_approval_boundary_id": (
            f"sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_{scenario}_demo_001"
        ),
        "record_type": "sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_sandbox_final_action": source_summary,
        "direct_command_approval_boundary": {
            "future_direct_command_allowed": True,
            "allowed_next_package": "Sandbox Candidate Ordering Arbitration Direct Command Minimal v0",
            "candidate_for_future_direct_command": direct_command,
            "candidate_source": "sandbox_candidate_ordering_arbitration_final_action",
            "direct_command_scope": "sandbox_only",
            "direct_command_created_in_this_package": False,
            "sandbox_execution_created": False,
            "execution_allowed_in_this_package": False,
            "future_execution_requires_separate_boundary": True,
            "future_memory_write_requires_separate_boundary": True,
            "future_retention_requires_separate_boundary": True,
            "future_predictor_influence_requires_separate_boundary": True,
            "future_production_promotion_requires_separate_boundary": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "human_summary": {
            "what_was_opened": f"Sandbox final_action {final_action} may enter a future direct command package.",
            "what_it_allows": "A future package may create a sandbox-only direct command from this arbitration final_action.",
            "what_is_blocked": "This package creates no direct command, execution, persistence, memory write, predictor use, direct feed, production behavior, or proof claims.",
            "plain_result": "The final action can approach direct command, but no command is created yet.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_sandbox_final_action"), errors, "source_sandbox_final_action")
    boundary = _as_dict(record.get("direct_command_approval_boundary"), errors, "direct_command_approval_boundary")
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
        "final_action": source.get("final_action"),
        "future_direct_command_allowed": boundary.get("future_direct_command_allowed") is True,
        "direct_command_creation_blocked": boundary.get("direct_command_created_in_this_package") is False
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


def run_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal_check() -> dict[str, Any]:
    source_records = run_sandbox_candidate_ordering_arbitration_final_action_minimal_check()["valid_records"]
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_record(record)
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
            "boundary_reason": "Opens an approval boundary for future sandbox-only direct command from arbitration final_action.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Arbitration final_action can now reach a future sandbox direct-command approval boundary.",
            "what_changed": "Sandbox final_action records may become future direct-command candidates.",
            "what_is_blocked": "No direct command, execution, persistence, predictor use, direct feed, production behavior, or proof claims are created.",
            "plain_result": "The arbitration action line has a checked gate before direct command creation.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    final = source["sandbox_final_action"]
    source_boundary = source["source_final_action_approval_boundary"]
    return {
        "source_final_action_record_id": source["final_action_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": final["scenario_id"],
        "approved_purpose": final["approved_purpose"],
        "candidate_family": final["candidate_family"],
        "source_selected_action": final["source_selected_action"],
        "final_action": final["final_action"],
        "final_action_created": final["final_action_created"],
        "final_action_scope": final["final_action_scope"],
        "final_action_source": final["final_action_source"],
        "source_direct_command_created": final["direct_command_created"],
        "source_sandbox_execution_created": final["sandbox_execution_created"],
        "source_execution_allowed_in_source_package": final["execution_allowed_in_this_package"],
        "source_future_direct_command_requires_separate_boundary": final[
            "future_direct_command_requires_separate_boundary"
        ],
        "source_future_execution_requires_separate_boundary": final["future_execution_requires_separate_boundary"],
        "source_rollback_available": final["rollback_available"],
        "source_audit_recorded": final["audit_recorded"],
        "source_candidate_for_future_final_action": source_boundary["candidate_for_future_final_action"],
        "source_arbitration_rules_preserved": final["arbitration_rules_preserved"]
        and source_boundary["source_arbitration_rules_preserved"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("final_action_created") is not True:
        errors.append("source_final_action_created_not_true")
    if source.get("final_action_scope") != "sandbox_only":
        errors.append("source_final_action_scope_not_sandbox_only")
    if source.get("final_action_source") != "sandbox_candidate_ordering_arbitration_final_action_approval_boundary":
        errors.append("source_final_action_source_not_expected")
    if source.get("final_action") != source.get("source_candidate_for_future_final_action"):
        errors.append("source_final_action_not_from_approved_candidate")
    if source.get("source_arbitration_rules_preserved") is not True:
        errors.append("source_arbitration_rules_preserved_not_true")
    for field in (
        "source_direct_command_created",
        "source_sandbox_execution_created",
        "source_execution_allowed_in_source_package",
    ):
        if source.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in (
        "source_future_direct_command_requires_separate_boundary",
        "source_future_execution_requires_separate_boundary",
        "source_rollback_available",
        "source_audit_recorded",
    ):
        if source.get(field) is not True:
            errors.append(f"{field}_not_true")


def _validate_boundary(boundary: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "future_direct_command_allowed": True,
        "allowed_next_package": "Sandbox Candidate Ordering Arbitration Direct Command Minimal v0",
        "candidate_for_future_direct_command": f"sandbox.arbitration.{source.get('final_action')}",
        "candidate_source": "sandbox_candidate_ordering_arbitration_final_action",
        "direct_command_scope": "sandbox_only",
        "direct_command_created_in_this_package": False,
        "sandbox_execution_created": False,
        "execution_allowed_in_this_package": False,
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
            errors.append(f"direct_command_approval_boundary_{field}_not_expected")


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
        record["direct_command_approval_boundary_id"] = (
            f"{record['direct_command_approval_boundary_id']}_invalid_{label}"
        )
        invalids.append(record)

    mutate(first, "bad_record_type", ("record_type",), "sandbox_direct_command_boundary")
    mutate(first, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(first, "source_not_validated", ("source_sandbox_final_action", "source_validated"), False)
    mutate(first, "source_final_action_not_created", ("source_sandbox_final_action", "final_action_created"), False)
    mutate(first, "source_wrong_scope", ("source_sandbox_final_action", "final_action_scope"), "production")
    mutate(first, "source_direct_command_created", ("source_sandbox_final_action", "source_direct_command_created"), True)
    mutate(first, "source_rules_not_preserved", ("source_sandbox_final_action", "source_arbitration_rules_preserved"), False)
    mutate(first, "wrong_future_command", ("direct_command_approval_boundary", "candidate_for_future_direct_command"), "sandbox.arbitration.wait")
    mutate(first, "future_not_allowed", ("direct_command_approval_boundary", "future_direct_command_allowed"), False)
    mutate(first, "wrong_command_scope", ("direct_command_approval_boundary", "direct_command_scope"), "production")
    mutate(first, "direct_command_created", ("direct_command_approval_boundary", "direct_command_created_in_this_package"), True)
    mutate(first, "execution", ("direct_command_approval_boundary", "sandbox_execution_created"), True)
    mutate(first, "execution_allowed", ("direct_command_approval_boundary", "execution_allowed_in_this_package"), True)
    mutate(first, "future_execution_boundary_missing", ("direct_command_approval_boundary", "future_execution_requires_separate_boundary"), False)
    mutate(first, "rollback_missing", ("direct_command_approval_boundary", "rollback_available"), False)
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
        "direct_command_approval_boundary_result_count": len(validation_results),
        "valid_direct_command_approval_boundary_count": len(valid),
        "invalid_direct_command_approval_boundary_count": len(validation_results) - len(valid),
        "future_direct_command_allowed_count": sum(1 for result in valid if result["future_direct_command_allowed"]),
        "reach_front_item_direct_command_candidate_count": sum(
            1 for result in valid if result["final_action"] == "reach_front_item"
        ),
        "wait_or_observe_direct_command_candidate_count": sum(
            1 for result in valid if result["final_action"] == "wait_or_observe"
        ),
        "observe_or_alternative_probe_direct_command_candidate_count": sum(
            1 for result in valid if result["final_action"] == "observe_or_alternative_probe"
        ),
        "direct_command_creation_blocked_count": sum(
            1 for result in valid if result["direct_command_creation_blocked"]
        ),
        "execution_blocked_count": sum(1 for result in valid if result["execution_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["direct_command_approval_boundary_result_count"] == 28
        and summary["valid_direct_command_approval_boundary_count"] == 3
        and summary["invalid_direct_command_approval_boundary_count"] == 25
        and summary["future_direct_command_allowed_count"] == 3
        and summary["reach_front_item_direct_command_candidate_count"] == 1
        and summary["wait_or_observe_direct_command_candidate_count"] == 1
        and summary["observe_or_alternative_probe_direct_command_candidate_count"] == 1
        and summary["direct_command_creation_blocked_count"] == 3
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
