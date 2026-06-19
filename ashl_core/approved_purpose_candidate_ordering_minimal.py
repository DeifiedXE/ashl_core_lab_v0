"""Advisory sandbox-only candidate ordering from approved purposes."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .approved_purpose_candidate_ordering_boundary_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_approved_purpose_candidate_ordering_boundary_record,
    run_approved_purpose_candidate_ordering_boundary_minimal_check,
    validate_approved_purpose_candidate_ordering_boundary_record,
)


COMMAND = "run-approved-purpose-candidate-ordering-minimal-check"
FLOW = "approved_purpose_candidate_ordering_minimal_v0"
PACKAGE_ID = "PKG-Phase0-ApprovedPurposeCandidateOrdering-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b123"
BOUNDARY_INDEX_AFTER = "2026-06-09-b124"

PURPOSE_ORDERING = {
    "approach_or_reach_item": {
        "candidate_family": "positive_item_interaction_candidates",
        "ordering_scope": "sandbox_positive_item_scope",
        "candidate_actions_before_ordering": [
            "wait_or_observe",
            "reach_front_item",
            "step_toward_item",
            "fallback_stop_and_report",
        ],
        "candidate_actions_after_ordering": [
            "reach_front_item",
            "step_toward_item",
            "wait_or_observe",
            "fallback_stop_and_report",
        ],
        "ordering_reason": "approved_purpose_approach_or_reach_item_prioritizes_bounded_positive_item_interaction",
        "primary_ranked_action": "reach_front_item",
    },
    "resolve_mismatch": {
        "candidate_family": "verification_or_observation_candidates",
        "ordering_scope": "sandbox_verification_scope",
        "candidate_actions_before_ordering": [
            "retry_same_action_without_check",
            "observe_or_alternative_probe",
            "check_before_retry",
            "fallback_stop_and_report",
        ],
        "candidate_actions_after_ordering": [
            "observe_or_alternative_probe",
            "check_before_retry",
            "fallback_stop_and_report",
            "retry_same_action_without_check",
        ],
        "ordering_reason": "approved_purpose_resolve_mismatch_prioritizes_verification_before_retry",
        "primary_ranked_action": "observe_or_alternative_probe",
    },
    "support_user_comfort": {
        "candidate_family": "bounded_comfort_support_candidates",
        "ordering_scope": "bounded_interaction_support_scope",
        "candidate_actions_before_ordering": [
            "continue_neutral_observation",
            "offer_low_pressure_support",
            "ask_if_help_needed",
            "stop_and_wait",
        ],
        "candidate_actions_after_ordering": [
            "offer_low_pressure_support",
            "ask_if_help_needed",
            "continue_neutral_observation",
            "stop_and_wait",
        ],
        "ordering_reason": "approved_purpose_support_user_comfort_prioritizes_bounded_low_pressure_support",
        "primary_ranked_action": "offer_low_pressure_support",
    },
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "ordering_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_ordering_boundary",
    "approved_purpose_ordering",
    "rollback_preview",
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


def build_approved_purpose_candidate_ordering_record(
    ordering_boundary_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(ordering_boundary_record)
        if ordering_boundary_record is not None
        else build_approved_purpose_candidate_ordering_boundary_record()
    )
    source_validation = validate_approved_purpose_candidate_ordering_boundary_record(source)
    if not source_validation["valid"]:
        raise ValueError("ordering_boundary_record must validate before approved purpose ordering")

    source_summary = _source_summary(source)
    purpose = source_summary["approved_purpose"]
    ordering = _derive_ordering(purpose)
    return {
        "ordering_record_id": f"approved_purpose_candidate_ordering_{purpose}_demo_001",
        "record_type": "approved_purpose_candidate_ordering_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_ordering_boundary": source_summary,
        "approved_purpose_ordering": ordering,
        "rollback_preview": {
            "rollback_available": True,
            "candidate_actions_restored": list(ordering["candidate_actions_before_ordering"]),
            "dirty_state_after_rollback": False,
            "persistent_update_performed": False,
        },
        "human_summary": {
            "what_was_ordered": f"Approved purpose {purpose} produced advisory sandbox candidate ordering.",
            "what_changed": "Candidate order changed inside the sandbox-only advisory record.",
            "what_is_blocked": "No selected_action, final_action, direct command, execution, memory write, predictor mutation, or proof claim is created.",
            "plain_result": "Approved purpose can now influence sandbox-only candidate order, but it still cannot choose or execute an action.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_approved_purpose_candidate_ordering_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "approved_purpose_candidate_ordering_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_ordering_boundary"), errors, "source_ordering_boundary")
    ordering = _as_dict(record.get("approved_purpose_ordering"), errors, "approved_purpose_ordering")
    rollback = _as_dict(record.get("rollback_preview"), errors, "rollback_preview")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_ordering(ordering, source, errors)
    _validate_rollback(rollback, ordering, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "approved_purpose": source.get("approved_purpose"),
        "candidate_ordering_applied": ordering.get("candidate_ordering_applied") is True,
        "candidate_order_changed": ordering.get("candidate_order_changed") is True,
        "sandbox_only_checked": ordering.get("ordering_is_sandbox_only") is True,
        "advisory_only_checked": ordering.get("ordering_is_advisory") is True,
        "selected_action_blocked": blocked.get("selected_action_created") is False
        and ordering.get("selected_action_created") is False,
        "final_action_blocked": blocked.get("final_action_created") is False
        and ordering.get("final_action_created") is False,
        "direct_command_blocked": blocked.get("direct_command_created") is False
        and ordering.get("direct_command_created") is False,
        "execution_blocked": blocked.get("sandbox_action_executed") is False
        and ordering.get("sandbox_action_executed") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False,
        "predictor_mutation_blocked": blocked.get("predictor_modified") is False
        and blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False,
        "manipulation_blocked": blocked.get("emotional_manipulation") is False
        and blocked.get("unlimited_reward_seeking") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
        "rollback_available": rollback.get("rollback_available") is True
        and rollback.get("dirty_state_after_rollback") is False,
    }


def run_approved_purpose_candidate_ordering_minimal_check() -> dict[str, Any]:
    source_records = run_approved_purpose_candidate_ordering_boundary_minimal_check()["valid_records"]
    valid_records = [build_approved_purpose_candidate_ordering_record(source) for source in source_records]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [validate_approved_purpose_candidate_ordering_record(record) for record in records]
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
            "boundary_reason": "Permits approved purposes to affect sandbox-only advisory candidate ordering.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Approved purpose candidate ordering was added.",
            "what_changed": "Approved purposes can reorder sandbox-only advisory candidates.",
            "what_is_blocked": "Selected_action, final_action, direct command, execution, persistence, predictor mutation, manipulation, and proof claims remain blocked.",
            "plain_result": "Purpose can shape candidate order, but it still cannot select or execute an action.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    source_purpose = source["source_approved_purpose"]
    boundary = source["candidate_ordering_boundary"]
    return {
        "source_ordering_boundary_id": source["ordering_boundary_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "approved_purpose": source_purpose["approved_purpose"],
        "approved_purpose_scope": source_purpose["approved_purpose_scope"],
        "candidate_ordering_boundary_opened": boundary["candidate_ordering_boundary_opened"],
        "allowed_candidate_family": boundary["allowed_candidate_family"],
        "ordering_scope": boundary["ordering_scope"],
        "candidate_ordering_allowed_in_future_package": boundary[
            "candidate_ordering_allowed_in_future_package"
        ],
        "source_candidate_ordering_applied_in_boundary_package": boundary[
            "candidate_ordering_applied_in_this_package"
        ],
        "source_selected_action_created": boundary["selected_action_created"],
        "source_final_action_created": boundary["final_action_created"],
        "source_direct_command_created": boundary["direct_command_created"],
        "source_sandbox_action_executed": boundary["sandbox_action_executed"],
    }


def _derive_ordering(purpose: str) -> dict[str, Any]:
    config = PURPOSE_ORDERING[purpose]
    before = list(config["candidate_actions_before_ordering"])
    after = list(config["candidate_actions_after_ordering"])
    return {
        "candidate_ordering_applied": True,
        "candidate_order_changed": before != after,
        "candidate_family": config["candidate_family"],
        "ordering_scope": config["ordering_scope"],
        "candidate_actions_before_ordering": before,
        "candidate_actions_after_ordering": after,
        "primary_ranked_action": config["primary_ranked_action"],
        "ordering_reason": config["ordering_reason"],
        "ordering_is_sandbox_only": True,
        "ordering_is_advisory": True,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_action_executed": False,
        "future_selected_action_requires_separate_boundary": True,
        "future_final_action_requires_separate_boundary": True,
        "future_direct_command_requires_separate_boundary": True,
        "future_execution_requires_separate_boundary": True,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    purpose = source.get("approved_purpose")
    if purpose not in PURPOSE_ORDERING:
        errors.append("approved_purpose_not_allowed")
        return
    expected = PURPOSE_ORDERING[purpose]
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("candidate_ordering_boundary_opened") is not True:
        errors.append("candidate_ordering_boundary_opened_not_true")
    if source.get("allowed_candidate_family") != expected["candidate_family"]:
        errors.append("allowed_candidate_family_not_expected")
    if source.get("ordering_scope") != expected["ordering_scope"]:
        errors.append("source_ordering_scope_not_expected")
    if source.get("candidate_ordering_allowed_in_future_package") is not True:
        errors.append("candidate_ordering_allowed_in_future_package_not_true")
    if source.get("source_candidate_ordering_applied_in_boundary_package") is not False:
        errors.append("source_candidate_ordering_applied_in_boundary_package_not_false")
    for field in (
        "source_selected_action_created",
        "source_final_action_created",
        "source_direct_command_created",
        "source_sandbox_action_executed",
    ):
        if source.get(field) is not False:
            errors.append(f"{field}_not_false")


def _validate_ordering(ordering: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    purpose = source.get("approved_purpose")
    expected = PURPOSE_ORDERING.get(purpose)
    if expected is None:
        return
    checks = {
        "candidate_ordering_applied": True,
        "candidate_order_changed": True,
        "candidate_family": expected["candidate_family"],
        "ordering_scope": expected["ordering_scope"],
        "candidate_actions_before_ordering": expected["candidate_actions_before_ordering"],
        "candidate_actions_after_ordering": expected["candidate_actions_after_ordering"],
        "primary_ranked_action": expected["primary_ranked_action"],
        "ordering_reason": expected["ordering_reason"],
        "ordering_is_sandbox_only": True,
        "ordering_is_advisory": True,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_action_executed": False,
        "future_selected_action_requires_separate_boundary": True,
        "future_final_action_requires_separate_boundary": True,
        "future_direct_command_requires_separate_boundary": True,
        "future_execution_requires_separate_boundary": True,
    }
    for field, value in checks.items():
        if ordering.get(field) != value:
            errors.append(f"approved_purpose_ordering_{field}_not_expected")
    after = ordering.get("candidate_actions_after_ordering", [])
    if not _ranked_first(after, expected["primary_ranked_action"]):
        errors.append("primary_ranked_action_not_first")
    if purpose == "resolve_mismatch" and not _ranked_before(after, "check_before_retry", "retry_same_action_without_check"):
        errors.append("check_before_retry_not_ranked_before_retry")
    if purpose == "support_user_comfort" and "force_user_happiness" in after:
        errors.append("manipulative_comfort_candidate_present")


def _validate_rollback(rollback: dict[str, Any], ordering: dict[str, Any], errors: list[str]) -> None:
    if rollback.get("rollback_available") is not True:
        errors.append("rollback_available_not_true")
    if rollback.get("candidate_actions_restored") != ordering.get("candidate_actions_before_ordering"):
        errors.append("candidate_actions_restored_not_expected")
    if rollback.get("dirty_state_after_rollback") is not False:
        errors.append("dirty_state_after_rollback_not_false")
    if rollback.get("persistent_update_performed") is not False:
        errors.append("rollback_persistent_update_performed_not_false")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_ordered", "what_changed", "what_is_blocked", "plain_result"):
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
        record["ordering_record_id"] = f"{record['ordering_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reward, "bad_record_type", ("record_type",), "approved_purpose_selected_action")
    mutate(reward, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reward, "source_not_validated", ("source_ordering_boundary", "source_validated"), False)
    mutate(reward, "source_boundary_not_opened", ("source_ordering_boundary", "candidate_ordering_boundary_opened"), False)
    mutate(reward, "source_not_allowed", ("source_ordering_boundary", "candidate_ordering_allowed_in_future_package"), False)
    mutate(reward, "unknown_purpose", ("source_ordering_boundary", "approved_purpose"), "make_user_happy")
    mutate(reward, "wrong_family", ("approved_purpose_ordering", "candidate_family"), "reward_chase")
    mutate(reward, "ordering_not_applied", ("approved_purpose_ordering", "candidate_ordering_applied"), False)
    mutate(reward, "order_not_changed", ("approved_purpose_ordering", "candidate_order_changed"), False)
    mutate(reward, "wrong_after", ("approved_purpose_ordering", "candidate_actions_after_ordering"), reward["approved_purpose_ordering"]["candidate_actions_before_ordering"])
    mutate(reward, "primary_not_first", ("approved_purpose_ordering", "candidate_actions_after_ordering"), ["wait_or_observe", "reach_front_item", "step_toward_item", "fallback_stop_and_report"])
    mutate(reward, "not_sandbox_only", ("approved_purpose_ordering", "ordering_is_sandbox_only"), False)
    mutate(reward, "not_advisory", ("approved_purpose_ordering", "ordering_is_advisory"), False)
    mutate(reward, "selected_action", ("approved_purpose_ordering", "selected_action_created"), True)
    mutate(reward, "final_action", ("approved_purpose_ordering", "final_action_created"), True)
    mutate(reward, "direct_command", ("approved_purpose_ordering", "direct_command_created"), True)
    mutate(reward, "execution", ("approved_purpose_ordering", "sandbox_action_executed"), True)
    mutate(mismatch, "check_after_retry", ("approved_purpose_ordering", "candidate_actions_after_ordering"), ["observe_or_alternative_probe", "retry_same_action_without_check", "check_before_retry", "fallback_stop_and_report"])
    mutate(mismatch, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(mismatch, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(mismatch, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(mismatch, "rollback_dirty", ("rollback_preview", "dirty_state_after_rollback"), True)
    mutate(comfort, "force_happiness", ("approved_purpose_ordering", "candidate_actions_after_ordering"), ["force_user_happiness", "offer_low_pressure_support", "ask_if_help_needed", "stop_and_wait"])
    mutate(comfort, "emotion_claim", ("blocked_flags", "emotion_recognition_claim"), True)
    mutate(comfort, "happiness_claim", ("blocked_flags", "user_happiness_claim"), True)
    mutate(comfort, "manipulation", ("blocked_flags", "emotional_manipulation"), True)
    mutate(comfort, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(comfort, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "approved_purpose_candidate_ordering_result_count": len(validation_results),
        "valid_approved_purpose_candidate_ordering_count": len(valid),
        "invalid_approved_purpose_candidate_ordering_count": len(validation_results) - len(valid),
        "candidate_ordering_applied_count": sum(1 for result in valid if result["candidate_ordering_applied"]),
        "candidate_order_changed_count": sum(1 for result in valid if result["candidate_order_changed"]),
        "approach_or_reach_item_ordering_count": sum(
            1 for result in valid if result["approved_purpose"] == "approach_or_reach_item"
        ),
        "resolve_mismatch_ordering_count": sum(
            1 for result in valid if result["approved_purpose"] == "resolve_mismatch"
        ),
        "support_user_comfort_ordering_count": sum(
            1 for result in valid if result["approved_purpose"] == "support_user_comfort"
        ),
        "sandbox_only_checked_count": sum(1 for result in valid if result["sandbox_only_checked"]),
        "advisory_only_checked_count": sum(1 for result in valid if result["advisory_only_checked"]),
        "selected_action_blocked_count": sum(1 for result in valid if result["selected_action_blocked"]),
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
        summary["valid_approved_purpose_candidate_ordering_count"] == 3
        and summary["invalid_approved_purpose_candidate_ordering_count"] == 28
        and summary["candidate_ordering_applied_count"] == 3
        and summary["candidate_order_changed_count"] == 3
        and summary["approach_or_reach_item_ordering_count"] == 1
        and summary["resolve_mismatch_ordering_count"] == 1
        and summary["support_user_comfort_ordering_count"] == 1
        and summary["sandbox_only_checked_count"] == 3
        and summary["advisory_only_checked_count"] == 3
        and summary["selected_action_blocked_count"] == 3
        and summary["final_action_blocked_count"] == 3
        and summary["direct_command_blocked_count"] == 3
        and summary["execution_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["manipulation_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["rollback_available_count"] == 3
    )


def _ranked_first(actions: Any, action: str) -> bool:
    return isinstance(actions, list) and len(actions) > 0 and actions[0] == action


def _ranked_before(actions: Any, first: str, second: str) -> bool:
    return isinstance(actions, list) and first in actions and second in actions and actions.index(first) < actions.index(second)


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
