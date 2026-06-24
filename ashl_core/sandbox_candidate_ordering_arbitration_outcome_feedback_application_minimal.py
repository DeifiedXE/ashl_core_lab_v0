"""Apply arbitration outcome feedback as a same-session sandbox record only."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_minimal import (
    ALLOWED_FEEDBACK_APPLICATION_TARGETS,
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record,
)


COMMAND = "run-sandbox-candidate-ordering-arbitration-outcome-feedback-application-minimal-check"
FLOW = "sandbox_candidate_ordering_arbitration_outcome_feedback_application_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingArbitrationOutcomeFeedbackApplication-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b151"
BOUNDARY_INDEX_AFTER = "2026-06-09-b152"

APPLICATION_EFFECTS = {
    "arbitration_positive_item_contact_feedback_application": {
        "application_label": "arbitration_positive_item_contact_feedback_applied_record_only",
        "application_valence": "bounded_positive_application_record",
        "recorded_signal": "positive_item_contact_feedback_available_for_future_review",
        "interpretation": "The positive item contact feedback is applied to a sandbox record only.",
    },
    "arbitration_wait_context_observation_feedback_application": {
        "application_label": "arbitration_wait_context_feedback_applied_record_only",
        "application_valence": "bounded_context_application_record",
        "recorded_signal": "wait_context_feedback_available_for_future_review",
        "interpretation": "The wait/context observation feedback is applied to a sandbox record only.",
    },
    "arbitration_mismatch_probe_context_feedback_application": {
        "application_label": "arbitration_mismatch_probe_feedback_applied_record_only",
        "application_valence": "bounded_probe_application_record",
        "recorded_signal": "mismatch_probe_feedback_available_for_future_review",
        "interpretation": "The mismatch probe feedback is applied to a sandbox record only.",
    },
}

BLOCKED_FLAGS = {
    "feedback_loop_created",
    "candidate_reordering_created",
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
    "feedback_application_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_feedback_application_approval_boundary",
    "same_session_feedback_application",
    "human_summary",
    "blocked_flags",
}


def build_sandbox_candidate_ordering_arbitration_outcome_feedback_application_record(
    feedback_application_approval_boundary_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(feedback_application_approval_boundary_record)
        if feedback_application_approval_boundary_record is not None
        else build_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record()
    )
    source_validation = (
        validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_record(source)
    )
    if not source_validation["valid"]:
        raise ValueError("feedback_application_approval_boundary_record must validate before feedback application")

    source_summary = _source_summary(source)
    scenario = source_summary["scenario_id"]
    application_type = source_summary["candidate_for_future_feedback_application"]
    effect = APPLICATION_EFFECTS[application_type]
    return {
        "feedback_application_record_id": (
            f"sandbox_candidate_ordering_arbitration_outcome_feedback_application_{scenario}_demo_001"
        ),
        "record_type": "sandbox_candidate_ordering_arbitration_outcome_feedback_application_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_feedback_application_approval_boundary": source_summary,
        "same_session_feedback_application": {
            "feedback_application_created": True,
            "feedback_applied": True,
            "feedback_application_scope": "same_session_sandbox_only",
            "feedback_application_effect_scope": "record_only_no_ordering_change",
            "feedback_application_source": "sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary",
            "scenario_id": scenario,
            "approved_purpose": source_summary["approved_purpose"],
            "candidate_family": source_summary["candidate_family"],
            "direct_command": source_summary["direct_command"],
            "observed_outcome": source_summary["observed_outcome"],
            "outcome_label": source_summary["outcome_label"],
            "source_feedback_type": source_summary["feedback_type"],
            "feedback_application_type": application_type,
            "feedback_application_label": effect["application_label"],
            "feedback_application_valence": effect["application_valence"],
            "recorded_signal": effect["recorded_signal"],
            "feedback_loop_created": False,
            "candidate_reordering_created": False,
            "candidate_scores_changed": False,
            "next_cycle_candidate_ordering_changed": False,
            "new_action_created": False,
            "new_selected_action_created": False,
            "new_final_action_created": False,
            "new_direct_command_created": False,
            "new_execution_created": False,
            "new_outcome_observation_created": False,
            "same_purpose_only": True,
            "same_session_only": True,
            "sandbox_only": True,
            "application_count": 1,
            "application_budget": 1,
            "budget_remaining": 0,
            "future_candidate_reordering_requires_separate_boundary": True,
            "future_memory_write_requires_separate_boundary": True,
            "future_retention_requires_separate_boundary": True,
            "future_predictor_influence_requires_separate_boundary": True,
            "future_production_promotion_requires_separate_boundary": True,
            "arbitration_rules_preserved": True,
            "rollback_available": True,
            "audit_recorded": True,
            "interpretation": effect["interpretation"],
        },
        "human_summary": {
            "what_was_created": f"Same-session sandbox feedback application record {application_type} was created.",
            "what_it_means": effect["interpretation"],
            "what_is_blocked": "The application record does not create a feedback loop, reorder candidates, change scores, create action/execution/outcome observation, write persistence, touch predictors, or prove learning.",
            "plain_result": "The feedback is applied only as a bounded sandbox record; it still cannot change the next choice.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "sandbox_candidate_ordering_arbitration_outcome_feedback_application_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(
        record.get("source_feedback_application_approval_boundary"),
        errors,
        "source_feedback_application_approval_boundary",
    )
    application = _as_dict(record.get("same_session_feedback_application"), errors, "same_session_feedback_application")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_application(application, source, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "direct_command": source.get("direct_command"),
        "observed_outcome": source.get("observed_outcome"),
        "outcome_label": source.get("outcome_label"),
        "feedback_application_type": application.get("feedback_application_type"),
        "feedback_application_created": application.get("feedback_application_created") is True,
        "feedback_applied": application.get("feedback_applied") is True,
        "record_only_application": application.get("feedback_application_effect_scope") == "record_only_no_ordering_change",
        "feedback_loop_blocked": application.get("feedback_loop_created") is False
        and blocked.get("feedback_loop_created") is False,
        "candidate_reordering_blocked": application.get("candidate_reordering_created") is False
        and application.get("candidate_scores_changed") is False
        and application.get("next_cycle_candidate_ordering_changed") is False
        and blocked.get("candidate_reordering_created") is False
        and blocked.get("candidate_scores_changed") is False
        and blocked.get("next_cycle_candidate_ordering_changed") is False,
        "action_creation_blocked": application.get("new_action_created") is False
        and application.get("new_selected_action_created") is False
        and application.get("new_final_action_created") is False
        and application.get("new_direct_command_created") is False
        and application.get("new_execution_created") is False
        and application.get("new_outcome_observation_created") is False,
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
        "arbitration_rules_preserved": application.get("arbitration_rules_preserved") is True,
    }


def run_sandbox_candidate_ordering_arbitration_outcome_feedback_application_minimal_check() -> dict[str, Any]:
    source_records = run_sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_outcome_feedback_application_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_outcome_feedback_application_record(record)
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
            "boundary_reason": "Creates same-session sandbox feedback application records without changing ordering or behavior.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Arbitration sandbox feedback can now be applied as same-session sandbox records.",
            "what_changed": "Feedback application records are created for the three arbitration feedback types.",
            "what_is_blocked": "The application does not create loops, reordering, actions, execution, outcome observations, persistence, predictor influence, production behavior, or proof claims.",
            "plain_result": "The feedback is marked applied inside a bounded record, but it still cannot change candidate ordering.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    boundary = source["feedback_application_approval_boundary"]
    feedback = source["source_feedback_record"]
    return {
        "source_feedback_application_approval_boundary_id": source["feedback_application_approval_boundary_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": feedback["scenario_id"],
        "approved_purpose": feedback["approved_purpose"],
        "candidate_family": feedback["candidate_family"],
        "direct_command": feedback["direct_command"],
        "observed_outcome": feedback["observed_outcome"],
        "outcome_label": feedback["outcome_label"],
        "feedback_type": feedback["feedback_type"],
        "future_feedback_application_allowed": boundary["future_feedback_application_allowed"],
        "candidate_for_future_feedback_application": boundary["candidate_for_future_feedback_application"],
        "feedback_application_scope": boundary["feedback_application_scope"],
        "feedback_applied_in_source_package": boundary["feedback_applied_in_this_package"],
        "feedback_loop_created_in_source_package": boundary["feedback_loop_created_in_this_package"],
        "candidate_reordering_created_in_source_package": boundary["candidate_reordering_created_in_this_package"],
        "candidate_scores_changed_in_source_package": boundary["candidate_scores_changed_in_this_package"],
        "next_cycle_candidate_ordering_changed_in_source_package": boundary[
            "next_cycle_candidate_ordering_changed_in_this_package"
        ],
        "new_action_created_in_source_package": boundary["new_action_created_in_this_package"],
        "new_outcome_observation_created_in_source_package": boundary[
            "new_outcome_observation_created_in_this_package"
        ],
        "source_arbitration_rules_preserved": boundary["arbitration_rules_preserved"],
        "source_rollback_available": boundary["rollback_available"],
        "source_audit_recorded": boundary["audit_recorded"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    application_type = source.get("candidate_for_future_feedback_application")
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if application_type not in APPLICATION_EFFECTS:
        errors.append("source_candidate_for_future_feedback_application_not_supported")
    if application_type != ALLOWED_FEEDBACK_APPLICATION_TARGETS.get(source.get("feedback_type")):
        errors.append("source_candidate_for_future_feedback_application_not_expected")
    expected = {
        "future_feedback_application_allowed": True,
        "feedback_application_scope": "same_session_sandbox_only",
        "feedback_applied_in_source_package": False,
        "feedback_loop_created_in_source_package": False,
        "candidate_reordering_created_in_source_package": False,
        "candidate_scores_changed_in_source_package": False,
        "next_cycle_candidate_ordering_changed_in_source_package": False,
        "new_action_created_in_source_package": False,
        "new_outcome_observation_created_in_source_package": False,
        "source_arbitration_rules_preserved": True,
        "source_rollback_available": True,
        "source_audit_recorded": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")


def _validate_application(application: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    application_type = application.get("feedback_application_type")
    effect = APPLICATION_EFFECTS.get(application_type)
    expected = {
        "feedback_application_created": True,
        "feedback_applied": True,
        "feedback_application_scope": "same_session_sandbox_only",
        "feedback_application_effect_scope": "record_only_no_ordering_change",
        "feedback_application_source": "sandbox_candidate_ordering_arbitration_outcome_feedback_application_approval_boundary",
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "candidate_family": source.get("candidate_family"),
        "direct_command": source.get("direct_command"),
        "observed_outcome": source.get("observed_outcome"),
        "outcome_label": source.get("outcome_label"),
        "source_feedback_type": source.get("feedback_type"),
        "feedback_application_type": source.get("candidate_for_future_feedback_application"),
        "feedback_loop_created": False,
        "candidate_reordering_created": False,
        "candidate_scores_changed": False,
        "next_cycle_candidate_ordering_changed": False,
        "new_action_created": False,
        "new_selected_action_created": False,
        "new_final_action_created": False,
        "new_direct_command_created": False,
        "new_execution_created": False,
        "new_outcome_observation_created": False,
        "same_purpose_only": True,
        "same_session_only": True,
        "sandbox_only": True,
        "application_count": 1,
        "application_budget": 1,
        "budget_remaining": 0,
        "future_candidate_reordering_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "arbitration_rules_preserved": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    if effect:
        expected.update(
            {
                "feedback_application_label": effect["application_label"],
                "feedback_application_valence": effect["application_valence"],
                "recorded_signal": effect["recorded_signal"],
                "interpretation": effect["interpretation"],
            }
        )
    for field, value in expected.items():
        if application.get(field) != value:
            errors.append(f"same_session_feedback_application_{field}_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_created", "what_it_means", "what_is_blocked", "plain_result"):
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
        record["feedback_application_record_id"] = f"{record['feedback_application_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "sandbox_feedback_application_runtime")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "source_not_validated", ("source_feedback_application_approval_boundary", "source_validated"), False)
    mutate(reach, "source_wrong_boundary_index", ("source_feedback_application_approval_boundary", "source_boundary_index"), "2026-06-09-b150")
    mutate(reach, "source_future_application_not_allowed", ("source_feedback_application_approval_boundary", "future_feedback_application_allowed"), False)
    mutate(reach, "source_wrong_scope", ("source_feedback_application_approval_boundary", "feedback_application_scope"), "production")
    mutate(reach, "source_bad_application_type", ("source_feedback_application_approval_boundary", "candidate_for_future_feedback_application"), "unknown")
    mutate(reach, "source_feedback_already_applied", ("source_feedback_application_approval_boundary", "feedback_applied_in_source_package"), True)
    mutate(reach, "source_feedback_loop_created", ("source_feedback_application_approval_boundary", "feedback_loop_created_in_source_package"), True)
    mutate(reach, "source_reordering_created", ("source_feedback_application_approval_boundary", "candidate_reordering_created_in_source_package"), True)
    mutate(reach, "source_scores_changed", ("source_feedback_application_approval_boundary", "candidate_scores_changed_in_source_package"), True)
    mutate(reach, "source_next_cycle_changed", ("source_feedback_application_approval_boundary", "next_cycle_candidate_ordering_changed_in_source_package"), True)
    mutate(reach, "application_not_created", ("same_session_feedback_application", "feedback_application_created"), False)
    mutate(reach, "feedback_not_applied", ("same_session_feedback_application", "feedback_applied"), False)
    mutate(reach, "wrong_application_scope", ("same_session_feedback_application", "feedback_application_scope"), "production")
    mutate(reach, "wrong_effect_scope", ("same_session_feedback_application", "feedback_application_effect_scope"), "ordering_change")
    mutate(reach, "wrong_application_type", ("same_session_feedback_application", "feedback_application_type"), "unknown")
    mutate(reach, "feedback_loop_created", ("same_session_feedback_application", "feedback_loop_created"), True)
    mutate(reach, "candidate_reordering_created", ("same_session_feedback_application", "candidate_reordering_created"), True)
    mutate(reach, "candidate_scores_changed", ("same_session_feedback_application", "candidate_scores_changed"), True)
    mutate(reach, "next_cycle_ordering_changed", ("same_session_feedback_application", "next_cycle_candidate_ordering_changed"), True)
    mutate(reach, "new_action_created", ("same_session_feedback_application", "new_action_created"), True)
    mutate(reach, "new_selected_action_created", ("same_session_feedback_application", "new_selected_action_created"), True)
    mutate(reach, "new_final_action_created", ("same_session_feedback_application", "new_final_action_created"), True)
    mutate(reach, "new_direct_command_created", ("same_session_feedback_application", "new_direct_command_created"), True)
    mutate(reach, "new_execution_created", ("same_session_feedback_application", "new_execution_created"), True)
    mutate(reach, "new_outcome_observation_created", ("same_session_feedback_application", "new_outcome_observation_created"), True)
    mutate(wait, "future_reordering_boundary_missing", ("same_session_feedback_application", "future_candidate_reordering_requires_separate_boundary"), False)
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
        "feedback_application_result_count": len(validation_results),
        "valid_feedback_application_count": len(valid),
        "invalid_feedback_application_count": len(validation_results) - len(valid),
        "feedback_application_created_count": sum(1 for result in valid if result["feedback_application_created"]),
        "feedback_applied_count": sum(1 for result in valid if result["feedback_applied"]),
        "record_only_application_count": sum(1 for result in valid if result["record_only_application"]),
        "positive_item_feedback_application_count": sum(
            1
            for result in valid
            if result["feedback_application_type"] == "arbitration_positive_item_contact_feedback_application"
        ),
        "wait_context_feedback_application_count": sum(
            1
            for result in valid
            if result["feedback_application_type"] == "arbitration_wait_context_observation_feedback_application"
        ),
        "mismatch_probe_feedback_application_count": sum(
            1
            for result in valid
            if result["feedback_application_type"] == "arbitration_mismatch_probe_context_feedback_application"
        ),
        "feedback_loop_blocked_count": sum(1 for result in valid if result["feedback_loop_blocked"]),
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
        summary["feedback_application_result_count"] == 42
        and summary["valid_feedback_application_count"] == 3
        and summary["invalid_feedback_application_count"] == 39
        and summary["feedback_application_created_count"] == 3
        and summary["feedback_applied_count"] == 3
        and summary["record_only_application_count"] == 3
        and summary["positive_item_feedback_application_count"] == 1
        and summary["wait_context_feedback_application_count"] == 1
        and summary["mismatch_probe_feedback_application_count"] == 1
        and summary["feedback_loop_blocked_count"] == 3
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
