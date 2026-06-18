"""Trace-only proto-purpose candidates derived from bounded experience patterns."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-experience-derived-proto-purpose-candidate-trace-minimal-check"
FLOW = "experience_derived_proto_purpose_candidate_trace_minimal_v0"

ALLOWED_EXPERIENCE_TYPES = {
    "reward_experience",
    "prediction_error_resolution_experience",
    "comfort_settling_experience",
}
ALLOWED_PROTO_PURPOSES = {
    "approach_or_reach_item",
    "resolve_mismatch",
    "support_user_comfort",
}
ALLOWED_GAP_TYPES = {
    "positive_item_state_gap",
    "prediction_error_gap",
    "care_state_gap",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "trace_id",
    "trace_type",
    "trace_mode",
    "experience_source",
    "experience_derived_expectation",
    "observed_state",
    "gap_assessment",
    "proto_purpose_candidate",
    "approval_boundary",
    "human_summary",
    "blocked_flags",
}
BLOCKED_FLAGS = {
    "approved_purpose_created",
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


def build_experience_derived_proto_purpose_candidate_traces() -> dict[str, Any]:
    records = [_build_record(case) for case in _case_definitions()]
    return {
        "record_set_id": "experience_derived_proto_purpose_candidate_trace_set_demo_001",
        "record_set_type": "experience_derived_proto_purpose_candidate_trace_set_minimal",
        "record_set_mode": "trace_only_proto_purpose_candidates",
        "record_count": len(records),
        "records": records,
        "human_summary": {
            "what_was_built": "Three experience-derived proto-purpose candidate traces were created.",
            "what_it_means": "Experience can shape ideal expected states that create proto-purpose candidates.",
            "what_is_blocked": "No proto-purpose is approved, ordered, selected, executed, remembered, or treated as proof of learning.",
            "plain_result": "Qingyin can now represent purpose pressure as trace evidence without granting action authority.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_experience_derived_proto_purpose_candidate_trace(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    if record.get("trace_type") != "experience_derived_proto_purpose_candidate_trace":
        errors.append("trace_type_not_expected")
    if record.get("trace_mode") != "proto_purpose_trace_only":
        errors.append("trace_mode_not_expected")

    experience = _as_dict(record.get("experience_source"), errors, "experience_source")
    expectation = _as_dict(record.get("experience_derived_expectation"), errors, "experience_derived_expectation")
    observed = _as_dict(record.get("observed_state"), errors, "observed_state")
    gap = _as_dict(record.get("gap_assessment"), errors, "gap_assessment")
    candidate = _as_dict(record.get("proto_purpose_candidate"), errors, "proto_purpose_candidate")
    approval = _as_dict(record.get("approval_boundary"), errors, "approval_boundary")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_experience(experience, errors)
    _validate_expectation(expectation, errors)
    _validate_observed_state(observed, errors)
    _validate_gap(gap, errors)
    _validate_candidate(candidate, expectation, gap, errors)
    _validate_approval(approval, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)
    _validate_case_pairing(experience, expectation, gap, candidate, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "experience_type": experience.get("experience_type"),
        "proto_purpose": candidate.get("proto_purpose"),
        "ideal_expected_state": expectation.get("ideal_expected_state"),
        "gap_detected": gap.get("gap_detected") is True,
        "proto_purpose_candidate_created": candidate.get("proto_purpose_candidate_created") is True,
        "requires_purpose_approval": approval.get("requires_purpose_approval") is True,
        "approved_purpose_blocked": approval.get("approved_purpose_created") is False
        and blocked.get("approved_purpose_created") is False,
        "action_authority_blocked": candidate.get("action_authority") is False
        and approval.get("action_authority_granted") is False,
        "ordering_blocked": blocked.get("candidate_ordering_changed") is False
        and blocked.get("candidate_reordering_applied") is False,
        "action_creation_blocked": blocked.get("selected_action_created") is False
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


def run_experience_derived_proto_purpose_candidate_trace_minimal_check() -> dict[str, Any]:
    record_set = build_experience_derived_proto_purpose_candidate_traces()
    valid_records = record_set["records"]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [validate_experience_derived_proto_purpose_candidate_trace(record) for record in records]
    valid_results = [result for result in validation_results if result["valid"]]
    summary = _summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "record_set": record_set,
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Experience-derived proto-purpose candidate traces were added.",
            "what_changed": "Reward, mismatch-resolution, and comfort-settling experience can each produce trace-only proto-purpose candidates.",
            "what_is_blocked": "No approved purpose, candidate ordering, selected_action, final_action, direct command, memory write, predictor mutation, or proof claim is created.",
            "plain_result": "The thinking line now has observable proto-purpose pressure without granting action authority.",
        },
        "valid_result_count": len(valid_results),
    }


def _case_definitions() -> list[dict[str, Any]]:
    return [
        {
            "suffix": "reward_item",
            "experience_type": "reward_experience",
            "experience_event": "item_contact_reward_observed",
            "experience_summary": "A reachable item contact produced a positive reward-like outcome in a bounded sandbox trace.",
            "expected_state": "reachable_item_contact_can_be_positive",
            "ideal_expected_state": "reachable_positive_item_contact_under_approved_purpose",
            "observed_state": "positive_item_not_currently_contacted",
            "gap_type": "positive_item_state_gap",
            "proto_purpose": "approach_or_reach_item",
            "proto_purpose_statement": "A positive item-contact experience can suggest approaching or reaching a reachable item, pending purpose approval.",
        },
        {
            "suffix": "mismatch_resolution",
            "experience_type": "prediction_error_resolution_experience",
            "experience_event": "observe_again_reduced_prediction_error",
            "experience_summary": "Re-observation reduced a mismatch in a controlled trace.",
            "expected_state": "re_observation_can_reduce_uncertainty",
            "ideal_expected_state": "uncertainty_is_lower",
            "observed_state": "uncertainty_or_mismatch_present",
            "gap_type": "prediction_error_gap",
            "proto_purpose": "resolve_mismatch",
            "proto_purpose_statement": "A mismatch-resolution experience can suggest observing or verifying again, pending purpose approval.",
        },
        {
            "suffix": "comfort_settling",
            "experience_type": "comfort_settling_experience",
            "experience_event": "trusted_comfort_reduced_pressure",
            "experience_summary": "Trusted comfort or safe review was associated with reduced pressure in a settling design trace.",
            "expected_state": "trusted_comfort_can_support_settling",
            "ideal_expected_state": "user_or_system_state_more_settled",
            "observed_state": "pressure_or_distress_context_present",
            "gap_type": "care_state_gap",
            "proto_purpose": "support_user_comfort",
            "proto_purpose_statement": "A comfort-settling experience can suggest supporting comfort or settling, pending purpose approval.",
        },
    ]


def _build_record(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "trace_id": f"experience_derived_proto_purpose_candidate_{case['suffix']}_demo_001",
        "trace_type": "experience_derived_proto_purpose_candidate_trace",
        "trace_mode": "proto_purpose_trace_only",
        "experience_source": {
            "experience_source_id": f"experience_source_{case['suffix']}_demo_001",
            "experience_type": case["experience_type"],
            "experience_event": case["experience_event"],
            "experience_summary": case["experience_summary"],
            "experience_source_scope": "bounded_trace_fixture",
            "experience_directly_creates_purpose": False,
        },
        "experience_derived_expectation": {
            "expected_state": case["expected_state"],
            "ideal_expected_state": case["ideal_expected_state"],
            "expectation_source": "experience_derived",
            "ideal_expected_state_created": True,
            "action_authority": False,
        },
        "observed_state": {
            "observed_state_id": f"observed_state_{case['suffix']}_demo_001",
            "observed_state": case["observed_state"],
            "observed_state_scope": "bounded_trace_fixture",
        },
        "gap_assessment": {
            "gap_type": case["gap_type"],
            "gap_detected": True,
            "gap_against_ideal_expected_state": True,
            "gap_summary": "Observed state differs from the experience-derived ideal expected state.",
        },
        "proto_purpose_candidate": {
            "proto_purpose": case["proto_purpose"],
            "proto_purpose_candidate_created": True,
            "proto_purpose_statement": case["proto_purpose_statement"],
            "candidate_scope": "trace_only",
            "action_authority": False,
        },
        "approval_boundary": {
            "requires_purpose_approval": True,
            "approved_purpose_created": False,
            "approved_purpose_id": None,
            "action_authority_granted": False,
            "candidate_ordering_allowed": False,
            "next_required_boundary": "proto_purpose_approval_boundary_minimal_v0",
        },
        "human_summary": {
            "what_was_observed": case["experience_summary"],
            "what_expectation_formed": f"Experience shaped ideal expected state: {case['ideal_expected_state']}.",
            "what_proto_purpose_was_created": case["proto_purpose_statement"],
            "what_is_blocked": "The proto-purpose remains trace-only and cannot authorize action or memory.",
            "plain_result": "An experience-derived ideal expectation created a proto-purpose candidate, but no approved purpose was created.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def _validate_experience(experience: dict[str, Any], errors: list[str]) -> None:
    for field in ("experience_source_id", "experience_event", "experience_summary", "experience_source_scope"):
        if not _non_empty_string(experience.get(field)):
            errors.append(f"experience_source_{field}_empty")
    if experience.get("experience_type") not in ALLOWED_EXPERIENCE_TYPES:
        errors.append("experience_source_experience_type_not_allowed")
    if experience.get("experience_source_scope") != "bounded_trace_fixture":
        errors.append("experience_source_scope_not_bounded_trace_fixture")
    if experience.get("experience_directly_creates_purpose") is not False:
        errors.append("experience_directly_creates_purpose_not_false")


def _validate_expectation(expectation: dict[str, Any], errors: list[str]) -> None:
    for field in ("expected_state", "ideal_expected_state", "expectation_source"):
        if not _non_empty_string(expectation.get(field)):
            errors.append(f"experience_derived_expectation_{field}_empty")
    if expectation.get("expectation_source") != "experience_derived":
        errors.append("expectation_source_not_experience_derived")
    if expectation.get("ideal_expected_state_created") is not True:
        errors.append("ideal_expected_state_created_not_true")
    if expectation.get("action_authority") is not False:
        errors.append("expectation_action_authority_not_false")


def _validate_observed_state(observed: dict[str, Any], errors: list[str]) -> None:
    for field in ("observed_state_id", "observed_state", "observed_state_scope"):
        if not _non_empty_string(observed.get(field)):
            errors.append(f"observed_state_{field}_empty")
    if observed.get("observed_state_scope") != "bounded_trace_fixture":
        errors.append("observed_state_scope_not_bounded_trace_fixture")


def _validate_gap(gap: dict[str, Any], errors: list[str]) -> None:
    if gap.get("gap_type") not in ALLOWED_GAP_TYPES:
        errors.append("gap_type_not_allowed")
    if gap.get("gap_detected") is not True:
        errors.append("gap_detected_not_true")
    if gap.get("gap_against_ideal_expected_state") is not True:
        errors.append("gap_against_ideal_expected_state_not_true")
    if not _non_empty_string(gap.get("gap_summary")):
        errors.append("gap_summary_empty")


def _validate_candidate(
    candidate: dict[str, Any],
    expectation: dict[str, Any],
    gap: dict[str, Any],
    errors: list[str],
) -> None:
    if candidate.get("proto_purpose") not in ALLOWED_PROTO_PURPOSES:
        errors.append("proto_purpose_not_allowed")
    if candidate.get("proto_purpose_candidate_created") is not True:
        errors.append("proto_purpose_candidate_created_not_true")
    if not _non_empty_string(candidate.get("proto_purpose_statement")):
        errors.append("proto_purpose_statement_empty")
    if candidate.get("candidate_scope") != "trace_only":
        errors.append("candidate_scope_not_trace_only")
    if candidate.get("action_authority") is not False:
        errors.append("proto_purpose_action_authority_not_false")
    if expectation.get("ideal_expected_state_created") is True and gap.get("gap_detected") is not True:
        errors.append("proto_purpose_requires_gap")


def _validate_approval(approval: dict[str, Any], errors: list[str]) -> None:
    if approval.get("requires_purpose_approval") is not True:
        errors.append("requires_purpose_approval_not_true")
    if approval.get("approved_purpose_created") is not False:
        errors.append("approved_purpose_created_not_false")
    if approval.get("approved_purpose_id") is not None:
        errors.append("approved_purpose_id_not_none")
    if approval.get("action_authority_granted") is not False:
        errors.append("action_authority_granted_not_false")
    if approval.get("candidate_ordering_allowed") is not False:
        errors.append("candidate_ordering_allowed_not_false")
    if approval.get("next_required_boundary") != "proto_purpose_approval_boundary_minimal_v0":
        errors.append("next_required_boundary_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in (
        "what_was_observed",
        "what_expectation_formed",
        "what_proto_purpose_was_created",
        "what_is_blocked",
        "plain_result",
    ):
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked_flags(blocked: dict[str, Any], errors: list[str]) -> None:
    for field in sorted(BLOCKED_FLAGS):
        if field not in blocked:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")


def _validate_case_pairing(
    experience: dict[str, Any],
    expectation: dict[str, Any],
    gap: dict[str, Any],
    candidate: dict[str, Any],
    errors: list[str],
) -> None:
    pairings = {
        "reward_experience": (
            "reachable_positive_item_contact_under_approved_purpose",
            "positive_item_state_gap",
            "approach_or_reach_item",
        ),
        "prediction_error_resolution_experience": (
            "uncertainty_is_lower",
            "prediction_error_gap",
            "resolve_mismatch",
        ),
        "comfort_settling_experience": (
            "user_or_system_state_more_settled",
            "care_state_gap",
            "support_user_comfort",
        ),
    }
    expected = pairings.get(experience.get("experience_type"))
    if expected is None:
        return
    expected_ideal, expected_gap, expected_proto = expected
    if expectation.get("ideal_expected_state") != expected_ideal:
        errors.append("case_ideal_expected_state_mismatch")
    if gap.get("gap_type") != expected_gap:
        errors.append("case_gap_type_mismatch")
    if candidate.get("proto_purpose") != expected_proto:
        errors.append("case_proto_purpose_mismatch")


def _invalid_records(reward: dict[str, Any], mismatch: dict[str, Any], comfort: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["trace_id"] = f"{record['trace_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reward, "bad_trace_mode", ("trace_mode",), "approved_purpose")
    mutate(reward, "bad_experience_type", ("experience_source", "experience_type"), "unbounded_reward")
    mutate(reward, "experience_direct_purpose", ("experience_source", "experience_directly_creates_purpose"), True)
    mutate(reward, "bad_expectation_source", ("experience_derived_expectation", "expectation_source"), "llm_free_text")
    mutate(reward, "expectation_action_authority", ("experience_derived_expectation", "action_authority"), True)
    mutate(reward, "gap_missing", ("gap_assessment", "gap_detected"), False)
    mutate(reward, "wrong_gap_type", ("gap_assessment", "gap_type"), "care_state_gap")
    mutate(reward, "wrong_proto_purpose", ("proto_purpose_candidate", "proto_purpose"), "support_user_comfort")
    mutate(reward, "candidate_scope", ("proto_purpose_candidate", "candidate_scope"), "ordering")
    mutate(reward, "candidate_action_authority", ("proto_purpose_candidate", "action_authority"), True)
    mutate(reward, "approval_not_required", ("approval_boundary", "requires_purpose_approval"), False)
    mutate(reward, "approved_purpose_created", ("approval_boundary", "approved_purpose_created"), True)
    mutate(reward, "approved_purpose_id", ("approval_boundary", "approved_purpose_id"), "approved_purpose_demo")
    mutate(reward, "action_authority_granted", ("approval_boundary", "action_authority_granted"), True)
    mutate(reward, "candidate_ordering_allowed", ("approval_boundary", "candidate_ordering_allowed"), True)
    mutate(reward, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(reward, "selected_action", ("blocked_flags", "selected_action_created"), True)
    mutate(reward, "final_action", ("blocked_flags", "final_action_created"), True)
    mutate(reward, "direct_command", ("blocked_flags", "direct_command_created"), True)
    mutate(reward, "reward_seeking", ("blocked_flags", "unlimited_reward_seeking"), True)
    mutate(mismatch, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(mismatch, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(comfort, "emotion_claim", ("blocked_flags", "emotion_recognition_claim"), True)
    mutate(comfort, "user_happiness_claim", ("blocked_flags", "user_happiness_claim"), True)
    mutate(comfort, "emotional_manipulation", ("blocked_flags", "emotional_manipulation"), True)
    mutate(comfort, "empty_human_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "proto_purpose_candidate_trace_result_count": len(validation_results),
        "valid_proto_purpose_candidate_trace_count": len(valid),
        "invalid_proto_purpose_candidate_trace_count": len(validation_results) - len(valid),
        "reward_experience_trace_count": sum(
            1 for result in valid if result["experience_type"] == "reward_experience"
        ),
        "prediction_error_resolution_trace_count": sum(
            1 for result in valid if result["experience_type"] == "prediction_error_resolution_experience"
        ),
        "comfort_settling_trace_count": sum(
            1 for result in valid if result["experience_type"] == "comfort_settling_experience"
        ),
        "approach_or_reach_item_proto_purpose_count": sum(
            1 for result in valid if result["proto_purpose"] == "approach_or_reach_item"
        ),
        "resolve_mismatch_proto_purpose_count": sum(
            1 for result in valid if result["proto_purpose"] == "resolve_mismatch"
        ),
        "support_user_comfort_proto_purpose_count": sum(
            1 for result in valid if result["proto_purpose"] == "support_user_comfort"
        ),
        "requires_purpose_approval_count": sum(
            1 for result in valid if result["requires_purpose_approval"]
        ),
        "approved_purpose_blocked_count": sum(
            1 for result in valid if result["approved_purpose_blocked"]
        ),
        "action_authority_blocked_count": sum(
            1 for result in valid if result["action_authority_blocked"]
        ),
        "ordering_blocked_count": sum(1 for result in valid if result["ordering_blocked"]),
        "action_creation_blocked_count": sum(
            1 for result in valid if result["action_creation_blocked"]
        ),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_mutation_blocked_count": sum(
            1 for result in valid if result["predictor_mutation_blocked"]
        ),
        "manipulation_blocked_count": sum(1 for result in valid if result["manipulation_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["valid_proto_purpose_candidate_trace_count"] == 3
        and summary["invalid_proto_purpose_candidate_trace_count"] == 26
        and summary["reward_experience_trace_count"] == 1
        and summary["prediction_error_resolution_trace_count"] == 1
        and summary["comfort_settling_trace_count"] == 1
        and summary["requires_purpose_approval_count"] == 3
        and summary["approved_purpose_blocked_count"] == 3
        and summary["action_authority_blocked_count"] == 3
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

