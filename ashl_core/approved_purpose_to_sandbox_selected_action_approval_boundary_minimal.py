"""Approval boundary from approved-purpose ordering to future sandbox selected_action."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .approved_purpose_candidate_ordering_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_approved_purpose_candidate_ordering_record,
    run_approved_purpose_candidate_ordering_minimal_check,
    validate_approved_purpose_candidate_ordering_record,
)


COMMAND = "run-approved-purpose-to-sandbox-selected-action-approval-boundary-minimal-check"
FLOW = "approved_purpose_to_sandbox_selected_action_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ApprovedPurposeToSandboxSelectedActionApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b124"
BOUNDARY_INDEX_AFTER = "2026-06-09-b125"

REQUIRED_TOP_LEVEL_FIELDS = {
    "approval_boundary_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_approved_purpose_ordering",
    "selected_action_approval_boundary",
    "human_summary",
    "blocked_flags",
}
BLOCKED_FLAGS = {
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
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


def build_approved_purpose_to_sandbox_selected_action_approval_boundary_record(
    approved_purpose_ordering_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(approved_purpose_ordering_record)
        if approved_purpose_ordering_record is not None
        else build_approved_purpose_candidate_ordering_record()
    )
    source_validation = validate_approved_purpose_candidate_ordering_record(source)
    if not source_validation["valid"]:
        raise ValueError("approved_purpose_ordering_record must validate before selected_action approval boundary")

    source_summary = _source_summary(source)
    top_candidate = source_summary["top_ranked_candidate"]
    return {
        "approval_boundary_id": (
            f"approved_purpose_to_sandbox_selected_action_approval_boundary_"
            f"{source_summary['approved_purpose']}_demo_001"
        ),
        "record_type": "approved_purpose_to_sandbox_selected_action_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_approved_purpose_ordering": source_summary,
        "selected_action_approval_boundary": {
            "future_selected_action_allowed": True,
            "allowed_next_package": "Approved Purpose Sandbox Selected Action Minimal v0",
            "candidate_for_future_selected_action": top_candidate,
            "candidate_source": "top_ranked_approved_purpose_advisory_ordering",
            "selected_action_scope": "sandbox_only",
            "selected_action_created_in_this_package": False,
            "final_action_created": False,
            "direct_command_created": False,
            "sandbox_action_executed": False,
            "execution_allowed_in_this_package": False,
            "future_final_action_requires_separate_boundary": True,
            "future_direct_command_requires_separate_boundary": True,
            "future_execution_requires_separate_boundary": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "human_summary": {
            "what_was_opened": "A future sandbox selected_action approval boundary was opened from approved-purpose ordering.",
            "what_it_allows": f"A future package may create a sandbox selected_action for {top_candidate}.",
            "what_is_blocked": "This package does not create selected_action, final_action, direct command, execution, persistence, predictor mutation, manipulation, or proof claims.",
            "plain_result": "Approved-purpose ordering may now approach selected_action, but no action is selected yet.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "approved_purpose_to_sandbox_selected_action_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_approved_purpose_ordering"), errors, "source_approved_purpose_ordering")
    boundary = _as_dict(record.get("selected_action_approval_boundary"), errors, "selected_action_approval_boundary")
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
        "future_selected_action_allowed": boundary.get("future_selected_action_allowed") is True,
        "selected_action_creation_blocked": boundary.get("selected_action_created_in_this_package") is False
        and blocked.get("selected_action_created") is False,
        "final_action_blocked": boundary.get("final_action_created") is False
        and blocked.get("final_action_created") is False,
        "direct_command_blocked": boundary.get("direct_command_created") is False
        and blocked.get("direct_command_created") is False,
        "execution_blocked": boundary.get("sandbox_action_executed") is False
        and boundary.get("execution_allowed_in_this_package") is False
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


def run_approved_purpose_to_sandbox_selected_action_approval_boundary_minimal_check() -> dict[str, Any]:
    source_records = run_approved_purpose_candidate_ordering_minimal_check()["valid_records"]
    valid_records = [
        build_approved_purpose_to_sandbox_selected_action_approval_boundary_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(record)
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
            "boundary_reason": "Opens an approval boundary for future sandbox selected_action from approved-purpose ordering.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Approved-purpose ordering can now reach a future sandbox selected_action approval boundary.",
            "what_changed": "Top-ranked approved-purpose advisory candidates may become future selected_action candidates.",
            "what_is_blocked": "No selected_action, final_action, direct command, execution, persistence, predictor mutation, manipulation, or proof claims are created.",
            "plain_result": "The purpose-to-action line has a checked gate before selected_action creation.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    source_ordering = source["approved_purpose_ordering"]
    source_boundary = source["source_ordering_boundary"]
    return {
        "source_ordering_record_id": source["ordering_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "approved_purpose": source_boundary["approved_purpose"],
        "candidate_family": source_ordering["candidate_family"],
        "ordering_scope": source_ordering["ordering_scope"],
        "candidate_ordering_applied": source_ordering["candidate_ordering_applied"],
        "candidate_order_changed": source_ordering["candidate_order_changed"],
        "ordering_is_sandbox_only": source_ordering["ordering_is_sandbox_only"],
        "ordering_is_advisory": source_ordering["ordering_is_advisory"],
        "candidate_actions_after_ordering": list(source_ordering["candidate_actions_after_ordering"]),
        "top_ranked_candidate": source_ordering["candidate_actions_after_ordering"][0],
        "source_selected_action_created": source_ordering["selected_action_created"],
        "source_final_action_created": source_ordering["final_action_created"],
        "source_direct_command_created": source_ordering["direct_command_created"],
        "source_sandbox_action_executed": source_ordering["sandbox_action_executed"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("candidate_ordering_applied") is not True:
        errors.append("source_candidate_ordering_applied_not_true")
    if source.get("candidate_order_changed") is not True:
        errors.append("source_candidate_order_changed_not_true")
    if source.get("ordering_is_sandbox_only") is not True:
        errors.append("source_ordering_is_sandbox_only_not_true")
    if source.get("ordering_is_advisory") is not True:
        errors.append("source_ordering_is_advisory_not_true")
    actions = source.get("candidate_actions_after_ordering")
    if not isinstance(actions, list) or not actions:
        errors.append("source_candidate_actions_after_ordering_empty")
    if source.get("top_ranked_candidate") != (actions[0] if isinstance(actions, list) and actions else None):
        errors.append("source_top_ranked_candidate_not_expected")
    for field in (
        "source_selected_action_created",
        "source_final_action_created",
        "source_direct_command_created",
        "source_sandbox_action_executed",
    ):
        if source.get(field) is not False:
            errors.append(f"{field}_not_false")


def _validate_boundary(boundary: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "future_selected_action_allowed": True,
        "allowed_next_package": "Approved Purpose Sandbox Selected Action Minimal v0",
        "candidate_for_future_selected_action": source.get("top_ranked_candidate"),
        "candidate_source": "top_ranked_approved_purpose_advisory_ordering",
        "selected_action_scope": "sandbox_only",
        "selected_action_created_in_this_package": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_action_executed": False,
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
        record["approval_boundary_id"] = f"{record['approval_boundary_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reward, "bad_record_type", ("record_type",), "approved_purpose_selected_action")
    mutate(reward, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reward, "source_not_validated", ("source_approved_purpose_ordering", "source_validated"), False)
    mutate(reward, "source_ordering_not_applied", ("source_approved_purpose_ordering", "candidate_ordering_applied"), False)
    mutate(reward, "source_not_advisory", ("source_approved_purpose_ordering", "ordering_is_advisory"), False)
    mutate(reward, "source_selected_action", ("source_approved_purpose_ordering", "source_selected_action_created"), True)
    mutate(reward, "future_not_allowed", ("selected_action_approval_boundary", "future_selected_action_allowed"), False)
    mutate(reward, "wrong_future_candidate", ("selected_action_approval_boundary", "candidate_for_future_selected_action"), "wait_or_observe")
    mutate(reward, "wrong_scope", ("selected_action_approval_boundary", "selected_action_scope"), "production")
    mutate(reward, "selected_action_created", ("selected_action_approval_boundary", "selected_action_created_in_this_package"), True)
    mutate(reward, "final_action", ("selected_action_approval_boundary", "final_action_created"), True)
    mutate(reward, "direct_command", ("selected_action_approval_boundary", "direct_command_created"), True)
    mutate(reward, "execution", ("selected_action_approval_boundary", "sandbox_action_executed"), True)
    mutate(reward, "execution_allowed", ("selected_action_approval_boundary", "execution_allowed_in_this_package"), True)
    mutate(reward, "rollback_missing", ("selected_action_approval_boundary", "rollback_available"), False)
    mutate(mismatch, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(mismatch, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(mismatch, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(mismatch, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(mismatch, "runtime_behavior", ("blocked_flags", "runtime_behavior_changed"), True)
    mutate(comfort, "emotion_claim", ("blocked_flags", "emotion_recognition_claim"), True)
    mutate(comfort, "happiness_claim", ("blocked_flags", "user_happiness_claim"), True)
    mutate(comfort, "manipulation", ("blocked_flags", "emotional_manipulation"), True)
    mutate(comfort, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(comfort, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "selected_action_approval_boundary_result_count": len(validation_results),
        "valid_selected_action_approval_boundary_count": len(valid),
        "invalid_selected_action_approval_boundary_count": len(validation_results) - len(valid),
        "future_selected_action_allowed_count": sum(
            1 for result in valid if result["future_selected_action_allowed"]
        ),
        "approach_or_reach_item_boundary_count": sum(
            1 for result in valid if result["approved_purpose"] == "approach_or_reach_item"
        ),
        "resolve_mismatch_boundary_count": sum(
            1 for result in valid if result["approved_purpose"] == "resolve_mismatch"
        ),
        "support_user_comfort_boundary_count": sum(
            1 for result in valid if result["approved_purpose"] == "support_user_comfort"
        ),
        "selected_action_creation_blocked_count": sum(
            1 for result in valid if result["selected_action_creation_blocked"]
        ),
        "final_action_blocked_count": sum(1 for result in valid if result["final_action_blocked"]),
        "direct_command_blocked_count": sum(1 for result in valid if result["direct_command_blocked"]),
        "execution_blocked_count": sum(1 for result in valid if result["execution_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_mutation_blocked_count": sum(1 for result in valid if result["predictor_mutation_blocked"]),
        "manipulation_blocked_count": sum(1 for result in valid if result["manipulation_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["valid_selected_action_approval_boundary_count"] == 3
        and summary["invalid_selected_action_approval_boundary_count"] == 25
        and summary["future_selected_action_allowed_count"] == 3
        and summary["approach_or_reach_item_boundary_count"] == 1
        and summary["resolve_mismatch_boundary_count"] == 1
        and summary["support_user_comfort_boundary_count"] == 1
        and summary["selected_action_creation_blocked_count"] == 3
        and summary["final_action_blocked_count"] == 3
        and summary["direct_command_blocked_count"] == 3
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
