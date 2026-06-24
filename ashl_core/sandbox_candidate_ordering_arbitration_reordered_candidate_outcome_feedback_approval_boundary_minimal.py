"""Approval boundary from reordered-candidate outcome observations to future feedback."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_record,
)


COMMAND = (
    "run-sandbox-candidate-ordering-arbitration-reordered-candidate-outcome-feedback-"
    "approval-boundary-minimal-check"
)
FLOW = "sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary_minimal_v0"
PACKAGE_ID = (
    "PKG-Phase0-SandboxCandidateOrderingArbitrationReorderedCandidateOutcomeFeedbackApprovalBoundary-"
    "Minimal-v0"
)
BOUNDARY_INDEX_BEFORE = "2026-06-09-b163"
BOUNDARY_INDEX_AFTER = "2026-06-09-b164"

ALLOWED_FEEDBACK_TARGETS = {
    "arbitration_reordered_positive_item_contact_observed": (
        "arbitration_reordered_positive_item_contact_feedback"
    ),
    "arbitration_reordered_wait_context_observed": (
        "arbitration_reordered_wait_context_observation_feedback"
    ),
    "arbitration_reordered_mismatch_probe_context_observed": (
        "arbitration_reordered_mismatch_probe_context_feedback"
    ),
}

BLOCKED_FLAGS = {
    "feedback_evaluation_created",
    "feedback_applied",
    "feedback_loop_created",
    "candidate_reordering_created",
    "candidate_scores_changed",
    "next_cycle_candidate_ordering_changed",
    "new_selected_action_created",
    "new_final_action_created",
    "new_direct_command_created",
    "new_execution_created",
    "new_outcome_observation_created",
    "production_action_selection",
    "runtime_action_selection",
    "runtime_behavior_changed",
    "production_behavior_changed",
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
    "persistent_feedback_written",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "proof_of_learning_claim",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "feedback_approval_boundary_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_outcome_observation",
    "feedback_approval_boundary",
    "human_summary",
    "blocked_flags",
}


def build_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary_record(
    outcome_observation_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(outcome_observation_record)
        if outcome_observation_record is not None
        else build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_record()
    )
    source_validation = (
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_record(
            source
        )
    )
    if not source_validation["valid"]:
        raise ValueError("outcome_observation_record must validate before feedback approval boundary")

    source_summary = _source_summary(source)
    scenario = source_summary["scenario_id"]
    outcome_label = source_summary["outcome_label"]
    feedback_target = ALLOWED_FEEDBACK_TARGETS[outcome_label]
    return {
        "feedback_approval_boundary_id": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_"
            f"approval_boundary_{scenario}_demo_001"
        ),
        "record_type": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_"
            "approval_boundary_minimal"
        ),
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_outcome_observation": source_summary,
        "feedback_approval_boundary": {
            "future_feedback_allowed": True,
            "allowed_next_package": (
                "Sandbox Candidate Ordering Arbitration Reordered Candidate Outcome Feedback Minimal v0"
            ),
            "candidate_for_future_feedback": feedback_target,
            "candidate_source": (
                "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation"
            ),
            "feedback_scope": "same_session_sandbox_only",
            "feedback_evaluation_created_in_this_package": False,
            "feedback_applied_in_this_package": False,
            "feedback_loop_created_in_this_package": False,
            "candidate_reordering_created_in_this_package": False,
            "candidate_scores_changed_in_this_package": False,
            "next_cycle_candidate_ordering_changed_in_this_package": False,
            "new_action_created_in_this_package": False,
            "new_selected_action_created_in_this_package": False,
            "new_final_action_created_in_this_package": False,
            "new_direct_command_created_in_this_package": False,
            "new_execution_created_in_this_package": False,
            "new_outcome_observation_created_in_this_package": False,
            "future_feedback_application_requires_separate_boundary": True,
            "future_candidate_reordering_requires_separate_boundary": True,
            "future_memory_write_requires_separate_boundary": True,
            "future_retention_requires_separate_boundary": True,
            "future_predictor_influence_requires_separate_boundary": True,
            "future_production_promotion_requires_separate_boundary": True,
            "arbitration_rules_preserved": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "human_summary": {
            "what_was_opened": f"Outcome label {outcome_label} may enter a future feedback package.",
            "what_it_allows": (
                "A future package may create same-session sandbox feedback evaluation from this "
                "reordered-candidate outcome observation."
            ),
            "what_is_blocked": (
                "This package creates no feedback evaluation, applies no feedback, creates no loop or "
                "reordering, changes no scores or next-cycle ordering, creates no action or execution, "
                "writes no persistence, touches no predictor, and makes no proof claim."
            ),
            "plain_result": (
                "The reordered sandbox result can approach a future feedback gate, but it still cannot "
                "change the next try."
            ),
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_"
            "approval_boundary_minimal"
        ),
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_outcome_observation"), errors, "source_outcome_observation")
    boundary = _as_dict(record.get("feedback_approval_boundary"), errors, "feedback_approval_boundary")
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
        "final_action": source.get("final_action"),
        "direct_command": source.get("direct_command"),
        "observed_outcome": source.get("observed_outcome"),
        "outcome_label": source.get("outcome_label"),
        "future_feedback_allowed": boundary.get("future_feedback_allowed") is True,
        "feedback_creation_blocked": boundary.get("feedback_evaluation_created_in_this_package") is False
        and boundary.get("feedback_loop_created_in_this_package") is False
        and blocked.get("feedback_evaluation_created") is False
        and blocked.get("feedback_loop_created") is False,
        "feedback_application_blocked": boundary.get("feedback_applied_in_this_package") is False
        and blocked.get("feedback_applied") is False,
        "candidate_reordering_blocked": boundary.get("candidate_reordering_created_in_this_package") is False
        and boundary.get("candidate_scores_changed_in_this_package") is False
        and boundary.get("next_cycle_candidate_ordering_changed_in_this_package") is False
        and blocked.get("candidate_reordering_created") is False
        and blocked.get("candidate_scores_changed") is False
        and blocked.get("next_cycle_candidate_ordering_changed") is False,
        "action_creation_blocked": boundary.get("new_action_created_in_this_package") is False
        and boundary.get("new_selected_action_created_in_this_package") is False
        and boundary.get("new_final_action_created_in_this_package") is False
        and boundary.get("new_direct_command_created_in_this_package") is False
        and boundary.get("new_execution_created_in_this_package") is False
        and boundary.get("new_outcome_observation_created_in_this_package") is False
        and blocked.get("new_selected_action_created") is False
        and blocked.get("new_final_action_created") is False
        and blocked.get("new_direct_command_created") is False
        and blocked.get("new_execution_created") is False
        and blocked.get("new_outcome_observation_created") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False
        and blocked.get("persistent_feedback_written") is False,
        "predictor_use_blocked": blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False,
        "direct_feed_blocked": blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
        "arbitration_rules_preserved": boundary.get("arbitration_rules_preserved") is True,
    }


def run_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary_minimal_check() -> dict[
    str, Any
]:
    source_records = (
        run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation_minimal_check()[
            "valid_records"
        ]
    )
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary_record(
            source
        )
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary_record(
            record
        )
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
            "boundary_reason": (
                "Opens a future same-session sandbox feedback boundary from reordered-candidate "
                "outcome observations."
            ),
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": (
                "Reordered-candidate outcome observations can now reach a future feedback approval boundary."
            ),
            "what_changed": "Observed reordered-candidate outcomes may become future feedback candidates.",
            "what_is_blocked": (
                "No feedback evaluation/application, reordering, score/order mutation, action creation, "
                "persistence, predictor use, direct feed, production behavior, or proof claim is created."
            ),
            "plain_result": (
                "The second pass can ask whether its observed result may be studied as feedback later."
            ),
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    observation = source["outcome_observation"]
    return {
        "source_outcome_observation_record_id": source["outcome_observation_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": observation["scenario_id"],
        "approved_purpose": observation["approved_purpose"],
        "candidate_family": observation["candidate_family"],
        "selected_action": observation["selected_action"],
        "final_action": observation["final_action"],
        "direct_command": observation["direct_command"],
        "outcome_scope": observation["outcome_scope"],
        "outcome_observation_created": observation["outcome_observation_created"],
        "observed_outcome": observation["observed_outcome"],
        "outcome_label": observation["outcome_label"],
        "feedback_loop_created": observation["feedback_loop_created"],
        "candidate_reordering_created": observation["candidate_reordering_created"],
        "candidate_scores_changed": observation["candidate_scores_changed"],
        "runtime_next_cycle_candidate_ordering_changed": observation[
            "runtime_next_cycle_candidate_ordering_changed"
        ],
        "new_selected_action_created": observation["new_selected_action_created"],
        "new_final_action_created": observation["new_final_action_created"],
        "new_direct_command_created": observation["new_direct_command_created"],
        "new_execution_created": observation["new_execution_created"],
        "future_feedback_requires_separate_boundary": observation["future_feedback_requires_separate_boundary"],
        "future_candidate_reordering_requires_separate_boundary": observation[
            "future_candidate_reordering_requires_separate_boundary"
        ],
        "future_memory_write_requires_separate_boundary": observation[
            "future_memory_write_requires_separate_boundary"
        ],
        "future_retention_requires_separate_boundary": observation[
            "future_retention_requires_separate_boundary"
        ],
        "future_predictor_influence_requires_separate_boundary": observation[
            "future_predictor_influence_requires_separate_boundary"
        ],
        "future_production_promotion_requires_separate_boundary": observation[
            "future_production_promotion_requires_separate_boundary"
        ],
        "source_reordering_preserved": observation["source_reordering_preserved"],
        "same_purpose_only": observation["same_purpose_only"],
        "source_arbitration_rules_preserved": observation["arbitration_rules_preserved"],
        "source_rollback_available": observation["rollback_available"],
        "source_audit_recorded": observation["audit_recorded"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("outcome_label") not in ALLOWED_FEEDBACK_TARGETS:
        errors.append("source_outcome_label_not_feedback_eligible")
    expected = {
        "outcome_scope": "same_session_sandbox_only",
        "outcome_observation_created": True,
        "feedback_loop_created": False,
        "candidate_reordering_created": False,
        "candidate_scores_changed": False,
        "runtime_next_cycle_candidate_ordering_changed": False,
        "new_selected_action_created": False,
        "new_final_action_created": False,
        "new_direct_command_created": False,
        "new_execution_created": False,
        "future_feedback_requires_separate_boundary": True,
        "future_candidate_reordering_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "source_reordering_preserved": True,
        "same_purpose_only": True,
        "source_arbitration_rules_preserved": True,
        "source_rollback_available": True,
        "source_audit_recorded": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"{field}_not_expected")


def _validate_boundary(boundary: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "future_feedback_allowed": True,
        "allowed_next_package": (
            "Sandbox Candidate Ordering Arbitration Reordered Candidate Outcome Feedback Minimal v0"
        ),
        "candidate_for_future_feedback": ALLOWED_FEEDBACK_TARGETS.get(source.get("outcome_label")),
        "candidate_source": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_outcome_observation"
        ),
        "feedback_scope": "same_session_sandbox_only",
        "feedback_evaluation_created_in_this_package": False,
        "feedback_applied_in_this_package": False,
        "feedback_loop_created_in_this_package": False,
        "candidate_reordering_created_in_this_package": False,
        "candidate_scores_changed_in_this_package": False,
        "next_cycle_candidate_ordering_changed_in_this_package": False,
        "new_action_created_in_this_package": False,
        "new_selected_action_created_in_this_package": False,
        "new_final_action_created_in_this_package": False,
        "new_direct_command_created_in_this_package": False,
        "new_execution_created_in_this_package": False,
        "new_outcome_observation_created_in_this_package": False,
        "future_feedback_application_requires_separate_boundary": True,
        "future_candidate_reordering_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "arbitration_rules_preserved": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    for field, value in expected.items():
        if boundary.get(field) != value:
            errors.append(f"feedback_approval_boundary_{field}_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_opened", "what_it_allows", "what_is_blocked", "plain_result"):
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked_flags(blocked: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(flag for flag in BLOCKED_FLAGS if flag not in blocked)
    errors.extend(f"missing_blocked_flag:{flag}" for flag in missing)
    extra = sorted(flag for flag in blocked if flag not in BLOCKED_FLAGS)
    errors.extend(f"unexpected_blocked_flag:{flag}" for flag in extra)
    for field in sorted(BLOCKED_FLAGS):
        if blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")


def _invalid_records(reach: dict[str, Any], wait: dict[str, Any], probe: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["feedback_approval_boundary_id"] = f"{record['feedback_approval_boundary_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "sandbox_reordered_feedback_boundary")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "boundary_not_required", ("boundary_change_required",), False)
    mutate(reach, "source_not_validated", ("source_outcome_observation", "source_validated"), False)
    mutate(reach, "source_wrong_boundary_index", ("source_outcome_observation", "source_boundary_index"), "b163")
    mutate(reach, "source_wrong_scope", ("source_outcome_observation", "outcome_scope"), "production")
    mutate(reach, "source_not_observed", ("source_outcome_observation", "outcome_observation_created"), False)
    mutate(reach, "source_feedback_already_created", ("source_outcome_observation", "feedback_loop_created"), True)
    mutate(reach, "source_reordering_created", ("source_outcome_observation", "candidate_reordering_created"), True)
    mutate(reach, "source_scores_changed", ("source_outcome_observation", "candidate_scores_changed"), True)
    mutate(
        reach,
        "source_runtime_next_changed",
        ("source_outcome_observation", "runtime_next_cycle_candidate_ordering_changed"),
        True,
    )
    mutate(reach, "source_selected_action_created", ("source_outcome_observation", "new_selected_action_created"), True)
    mutate(reach, "source_final_action_created", ("source_outcome_observation", "new_final_action_created"), True)
    mutate(reach, "source_direct_command_created", ("source_outcome_observation", "new_direct_command_created"), True)
    mutate(reach, "source_execution_created", ("source_outcome_observation", "new_execution_created"), True)
    mutate(
        reach,
        "source_future_feedback_boundary_missing",
        ("source_outcome_observation", "future_feedback_requires_separate_boundary"),
        False,
    )
    mutate(
        reach,
        "source_future_reordering_boundary_missing",
        ("source_outcome_observation", "future_candidate_reordering_requires_separate_boundary"),
        False,
    )
    mutate(
        reach,
        "source_future_memory_missing",
        ("source_outcome_observation", "future_memory_write_requires_separate_boundary"),
        False,
    )
    mutate(
        reach,
        "source_future_retention_missing",
        ("source_outcome_observation", "future_retention_requires_separate_boundary"),
        False,
    )
    mutate(
        reach,
        "source_future_predictor_missing",
        ("source_outcome_observation", "future_predictor_influence_requires_separate_boundary"),
        False,
    )
    mutate(
        reach,
        "source_future_production_missing",
        ("source_outcome_observation", "future_production_promotion_requires_separate_boundary"),
        False,
    )
    mutate(reach, "source_reordering_not_preserved", ("source_outcome_observation", "source_reordering_preserved"), False)
    mutate(reach, "source_not_same_purpose", ("source_outcome_observation", "same_purpose_only"), False)
    mutate(reach, "source_rules_not_preserved", ("source_outcome_observation", "source_arbitration_rules_preserved"), False)
    mutate(reach, "source_rollback_missing", ("source_outcome_observation", "source_rollback_available"), False)
    mutate(reach, "source_audit_missing", ("source_outcome_observation", "source_audit_recorded"), False)
    mutate(reach, "source_bad_outcome_label", ("source_outcome_observation", "outcome_label"), "unknown")
    mutate(reach, "future_feedback_not_allowed", ("feedback_approval_boundary", "future_feedback_allowed"), False)
    mutate(reach, "wrong_next_package", ("feedback_approval_boundary", "allowed_next_package"), "Feedback Minimal v0")
    mutate(reach, "wrong_feedback_candidate", ("feedback_approval_boundary", "candidate_for_future_feedback"), "unknown")
    mutate(reach, "wrong_candidate_source", ("feedback_approval_boundary", "candidate_source"), "older_line")
    mutate(reach, "wrong_feedback_scope", ("feedback_approval_boundary", "feedback_scope"), "production")
    mutate(
        reach,
        "feedback_evaluation_created",
        ("feedback_approval_boundary", "feedback_evaluation_created_in_this_package"),
        True,
    )
    mutate(reach, "feedback_applied", ("feedback_approval_boundary", "feedback_applied_in_this_package"), True)
    mutate(reach, "feedback_loop_created", ("feedback_approval_boundary", "feedback_loop_created_in_this_package"), True)
    mutate(
        reach,
        "candidate_reordering_created",
        ("feedback_approval_boundary", "candidate_reordering_created_in_this_package"),
        True,
    )
    mutate(reach, "candidate_scores_changed", ("feedback_approval_boundary", "candidate_scores_changed_in_this_package"), True)
    mutate(
        reach,
        "next_cycle_changed",
        ("feedback_approval_boundary", "next_cycle_candidate_ordering_changed_in_this_package"),
        True,
    )
    mutate(reach, "new_action_created", ("feedback_approval_boundary", "new_action_created_in_this_package"), True)
    mutate(
        reach,
        "new_selected_action_created",
        ("feedback_approval_boundary", "new_selected_action_created_in_this_package"),
        True,
    )
    mutate(reach, "new_final_action_created", ("feedback_approval_boundary", "new_final_action_created_in_this_package"), True)
    mutate(
        reach,
        "new_direct_command_created",
        ("feedback_approval_boundary", "new_direct_command_created_in_this_package"),
        True,
    )
    mutate(reach, "new_execution_created", ("feedback_approval_boundary", "new_execution_created_in_this_package"), True)
    mutate(
        reach,
        "new_outcome_observation_created",
        ("feedback_approval_boundary", "new_outcome_observation_created_in_this_package"),
        True,
    )
    mutate(
        reach,
        "future_feedback_application_boundary_missing",
        ("feedback_approval_boundary", "future_feedback_application_requires_separate_boundary"),
        False,
    )
    mutate(
        reach,
        "future_reordering_boundary_missing",
        ("feedback_approval_boundary", "future_candidate_reordering_requires_separate_boundary"),
        False,
    )
    mutate(reach, "future_memory_missing", ("feedback_approval_boundary", "future_memory_write_requires_separate_boundary"), False)
    mutate(reach, "future_retention_missing", ("feedback_approval_boundary", "future_retention_requires_separate_boundary"), False)
    mutate(
        reach,
        "future_predictor_missing",
        ("feedback_approval_boundary", "future_predictor_influence_requires_separate_boundary"),
        False,
    )
    mutate(
        reach,
        "future_production_missing",
        ("feedback_approval_boundary", "future_production_promotion_requires_separate_boundary"),
        False,
    )
    mutate(reach, "rules_not_preserved", ("feedback_approval_boundary", "arbitration_rules_preserved"), False)
    mutate(reach, "rollback_missing", ("feedback_approval_boundary", "rollback_available"), False)
    mutate(reach, "audit_missing", ("feedback_approval_boundary", "audit_recorded"), False)
    mutate(wait, "blocked_feedback_evaluation", ("blocked_flags", "feedback_evaluation_created"), True)
    mutate(wait, "blocked_feedback_applied", ("blocked_flags", "feedback_applied"), True)
    mutate(wait, "blocked_feedback_loop", ("blocked_flags", "feedback_loop_created"), True)
    mutate(wait, "blocked_reordering", ("blocked_flags", "candidate_reordering_created"), True)
    mutate(wait, "blocked_scores", ("blocked_flags", "candidate_scores_changed"), True)
    mutate(wait, "blocked_next_cycle", ("blocked_flags", "next_cycle_candidate_ordering_changed"), True)
    mutate(wait, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(wait, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(wait, "new_retention", ("blocked_flags", "new_retention_written"), True)
    mutate(wait, "persistent_feedback", ("blocked_flags", "persistent_feedback_written"), True)
    mutate(wait, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(wait, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(wait, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(probe, "direct_endocrine_feed", ("blocked_flags", "direct_endocrine_feed"), True)
    mutate(probe, "direct_tendency_feed", ("blocked_flags", "direct_tendency_feed"), True)
    mutate(probe, "runtime_behavior_changed", ("blocked_flags", "runtime_behavior_changed"), True)
    mutate(probe, "production_behavior_changed", ("blocked_flags", "production_behavior_changed"), True)
    mutate(probe, "new_selected_action", ("blocked_flags", "new_selected_action_created"), True)
    mutate(probe, "new_final_action", ("blocked_flags", "new_final_action_created"), True)
    mutate(probe, "new_direct_command", ("blocked_flags", "new_direct_command_created"), True)
    mutate(probe, "new_execution", ("blocked_flags", "new_execution_created"), True)
    mutate(probe, "new_outcome_observation", ("blocked_flags", "new_outcome_observation_created"), True)
    mutate(probe, "purpose_changed_by_tendency", ("blocked_flags", "purpose_changed_by_tendency"), True)
    mutate(probe, "raw_weighted_sum", ("blocked_flags", "raw_weighted_sum_used"), True)
    mutate(probe, "affordance_as_desire", ("blocked_flags", "affordance_used_as_desire"), True)
    mutate(probe, "cross_purpose_feedback", ("blocked_flags", "feedback_cross_purpose_applied"), True)
    mutate(probe, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "feedback_approval_boundary_result_count": len(validation_results),
        "valid_feedback_approval_boundary_count": len(valid),
        "invalid_feedback_approval_boundary_count": len(validation_results) - len(valid),
        "future_feedback_allowed_count": sum(1 for result in valid if result["future_feedback_allowed"]),
        "positive_item_feedback_boundary_count": sum(
            1
            for result in valid
            if result["outcome_label"] == "arbitration_reordered_positive_item_contact_observed"
        ),
        "wait_context_feedback_boundary_count": sum(
            1 for result in valid if result["outcome_label"] == "arbitration_reordered_wait_context_observed"
        ),
        "mismatch_probe_feedback_boundary_count": sum(
            1
            for result in valid
            if result["outcome_label"] == "arbitration_reordered_mismatch_probe_context_observed"
        ),
        "feedback_creation_blocked_count": sum(1 for result in valid if result["feedback_creation_blocked"]),
        "feedback_application_blocked_count": sum(1 for result in valid if result["feedback_application_blocked"]),
        "candidate_reordering_blocked_count": sum(1 for result in valid if result["candidate_reordering_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "arbitration_rules_preserved_count": sum(1 for result in valid if result["arbitration_rules_preserved"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["feedback_approval_boundary_result_count"] == 84
        and summary["valid_feedback_approval_boundary_count"] == 3
        and summary["invalid_feedback_approval_boundary_count"] == 81
        and summary["future_feedback_allowed_count"] == 3
        and summary["positive_item_feedback_boundary_count"] == 1
        and summary["wait_context_feedback_boundary_count"] == 1
        and summary["mismatch_probe_feedback_boundary_count"] == 1
        and summary["feedback_creation_blocked_count"] == 3
        and summary["feedback_application_blocked_count"] == 3
        and summary["candidate_reordering_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["arbitration_rules_preserved_count"] == 3
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
