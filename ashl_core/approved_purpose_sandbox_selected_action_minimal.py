"""Create sandbox-only selected_action records from approved-purpose action boundary."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .approved_purpose_to_sandbox_selected_action_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_approved_purpose_to_sandbox_selected_action_approval_boundary_record,
    run_approved_purpose_to_sandbox_selected_action_approval_boundary_minimal_check,
    validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record,
)


COMMAND = "run-approved-purpose-sandbox-selected-action-minimal-check"
FLOW = "approved_purpose_sandbox_selected_action_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ApprovedPurposeSandboxSelectedAction-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b125"
BOUNDARY_INDEX_AFTER = "2026-06-09-b126"

REQUIRED_TOP_LEVEL_FIELDS = {
    "selected_action_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_selected_action_approval_boundary",
    "sandbox_selected_action",
    "rollback_preview",
    "human_summary",
    "blocked_flags",
}
BLOCKED_FLAGS = {
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


def build_approved_purpose_sandbox_selected_action_record(
    selected_action_approval_boundary_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(selected_action_approval_boundary_record)
        if selected_action_approval_boundary_record is not None
        else build_approved_purpose_to_sandbox_selected_action_approval_boundary_record()
    )
    source_validation = validate_approved_purpose_to_sandbox_selected_action_approval_boundary_record(source)
    if not source_validation["valid"]:
        raise ValueError("selected_action_approval_boundary_record must validate before selected_action creation")

    source_summary = _source_summary(source)
    selected_action = source_summary["candidate_for_future_selected_action"]
    purpose = source_summary["approved_purpose"]
    return {
        "selected_action_record_id": f"approved_purpose_sandbox_selected_action_{purpose}_demo_001",
        "record_type": "approved_purpose_sandbox_selected_action_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_selected_action_approval_boundary": source_summary,
        "sandbox_selected_action": {
            "selected_action_created": True,
            "selected_action": selected_action,
            "selected_action_source": "approved_purpose_selected_action_approval_boundary",
            "selected_action_scope": "sandbox_only",
            "selection_reason": "top_ranked_approved_purpose_advisory_candidate",
            "approved_purpose": purpose,
            "candidate_family": source_summary["candidate_family"],
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
        "rollback_preview": {
            "rollback_available": True,
            "selected_action_removed_on_rollback": True,
            "dirty_state_after_rollback": False,
            "persistent_update_performed": False,
        },
        "human_summary": {
            "what_was_selected": f"Approved purpose {purpose} created sandbox-only selected_action {selected_action}.",
            "what_changed": "A top-ranked approved-purpose advisory candidate became a sandbox-only selected_action record.",
            "what_is_blocked": "Final_action, direct command, execution, persistence, predictor access or mutation, manipulation, and proof claims remain blocked.",
            "plain_result": "Approved purpose can now create a sandbox selected_action, but it still cannot finalize or execute an action.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_approved_purpose_sandbox_selected_action_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "approved_purpose_sandbox_selected_action_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_selected_action_approval_boundary"), errors, "source_selected_action_approval_boundary")
    selected = _as_dict(record.get("sandbox_selected_action"), errors, "sandbox_selected_action")
    rollback = _as_dict(record.get("rollback_preview"), errors, "rollback_preview")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_selected_action(selected, source, errors)
    _validate_rollback(rollback, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "approved_purpose": source.get("approved_purpose"),
        "selected_action": selected.get("selected_action"),
        "selected_action_created": selected.get("selected_action_created") is True,
        "sandbox_only_selected_action": selected.get("selected_action_scope") == "sandbox_only",
        "final_action_blocked": selected.get("final_action_created") is False
        and blocked.get("final_action_created") is False,
        "direct_command_blocked": selected.get("direct_command_created") is False
        and blocked.get("direct_command_created") is False,
        "execution_blocked": selected.get("sandbox_action_executed") is False
        and selected.get("execution_allowed_in_this_package") is False
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
        "rollback_available": selected.get("rollback_available") is True
        and rollback.get("rollback_available") is True
        and rollback.get("dirty_state_after_rollback") is False,
    }


def run_approved_purpose_sandbox_selected_action_minimal_check() -> dict[str, Any]:
    source_records = run_approved_purpose_to_sandbox_selected_action_approval_boundary_minimal_check()["valid_records"]
    valid_records = [build_approved_purpose_sandbox_selected_action_record(source) for source in source_records]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [validate_approved_purpose_sandbox_selected_action_record(record) for record in records]
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
            "boundary_reason": "Creates sandbox-only selected_action records from approved-purpose selected-action approval boundary.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Approved-purpose sandbox selected_action creation was added.",
            "what_changed": "Top-ranked approved-purpose advisory candidates can become sandbox-only selected_action records.",
            "what_is_blocked": "Final_action, direct command, execution, persistence, predictor access or mutation, manipulation, and proof claims remain blocked.",
            "plain_result": "Purpose can now select a sandbox action record, but it still cannot finalize or execute it.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    source_ordering = source["source_approved_purpose_ordering"]
    boundary = source["selected_action_approval_boundary"]
    return {
        "source_approval_boundary_id": source["approval_boundary_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "approved_purpose": source_ordering["approved_purpose"],
        "candidate_family": source_ordering["candidate_family"],
        "ordering_scope": source_ordering["ordering_scope"],
        "candidate_for_future_selected_action": boundary["candidate_for_future_selected_action"],
        "future_selected_action_allowed": boundary["future_selected_action_allowed"],
        "selected_action_scope": boundary["selected_action_scope"],
        "source_selected_action_created_in_source_package": boundary["selected_action_created_in_this_package"],
        "source_final_action_created": boundary["final_action_created"],
        "source_direct_command_created": boundary["direct_command_created"],
        "source_sandbox_action_executed": boundary["sandbox_action_executed"],
        "source_execution_allowed_in_source_package": boundary["execution_allowed_in_this_package"],
        "future_final_action_requires_separate_boundary": boundary["future_final_action_requires_separate_boundary"],
        "future_direct_command_requires_separate_boundary": boundary["future_direct_command_requires_separate_boundary"],
        "future_execution_requires_separate_boundary": boundary["future_execution_requires_separate_boundary"],
        "source_rollback_available": boundary["rollback_available"],
        "source_audit_recorded": boundary["audit_recorded"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("future_selected_action_allowed") is not True:
        errors.append("source_future_selected_action_allowed_not_true")
    if source.get("selected_action_scope") != "sandbox_only":
        errors.append("source_selected_action_scope_not_sandbox_only")
    for field in (
        "source_selected_action_created_in_source_package",
        "source_final_action_created",
        "source_direct_command_created",
        "source_sandbox_action_executed",
        "source_execution_allowed_in_source_package",
    ):
        if source.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in (
        "future_final_action_requires_separate_boundary",
        "future_direct_command_requires_separate_boundary",
        "future_execution_requires_separate_boundary",
        "source_rollback_available",
        "source_audit_recorded",
    ):
        if source.get(field) is not True:
            errors.append(f"{field}_not_true")
    if not _non_empty_string(source.get("candidate_for_future_selected_action")):
        errors.append("source_candidate_for_future_selected_action_empty")


def _validate_selected_action(selected: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "selected_action_created": True,
        "selected_action": source.get("candidate_for_future_selected_action"),
        "selected_action_source": "approved_purpose_selected_action_approval_boundary",
        "selected_action_scope": "sandbox_only",
        "selection_reason": "top_ranked_approved_purpose_advisory_candidate",
        "approved_purpose": source.get("approved_purpose"),
        "candidate_family": source.get("candidate_family"),
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
        if selected.get(field) != value:
            errors.append(f"sandbox_selected_action_{field}_not_expected")


def _validate_rollback(rollback: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "rollback_available": True,
        "selected_action_removed_on_rollback": True,
        "dirty_state_after_rollback": False,
        "persistent_update_performed": False,
    }
    for field, value in expected.items():
        if rollback.get(field) != value:
            errors.append(f"rollback_preview_{field}_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_selected", "what_changed", "what_is_blocked", "plain_result"):
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
        record["selected_action_record_id"] = f"{record['selected_action_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reward, "bad_record_type", ("record_type",), "approved_purpose_selected_action")
    mutate(reward, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reward, "source_not_validated", ("source_selected_action_approval_boundary", "source_validated"), False)
    mutate(reward, "source_future_not_allowed", ("source_selected_action_approval_boundary", "future_selected_action_allowed"), False)
    mutate(reward, "source_selected_action", ("source_selected_action_approval_boundary", "source_selected_action_created_in_source_package"), True)
    mutate(reward, "wrong_selected_action", ("sandbox_selected_action", "selected_action"), "wait_or_observe")
    mutate(reward, "selected_action_not_created", ("sandbox_selected_action", "selected_action_created"), False)
    mutate(reward, "wrong_scope", ("sandbox_selected_action", "selected_action_scope"), "production")
    mutate(reward, "wrong_source", ("sandbox_selected_action", "selected_action_source"), "unapproved_candidate")
    mutate(reward, "final_action", ("sandbox_selected_action", "final_action_created"), True)
    mutate(reward, "direct_command", ("sandbox_selected_action", "direct_command_created"), True)
    mutate(reward, "execution", ("sandbox_selected_action", "sandbox_action_executed"), True)
    mutate(reward, "execution_allowed", ("sandbox_selected_action", "execution_allowed_in_this_package"), True)
    mutate(reward, "future_final_boundary_missing", ("sandbox_selected_action", "future_final_action_requires_separate_boundary"), False)
    mutate(reward, "rollback_dirty", ("rollback_preview", "dirty_state_after_rollback"), True)
    mutate(reward, "rollback_not_available", ("rollback_preview", "rollback_available"), False)
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
        "selected_action_result_count": len(validation_results),
        "valid_selected_action_count": len(valid),
        "invalid_selected_action_count": len(validation_results) - len(valid),
        "selected_action_created_count": sum(1 for result in valid if result["selected_action_created"]),
        "approach_or_reach_item_selected_count": sum(
            1
            for result in valid
            if result["approved_purpose"] == "approach_or_reach_item"
            and result["selected_action"] == "reach_front_item"
        ),
        "resolve_mismatch_selected_count": sum(
            1
            for result in valid
            if result["approved_purpose"] == "resolve_mismatch"
            and result["selected_action"] == "observe_or_alternative_probe"
        ),
        "support_user_comfort_selected_count": sum(
            1
            for result in valid
            if result["approved_purpose"] == "support_user_comfort"
            and result["selected_action"] == "offer_low_pressure_support"
        ),
        "sandbox_only_selected_action_count": sum(1 for result in valid if result["sandbox_only_selected_action"]),
        "final_action_blocked_count": sum(1 for result in valid if result["final_action_blocked"]),
        "direct_command_blocked_count": sum(1 for result in valid if result["direct_command_blocked"]),
        "execution_blocked_count": sum(1 for result in valid if result["execution_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_mutation_blocked_count": sum(1 for result in valid if result["predictor_mutation_blocked"]),
        "manipulation_blocked_count": sum(1 for result in valid if result["manipulation_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "rollback_available_count": sum(1 for result in valid if result["rollback_available"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["valid_selected_action_count"] == 3
        and summary["invalid_selected_action_count"] == 28
        and summary["selected_action_created_count"] == 3
        and summary["approach_or_reach_item_selected_count"] == 1
        and summary["resolve_mismatch_selected_count"] == 1
        and summary["support_user_comfort_selected_count"] == 1
        and summary["sandbox_only_selected_action_count"] == 3
        and summary["final_action_blocked_count"] == 3
        and summary["direct_command_blocked_count"] == 3
        and summary["execution_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["manipulation_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["rollback_available_count"] == 3
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
