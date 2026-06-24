"""Create same-session sandbox feedback records from reordered-candidate outcomes."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary_minimal import (
    ALLOWED_FEEDBACK_TARGETS,
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary_record,
)


COMMAND = "run-sandbox-candidate-ordering-arbitration-reordered-candidate-outcome-feedback-minimal-check"
FLOW = "sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingArbitrationReorderedCandidateOutcomeFeedback-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b164"
BOUNDARY_INDEX_AFTER = "2026-06-09-b165"

FEEDBACK_SHAPES = {
    "arbitration_reordered_positive_item_contact_feedback": {
        "feedback_label": "arbitration_reordered_positive_item_contact_feedback_recorded",
        "feedback_valence": "bounded_positive",
        "success_signal": 1.0,
        "blocked_signal": 0.0,
        "uncertainty_signal": 0.0,
        "harm_signal": 0.0,
        "interpretation": "The reordered-candidate sandbox command reached the front item.",
    },
    "arbitration_reordered_wait_context_observation_feedback": {
        "feedback_label": "arbitration_reordered_wait_context_feedback_recorded",
        "feedback_valence": "bounded_context_observation",
        "success_signal": 0.2,
        "blocked_signal": 0.0,
        "uncertainty_signal": 0.4,
        "harm_signal": 0.0,
        "interpretation": "The reordered-candidate sandbox command waited or observed local context.",
    },
    "arbitration_reordered_mismatch_probe_context_feedback": {
        "feedback_label": "arbitration_reordered_mismatch_probe_context_feedback_recorded",
        "feedback_valence": "bounded_probe_resolution",
        "success_signal": 0.4,
        "blocked_signal": 0.0,
        "uncertainty_signal": 0.2,
        "harm_signal": 0.0,
        "interpretation": "The reordered-candidate sandbox command probed context for mismatch resolution.",
    },
}

BLOCKED_FLAGS = {
    "feedback_applied",
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
    "feedback_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_feedback_approval_boundary",
    "same_session_feedback",
    "human_summary",
    "blocked_flags",
}


def build_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_record(
    feedback_approval_boundary_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(feedback_approval_boundary_record)
        if feedback_approval_boundary_record is not None
        else build_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary_record()
    )
    source_validation = (
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary_record(
            source
        )
    )
    if not source_validation["valid"]:
        raise ValueError("feedback_approval_boundary_record must validate before feedback record")

    source_summary = _source_summary(source)
    scenario = source_summary["scenario_id"]
    feedback_type = source_summary["candidate_for_future_feedback"]
    shape = FEEDBACK_SHAPES[feedback_type]
    return {
        "feedback_record_id": (
            f"sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_{scenario}_demo_001"
        ),
        "record_type": "sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_feedback_approval_boundary": source_summary,
        "same_session_feedback": {
            "feedback_created": True,
            "feedback_evaluation_created": True,
            "feedback_scope": "same_session_sandbox_only",
            "feedback_source": (
                "sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary"
            ),
            "scenario_id": scenario,
            "approved_purpose": source_summary["approved_purpose"],
            "candidate_family": source_summary["candidate_family"],
            "selected_action": source_summary["selected_action"],
            "final_action": source_summary["final_action"],
            "direct_command": source_summary["direct_command"],
            "observed_outcome": source_summary["observed_outcome"],
            "outcome_label": source_summary["outcome_label"],
            "feedback_type": feedback_type,
            "feedback_label": shape["feedback_label"],
            "feedback_valence": shape["feedback_valence"],
            "signals": {
                "success": shape["success_signal"],
                "blocked": shape["blocked_signal"],
                "uncertainty": shape["uncertainty_signal"],
                "harm": shape["harm_signal"],
            },
            "feedback_applied": False,
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
            "feedback_count": 1,
            "feedback_budget": 1,
            "budget_remaining": 0,
            "future_feedback_application_requires_separate_boundary": True,
            "future_candidate_reordering_requires_separate_boundary": True,
            "future_memory_write_requires_separate_boundary": True,
            "future_retention_requires_separate_boundary": True,
            "future_predictor_influence_requires_separate_boundary": True,
            "future_production_promotion_requires_separate_boundary": True,
            "arbitration_rules_preserved": True,
            "rollback_available": True,
            "audit_recorded": True,
            "interpretation": shape["interpretation"],
        },
        "human_summary": {
            "what_was_created": f"Same-session sandbox feedback evaluation {feedback_type} was created.",
            "what_it_means": shape["interpretation"],
            "what_is_blocked": (
                "The feedback is not applied, does not reorder candidates, changes no score or next-cycle "
                "ordering, creates no action or execution, writes no persistence, touches no predictor, "
                "and makes no proof claim."
            ),
            "plain_result": (
                "The reordered observed outcome now has bounded feedback evidence, but it still cannot "
                "change the next choice."
            ),
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_feedback_approval_boundary"), errors, "source_feedback_approval_boundary")
    feedback = _as_dict(record.get("same_session_feedback"), errors, "same_session_feedback")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_feedback(feedback, source, errors)
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
        "feedback_type": feedback.get("feedback_type"),
        "feedback_created": feedback.get("feedback_created") is True,
        "feedback_evaluation_created": feedback.get("feedback_evaluation_created") is True,
        "sandbox_only_feedback": feedback.get("feedback_scope") == "same_session_sandbox_only"
        and feedback.get("sandbox_only") is True
        and feedback.get("same_session_only") is True,
        "feedback_budget_checked": feedback.get("feedback_count") == 1
        and feedback.get("feedback_budget") == 1
        and feedback.get("budget_remaining") == 0,
        "feedback_application_blocked": feedback.get("feedback_applied") is False
        and blocked.get("feedback_applied") is False
        and blocked.get("feedback_loop_created") is False,
        "candidate_reordering_blocked": feedback.get("candidate_reordering_created") is False
        and feedback.get("candidate_scores_changed") is False
        and feedback.get("next_cycle_candidate_ordering_changed") is False
        and blocked.get("candidate_reordering_created") is False
        and blocked.get("candidate_scores_changed") is False
        and blocked.get("next_cycle_candidate_ordering_changed") is False,
        "action_creation_blocked": feedback.get("new_action_created") is False
        and feedback.get("new_selected_action_created") is False
        and feedback.get("new_final_action_created") is False
        and feedback.get("new_direct_command_created") is False
        and feedback.get("new_execution_created") is False
        and feedback.get("new_outcome_observation_created") is False,
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
        "arbitration_rules_preserved": feedback.get("arbitration_rules_preserved") is True,
        "rollback_available": feedback.get("rollback_available") is True,
    }


def run_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_minimal_check() -> dict[
    str, Any
]:
    source_records = (
        run_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary_minimal_check()[
            "valid_records"
        ]
    )
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_record(source)
        for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_record(record)
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
                "Creates same-session sandbox feedback evaluation records from reordered-candidate "
                "outcome approval boundaries."
            ),
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": (
                "Reordered-candidate outcome feedback records can now be created for the same session."
            ),
            "what_changed": "B164 approval boundaries can become bounded sandbox-only feedback evidence.",
            "what_is_blocked": (
                "Feedback is not applied, does not reorder candidates, changes no score or next-cycle "
                "ordering, creates no action or execution, writes no memory, touches no predictor, "
                "and makes no proof claim."
            ),
            "plain_result": (
                "The second pass can now record feedback from observed outcomes, but that feedback "
                "cannot change behavior yet."
            ),
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    boundary = source["feedback_approval_boundary"]
    observation = source["source_outcome_observation"]
    return {
        "source_feedback_approval_boundary_id": source["feedback_approval_boundary_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": observation["scenario_id"],
        "approved_purpose": observation["approved_purpose"],
        "candidate_family": observation["candidate_family"],
        "selected_action": observation["selected_action"],
        "final_action": observation["final_action"],
        "direct_command": observation["direct_command"],
        "observed_outcome": observation["observed_outcome"],
        "outcome_label": observation["outcome_label"],
        "candidate_for_future_feedback": boundary["candidate_for_future_feedback"],
        "feedback_scope": boundary["feedback_scope"],
        "future_feedback_allowed": boundary["future_feedback_allowed"],
        "feedback_evaluation_created_in_source_package": boundary[
            "feedback_evaluation_created_in_this_package"
        ],
        "feedback_applied_in_source_package": boundary["feedback_applied_in_this_package"],
        "feedback_loop_created_in_source_package": boundary["feedback_loop_created_in_this_package"],
        "candidate_reordering_created_in_source_package": boundary[
            "candidate_reordering_created_in_this_package"
        ],
        "candidate_scores_changed_in_source_package": boundary["candidate_scores_changed_in_this_package"],
        "next_cycle_candidate_ordering_changed_in_source_package": boundary[
            "next_cycle_candidate_ordering_changed_in_this_package"
        ],
        "new_action_created_in_source_package": boundary["new_action_created_in_this_package"],
        "new_selected_action_created_in_source_package": boundary[
            "new_selected_action_created_in_this_package"
        ],
        "new_final_action_created_in_source_package": boundary["new_final_action_created_in_this_package"],
        "new_direct_command_created_in_source_package": boundary[
            "new_direct_command_created_in_this_package"
        ],
        "new_execution_created_in_source_package": boundary["new_execution_created_in_this_package"],
        "new_outcome_observation_created_in_source_package": boundary[
            "new_outcome_observation_created_in_this_package"
        ],
        "future_feedback_application_requires_separate_boundary": boundary[
            "future_feedback_application_requires_separate_boundary"
        ],
        "future_candidate_reordering_requires_separate_boundary": boundary[
            "future_candidate_reordering_requires_separate_boundary"
        ],
        "source_arbitration_rules_preserved": boundary["arbitration_rules_preserved"],
        "source_rollback_available": boundary["rollback_available"],
        "source_audit_recorded": boundary["audit_recorded"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    feedback_type = source.get("candidate_for_future_feedback")
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("outcome_label") not in ALLOWED_FEEDBACK_TARGETS:
        errors.append("source_outcome_label_not_feedback_eligible")
    if feedback_type not in FEEDBACK_SHAPES:
        errors.append("source_candidate_for_future_feedback_not_supported")
    if feedback_type != ALLOWED_FEEDBACK_TARGETS.get(source.get("outcome_label")):
        errors.append("source_candidate_for_future_feedback_not_expected")
    expected = {
        "feedback_scope": "same_session_sandbox_only",
        "future_feedback_allowed": True,
        "feedback_evaluation_created_in_source_package": False,
        "feedback_applied_in_source_package": False,
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
        "future_feedback_application_requires_separate_boundary": True,
        "future_candidate_reordering_requires_separate_boundary": True,
        "source_arbitration_rules_preserved": True,
        "source_rollback_available": True,
        "source_audit_recorded": True,
    }
    for field, value in expected.items():
        if source.get(field) != value:
            errors.append(f"source_{field}_not_expected")


def _validate_feedback(feedback: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    feedback_type = feedback.get("feedback_type")
    shape = FEEDBACK_SHAPES.get(feedback_type)
    expected = {
        "feedback_created": True,
        "feedback_evaluation_created": True,
        "feedback_scope": "same_session_sandbox_only",
        "feedback_source": (
            "sandbox_candidate_ordering_arbitration_reordered_candidate_outcome_feedback_approval_boundary"
        ),
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "candidate_family": source.get("candidate_family"),
        "selected_action": source.get("selected_action"),
        "final_action": source.get("final_action"),
        "direct_command": source.get("direct_command"),
        "observed_outcome": source.get("observed_outcome"),
        "outcome_label": source.get("outcome_label"),
        "feedback_type": source.get("candidate_for_future_feedback"),
        "feedback_applied": False,
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
        "feedback_count": 1,
        "feedback_budget": 1,
        "budget_remaining": 0,
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
    if shape:
        expected.update(
            {
                "feedback_label": shape["feedback_label"],
                "feedback_valence": shape["feedback_valence"],
                "interpretation": shape["interpretation"],
            }
        )
    for field, value in expected.items():
        if feedback.get(field) != value:
            errors.append(f"same_session_feedback_{field}_not_expected")

    signals = _as_dict(feedback.get("signals"), errors, "same_session_feedback_signals")
    if shape:
        expected_signals = {
            "success": shape["success_signal"],
            "blocked": shape["blocked_signal"],
            "uncertainty": shape["uncertainty_signal"],
            "harm": shape["harm_signal"],
        }
        for field, value in expected_signals.items():
            if signals.get(field) != value:
                errors.append(f"same_session_feedback_signals_{field}_not_expected")


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
        record["feedback_record_id"] = f"{record['feedback_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "sandbox_reordered_feedback_runtime")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(reach, "boundary_not_required", ("boundary_change_required",), False)
    mutate(reach, "source_not_validated", ("source_feedback_approval_boundary", "source_validated"), False)
    mutate(reach, "source_wrong_boundary_index", ("source_feedback_approval_boundary", "source_boundary_index"), "b164")
    mutate(reach, "source_future_feedback_not_allowed", ("source_feedback_approval_boundary", "future_feedback_allowed"), False)
    mutate(reach, "source_wrong_feedback_scope", ("source_feedback_approval_boundary", "feedback_scope"), "production")
    mutate(reach, "source_bad_outcome_label", ("source_feedback_approval_boundary", "outcome_label"), "unknown")
    mutate(
        reach,
        "source_bad_feedback_candidate",
        ("source_feedback_approval_boundary", "candidate_for_future_feedback"),
        "unknown",
    )
    mutate(
        reach,
        "source_feedback_evaluation_already_created",
        ("source_feedback_approval_boundary", "feedback_evaluation_created_in_source_package"),
        True,
    )
    mutate(reach, "source_feedback_applied", ("source_feedback_approval_boundary", "feedback_applied_in_source_package"), True)
    mutate(
        reach,
        "source_feedback_loop_created",
        ("source_feedback_approval_boundary", "feedback_loop_created_in_source_package"),
        True,
    )
    mutate(
        reach,
        "source_reordering_created",
        ("source_feedback_approval_boundary", "candidate_reordering_created_in_source_package"),
        True,
    )
    mutate(
        reach,
        "source_scores_changed",
        ("source_feedback_approval_boundary", "candidate_scores_changed_in_source_package"),
        True,
    )
    mutate(
        reach,
        "source_next_cycle_changed",
        ("source_feedback_approval_boundary", "next_cycle_candidate_ordering_changed_in_source_package"),
        True,
    )
    mutate(
        reach,
        "source_action_created",
        ("source_feedback_approval_boundary", "new_action_created_in_source_package"),
        True,
    )
    mutate(
        reach,
        "source_outcome_observation_created",
        ("source_feedback_approval_boundary", "new_outcome_observation_created_in_source_package"),
        True,
    )
    mutate(reach, "feedback_not_created", ("same_session_feedback", "feedback_created"), False)
    mutate(reach, "feedback_evaluation_missing", ("same_session_feedback", "feedback_evaluation_created"), False)
    mutate(reach, "wrong_feedback_scope", ("same_session_feedback", "feedback_scope"), "production")
    mutate(reach, "wrong_feedback_source", ("same_session_feedback", "feedback_source"), "older_line")
    mutate(reach, "wrong_feedback_type", ("same_session_feedback", "feedback_type"), "unknown")
    mutate(reach, "wrong_feedback_label", ("same_session_feedback", "feedback_label"), "unknown")
    mutate(reach, "wrong_success_signal", ("same_session_feedback", "signals", "success"), 0.0)
    mutate(reach, "wrong_uncertainty_signal", ("same_session_feedback", "signals", "uncertainty"), 1.0)
    mutate(reach, "feedback_applied", ("same_session_feedback", "feedback_applied"), True)
    mutate(reach, "feedback_loop_created", ("same_session_feedback", "feedback_loop_created"), True)
    mutate(reach, "candidate_reordering_created", ("same_session_feedback", "candidate_reordering_created"), True)
    mutate(reach, "candidate_scores_changed", ("same_session_feedback", "candidate_scores_changed"), True)
    mutate(reach, "next_cycle_ordering_changed", ("same_session_feedback", "next_cycle_candidate_ordering_changed"), True)
    mutate(reach, "new_action_created", ("same_session_feedback", "new_action_created"), True)
    mutate(reach, "new_selected_action_created", ("same_session_feedback", "new_selected_action_created"), True)
    mutate(reach, "new_final_action_created", ("same_session_feedback", "new_final_action_created"), True)
    mutate(reach, "new_direct_command_created", ("same_session_feedback", "new_direct_command_created"), True)
    mutate(reach, "new_execution_created", ("same_session_feedback", "new_execution_created"), True)
    mutate(reach, "new_outcome_observation_created", ("same_session_feedback", "new_outcome_observation_created"), True)
    mutate(reach, "not_same_purpose", ("same_session_feedback", "same_purpose_only"), False)
    mutate(reach, "not_same_session", ("same_session_feedback", "same_session_only"), False)
    mutate(reach, "not_sandbox", ("same_session_feedback", "sandbox_only"), False)
    mutate(reach, "feedback_count_two", ("same_session_feedback", "feedback_count"), 2)
    mutate(reach, "feedback_budget_two", ("same_session_feedback", "feedback_budget"), 2)
    mutate(reach, "budget_remaining_one", ("same_session_feedback", "budget_remaining"), 1)
    mutate(
        wait,
        "future_application_boundary_missing",
        ("same_session_feedback", "future_feedback_application_requires_separate_boundary"),
        False,
    )
    mutate(
        wait,
        "future_reordering_boundary_missing",
        ("same_session_feedback", "future_candidate_reordering_requires_separate_boundary"),
        False,
    )
    mutate(wait, "future_memory_missing", ("same_session_feedback", "future_memory_write_requires_separate_boundary"), False)
    mutate(wait, "future_retention_missing", ("same_session_feedback", "future_retention_requires_separate_boundary"), False)
    mutate(
        wait,
        "future_predictor_missing",
        ("same_session_feedback", "future_predictor_influence_requires_separate_boundary"),
        False,
    )
    mutate(
        wait,
        "future_production_missing",
        ("same_session_feedback", "future_production_promotion_requires_separate_boundary"),
        False,
    )
    mutate(wait, "rules_not_preserved", ("same_session_feedback", "arbitration_rules_preserved"), False)
    mutate(wait, "rollback_missing", ("same_session_feedback", "rollback_available"), False)
    mutate(wait, "audit_missing", ("same_session_feedback", "audit_recorded"), False)
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
        "feedback_result_count": len(validation_results),
        "valid_feedback_count": len(valid),
        "invalid_feedback_count": len(validation_results) - len(valid),
        "feedback_created_count": sum(1 for result in valid if result["feedback_created"]),
        "feedback_evaluation_created_count": sum(1 for result in valid if result["feedback_evaluation_created"]),
        "sandbox_only_feedback_count": sum(1 for result in valid if result["sandbox_only_feedback"]),
        "feedback_budget_checked_count": sum(1 for result in valid if result["feedback_budget_checked"]),
        "positive_item_feedback_count": sum(
            1
            for result in valid
            if result["feedback_type"] == "arbitration_reordered_positive_item_contact_feedback"
        ),
        "wait_context_feedback_count": sum(
            1
            for result in valid
            if result["feedback_type"] == "arbitration_reordered_wait_context_observation_feedback"
        ),
        "mismatch_probe_feedback_count": sum(
            1
            for result in valid
            if result["feedback_type"] == "arbitration_reordered_mismatch_probe_context_feedback"
        ),
        "feedback_application_blocked_count": sum(1 for result in valid if result["feedback_application_blocked"]),
        "candidate_reordering_blocked_count": sum(1 for result in valid if result["candidate_reordering_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "arbitration_rules_preserved_count": sum(1 for result in valid if result["arbitration_rules_preserved"]),
        "rollback_available_count": sum(1 for result in valid if result["rollback_available"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["feedback_result_count"] == 81
        and summary["valid_feedback_count"] == 3
        and summary["invalid_feedback_count"] == 78
        and summary["feedback_created_count"] == 3
        and summary["feedback_evaluation_created_count"] == 3
        and summary["sandbox_only_feedback_count"] == 3
        and summary["feedback_budget_checked_count"] == 3
        and summary["positive_item_feedback_count"] == 1
        and summary["wait_context_feedback_count"] == 1
        and summary["mismatch_probe_feedback_count"] == 1
        and summary["feedback_application_blocked_count"] == 3
        and summary["candidate_reordering_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["arbitration_rules_preserved_count"] == 3
        and summary["rollback_available_count"] == 3
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
