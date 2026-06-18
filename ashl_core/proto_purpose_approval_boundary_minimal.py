"""Approval boundary for trace-only proto-purpose candidates."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .experience_derived_proto_purpose_candidate_trace_minimal import (
    build_experience_derived_proto_purpose_candidate_traces,
    validate_experience_derived_proto_purpose_candidate_trace,
)


COMMAND = "run-proto-purpose-approval-boundary-minimal-check"
FLOW = "proto_purpose_approval_boundary_minimal_v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b121"
BOUNDARY_INDEX_AFTER = "2026-06-09-b122"

ALLOWED_PROTO_PURPOSES = {
    "approach_or_reach_item",
    "resolve_mismatch",
    "support_user_comfort",
}
APPROVED_PURPOSE_SCOPES = {
    "approach_or_reach_item": "bounded_positive_item_contact_scope",
    "resolve_mismatch": "bounded_verification_scope",
    "support_user_comfort": "bounded_comfort_support_scope",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "approval_record_id",
    "approval_record_type",
    "approval_mode",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_proto_purpose_trace",
    "purpose_approval_decision",
    "approved_purpose_record",
    "downstream_boundary",
    "human_summary",
    "blocked_flags",
}
BLOCKED_FLAGS = {
    "candidate_ordering_changed",
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


def build_proto_purpose_approval_boundary_record(
    proto_purpose_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(proto_purpose_trace) if proto_purpose_trace is not None else (
        build_experience_derived_proto_purpose_candidate_traces()["records"][0]
    )
    source_validation = validate_experience_derived_proto_purpose_candidate_trace(source)
    if not source_validation["valid"]:
        raise ValueError("proto_purpose_trace must validate before approval boundary")

    proto_purpose = source["proto_purpose_candidate"]["proto_purpose"]
    source_summary = _source_summary(source)
    scope = APPROVED_PURPOSE_SCOPES[proto_purpose]
    return {
        "approval_record_id": f"proto_purpose_approval_boundary_{proto_purpose}_demo_001",
        "approval_record_type": "proto_purpose_approval_boundary_minimal",
        "approval_mode": "bounded_proto_purpose_to_approved_purpose_boundary",
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_proto_purpose_trace": source_summary,
        "purpose_approval_decision": {
            "decision": "approved_as_bounded_purpose",
            "reviewer": "explicit_boundary_fixture",
            "approval_reason": "The proto-purpose is bounded, trace-derived, and remains blocked from action authority in this package.",
            "approval_scope": scope,
            "approval_is_action_authority": False,
        },
        "approved_purpose_record": {
            "approved_purpose_created": True,
            "approved_purpose_id": f"approved_purpose_{proto_purpose}_demo_001",
            "approved_purpose": proto_purpose,
            "approved_purpose_scope": scope,
            "source_trace_id": source["trace_id"],
            "source_experience_type": source["experience_source"]["experience_type"],
            "source_ideal_expected_state": source["experience_derived_expectation"]["ideal_expected_state"],
            "purpose_is_bounded": True,
            "purpose_is_trace_derived": True,
            "action_authority_granted": False,
        },
        "downstream_boundary": {
            "may_enter_future_candidate_ordering_boundary": True,
            "candidate_ordering_authorized_in_this_package": False,
            "candidate_ordering_changed": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "sandbox_action_executed": False,
            "next_required_boundary": "approved_purpose_candidate_ordering_boundary_minimal_v0",
        },
        "human_summary": {
            "what_was_approved": f"The proto-purpose {proto_purpose} was approved as a bounded purpose.",
            "what_it_allows": "The approved purpose may enter a future candidate-ordering boundary.",
            "what_is_blocked": "This package does not order candidates, create actions, execute commands, write memory, mutate predictors, or prove learning.",
            "plain_result": "A trace-only proto-purpose became an approved bounded purpose, but no action authority was granted.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_proto_purpose_approval_boundary_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    if record.get("approval_record_type") != "proto_purpose_approval_boundary_minimal":
        errors.append("approval_record_type_not_expected")
    if record.get("approval_mode") != "bounded_proto_purpose_to_approved_purpose_boundary":
        errors.append("approval_mode_not_expected")
    if record.get("boundary_index_before") != BOUNDARY_INDEX_BEFORE:
        errors.append("boundary_index_before_not_expected")
    if record.get("boundary_index_after") != BOUNDARY_INDEX_AFTER:
        errors.append("boundary_index_after_not_expected")
    if record.get("boundary_change_required") is not True:
        errors.append("boundary_change_required_not_true")

    source = _as_dict(record.get("source_proto_purpose_trace"), errors, "source_proto_purpose_trace")
    decision = _as_dict(record.get("purpose_approval_decision"), errors, "purpose_approval_decision")
    purpose = _as_dict(record.get("approved_purpose_record"), errors, "approved_purpose_record")
    downstream = _as_dict(record.get("downstream_boundary"), errors, "downstream_boundary")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_decision(decision, source, errors)
    _validate_approved_purpose(purpose, source, decision, errors)
    _validate_downstream(downstream, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "proto_purpose": source.get("proto_purpose"),
        "approved_purpose_created": purpose.get("approved_purpose_created") is True,
        "may_enter_future_candidate_ordering_boundary": (
            downstream.get("may_enter_future_candidate_ordering_boundary") is True
        ),
        "candidate_ordering_blocked": downstream.get("candidate_ordering_authorized_in_this_package") is False
        and downstream.get("candidate_ordering_changed") is False
        and blocked.get("candidate_ordering_changed") is False
        and blocked.get("candidate_reordering_applied") is False,
        "action_creation_blocked": downstream.get("selected_action_created") is False
        and downstream.get("final_action_created") is False
        and downstream.get("direct_command_created") is False
        and downstream.get("sandbox_action_executed") is False
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


def run_proto_purpose_approval_boundary_minimal_check() -> dict[str, Any]:
    source_records = build_experience_derived_proto_purpose_candidate_traces()["records"]
    valid_records = [build_proto_purpose_approval_boundary_record(source) for source in source_records]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [validate_proto_purpose_approval_boundary_record(record) for record in records]
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
            "boundary_reason": "Creates a bounded approved-purpose validation boundary from trace-only proto-purpose candidates.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A proto-purpose approval boundary was added.",
            "what_changed": "Trace-only proto-purpose candidates can become bounded approved_purpose records.",
            "what_is_blocked": "Approved purpose does not grant candidate ordering, action creation, command execution, memory writes, predictor mutation, or proof claims.",
            "plain_result": "The thinking line can now approve bounded purposes while keeping action authority blocked.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_trace_id": source["trace_id"],
        "source_trace_type": source["trace_type"],
        "source_validated": True,
        "experience_type": source["experience_source"]["experience_type"],
        "ideal_expected_state": source["experience_derived_expectation"]["ideal_expected_state"],
        "gap_type": source["gap_assessment"]["gap_type"],
        "proto_purpose": source["proto_purpose_candidate"]["proto_purpose"],
        "proto_purpose_candidate_created": source["proto_purpose_candidate"]["proto_purpose_candidate_created"],
        "source_requires_purpose_approval": source["approval_boundary"]["requires_purpose_approval"],
        "source_approved_purpose_created": source["approval_boundary"]["approved_purpose_created"],
        "source_action_authority_granted": source["approval_boundary"]["action_authority_granted"],
        "source_candidate_ordering_allowed": source["approval_boundary"]["candidate_ordering_allowed"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    for field in ("source_trace_id", "source_trace_type", "experience_type", "ideal_expected_state", "gap_type"):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_proto_purpose_trace_{field}_empty")
    if source.get("source_trace_type") != "experience_derived_proto_purpose_candidate_trace":
        errors.append("source_trace_type_not_expected")
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("proto_purpose") not in ALLOWED_PROTO_PURPOSES:
        errors.append("source_proto_purpose_not_allowed")
    if source.get("proto_purpose_candidate_created") is not True:
        errors.append("source_proto_purpose_candidate_created_not_true")
    if source.get("source_requires_purpose_approval") is not True:
        errors.append("source_requires_purpose_approval_not_true")
    if source.get("source_approved_purpose_created") is not False:
        errors.append("source_approved_purpose_created_not_false")
    if source.get("source_action_authority_granted") is not False:
        errors.append("source_action_authority_granted_not_false")
    if source.get("source_candidate_ordering_allowed") is not False:
        errors.append("source_candidate_ordering_allowed_not_false")


def _validate_decision(decision: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    if decision.get("decision") != "approved_as_bounded_purpose":
        errors.append("decision_not_approved_as_bounded_purpose")
    for field in ("reviewer", "approval_reason", "approval_scope"):
        if not _non_empty_string(decision.get(field)):
            errors.append(f"purpose_approval_decision_{field}_empty")
    if decision.get("approval_scope") != APPROVED_PURPOSE_SCOPES.get(source.get("proto_purpose")):
        errors.append("approval_scope_not_expected_for_proto_purpose")
    if decision.get("approval_is_action_authority") is not False:
        errors.append("approval_is_action_authority_not_false")


def _validate_approved_purpose(
    purpose: dict[str, Any],
    source: dict[str, Any],
    decision: dict[str, Any],
    errors: list[str],
) -> None:
    if purpose.get("approved_purpose_created") is not True:
        errors.append("approved_purpose_created_not_true")
    if not _non_empty_string(purpose.get("approved_purpose_id")):
        errors.append("approved_purpose_id_empty")
    if purpose.get("approved_purpose") != source.get("proto_purpose"):
        errors.append("approved_purpose_not_source_proto_purpose")
    if purpose.get("approved_purpose_scope") != decision.get("approval_scope"):
        errors.append("approved_purpose_scope_not_decision_scope")
    if purpose.get("source_trace_id") != source.get("source_trace_id"):
        errors.append("approved_purpose_source_trace_id_not_source")
    if purpose.get("source_experience_type") != source.get("experience_type"):
        errors.append("approved_purpose_source_experience_type_not_source")
    if purpose.get("source_ideal_expected_state") != source.get("ideal_expected_state"):
        errors.append("approved_purpose_source_ideal_expected_state_not_source")
    if purpose.get("purpose_is_bounded") is not True:
        errors.append("purpose_is_bounded_not_true")
    if purpose.get("purpose_is_trace_derived") is not True:
        errors.append("purpose_is_trace_derived_not_true")
    if purpose.get("action_authority_granted") is not False:
        errors.append("approved_purpose_action_authority_granted_not_false")


def _validate_downstream(downstream: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "may_enter_future_candidate_ordering_boundary": True,
        "candidate_ordering_authorized_in_this_package": False,
        "candidate_ordering_changed": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "sandbox_action_executed": False,
        "next_required_boundary": "approved_purpose_candidate_ordering_boundary_minimal_v0",
    }
    for field, value in expected.items():
        if downstream.get(field) != value:
            errors.append(f"downstream_boundary_{field}_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_approved", "what_it_allows", "what_is_blocked", "plain_result"):
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
        record["approval_record_id"] = f"{record['approval_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reward, "bad_mode", ("approval_mode",), "free_purpose_creation")
    mutate(reward, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reward, "boundary_not_required", ("boundary_change_required",), False)
    mutate(reward, "source_not_validated", ("source_proto_purpose_trace", "source_validated"), False)
    mutate(reward, "source_unknown_proto", ("source_proto_purpose_trace", "proto_purpose"), "seek_reward_forever")
    mutate(reward, "source_already_approved", ("source_proto_purpose_trace", "source_approved_purpose_created"), True)
    mutate(reward, "source_action_authority", ("source_proto_purpose_trace", "source_action_authority_granted"), True)
    mutate(reward, "source_ordering_allowed", ("source_proto_purpose_trace", "source_candidate_ordering_allowed"), True)
    mutate(reward, "bad_decision", ("purpose_approval_decision", "decision"), "auto_apply")
    mutate(reward, "bad_scope", ("purpose_approval_decision", "approval_scope"), "unbounded_reward_scope")
    mutate(reward, "approval_is_action_authority", ("purpose_approval_decision", "approval_is_action_authority"), True)
    mutate(reward, "approved_purpose_not_created", ("approved_purpose_record", "approved_purpose_created"), False)
    mutate(reward, "approved_purpose_wrong", ("approved_purpose_record", "approved_purpose"), "support_user_comfort")
    mutate(reward, "purpose_unbounded", ("approved_purpose_record", "purpose_is_bounded"), False)
    mutate(reward, "purpose_not_trace_derived", ("approved_purpose_record", "purpose_is_trace_derived"), False)
    mutate(reward, "purpose_action_authority", ("approved_purpose_record", "action_authority_granted"), True)
    mutate(reward, "future_ordering_not_allowed", ("downstream_boundary", "may_enter_future_candidate_ordering_boundary"), False)
    mutate(reward, "ordering_authorized", ("downstream_boundary", "candidate_ordering_authorized_in_this_package"), True)
    mutate(reward, "ordering_changed", ("downstream_boundary", "candidate_ordering_changed"), True)
    mutate(reward, "selected_action", ("downstream_boundary", "selected_action_created"), True)
    mutate(reward, "final_action", ("downstream_boundary", "final_action_created"), True)
    mutate(reward, "direct_command", ("downstream_boundary", "direct_command_created"), True)
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
        "proto_purpose_approval_boundary_result_count": len(validation_results),
        "valid_proto_purpose_approval_boundary_count": len(valid),
        "invalid_proto_purpose_approval_boundary_count": len(validation_results) - len(valid),
        "approved_purpose_created_count": sum(1 for result in valid if result["approved_purpose_created"]),
        "approach_or_reach_item_approved_count": sum(
            1 for result in valid if result["proto_purpose"] == "approach_or_reach_item"
        ),
        "resolve_mismatch_approved_count": sum(
            1 for result in valid if result["proto_purpose"] == "resolve_mismatch"
        ),
        "support_user_comfort_approved_count": sum(
            1 for result in valid if result["proto_purpose"] == "support_user_comfort"
        ),
        "may_enter_future_candidate_ordering_boundary_count": sum(
            1 for result in valid if result["may_enter_future_candidate_ordering_boundary"]
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
        summary["valid_proto_purpose_approval_boundary_count"] == 3
        and summary["invalid_proto_purpose_approval_boundary_count"] == 29
        and summary["approved_purpose_created_count"] == 3
        and summary["approach_or_reach_item_approved_count"] == 1
        and summary["resolve_mismatch_approved_count"] == 1
        and summary["support_user_comfort_approved_count"] == 1
        and summary["may_enter_future_candidate_ordering_boundary_count"] == 3
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

