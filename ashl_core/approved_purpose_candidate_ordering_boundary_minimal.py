"""Boundary for approved purposes to enter future candidate ordering."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .proto_purpose_approval_boundary_minimal import (
    build_proto_purpose_approval_boundary_record,
    run_proto_purpose_approval_boundary_minimal_check,
    validate_proto_purpose_approval_boundary_record,
)


COMMAND = "run-approved-purpose-candidate-ordering-boundary-minimal-check"
FLOW = "approved_purpose_candidate_ordering_boundary_minimal_v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b122"
BOUNDARY_INDEX_AFTER = "2026-06-09-b123"

PURPOSE_TO_ALLOWED_CANDIDATE_FAMILY = {
    "approach_or_reach_item": "positive_item_interaction_candidates",
    "resolve_mismatch": "verification_or_observation_candidates",
    "support_user_comfort": "bounded_comfort_support_candidates",
}
PURPOSE_TO_ORDERING_SCOPE = {
    "approach_or_reach_item": "sandbox_positive_item_scope",
    "resolve_mismatch": "sandbox_verification_scope",
    "support_user_comfort": "bounded_interaction_support_scope",
}
PURPOSE_TO_APPROVED_SCOPE = {
    "approach_or_reach_item": "bounded_positive_item_contact_scope",
    "resolve_mismatch": "bounded_verification_scope",
    "support_user_comfort": "bounded_comfort_support_scope",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "ordering_boundary_id",
    "ordering_boundary_type",
    "boundary_mode",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_approved_purpose",
    "candidate_ordering_boundary",
    "human_summary",
    "blocked_flags",
}
BLOCKED_FLAGS = {
    "candidate_ordering_applied",
    "candidate_reordering_applied",
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
    "predictor_modified",
    "persistent_policy_written",
    "semantic_vision",
    "emotion_recognition_claim",
    "user_happiness_claim",
    "unlimited_reward_seeking",
    "emotional_manipulation",
    "proof_of_learning_claim",
}


def build_approved_purpose_candidate_ordering_boundary_record(
    proto_purpose_approval_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(proto_purpose_approval_record) if proto_purpose_approval_record is not None else (
        build_proto_purpose_approval_boundary_record()
    )
    source_validation = validate_proto_purpose_approval_boundary_record(source)
    if not source_validation["valid"]:
        raise ValueError("proto_purpose_approval_record must validate before candidate ordering boundary")

    source_summary = _source_summary(source)
    approved_purpose = source_summary["approved_purpose"]
    return {
        "ordering_boundary_id": f"approved_purpose_candidate_ordering_boundary_{approved_purpose}_demo_001",
        "ordering_boundary_type": "approved_purpose_candidate_ordering_boundary_minimal",
        "boundary_mode": "approved_purpose_to_future_candidate_ordering_boundary",
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_approved_purpose": source_summary,
        "candidate_ordering_boundary": {
            "candidate_ordering_boundary_opened": True,
            "allowed_candidate_family": PURPOSE_TO_ALLOWED_CANDIDATE_FAMILY[approved_purpose],
            "ordering_scope": PURPOSE_TO_ORDERING_SCOPE[approved_purpose],
            "candidate_ordering_allowed_in_future_package": True,
            "candidate_ordering_applied_in_this_package": False,
            "candidate_ordering_changed": False,
            "candidate_order_before": [],
            "candidate_order_after": [],
            "ordering_delta": 0.0,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "sandbox_action_executed": False,
            "next_required_boundary": "approved_purpose_candidate_ordering_minimal_v0",
        },
        "human_summary": {
            "what_was_opened": f"The approved purpose {approved_purpose} may enter a future candidate-ordering package.",
            "what_it_allows": "A future package may derive candidate families from approved purpose scope.",
            "what_is_blocked": "This package does not apply candidate ordering, create actions, execute commands, write memory, mutate predictors, or prove learning.",
            "plain_result": "Approved purpose reached the candidate-ordering boundary, but no candidate order changed.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_approved_purpose_candidate_ordering_boundary_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    if record.get("ordering_boundary_type") != "approved_purpose_candidate_ordering_boundary_minimal":
        errors.append("ordering_boundary_type_not_expected")
    if record.get("boundary_mode") != "approved_purpose_to_future_candidate_ordering_boundary":
        errors.append("boundary_mode_not_expected")
    if record.get("boundary_index_before") != BOUNDARY_INDEX_BEFORE:
        errors.append("boundary_index_before_not_expected")
    if record.get("boundary_index_after") != BOUNDARY_INDEX_AFTER:
        errors.append("boundary_index_after_not_expected")
    if record.get("boundary_change_required") is not True:
        errors.append("boundary_change_required_not_true")

    source = _as_dict(record.get("source_approved_purpose"), errors, "source_approved_purpose")
    boundary = _as_dict(record.get("candidate_ordering_boundary"), errors, "candidate_ordering_boundary")
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
        "candidate_ordering_boundary_opened": boundary.get("candidate_ordering_boundary_opened") is True,
        "candidate_ordering_allowed_in_future_package": (
            boundary.get("candidate_ordering_allowed_in_future_package") is True
        ),
        "candidate_ordering_blocked": boundary.get("candidate_ordering_applied_in_this_package") is False
        and boundary.get("candidate_ordering_changed") is False
        and boundary.get("candidate_order_before") == []
        and boundary.get("candidate_order_after") == []
        and boundary.get("ordering_delta") == 0.0
        and blocked.get("candidate_ordering_applied") is False
        and blocked.get("candidate_reordering_applied") is False,
        "action_creation_blocked": boundary.get("selected_action_created") is False
        and boundary.get("final_action_created") is False
        and boundary.get("direct_command_created") is False
        and boundary.get("sandbox_action_executed") is False
        and blocked.get("selected_action_created") is False
        and blocked.get("final_action_created") is False
        and blocked.get("direct_command_created") is False
        and blocked.get("sandbox_action_executed") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False,
        "predictor_mutation_blocked": blocked.get("predictor_modified") is False,
        "manipulation_blocked": blocked.get("unlimited_reward_seeking") is False
        and blocked.get("emotional_manipulation") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
    }


def run_approved_purpose_candidate_ordering_boundary_minimal_check() -> dict[str, Any]:
    source_records = run_proto_purpose_approval_boundary_minimal_check()["valid_records"]
    valid_records = [build_approved_purpose_candidate_ordering_boundary_record(source) for source in source_records]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_approved_purpose_candidate_ordering_boundary_record(record)
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
            "boundary_reason": "Opens a validation boundary for approved purposes to enter a future candidate-ordering package.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "An approved-purpose candidate-ordering boundary was added.",
            "what_changed": "Bounded approved purposes may reach a future candidate-ordering package.",
            "what_is_blocked": "Candidate ordering, selected_action, final_action, direct command, execution, memory write, predictor mutation, and proof claims remain blocked.",
            "plain_result": "Approved purpose can now approach candidate ordering without changing any candidate order.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    purpose = source["approved_purpose_record"]
    downstream = source["downstream_boundary"]
    return {
        "source_approval_record_id": source["approval_record_id"],
        "source_validated": True,
        "approved_purpose_created": purpose["approved_purpose_created"],
        "approved_purpose_id": purpose["approved_purpose_id"],
        "approved_purpose": purpose["approved_purpose"],
        "approved_purpose_scope": purpose["approved_purpose_scope"],
        "purpose_is_bounded": purpose["purpose_is_bounded"],
        "purpose_is_trace_derived": purpose["purpose_is_trace_derived"],
        "action_authority_granted": purpose["action_authority_granted"],
        "source_may_enter_future_candidate_ordering_boundary": (
            downstream["may_enter_future_candidate_ordering_boundary"]
        ),
        "source_candidate_ordering_authorized_in_this_package": (
            downstream["candidate_ordering_authorized_in_this_package"]
        ),
        "source_candidate_ordering_changed": downstream["candidate_ordering_changed"],
        "source_selected_action_created": downstream["selected_action_created"],
        "source_final_action_created": downstream["final_action_created"],
        "source_direct_command_created": downstream["direct_command_created"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    for field in ("source_approval_record_id", "approved_purpose_id", "approved_purpose", "approved_purpose_scope"):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_approved_purpose_{field}_empty")
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("approved_purpose") not in PURPOSE_TO_ALLOWED_CANDIDATE_FAMILY:
        errors.append("approved_purpose_not_allowed")
    if source.get("approved_purpose_created") is not True:
        errors.append("approved_purpose_created_not_true")
    if source.get("approved_purpose_scope") != PURPOSE_TO_APPROVED_SCOPE.get(source.get("approved_purpose")):
        errors.append("approved_purpose_scope_not_expected")
    if source.get("purpose_is_bounded") is not True:
        errors.append("purpose_is_bounded_not_true")
    if source.get("purpose_is_trace_derived") is not True:
        errors.append("purpose_is_trace_derived_not_true")
    if source.get("action_authority_granted") is not False:
        errors.append("source_action_authority_granted_not_false")
    if source.get("source_may_enter_future_candidate_ordering_boundary") is not True:
        errors.append("source_may_enter_future_candidate_ordering_boundary_not_true")
    if source.get("source_candidate_ordering_authorized_in_this_package") is not False:
        errors.append("source_candidate_ordering_authorized_in_this_package_not_false")
    if source.get("source_candidate_ordering_changed") is not False:
        errors.append("source_candidate_ordering_changed_not_false")
    if source.get("source_selected_action_created") is not False:
        errors.append("source_selected_action_created_not_false")
    if source.get("source_final_action_created") is not False:
        errors.append("source_final_action_created_not_false")
    if source.get("source_direct_command_created") is not False:
        errors.append("source_direct_command_created_not_false")


def _validate_boundary(boundary: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    approved_purpose = source.get("approved_purpose")
    if boundary.get("candidate_ordering_boundary_opened") is not True:
        errors.append("candidate_ordering_boundary_opened_not_true")
    if boundary.get("allowed_candidate_family") != PURPOSE_TO_ALLOWED_CANDIDATE_FAMILY.get(approved_purpose):
        errors.append("allowed_candidate_family_not_expected")
    if boundary.get("ordering_scope") != PURPOSE_TO_ORDERING_SCOPE.get(approved_purpose):
        errors.append("ordering_scope_not_expected")
    expected = {
        "candidate_ordering_allowed_in_future_package": True,
        "candidate_ordering_applied_in_this_package": False,
        "candidate_ordering_changed": False,
        "candidate_order_before": [],
        "candidate_order_after": [],
        "ordering_delta": 0.0,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_action_executed": False,
        "next_required_boundary": "approved_purpose_candidate_ordering_minimal_v0",
    }
    for field, value in expected.items():
        if boundary.get(field) != value:
            errors.append(f"candidate_ordering_boundary_{field}_not_expected")


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
        record["ordering_boundary_id"] = f"{record['ordering_boundary_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reward, "bad_mode", ("boundary_mode",), "ordering_implementation")
    mutate(reward, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reward, "boundary_not_required", ("boundary_change_required",), False)
    mutate(reward, "source_not_validated", ("source_approved_purpose", "source_validated"), False)
    mutate(reward, "approved_purpose_not_created", ("source_approved_purpose", "approved_purpose_created"), False)
    mutate(reward, "unknown_purpose", ("source_approved_purpose", "approved_purpose"), "make_user_happy")
    mutate(reward, "source_action_authority", ("source_approved_purpose", "action_authority_granted"), True)
    mutate(reward, "source_ordering_changed", ("source_approved_purpose", "source_candidate_ordering_changed"), True)
    mutate(reward, "boundary_not_opened", ("candidate_ordering_boundary", "candidate_ordering_boundary_opened"), False)
    mutate(reward, "wrong_candidate_family", ("candidate_ordering_boundary", "allowed_candidate_family"), "reward_chase")
    mutate(reward, "wrong_ordering_scope", ("candidate_ordering_boundary", "ordering_scope"), "unbounded")
    mutate(reward, "future_ordering_not_allowed", ("candidate_ordering_boundary", "candidate_ordering_allowed_in_future_package"), False)
    mutate(reward, "ordering_applied", ("candidate_ordering_boundary", "candidate_ordering_applied_in_this_package"), True)
    mutate(reward, "ordering_changed", ("candidate_ordering_boundary", "candidate_ordering_changed"), True)
    mutate(reward, "order_before_nonempty", ("candidate_ordering_boundary", "candidate_order_before"), ["a"])
    mutate(reward, "order_after_nonempty", ("candidate_ordering_boundary", "candidate_order_after"), ["b"])
    mutate(reward, "ordering_delta_nonzero", ("candidate_ordering_boundary", "ordering_delta"), 0.1)
    mutate(reward, "selected_action", ("candidate_ordering_boundary", "selected_action_created"), True)
    mutate(reward, "final_action", ("candidate_ordering_boundary", "final_action_created"), True)
    mutate(reward, "direct_command", ("candidate_ordering_boundary", "direct_command_created"), True)
    mutate(reward, "sandbox_execution", ("candidate_ordering_boundary", "sandbox_action_executed"), True)
    mutate(reward, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(mismatch, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(mismatch, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(comfort, "emotion_claim", ("blocked_flags", "emotion_recognition_claim"), True)
    mutate(comfort, "user_happiness_claim", ("blocked_flags", "user_happiness_claim"), True)
    mutate(comfort, "emotional_manipulation", ("blocked_flags", "emotional_manipulation"), True)
    mutate(comfort, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "approved_purpose_candidate_ordering_boundary_result_count": len(validation_results),
        "valid_approved_purpose_candidate_ordering_boundary_count": len(valid),
        "invalid_approved_purpose_candidate_ordering_boundary_count": len(validation_results) - len(valid),
        "candidate_ordering_boundary_opened_count": sum(
            1 for result in valid if result["candidate_ordering_boundary_opened"]
        ),
        "future_candidate_ordering_allowed_count": sum(
            1 for result in valid if result["candidate_ordering_allowed_in_future_package"]
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
        "candidate_ordering_blocked_count": sum(1 for result in valid if result["candidate_ordering_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_mutation_blocked_count": sum(1 for result in valid if result["predictor_mutation_blocked"]),
        "manipulation_blocked_count": sum(1 for result in valid if result["manipulation_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["valid_approved_purpose_candidate_ordering_boundary_count"] == 3
        and summary["invalid_approved_purpose_candidate_ordering_boundary_count"] == 28
        and summary["candidate_ordering_boundary_opened_count"] == 3
        and summary["future_candidate_ordering_allowed_count"] == 3
        and summary["approach_or_reach_item_boundary_count"] == 1
        and summary["resolve_mismatch_boundary_count"] == 1
        and summary["support_user_comfort_boundary_count"] == 1
        and summary["candidate_ordering_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
