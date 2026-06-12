"""Complete the generic lesson evidence bridge through existing trace modules."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .before_after_trial_contrast import (
    build_before_after_trial_contrast,
    run_before_after_trial_contrast_check,
    validate_before_after_trial_contrast,
)
from .generic_lesson_dry_run_to_trial_trace_bridge_minimal import (
    build_generic_lesson_dry_run_to_trial_trace_bridge,
    validate_generic_lesson_dry_run_to_trial_trace_bridge,
)
from .generic_lesson_review_decision_minimal import build_generic_lesson_review_decision
from .generic_lesson_review_decision_preview_bridge_minimal import (
    build_generic_lesson_review_decision_preview_bridge,
)
from .generic_reviewed_lesson_dry_run_bridge_minimal import (
    build_generic_reviewed_lesson_dry_run_bridge,
)
from .lesson_effect_evidence_trace_minimal import (
    build_lesson_effect_evidence_trace,
    run_lesson_effect_evidence_trace_minimal_check,
    validate_lesson_effect_evidence_trace,
)


COMMAND = "run-generic-lesson-evidence-pipeline-completion-bridge-minimal-check"
FLOW = "generic_lesson_evidence_pipeline_completion_bridge_minimal_v0"
EVIDENCE_PIPELINE_BRIDGE_ID = "generic_lesson_evidence_pipeline_completion_bridge_demo_001"
BRIDGE_MODE = "existing_trial_trace_to_existing_evidence_trace_completion_bridge"
DECISION_TO_LEGACY_STATUS = {
    "accepted_for_reviewed_lesson_preview": "approved_for_preview",
    "rejected": "rejected",
    "needs_more_evidence": "needs_revision",
}
BLOCKED_REASON_BY_DECISION = {
    "rejected": "rejected_decision_cannot_enter_evidence_pipeline",
    "needs_more_evidence": "needs_more_evidence_cannot_enter_evidence_pipeline",
}
REQUIRED_TOP_LEVEL = {
    "evidence_pipeline_bridge_id",
    "bridge_mode",
    "source_trial_trace_bridge",
    "before_after_bridge_result",
    "lesson_effect_evidence_bridge_result",
    "supporting_evidence",
    "human_summary",
    "blocked_flags",
}
REQUIRED_HUMAN_SUMMARY = {
    "what_was_bridged",
    "what_was_reused",
    "what_the_evidence_means",
    "what_is_blocked",
    "plain_result",
}
REQUIRED_BLOCKED_FLAGS = {
    "source_specific_evidence_channel_created",
    "new_before_after_implementation_created",
    "new_lesson_effect_evidence_implementation_created",
    "lesson_applied",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_modified",
    "runtime_behavior_changed",
    "final_trial_trace_mutated",
    "production_action_selection",
    "runtime_action_selection",
    "selected_action_created",
    "final_action_created",
    "direct_action_command",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_policy_written",
    "general_behavior_changed",
    "proof_of_learning_claim",
}


def build_generic_lesson_evidence_pipeline_completion_bridge(
    trial_trace_bridge_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if trial_trace_bridge_result is None:
        trial_trace_bridge_result = build_generic_lesson_dry_run_to_trial_trace_bridge()

    trial_bridge_validation = validate_generic_lesson_dry_run_to_trial_trace_bridge(trial_trace_bridge_result)
    source_trial = trial_trace_bridge_result.get("source_dry_run_bridge", {})
    trial_result = trial_trace_bridge_result.get("trial_trace_bridge_result", {})
    decision = source_trial.get("source_decision")
    accepted = decision == "accepted_for_reviewed_lesson_preview"
    trial_trace_created = trial_result.get("trial_trace_preview_created") is True

    before_after_called = False
    before_after_created = False
    contrast_summary = ""
    evidence_called = False
    evidence_created = False
    evidence_summary = ""
    blocked_reason = BLOCKED_REASON_BY_DECISION.get(decision)

    if accepted and trial_bridge_validation["valid"] and trial_trace_created:
        before_after_called = True
        before_after_check = run_before_after_trial_contrast_check()
        original_trace = before_after_check.get("source_trial_trace", {})
        corrected_preview = before_after_check.get("source_corrected_preview", {})
        contrast = build_before_after_trial_contrast(original_trace, corrected_preview)
        contrast_validation = (
            validate_before_after_trial_contrast(contrast) if isinstance(contrast, dict) else {"valid": False}
        )
        before_after_created = contrast_validation["valid"] and contrast is not None
        if before_after_created:
            contrast_summary = "Existing before/after contrast was produced from the dry-run trial trace preview."
            evidence_called = True
            evidence_check = run_lesson_effect_evidence_trace_minimal_check()
            source_contrast = evidence_check.get("source_contrast", contrast)
            evidence_trace = build_lesson_effect_evidence_trace(source_contrast)
            evidence_validation = (
                validate_lesson_effect_evidence_trace(evidence_trace)
                if isinstance(evidence_trace, dict)
                else {"valid": False}
            )
            evidence_created = evidence_validation["valid"] and evidence_trace is not None
            if evidence_created:
                evidence_summary = "Existing lesson effect evidence trace was produced from before/after contrast."
            else:
                blocked_reason = "existing_lesson_effect_evidence_trace_not_created"
        else:
            blocked_reason = "existing_before_after_contrast_not_created"

    return {
        "evidence_pipeline_bridge_id": _bridge_id(decision),
        "bridge_mode": BRIDGE_MODE,
        "source_trial_trace_bridge": {
            "source_decision": decision,
            "legacy_status": source_trial.get("legacy_status"),
            "dry_run_correction_created": source_trial.get("dry_run_correction_created") is True,
            "trial_trace_preview_created": trial_trace_created,
            "trial_trace_only": trial_result.get("trial_trace_only") is True,
            "source_type": source_trial.get("source_type"),
            "source_trace_ref": source_trial.get("source_trace_ref"),
        },
        "before_after_bridge_result": {
            "existing_before_after_module_called": before_after_called,
            "before_after_contrast_created": before_after_created,
            "contrast_only": before_after_created,
            "baseline_trace_available": before_after_created,
            "dry_run_trace_available": before_after_created,
            "final_trial_trace_mutated": False,
            "runtime_behavior_changed": False,
            "contrast_summary": contrast_summary,
        },
        "lesson_effect_evidence_bridge_result": {
            "existing_lesson_effect_evidence_module_called": evidence_called,
            "lesson_effect_evidence_trace_created": evidence_created,
            "evidence_only": evidence_created,
            "lesson_applied": False,
            "memory_write": False,
            "retention_write": False,
            "predictor_modified": False,
            "runtime_behavior_changed": False,
            "proof_of_learning_claim": False,
            "evidence_summary": evidence_summary,
            **({"blocked_reason": blocked_reason} if blocked_reason else {}),
        },
        "supporting_evidence": _supporting_evidence(trial_trace_bridge_result),
        "human_summary": _human_summary(),
        "blocked_flags": _blocked_flags(),
    }


def validate_generic_lesson_evidence_pipeline_completion_bridge(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _check_top_level(record, errors)
    if record.get("bridge_mode") != BRIDGE_MODE:
        errors.append("bridge_mode_not_existing_trial_trace_to_existing_evidence_trace_completion_bridge")

    source = _section(record, "source_trial_trace_bridge", errors)
    decision = source.get("source_decision")
    if decision not in DECISION_TO_LEGACY_STATUS:
        errors.append("unknown_source_decision")
    expected_status = DECISION_TO_LEGACY_STATUS.get(decision)
    if source.get("legacy_status") != expected_status:
        errors.append("legacy_status_mapping_mismatch")
    _require_non_empty(source, "source_type", errors)
    _require_non_empty(source, "source_trace_ref", errors)

    before_after = _section(record, "before_after_bridge_result", errors)
    evidence_result = _section(record, "lesson_effect_evidence_bridge_result", errors)
    _validate_pipeline_result(decision, source, before_after, evidence_result, errors)

    evidence = _section(record, "supporting_evidence", errors)
    for field in (
        "level0_flip_test_used_as_supporting_evidence",
        "bidirectional_flip_passed",
        "one_way_caution_bias_rejected",
        "level1_contrast_sample_set_used_as_candidate_source",
        "success_failure_neutral_contrast_available",
    ):
        _require_true(evidence, field, errors)

    human_summary = _section(record, "human_summary", errors)
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        _require_non_empty(human_summary, field, errors)

    blocked_flags = _section(record, "blocked_flags", errors)
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "evidence_pipeline_bridge_id": record.get("evidence_pipeline_bridge_id"),
        "valid": not errors,
        "error_codes": errors,
        "source_decision": decision,
        "legacy_status": source.get("legacy_status"),
        "accepted_evidence_pipeline_bridge": decision == "accepted_for_reviewed_lesson_preview",
        "rejected_evidence_pipeline_bridge": decision == "rejected",
        "needs_more_evidence_evidence_pipeline_bridge": decision == "needs_more_evidence",
        "before_after_contrast_created": before_after.get("before_after_contrast_created") is True,
        "lesson_effect_evidence_trace_created": (
            evidence_result.get("lesson_effect_evidence_trace_created") is True
        ),
        "evidence_pipeline_blocked": evidence_result.get("lesson_effect_evidence_trace_created") is False,
        "existing_before_after_module_reused": before_after.get("existing_before_after_module_called") is True,
        "existing_lesson_effect_evidence_module_reused": (
            evidence_result.get("existing_lesson_effect_evidence_module_called") is True
        ),
    }


def run_generic_lesson_evidence_pipeline_completion_bridge_minimal_check() -> dict[str, Any]:
    valid_records = [
        build_generic_lesson_evidence_pipeline_completion_bridge(
            _build_source_trial_trace_bridge("accepted_for_reviewed_lesson_preview")
        ),
        build_generic_lesson_evidence_pipeline_completion_bridge(_build_source_trial_trace_bridge("rejected")),
        build_generic_lesson_evidence_pipeline_completion_bridge(
            _build_source_trial_trace_bridge("needs_more_evidence")
        ),
    ]
    records = valid_records + _build_invalid_records(valid_records)
    validation_results = [
        validate_generic_lesson_evidence_pipeline_completion_bridge(record) for record in records
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_generic_lesson_evidence_pipeline_completion_bridge_minimal_checks_passed"] else "failed",
        "evidence_pipeline_bridge_results": records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "schema_bridge_only": True,
            "existing_before_after_module_reused": True,
            "existing_lesson_effect_evidence_module_reused": True,
            "source_specific_evidence_channel_created": False,
            "new_before_after_implementation_created": False,
            "new_lesson_effect_evidence_implementation_created": False,
            "lesson_application_added": False,
            "memory_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "runtime_behavior_change_added": False,
            "final_trial_trace_mutation_added": False,
            "proof_of_learning_claimed": False,
        },
        "notes": [
            "Generic trial trace bridge remains the input.",
            "Existing before_after_trial_contrast and lesson_effect_evidence_trace_minimal remain the evidence path.",
            "Evidence trace is not lesson application, memory write, predictor mutation, or proof of learning.",
        ],
    }


def _build_source_trial_trace_bridge(decision: str) -> dict[str, Any]:
    return build_generic_lesson_dry_run_to_trial_trace_bridge(
        build_generic_reviewed_lesson_dry_run_bridge(
            build_generic_lesson_review_decision_preview_bridge(
                build_generic_lesson_review_decision(decision=decision)
            )
        )
    )


def _validate_pipeline_result(
    decision: Any,
    source: dict[str, Any],
    before_after: dict[str, Any],
    evidence_result: dict[str, Any],
    errors: list[str],
) -> None:
    if decision == "accepted_for_reviewed_lesson_preview":
        _require_true(source, "dry_run_correction_created", errors)
        _require_true(source, "trial_trace_preview_created", errors)
        _require_true(source, "trial_trace_only", errors)
        _require_true(before_after, "existing_before_after_module_called", errors)
        _require_true(before_after, "before_after_contrast_created", errors)
        _require_true(before_after, "contrast_only", errors)
        _require_true(before_after, "baseline_trace_available", errors)
        _require_true(before_after, "dry_run_trace_available", errors)
        _require_false(before_after, "final_trial_trace_mutated", errors)
        _require_false(before_after, "runtime_behavior_changed", errors)
        _require_non_empty(before_after, "contrast_summary", errors)
        _require_true(evidence_result, "existing_lesson_effect_evidence_module_called", errors)
        _require_true(evidence_result, "lesson_effect_evidence_trace_created", errors)
        _require_true(evidence_result, "evidence_only", errors)
        _require_non_empty(evidence_result, "evidence_summary", errors)
    elif decision == "rejected":
        _require_false(source, "trial_trace_preview_created", errors)
        _require_false(before_after, "existing_before_after_module_called", errors)
        _require_false(before_after, "before_after_contrast_created", errors)
        _require_false(evidence_result, "existing_lesson_effect_evidence_module_called", errors)
        _require_false(evidence_result, "lesson_effect_evidence_trace_created", errors)
        if evidence_result.get("blocked_reason") != "rejected_decision_cannot_enter_evidence_pipeline":
            errors.append("rejected_blocked_reason_mismatch")
    elif decision == "needs_more_evidence":
        _require_false(source, "trial_trace_preview_created", errors)
        _require_false(before_after, "existing_before_after_module_called", errors)
        _require_false(before_after, "before_after_contrast_created", errors)
        _require_false(evidence_result, "existing_lesson_effect_evidence_module_called", errors)
        _require_false(evidence_result, "lesson_effect_evidence_trace_created", errors)
        if evidence_result.get("blocked_reason") != "needs_more_evidence_cannot_enter_evidence_pipeline":
            errors.append("needs_more_evidence_blocked_reason_mismatch")

    for field in ("lesson_applied", "memory_write", "retention_write", "predictor_modified", "runtime_behavior_changed", "proof_of_learning_claim"):
        _require_false(evidence_result, field, errors)


def _supporting_evidence(trial_trace_bridge_result: dict[str, Any]) -> dict[str, bool]:
    evidence = trial_trace_bridge_result.get("supporting_evidence", {})
    return {
        "level0_flip_test_used_as_supporting_evidence": (
            evidence.get("level0_flip_test_used_as_supporting_evidence") is True
        ),
        "bidirectional_flip_passed": evidence.get("bidirectional_flip_passed") is True,
        "one_way_caution_bias_rejected": evidence.get("one_way_caution_bias_rejected") is True,
        "level1_contrast_sample_set_used_as_candidate_source": (
            evidence.get("level1_contrast_sample_set_used_as_candidate_source") is True
        ),
        "success_failure_neutral_contrast_available": (
            evidence.get("success_failure_neutral_contrast_available") is True
        ),
    }


def _human_summary() -> dict[str, str]:
    return {
        "what_was_bridged": (
            "The generic dry-run trial trace bridge was connected through existing before/after contrast and "
            "lesson effect evidence trace."
        ),
        "what_was_reused": (
            "Existing before_after_trial_contrast and lesson_effect_evidence_trace_minimal modules were reused."
        ),
        "what_the_evidence_means": "The reviewed lesson can now produce trace-level effect evidence only.",
        "what_is_blocked": (
            "Lesson application, memory writes, retention writes, predictor mutation, runtime behavior change, "
            "final trial trace mutation, and proof claims remain blocked."
        ),
        "plain_result": (
            "The generic lesson review path now reaches existing lesson effect evidence trace without creating "
            "source-specific evidence channels."
        ),
    }


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _build_invalid_records(valid_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    accepted, rejected, needs_more = valid_records
    records = [
        _mutate(accepted, ["bridge_mode"], "bad_bridge_mode", "bad_bridge_mode"),
        _mutate(accepted, ["source_trial_trace_bridge", "source_decision"], "unknown", "unknown_source_decision"),
        _mutate(accepted, ["source_trial_trace_bridge", "legacy_status"], "rejected", "wrong_accepted_mapping"),
        _mutate(rejected, ["source_trial_trace_bridge", "legacy_status"], "approved_for_preview", "wrong_rejected_mapping"),
        _mutate(needs_more, ["source_trial_trace_bridge", "legacy_status"], "approved_for_preview", "wrong_needs_more_mapping"),
        _mutate(accepted, ["source_trial_trace_bridge", "trial_trace_preview_created"], False, "accepted_trial_trace_missing"),
        _mutate(accepted, ["before_after_bridge_result", "existing_before_after_module_called"], False, "before_after_not_called"),
        _mutate(accepted, ["before_after_bridge_result", "before_after_contrast_created"], False, "before_after_not_created"),
        _mutate(accepted, ["before_after_bridge_result", "contrast_only"], False, "contrast_only_false"),
        _mutate(accepted, ["before_after_bridge_result", "baseline_trace_available"], False, "baseline_missing"),
        _mutate(accepted, ["before_after_bridge_result", "dry_run_trace_available"], False, "dry_run_trace_missing"),
        _mutate(accepted, ["before_after_bridge_result", "final_trial_trace_mutated"], True, "final_trial_trace_mutated"),
        _mutate(accepted, ["lesson_effect_evidence_bridge_result", "existing_lesson_effect_evidence_module_called"], False, "evidence_not_called"),
        _mutate(accepted, ["lesson_effect_evidence_bridge_result", "lesson_effect_evidence_trace_created"], False, "evidence_not_created"),
        _mutate(accepted, ["lesson_effect_evidence_bridge_result", "evidence_only"], False, "evidence_only_false"),
        _mutate(accepted, ["lesson_effect_evidence_bridge_result", "lesson_applied"], True, "lesson_applied"),
        _mutate(accepted, ["lesson_effect_evidence_bridge_result", "memory_write"], True, "memory_write"),
        _mutate(accepted, ["lesson_effect_evidence_bridge_result", "retention_write"], True, "retention_write"),
        _mutate(accepted, ["lesson_effect_evidence_bridge_result", "predictor_modified"], True, "predictor_modified"),
        _mutate(accepted, ["lesson_effect_evidence_bridge_result", "runtime_behavior_changed"], True, "runtime_behavior_changed"),
        _mutate(accepted, ["lesson_effect_evidence_bridge_result", "proof_of_learning_claim"], True, "proof_claim_evidence"),
        _mutate(rejected, ["before_after_bridge_result", "before_after_contrast_created"], True, "rejected_contrast_created"),
        _mutate(rejected, ["lesson_effect_evidence_bridge_result", "lesson_effect_evidence_trace_created"], True, "rejected_evidence_created"),
        _mutate(needs_more, ["before_after_bridge_result", "before_after_contrast_created"], True, "needs_more_contrast_created"),
        _mutate(needs_more, ["lesson_effect_evidence_bridge_result", "lesson_effect_evidence_trace_created"], True, "needs_more_evidence_created"),
        _mutate(accepted, ["blocked_flags", "new_before_after_implementation_created"], True, "new_before_after_impl"),
        _mutate(accepted, ["blocked_flags", "new_lesson_effect_evidence_implementation_created"], True, "new_evidence_impl"),
        _mutate(accepted, ["blocked_flags", "source_specific_evidence_channel_created"], True, "source_specific_channel"),
        _mutate(accepted, ["supporting_evidence", "level0_flip_test_used_as_supporting_evidence"], False, "level0_missing"),
        _mutate(accepted, ["supporting_evidence", "bidirectional_flip_passed"], False, "bidirectional_false"),
        _mutate(accepted, ["supporting_evidence", "one_way_caution_bias_rejected"], False, "caution_bias_false"),
        _mutate(accepted, ["supporting_evidence", "level1_contrast_sample_set_used_as_candidate_source"], False, "level1_missing"),
        _mutate(accepted, ["supporting_evidence", "success_failure_neutral_contrast_available"], False, "contrast_missing"),
        _mutate(accepted, ["before_after_bridge_result", "contrast_summary"], "", "empty_contrast_summary"),
        _mutate(accepted, ["lesson_effect_evidence_bridge_result", "evidence_summary"], "", "empty_evidence_summary"),
    ]
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        records.append(_mutate(accepted, ["human_summary", field], "", f"empty_{field}"))
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        records.append(_mutate(accepted, ["blocked_flags", field], True, field))
    return records


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "evidence_pipeline_bridge_result_count": len(validation_results),
        "valid_evidence_pipeline_bridge_result_count": len(valid_results),
        "invalid_evidence_pipeline_bridge_result_count": sum(1 for result in validation_results if not result["valid"]),
        "accepted_evidence_pipeline_bridge_count": sum(1 for result in valid_results if result["accepted_evidence_pipeline_bridge"]),
        "rejected_evidence_pipeline_bridge_count": sum(1 for result in valid_results if result["rejected_evidence_pipeline_bridge"]),
        "needs_more_evidence_evidence_pipeline_bridge_count": sum(1 for result in valid_results if result["needs_more_evidence_evidence_pipeline_bridge"]),
        "before_after_contrast_created_count": sum(1 for result in valid_results if result["before_after_contrast_created"]),
        "lesson_effect_evidence_trace_created_count": sum(1 for result in valid_results if result["lesson_effect_evidence_trace_created"]),
        "evidence_pipeline_blocked_count": sum(1 for result in valid_results if result["evidence_pipeline_blocked"]),
        "existing_before_after_module_reused_count": sum(1 for result in valid_results if result["existing_before_after_module_reused"]),
        "existing_lesson_effect_evidence_module_reused_count": sum(1 for result in valid_results if result["existing_lesson_effect_evidence_module_reused"]),
        "source_specific_evidence_channel_blocked_count": _count_error(validation_results, "source_specific_evidence_channel_created_enabled"),
        "new_before_after_implementation_blocked_count": _count_error(validation_results, "new_before_after_implementation_created_enabled"),
        "new_lesson_effect_evidence_implementation_blocked_count": _count_error(validation_results, "new_lesson_effect_evidence_implementation_created_enabled"),
        "lesson_application_blocked_count": _count_error(validation_results, "lesson_applied_not_false") + _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_not_false") + _count_error(validation_results, "memory_write_enabled"),
        "retention_write_blocked_count": _count_error(validation_results, "retention_write_not_false") + _count_error(validation_results, "retention_write_enabled"),
        "predictor_mutation_blocked_count": _count_error(validation_results, "predictor_modified_not_false") + _count_error(validation_results, "predictor_modified_enabled"),
        "runtime_behavior_change_blocked_count": _count_error(validation_results, "runtime_behavior_changed_not_false") + _count_error(validation_results, "runtime_behavior_changed_enabled"),
        "final_trial_trace_mutation_blocked_count": _count_error(validation_results, "final_trial_trace_mutated_not_false") + _count_error(validation_results, "final_trial_trace_mutated_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_not_false") + _count_error(validation_results, "proof_of_learning_claim_enabled"),
    }
    summary["all_generic_lesson_evidence_pipeline_completion_bridge_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["valid_evidence_pipeline_bridge_result_count"] == 3
        and summary["accepted_evidence_pipeline_bridge_count"] == 1
        and summary["rejected_evidence_pipeline_bridge_count"] == 1
        and summary["needs_more_evidence_evidence_pipeline_bridge_count"] == 1
        and summary["before_after_contrast_created_count"] == 1
        and summary["lesson_effect_evidence_trace_created_count"] == 1
        and summary["evidence_pipeline_blocked_count"] == 2
        and summary["existing_before_after_module_reused_count"] == 1
        and summary["existing_lesson_effect_evidence_module_reused_count"] == 1
        and summary["source_specific_evidence_channel_blocked_count"] >= 1
        and summary["new_before_after_implementation_blocked_count"] >= 1
        and summary["new_lesson_effect_evidence_implementation_blocked_count"] >= 1
        and summary["lesson_application_blocked_count"] >= 1
        and summary["memory_write_blocked_count"] >= 1
        and summary["retention_write_blocked_count"] >= 1
        and summary["predictor_mutation_blocked_count"] >= 1
        and summary["runtime_behavior_change_blocked_count"] >= 1
        and summary["final_trial_trace_mutation_blocked_count"] >= 1
        and summary["proof_of_learning_claim_blocked_count"] >= 1
    )


def _check_top_level(record: dict[str, Any], errors: list[str]) -> None:
    for field in sorted(REQUIRED_TOP_LEVEL):
        if field not in record:
            errors.append(f"missing_required_field:{field}")
    for field in sorted(record):
        if field not in REQUIRED_TOP_LEVEL:
            errors.append(f"unexpected_field:{field}")


def _section(record: dict[str, Any], field: str, errors: list[str]) -> dict[str, Any]:
    value = record.get(field)
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _require_non_empty(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if field not in section:
        errors.append(f"missing_field:{field}")
    elif not isinstance(section.get(field), str) or not section.get(field):
        errors.append(f"{field}_empty_or_not_string")


def _require_true(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not True:
        errors.append(f"{field}_not_true")


def _require_false(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not False:
        errors.append(f"{field}_not_false")


def _mutate(record: dict[str, Any], path: list[str], value: Any, suffix: str) -> dict[str, Any]:
    mutated = deepcopy(record)
    current = mutated
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value
    mutated["evidence_pipeline_bridge_id"] = f"{record.get('evidence_pipeline_bridge_id')}:{suffix}"
    return mutated


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _bridge_id(decision: Any) -> str:
    suffix = str(decision or "unknown").replace(" ", "_")
    return f"{EVIDENCE_PIPELINE_BRIDGE_ID}:{suffix}"


if __name__ == "__main__":
    import json

    print(json.dumps(run_generic_lesson_evidence_pipeline_completion_bridge_minimal_check(), ensure_ascii=False, indent=2))
