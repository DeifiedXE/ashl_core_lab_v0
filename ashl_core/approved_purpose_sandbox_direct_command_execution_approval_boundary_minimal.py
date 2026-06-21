"""Approval boundary from approved-purpose direct_command to future execution."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .approved_purpose_sandbox_direct_command_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_approved_purpose_sandbox_direct_command_record,
    run_approved_purpose_sandbox_direct_command_minimal_check,
    validate_approved_purpose_sandbox_direct_command_record,
)


COMMAND = "run-approved-purpose-sandbox-direct-command-execution-approval-boundary-minimal-check"
FLOW = "approved_purpose_sandbox_direct_command_execution_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ApprovedPurposeSandboxDirectCommandExecutionApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b130"
BOUNDARY_INDEX_AFTER = "2026-06-09-b131"

BLOCKED_FLAGS = {
    "sandbox_action_executed",
    "production_action_selection",
    "runtime_action_selection",
    "runtime_behavior_changed",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "persistent_policy_written",
    "persistent_purpose_written",
    "semantic_vision",
    "emotion_recognition_claim",
    "user_happiness_claim",
    "unlimited_reward_seeking",
    "emotional_manipulation",
    "proof_of_learning_claim",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "execution_approval_boundary_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_sandbox_direct_command",
    "execution_approval_boundary",
    "human_summary",
    "blocked_flags",
}


def build_approved_purpose_sandbox_direct_command_execution_approval_boundary_record(
    sandbox_direct_command_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(sandbox_direct_command_record)
        if sandbox_direct_command_record is not None
        else build_approved_purpose_sandbox_direct_command_record()
    )
    source_validation = validate_approved_purpose_sandbox_direct_command_record(source)
    if not source_validation["valid"]:
        raise ValueError("sandbox_direct_command_record must validate before execution approval boundary")

    source_summary = _source_summary(source)
    purpose = source_summary["approved_purpose"]
    direct_command = source_summary["direct_command"]
    return {
        "execution_approval_boundary_id": (
            f"approved_purpose_sandbox_direct_command_execution_approval_boundary_{purpose}_demo_001"
        ),
        "record_type": "approved_purpose_sandbox_direct_command_execution_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_sandbox_direct_command": source_summary,
        "execution_approval_boundary": {
            "future_execution_allowed": True,
            "allowed_next_package": "Approved Purpose Sandbox Direct Command Execution Minimal v0",
            "candidate_for_future_execution": direct_command,
            "candidate_source": "approved_purpose_sandbox_direct_command",
            "execution_scope": "sandbox_only",
            "sandbox_action_executed_in_this_package": False,
            "execution_result_created_in_this_package": False,
            "future_outcome_observation_requires_separate_boundary": True,
            "future_memory_write_requires_separate_boundary": True,
            "future_retention_requires_separate_boundary": True,
            "future_predictor_influence_requires_separate_boundary": True,
            "future_production_promotion_requires_separate_boundary": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "human_summary": {
            "what_was_opened": f"Sandbox direct_command {direct_command} may enter a future execution package.",
            "what_it_allows": "A future package may execute this sandbox-only direct_command once.",
            "what_is_blocked": "This package executes nothing and creates no execution result, persistence, predictor access or mutation, manipulation, or proof claims.",
            "plain_result": "The direct command can approach execution, but it is not executed yet.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_approved_purpose_sandbox_direct_command_execution_approval_boundary_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "approved_purpose_sandbox_direct_command_execution_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_sandbox_direct_command"), errors, "source_sandbox_direct_command")
    boundary = _as_dict(record.get("execution_approval_boundary"), errors, "execution_approval_boundary")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_boundary(boundary, source, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "approved_purpose": source.get("approved_purpose"),
        "direct_command": source.get("direct_command"),
        "future_execution_allowed": boundary.get("future_execution_allowed") is True,
        "execution_blocked": boundary.get("sandbox_action_executed_in_this_package") is False
        and boundary.get("execution_result_created_in_this_package") is False
        and blocked.get("sandbox_action_executed") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False,
        "predictor_mutation_blocked": blocked.get("predictor_modified") is False
        and blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False,
        "manipulation_blocked": blocked.get("emotional_manipulation") is False
        and blocked.get("unlimited_reward_seeking") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
    }


def run_approved_purpose_sandbox_direct_command_execution_approval_boundary_minimal_check() -> dict[str, Any]:
    source_records = run_approved_purpose_sandbox_direct_command_minimal_check()["valid_records"]
    valid_records = [
        build_approved_purpose_sandbox_direct_command_execution_approval_boundary_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_approved_purpose_sandbox_direct_command_execution_approval_boundary_record(record)
        for record in records
    ]
    summary = _summary(validation_results)
    valid_results = [result for result in validation_results if result["valid"]]
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Opens an approval boundary for future sandbox-only execution from approved-purpose direct_command.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Approved-purpose direct_command can now reach a future sandbox execution approval boundary.",
            "what_changed": "Sandbox direct_command records may become future execution candidates.",
            "what_is_blocked": "No execution, execution result, persistence, predictor mutation, manipulation, or proof claims are created.",
            "plain_result": "The purpose-to-action line has a checked gate before execution.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    command = source["sandbox_direct_command"]
    return {
        "source_direct_command_record_id": source["direct_command_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "approved_purpose": command["approved_purpose"],
        "candidate_family": command["candidate_family"],
        "source_final_action": command["source_final_action"],
        "direct_command": command["direct_command"],
        "direct_command_created": command["direct_command_created"],
        "direct_command_scope": command["direct_command_scope"],
        "direct_command_source": command["direct_command_source"],
        "source_sandbox_action_executed": command["sandbox_action_executed"],
        "source_execution_allowed_in_source_package": command["execution_allowed_in_this_package"],
        "source_future_execution_requires_separate_boundary": command["future_execution_requires_separate_boundary"],
        "source_rollback_available": command["rollback_available"],
        "source_audit_recorded": command["audit_recorded"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("direct_command_created") is not True:
        errors.append("source_direct_command_created_not_true")
    if source.get("direct_command_scope") != "sandbox_only":
        errors.append("source_direct_command_scope_not_sandbox_only")
    if source.get("direct_command_source") != "approved_purpose_sandbox_direct_command_approval_boundary":
        errors.append("source_direct_command_source_not_expected")
    for field in ("source_sandbox_action_executed", "source_execution_allowed_in_source_package"):
        if source.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in (
        "source_future_execution_requires_separate_boundary",
        "source_rollback_available",
        "source_audit_recorded",
    ):
        if source.get(field) is not True:
            errors.append(f"{field}_not_true")


def _validate_boundary(boundary: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "future_execution_allowed": True,
        "allowed_next_package": "Approved Purpose Sandbox Direct Command Execution Minimal v0",
        "candidate_for_future_execution": source.get("direct_command"),
        "candidate_source": "approved_purpose_sandbox_direct_command",
        "execution_scope": "sandbox_only",
        "sandbox_action_executed_in_this_package": False,
        "execution_result_created_in_this_package": False,
        "future_outcome_observation_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    for field, value in expected.items():
        if boundary.get(field) != value:
            errors.append(f"execution_approval_boundary_{field}_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_opened", "what_it_allows", "what_is_blocked", "plain_result"):
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked_flags(blocked: dict[str, Any], errors: list[str]) -> None:
    for field in sorted(BLOCKED_FLAGS):
        if field not in blocked:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")


def _invalid_records(reward: dict[str, Any], mismatch: dict[str, Any], comfort: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["execution_approval_boundary_id"] = f"{record['execution_approval_boundary_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reward, "bad_record_type", ("record_type",), "approved_purpose_execution_boundary")
    mutate(reward, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reward, "source_not_validated", ("source_sandbox_direct_command", "source_validated"), False)
    mutate(reward, "source_command_not_created", ("source_sandbox_direct_command", "direct_command_created"), False)
    mutate(reward, "source_wrong_scope", ("source_sandbox_direct_command", "direct_command_scope"), "production")
    mutate(reward, "future_not_allowed", ("execution_approval_boundary", "future_execution_allowed"), False)
    mutate(reward, "wrong_future_execution", ("execution_approval_boundary", "candidate_for_future_execution"), "sandbox.approved_purpose.wait")
    mutate(reward, "wrong_scope", ("execution_approval_boundary", "execution_scope"), "production")
    mutate(reward, "executed", ("execution_approval_boundary", "sandbox_action_executed_in_this_package"), True)
    mutate(reward, "result_created", ("execution_approval_boundary", "execution_result_created_in_this_package"), True)
    mutate(reward, "future_observation_missing", ("execution_approval_boundary", "future_outcome_observation_requires_separate_boundary"), False)
    mutate(mismatch, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(mismatch, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(mismatch, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(mismatch, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(mismatch, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(mismatch, "runtime_behavior", ("blocked_flags", "runtime_behavior_changed"), True)
    mutate(comfort, "emotion_claim", ("blocked_flags", "emotion_recognition_claim"), True)
    mutate(comfort, "happiness_claim", ("blocked_flags", "user_happiness_claim"), True)
    mutate(comfort, "manipulation", ("blocked_flags", "emotional_manipulation"), True)
    mutate(comfort, "unlimited_reward", ("blocked_flags", "unlimited_reward_seeking"), True)
    mutate(comfort, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(comfort, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "execution_approval_boundary_result_count": len(validation_results),
        "valid_execution_approval_boundary_count": len(valid),
        "invalid_execution_approval_boundary_count": len(validation_results) - len(valid),
        "future_execution_allowed_count": sum(1 for result in valid if result["future_execution_allowed"]),
        "approach_or_reach_item_boundary_count": sum(
            1 for result in valid if result["approved_purpose"] == "approach_or_reach_item"
        ),
        "resolve_mismatch_boundary_count": sum(
            1 for result in valid if result["approved_purpose"] == "resolve_mismatch"
        ),
        "support_user_comfort_boundary_count": sum(
            1 for result in valid if result["approved_purpose"] == "support_user_comfort"
        ),
        "execution_blocked_count": sum(1 for result in valid if result["execution_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_mutation_blocked_count": sum(1 for result in valid if result["predictor_mutation_blocked"]),
        "manipulation_blocked_count": sum(1 for result in valid if result["manipulation_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["valid_execution_approval_boundary_count"] == 3
        and summary["invalid_execution_approval_boundary_count"] == 23
        and summary["future_execution_allowed_count"] == 3
        and summary["approach_or_reach_item_boundary_count"] == 1
        and summary["resolve_mismatch_boundary_count"] == 1
        and summary["support_user_comfort_boundary_count"] == 1
        and summary["execution_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["manipulation_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
