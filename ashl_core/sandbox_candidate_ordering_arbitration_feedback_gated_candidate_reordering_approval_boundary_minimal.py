"""Approval boundary for future arbitration feedback-gated candidate reordering."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_outcome_feedback_application_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_outcome_feedback_application_record,
    run_sandbox_candidate_ordering_arbitration_outcome_feedback_application_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_record,
)


COMMAND = "run-sandbox-candidate-ordering-arbitration-feedback-gated-candidate-reordering-approval-boundary-minimal-check"
FLOW = "sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingArbitrationFeedbackGatedCandidateReorderingApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b152"
BOUNDARY_INDEX_AFTER = "2026-06-09-b153"

FEEDBACK_APPLICATION_TO_REORDERING_TARGET = {
    "arbitration_positive_item_contact_feedback_application": {
        "candidate_for_future_reordering": "reach_front_item",
        "future_reordering_label": "positive_item_contact_feedback_may_prioritize_reach",
        "boundary_reason": "Record-only positive item contact feedback may support future advisory candidate reordering.",
    },
    "arbitration_wait_context_observation_feedback_application": {
        "candidate_for_future_reordering": "wait_or_observe",
        "future_reordering_label": "wait_context_feedback_may_prioritize_observation",
        "boundary_reason": "Record-only wait/context feedback may support future advisory wait-or-observe ordering.",
    },
    "arbitration_mismatch_probe_context_feedback_application": {
        "candidate_for_future_reordering": "observe_or_alternative_probe",
        "future_reordering_label": "mismatch_probe_feedback_may_prioritize_probe",
        "boundary_reason": "Record-only mismatch probe feedback may support future advisory verification ordering.",
    },
}

BLOCKED_FLAGS = {
    "feedback_application_created_in_this_package",
    "feedback_loop_created",
    "candidate_reordering_created",
    "candidate_reordering_applied",
    "candidate_ordering_changed",
    "candidate_scores_changed",
    "next_cycle_candidate_ordering_changed",
    "new_action_created",
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
    "reordering_approval_boundary_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_feedback_application",
    "feedback_gated_reordering_approval_boundary",
    "feedback_reordering_safety_boundary",
    "human_summary",
    "blocked_flags",
}


def build_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_record(
    feedback_application_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(feedback_application_record)
        if feedback_application_record is not None
        else build_sandbox_candidate_ordering_arbitration_outcome_feedback_application_record()
    )
    source_validation = validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_record(source)
    if not source_validation["valid"]:
        raise ValueError("feedback_application_record must validate before reordering approval boundary")

    source_summary = _source_summary(source)
    application_type = source_summary["feedback_application_type"]
    target = FEEDBACK_APPLICATION_TO_REORDERING_TARGET[application_type]
    scenario = source_summary["scenario_id"]
    return {
        "reordering_approval_boundary_id": (
            "sandbox_candidate_ordering_arbitration_feedback_gated_reordering_approval_boundary_"
            f"{scenario}_demo_001"
        ),
        "record_type": "sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_feedback_application": source_summary,
        "feedback_gated_reordering_approval_boundary": {
            "future_candidate_reordering_allowed": True,
            "allowed_next_package": "Sandbox Candidate Ordering Arbitration Feedback-Gated Candidate Reordering Minimal v0",
            "candidate_for_future_reordering": target["candidate_for_future_reordering"],
            "future_reordering_label": target["future_reordering_label"],
            "candidate_source": "sandbox_candidate_ordering_arbitration_outcome_feedback_application",
            "feedback_application_type": application_type,
            "reordering_scope": "same_session_sandbox_only",
            "reordering_effect_scope": "future_advisory_candidate_ordering_only",
            "feedback_application_created_in_this_package": False,
            "feedback_loop_created_in_this_package": False,
            "candidate_reordering_applied_in_this_package": False,
            "candidate_ordering_changed_in_this_package": False,
            "candidate_scores_changed_in_this_package": False,
            "next_cycle_candidate_ordering_changed_in_this_package": False,
            "candidate_order_before": [],
            "candidate_order_after": [],
            "ordering_delta": 0.0,
            "new_action_created_in_this_package": False,
            "new_selected_action_created_in_this_package": False,
            "new_final_action_created_in_this_package": False,
            "new_direct_command_created_in_this_package": False,
            "new_execution_created_in_this_package": False,
            "new_outcome_observation_created_in_this_package": False,
            "future_selected_action_requires_separate_boundary": True,
            "future_final_action_requires_separate_boundary": True,
            "future_direct_command_requires_separate_boundary": True,
            "future_execution_requires_separate_boundary": True,
            "future_memory_write_requires_separate_boundary": True,
            "future_retention_requires_separate_boundary": True,
            "future_predictor_influence_requires_separate_boundary": True,
            "future_production_promotion_requires_separate_boundary": True,
            "arbitration_rules_preserved": True,
            "rollback_available": True,
            "audit_recorded": True,
            "boundary_reason": target["boundary_reason"],
        },
        "feedback_reordering_safety_boundary": {
            "same_session_scope_required": True,
            "sandbox_scope_required": True,
            "same_purpose_only": True,
            "record_only_feedback_application_required": True,
            "direct_endocrine_feed_allowed": False,
            "direct_tendency_feed_allowed": False,
            "memory_write_requires_separate_boundary": True,
            "retention_write_requires_separate_boundary": True,
            "predictor_influence_requires_separate_boundary": True,
            "production_promotion_requires_separate_boundary": True,
            "proof_of_learning_claim_allowed": False,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "human_summary": {
            "what_was_opened": "A future sandbox-only feedback-gated candidate reordering approval boundary was opened.",
            "what_it_allows": f"A future package may consider {application_type} for advisory candidate reordering.",
            "what_is_blocked": "This package does not reorder candidates, change scores, alter next-cycle ordering, create actions, execute, observe outcomes, persist feedback, write memory, touch predictors, feed endocrine/tendency systems, change production behavior, or prove learning.",
            "plain_result": "Record-only feedback may approach future ordering review, but no candidate order changed now.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_feedback_application"), errors, "source_feedback_application")
    boundary = _as_dict(
        record.get("feedback_gated_reordering_approval_boundary"),
        errors,
        "feedback_gated_reordering_approval_boundary",
    )
    safety = _as_dict(
        record.get("feedback_reordering_safety_boundary"),
        errors,
        "feedback_reordering_safety_boundary",
    )
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_boundary(boundary, source, errors)
    _validate_safety(safety, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "direct_command": source.get("direct_command"),
        "feedback_application_type": source.get("feedback_application_type"),
        "candidate_for_future_reordering": boundary.get("candidate_for_future_reordering"),
        "future_candidate_reordering_allowed": boundary.get("future_candidate_reordering_allowed") is True,
        "candidate_reordering_blocked": boundary.get("candidate_reordering_applied_in_this_package") is False
        and boundary.get("candidate_ordering_changed_in_this_package") is False
        and boundary.get("candidate_scores_changed_in_this_package") is False
        and boundary.get("next_cycle_candidate_ordering_changed_in_this_package") is False
        and boundary.get("candidate_order_before") == []
        and boundary.get("candidate_order_after") == []
        and boundary.get("ordering_delta") == 0.0
        and blocked.get("candidate_reordering_created") is False
        and blocked.get("candidate_reordering_applied") is False
        and blocked.get("candidate_ordering_changed") is False
        and blocked.get("candidate_scores_changed") is False
        and blocked.get("next_cycle_candidate_ordering_changed") is False,
        "feedback_loop_blocked": boundary.get("feedback_loop_created_in_this_package") is False
        and blocked.get("feedback_loop_created") is False,
        "action_creation_blocked": boundary.get("new_action_created_in_this_package") is False
        and boundary.get("new_selected_action_created_in_this_package") is False
        and boundary.get("new_final_action_created_in_this_package") is False
        and boundary.get("new_direct_command_created_in_this_package") is False
        and boundary.get("new_execution_created_in_this_package") is False
        and boundary.get("new_outcome_observation_created_in_this_package") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False
        and blocked.get("persistent_feedback_written") is False,
        "predictor_use_blocked": blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False,
        "direct_feed_blocked": safety.get("direct_endocrine_feed_allowed") is False
        and safety.get("direct_tendency_feed_allowed") is False
        and blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False,
        "proof_claim_blocked": safety.get("proof_of_learning_claim_allowed") is False
        and blocked.get("proof_of_learning_claim") is False,
        "arbitration_rules_preserved": boundary.get("arbitration_rules_preserved") is True,
    }


def run_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_minimal_check() -> dict[str, Any]:
    source_records = run_sandbox_candidate_ordering_arbitration_outcome_feedback_application_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_record(
            source
        )
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_feedback_gated_candidate_reordering_approval_boundary_record(
            record
        )
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
            "boundary_reason": "Opens a future candidate reordering approval boundary from record-only arbitration feedback applications.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Record-only arbitration feedback applications can now reach a future reordering approval boundary.",
            "what_changed": "The next package may study sandbox-only advisory candidate reordering from b152 records.",
            "what_is_blocked": "No reordering, scoring change, next-cycle ordering change, action, execution, outcome observation, persistence, predictor influence, production behavior, or proof claim is created.",
            "plain_result": "The feedback can be reviewed for future ordering, but it still cannot change the next choice.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    application = source["same_session_feedback_application"]
    return {
        "source_feedback_application_record_id": source["feedback_application_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": application["scenario_id"],
        "approved_purpose": application["approved_purpose"],
        "candidate_family": application["candidate_family"],
        "direct_command": application["direct_command"],
        "observed_outcome": application["observed_outcome"],
        "outcome_label": application["outcome_label"],
        "source_feedback_type": application["source_feedback_type"],
        "feedback_application_type": application["feedback_application_type"],
        "feedback_application_created": application["feedback_application_created"],
        "feedback_applied": application["feedback_applied"],
        "feedback_application_scope": application["feedback_application_scope"],
        "feedback_application_effect_scope": application["feedback_application_effect_scope"],
        "feedback_loop_created_in_source_package": application["feedback_loop_created"],
        "candidate_reordering_created_in_source_package": application["candidate_reordering_created"],
        "candidate_scores_changed_in_source_package": application["candidate_scores_changed"],
        "next_cycle_candidate_ordering_changed_in_source_package": application[
            "next_cycle_candidate_ordering_changed"
        ],
        "new_action_created_in_source_package": application["new_action_created"],
        "new_selected_action_created_in_source_package": application["new_selected_action_created"],
        "new_final_action_created_in_source_package": application["new_final_action_created"],
        "new_direct_command_created_in_source_package": application["new_direct_command_created"],
        "new_execution_created_in_source_package": application["new_execution_created"],
        "new_outcome_observation_created_in_source_package": application["new_outcome_observation_created"],
        "same_purpose_only": application["same_purpose_only"],
        "same_session_only": application["same_session_only"],
        "sandbox_only": application["sandbox_only"],
        "future_candidate_reordering_requires_separate_boundary": application[
            "future_candidate_reordering_requires_separate_boundary"
        ],
        "source_arbitration_rules_preserved": application["arbitration_rules_preserved"],
        "source_rollback_available": application["rollback_available"],
        "source_audit_recorded": application["audit_recorded"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    application_type = source.get("feedback_application_type")
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if application_type not in FEEDBACK_APPLICATION_TO_REORDERING_TARGET:
        errors.append("source_feedback_application_type_not_supported")
    expected = {
        "feedback_application_created": True,
        "feedback_applied": True,
        "feedback_application_scope": "same_session_sandbox_only",
        "feedback_application_effect_scope": "record_only_no_ordering_change",
        "feedback_loop_created_in_source_package": False,
        "candidate_reordering_created_in_source_package": False,
        "candidate_scores_changed_in_source_package": False,
        "next_cycle_candidate_ordering_changed_in_source_package": False,
        "new_action_created_in_source_package": False,
        "new_selected_action_created_in_source_package": False,
        "new_final_action_created_in_source_package": False,
        "new_direct_command_created_in_source_package": False,
        "new_execution_created_in_source_package": False,
        "new_outcome_observation_created_in_source_package": False,
        "same_purpose_only": True,
        "same_session_only": True,
        "sandbox_only": True,
        "future_candidate_reordering_requires_separate_boundary": True,
        "source_arbitration_rules_preserved": True,
        "source_rollback_available": True,
        "source_audit_recorded": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")


def _validate_boundary(boundary: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    application_type = source.get("feedback_application_type")
    target = FEEDBACK_APPLICATION_TO_REORDERING_TARGET.get(application_type)
    expected = {
        "future_candidate_reordering_allowed": True,
        "allowed_next_package": "Sandbox Candidate Ordering Arbitration Feedback-Gated Candidate Reordering Minimal v0",
        "candidate_source": "sandbox_candidate_ordering_arbitration_outcome_feedback_application",
        "feedback_application_type": application_type,
        "reordering_scope": "same_session_sandbox_only",
        "reordering_effect_scope": "future_advisory_candidate_ordering_only",
        "feedback_application_created_in_this_package": False,
        "feedback_loop_created_in_this_package": False,
        "candidate_reordering_applied_in_this_package": False,
        "candidate_ordering_changed_in_this_package": False,
        "candidate_scores_changed_in_this_package": False,
        "next_cycle_candidate_ordering_changed_in_this_package": False,
        "candidate_order_before": [],
        "candidate_order_after": [],
        "ordering_delta": 0.0,
        "new_action_created_in_this_package": False,
        "new_selected_action_created_in_this_package": False,
        "new_final_action_created_in_this_package": False,
        "new_direct_command_created_in_this_package": False,
        "new_execution_created_in_this_package": False,
        "new_outcome_observation_created_in_this_package": False,
        "future_selected_action_requires_separate_boundary": True,
        "future_final_action_requires_separate_boundary": True,
        "future_direct_command_requires_separate_boundary": True,
        "future_execution_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "arbitration_rules_preserved": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    if target:
        expected.update(
            {
                "candidate_for_future_reordering": target["candidate_for_future_reordering"],
                "future_reordering_label": target["future_reordering_label"],
                "boundary_reason": target["boundary_reason"],
            }
        )
    for field, value in expected.items():
        if boundary.get(field) != value:
            errors.append(f"feedback_gated_reordering_approval_boundary_{field}_not_expected")


def _validate_safety(safety: dict[str, Any], errors: list[str]) -> None:
    expected_true = [
        "same_session_scope_required",
        "sandbox_scope_required",
        "same_purpose_only",
        "record_only_feedback_application_required",
        "memory_write_requires_separate_boundary",
        "retention_write_requires_separate_boundary",
        "predictor_influence_requires_separate_boundary",
        "production_promotion_requires_separate_boundary",
        "rollback_available",
        "audit_recorded",
    ]
    for field in expected_true:
        if safety.get(field) is not True:
            errors.append(f"feedback_reordering_safety_boundary_{field}_not_true")
    for field in (
        "direct_endocrine_feed_allowed",
        "direct_tendency_feed_allowed",
        "proof_of_learning_claim_allowed",
    ):
        if safety.get(field) is not False:
            errors.append(f"feedback_reordering_safety_boundary_{field}_not_false")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_opened", "what_it_allows", "what_is_blocked", "plain_result"):
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked(blocked: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(flag for flag in BLOCKED_FLAGS if flag not in blocked)
    errors.extend(f"missing_blocked_flag:{flag}" for flag in missing)
    extra = sorted(flag for flag in blocked if flag not in BLOCKED_FLAGS)
    errors.extend(f"unexpected_blocked_flag:{flag}" for flag in extra)
    for flag in sorted(BLOCKED_FLAGS):
        if blocked.get(flag) is not False:
            errors.append(f"blocked_flags_{flag}_not_false")


def _invalid_records(reach: dict[str, Any], wait: dict[str, Any], probe: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["reordering_approval_boundary_id"] = f"{record['reordering_approval_boundary_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "sandbox_reordering_runtime")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "source_not_validated", ("source_feedback_application", "source_validated"), False)
    mutate(reach, "source_wrong_boundary_index", ("source_feedback_application", "source_boundary_index"), "2026-06-09-b151")
    mutate(reach, "source_application_not_created", ("source_feedback_application", "feedback_application_created"), False)
    mutate(reach, "source_feedback_not_applied", ("source_feedback_application", "feedback_applied"), False)
    mutate(reach, "source_wrong_scope", ("source_feedback_application", "feedback_application_scope"), "production")
    mutate(reach, "source_wrong_effect_scope", ("source_feedback_application", "feedback_application_effect_scope"), "ordering_change")
    mutate(reach, "source_bad_application_type", ("source_feedback_application", "feedback_application_type"), "unknown")
    mutate(reach, "source_feedback_loop_created", ("source_feedback_application", "feedback_loop_created_in_source_package"), True)
    mutate(reach, "source_reordering_created", ("source_feedback_application", "candidate_reordering_created_in_source_package"), True)
    mutate(reach, "source_scores_changed", ("source_feedback_application", "candidate_scores_changed_in_source_package"), True)
    mutate(reach, "source_next_cycle_changed", ("source_feedback_application", "next_cycle_candidate_ordering_changed_in_source_package"), True)
    mutate(reach, "source_future_reordering_missing", ("source_feedback_application", "future_candidate_reordering_requires_separate_boundary"), False)
    mutate(reach, "future_reordering_not_allowed", ("feedback_gated_reordering_approval_boundary", "future_candidate_reordering_allowed"), False)
    mutate(reach, "wrong_next_package", ("feedback_gated_reordering_approval_boundary", "allowed_next_package"), "Sandbox Candidate Ordering Arbitration Feedback-Gated Candidate Reordering Minimal v1")
    mutate(reach, "wrong_reordering_candidate", ("feedback_gated_reordering_approval_boundary", "candidate_for_future_reordering"), "wait_or_observe")
    mutate(reach, "wrong_reordering_scope", ("feedback_gated_reordering_approval_boundary", "reordering_scope"), "production")
    mutate(reach, "wrong_reordering_effect_scope", ("feedback_gated_reordering_approval_boundary", "reordering_effect_scope"), "actual_ordering_change")
    mutate(reach, "feedback_application_created_here", ("feedback_gated_reordering_approval_boundary", "feedback_application_created_in_this_package"), True)
    mutate(reach, "feedback_loop_created_here", ("feedback_gated_reordering_approval_boundary", "feedback_loop_created_in_this_package"), True)
    mutate(reach, "reordering_applied", ("feedback_gated_reordering_approval_boundary", "candidate_reordering_applied_in_this_package"), True)
    mutate(reach, "ordering_changed", ("feedback_gated_reordering_approval_boundary", "candidate_ordering_changed_in_this_package"), True)
    mutate(reach, "scores_changed", ("feedback_gated_reordering_approval_boundary", "candidate_scores_changed_in_this_package"), True)
    mutate(reach, "next_cycle_ordering_changed", ("feedback_gated_reordering_approval_boundary", "next_cycle_candidate_ordering_changed_in_this_package"), True)
    mutate(reach, "order_before_not_empty", ("feedback_gated_reordering_approval_boundary", "candidate_order_before"), ["wait_or_observe"])
    mutate(reach, "order_after_not_empty", ("feedback_gated_reordering_approval_boundary", "candidate_order_after"), ["reach_front_item"])
    mutate(reach, "ordering_delta", ("feedback_gated_reordering_approval_boundary", "ordering_delta"), 1.0)
    mutate(reach, "new_action_created", ("feedback_gated_reordering_approval_boundary", "new_action_created_in_this_package"), True)
    mutate(reach, "new_selected_action_created", ("feedback_gated_reordering_approval_boundary", "new_selected_action_created_in_this_package"), True)
    mutate(reach, "new_final_action_created", ("feedback_gated_reordering_approval_boundary", "new_final_action_created_in_this_package"), True)
    mutate(reach, "new_direct_command_created", ("feedback_gated_reordering_approval_boundary", "new_direct_command_created_in_this_package"), True)
    mutate(reach, "new_execution_created", ("feedback_gated_reordering_approval_boundary", "new_execution_created_in_this_package"), True)
    mutate(reach, "new_outcome_observation_created", ("feedback_gated_reordering_approval_boundary", "new_outcome_observation_created_in_this_package"), True)
    mutate(wait, "future_selected_action_boundary_missing", ("feedback_gated_reordering_approval_boundary", "future_selected_action_requires_separate_boundary"), False)
    mutate(wait, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(wait, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(wait, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(wait, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(wait, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(wait, "direct_endocrine_feed", ("blocked_flags", "direct_endocrine_feed"), True)
    mutate(wait, "direct_tendency_feed", ("blocked_flags", "direct_tendency_feed"), True)
    mutate(probe, "runtime_behavior_changed", ("blocked_flags", "runtime_behavior_changed"), True)
    mutate(probe, "production_behavior_changed", ("blocked_flags", "production_behavior_changed"), True)
    mutate(probe, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "reordering_approval_boundary_result_count": len(validation_results),
        "valid_reordering_approval_boundary_count": len(valid),
        "invalid_reordering_approval_boundary_count": len(validation_results) - len(valid),
        "future_candidate_reordering_allowed_count": sum(
            1 for result in valid if result["future_candidate_reordering_allowed"]
        ),
        "positive_item_reordering_boundary_count": sum(
            1
            for result in valid
            if result["candidate_for_future_reordering"] == "reach_front_item"
        ),
        "wait_context_reordering_boundary_count": sum(
            1
            for result in valid
            if result["candidate_for_future_reordering"] == "wait_or_observe"
        ),
        "mismatch_probe_reordering_boundary_count": sum(
            1
            for result in valid
            if result["candidate_for_future_reordering"] == "observe_or_alternative_probe"
        ),
        "candidate_reordering_blocked_count": sum(1 for result in valid if result["candidate_reordering_blocked"]),
        "feedback_loop_blocked_count": sum(1 for result in valid if result["feedback_loop_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "arbitration_rules_preserved_count": sum(1 for result in valid if result["arbitration_rules_preserved"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["reordering_approval_boundary_result_count"] == 49
        and summary["valid_reordering_approval_boundary_count"] == 3
        and summary["invalid_reordering_approval_boundary_count"] == 46
        and summary["future_candidate_reordering_allowed_count"] == 3
        and summary["positive_item_reordering_boundary_count"] == 1
        and summary["wait_context_reordering_boundary_count"] == 1
        and summary["mismatch_probe_reordering_boundary_count"] == 1
        and summary["candidate_reordering_blocked_count"] == 3
        and summary["feedback_loop_blocked_count"] == 3
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
