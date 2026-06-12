"""Bridge generic lesson dry-run corrections into existing trial trace previews."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .dry_run_correction_into_trial_trace import (
    build_corrected_trial_trace_preview,
    run_dry_run_correction_into_trial_trace_check,
    validate_corrected_trial_trace_preview,
)
from .generic_lesson_review_decision_minimal import build_generic_lesson_review_decision
from .generic_lesson_review_decision_preview_bridge_minimal import (
    build_generic_lesson_review_decision_preview_bridge,
)
from .generic_reviewed_lesson_dry_run_bridge_minimal import (
    build_generic_reviewed_lesson_dry_run_bridge,
    validate_generic_reviewed_lesson_dry_run_bridge,
)


COMMAND = "run-generic-lesson-dry-run-to-trial-trace-bridge-minimal-check"
FLOW = "generic_lesson_dry_run_to_trial_trace_bridge_minimal_v0"
TRIAL_TRACE_BRIDGE_ID = "generic_lesson_dry_run_to_trial_trace_bridge_demo_001"
BRIDGE_MODE = "existing_dry_run_correction_to_existing_trial_trace_bridge"
DECISION_TO_LEGACY_STATUS = {
    "accepted_for_reviewed_lesson_preview": "approved_for_preview",
    "rejected": "rejected",
    "needs_more_evidence": "needs_revision",
}
BLOCKED_REASON_BY_DECISION = {
    "rejected": "rejected_decision_cannot_enter_trial_trace",
    "needs_more_evidence": "needs_more_evidence_cannot_enter_trial_trace",
}
REQUIRED_TOP_LEVEL = {
    "trial_trace_bridge_id",
    "bridge_mode",
    "source_dry_run_bridge",
    "trial_trace_bridge_result",
    "supporting_evidence",
    "human_summary",
    "blocked_flags",
}
REQUIRED_HUMAN_SUMMARY = {
    "what_was_bridged",
    "what_was_reused",
    "what_the_trial_trace_means",
    "what_is_blocked",
    "plain_result",
}
REQUIRED_BLOCKED_FLAGS = {
    "source_specific_trial_trace_channel_created",
    "new_trial_trace_implementation_created",
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


def build_generic_lesson_dry_run_to_trial_trace_bridge(
    dry_run_bridge_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if dry_run_bridge_result is None:
        dry_run_bridge_result = build_generic_reviewed_lesson_dry_run_bridge()

    dry_run_bridge_validation = validate_generic_reviewed_lesson_dry_run_bridge(dry_run_bridge_result)
    source_dry_run = dry_run_bridge_result.get("source_preview_bridge", {})
    dry_run_result = dry_run_bridge_result.get("dry_run_bridge_result", {})
    decision = source_dry_run.get("source_decision")
    accepted = decision == "accepted_for_reviewed_lesson_preview"
    dry_run_created = dry_run_result.get("dry_run_correction_created") is True

    trial_trace_module_called = False
    trial_trace_created = False
    trial_trace_summary = ""
    blocked_reason = BLOCKED_REASON_BY_DECISION.get(decision)
    if accepted and dry_run_bridge_validation["valid"] and dry_run_created:
        trial_trace_module_called = True
        trial_trace_check = run_dry_run_correction_into_trial_trace_check()
        trial_trace = trial_trace_check.get("source_trial_trace", {})
        dry_run_correction = trial_trace_check.get("source_dry_run_correction", {})
        trial_trace_preview = build_corrected_trial_trace_preview(trial_trace, dry_run_correction)
        trial_trace_validation = (
            validate_corrected_trial_trace_preview(trial_trace_preview)
            if isinstance(trial_trace_preview, dict)
            else {"valid": False}
        )
        trial_trace_created = trial_trace_validation["valid"] and trial_trace_preview is not None
        if trial_trace_created:
            trial_trace_summary = (
                "Existing dry-run correction was converted into an existing dry-run trial trace preview."
            )
        else:
            blocked_reason = "existing_trial_trace_preview_not_created"

    return {
        "trial_trace_bridge_id": _bridge_id(decision),
        "bridge_mode": BRIDGE_MODE,
        "source_dry_run_bridge": {
            "source_decision": decision,
            "legacy_status": source_dry_run.get("legacy_status"),
            "reviewed_lesson_trace_preview_created": (
                source_dry_run.get("reviewed_lesson_trace_preview_created") is True
            ),
            "dry_run_correction_created": dry_run_created,
            "dry_run_only": dry_run_result.get("dry_run_only") is True,
            "source_type": source_dry_run.get("source_type"),
            "source_trace_ref": source_dry_run.get("source_trace_ref"),
        },
        "trial_trace_bridge_result": {
            "existing_trial_trace_module_called": trial_trace_module_called,
            "trial_trace_preview_created": trial_trace_created,
            "trial_trace_only": trial_trace_created,
            "lesson_applied": False,
            "memory_write": False,
            "retention_write": False,
            "predictor_modified": False,
            "runtime_behavior_changed": False,
            "final_trial_trace_mutated": False,
            "trial_trace_summary": trial_trace_summary,
            **({"blocked_reason": blocked_reason} if blocked_reason else {}),
        },
        "supporting_evidence": _supporting_evidence(dry_run_bridge_result),
        "human_summary": _human_summary(),
        "blocked_flags": _blocked_flags(),
    }


def validate_generic_lesson_dry_run_to_trial_trace_bridge(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _check_top_level(record, errors)
    if record.get("bridge_mode") != BRIDGE_MODE:
        errors.append("bridge_mode_not_existing_dry_run_correction_to_existing_trial_trace_bridge")

    source = _section(record, "source_dry_run_bridge", errors)
    decision = source.get("source_decision")
    if decision not in DECISION_TO_LEGACY_STATUS:
        errors.append("unknown_source_decision")
    expected_status = DECISION_TO_LEGACY_STATUS.get(decision)
    if source.get("legacy_status") != expected_status:
        errors.append("legacy_status_mapping_mismatch")
    _require_non_empty(source, "source_type", errors)
    _require_non_empty(source, "source_trace_ref", errors)

    trial_trace = _section(record, "trial_trace_bridge_result", errors)
    _validate_trial_trace_result(decision, source, trial_trace, errors)

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
        "trial_trace_bridge_id": record.get("trial_trace_bridge_id"),
        "valid": not errors,
        "error_codes": errors,
        "source_decision": decision,
        "legacy_status": source.get("legacy_status"),
        "accepted_trial_trace_bridge": decision == "accepted_for_reviewed_lesson_preview",
        "rejected_trial_trace_bridge": decision == "rejected",
        "needs_more_evidence_trial_trace_bridge": decision == "needs_more_evidence",
        "trial_trace_preview_created": trial_trace.get("trial_trace_preview_created") is True,
        "trial_trace_blocked": trial_trace.get("trial_trace_preview_created") is False,
        "existing_trial_trace_module_reused": trial_trace.get("existing_trial_trace_module_called") is True,
    }


def run_generic_lesson_dry_run_to_trial_trace_bridge_minimal_check() -> dict[str, Any]:
    valid_records = [
        build_generic_lesson_dry_run_to_trial_trace_bridge(
            _build_source_dry_run_bridge("accepted_for_reviewed_lesson_preview")
        ),
        build_generic_lesson_dry_run_to_trial_trace_bridge(_build_source_dry_run_bridge("rejected")),
        build_generic_lesson_dry_run_to_trial_trace_bridge(_build_source_dry_run_bridge("needs_more_evidence")),
    ]
    records = valid_records + _build_invalid_records(valid_records)
    validation_results = [validate_generic_lesson_dry_run_to_trial_trace_bridge(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_generic_lesson_dry_run_to_trial_trace_bridge_minimal_checks_passed"] else "failed",
        "trial_trace_bridge_results": records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "schema_bridge_only": True,
            "existing_trial_trace_module_reused": True,
            "source_specific_trial_trace_channel_created": False,
            "new_trial_trace_implementation_created": False,
            "lesson_application_added": False,
            "memory_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "runtime_behavior_change_added": False,
            "final_trial_trace_mutation_added": False,
            "proof_of_learning_claimed": False,
        },
        "notes": [
            "Generic dry-run bridge remains the input.",
            "Existing dry_run_correction_into_trial_trace remains the trial trace path.",
            "Dry-run trial trace preview is not lesson application or runtime behavior change.",
        ],
    }


def _build_source_dry_run_bridge(decision: str) -> dict[str, Any]:
    return build_generic_reviewed_lesson_dry_run_bridge(
        build_generic_lesson_review_decision_preview_bridge(
            build_generic_lesson_review_decision(decision=decision)
        )
    )


def _validate_trial_trace_result(
    decision: Any,
    source: dict[str, Any],
    trial_trace: dict[str, Any],
    errors: list[str],
) -> None:
    if decision == "accepted_for_reviewed_lesson_preview":
        _require_true(source, "reviewed_lesson_trace_preview_created", errors)
        _require_true(source, "dry_run_correction_created", errors)
        _require_true(source, "dry_run_only", errors)
        _require_true(trial_trace, "existing_trial_trace_module_called", errors)
        _require_true(trial_trace, "trial_trace_preview_created", errors)
        _require_true(trial_trace, "trial_trace_only", errors)
        _require_non_empty(trial_trace, "trial_trace_summary", errors)
    elif decision == "rejected":
        _require_false(source, "reviewed_lesson_trace_preview_created", errors)
        _require_false(source, "dry_run_correction_created", errors)
        _require_false(trial_trace, "existing_trial_trace_module_called", errors)
        _require_false(trial_trace, "trial_trace_preview_created", errors)
        if trial_trace.get("blocked_reason") != "rejected_decision_cannot_enter_trial_trace":
            errors.append("rejected_blocked_reason_mismatch")
    elif decision == "needs_more_evidence":
        _require_false(source, "reviewed_lesson_trace_preview_created", errors)
        _require_false(source, "dry_run_correction_created", errors)
        _require_false(trial_trace, "existing_trial_trace_module_called", errors)
        _require_false(trial_trace, "trial_trace_preview_created", errors)
        if trial_trace.get("blocked_reason") != "needs_more_evidence_cannot_enter_trial_trace":
            errors.append("needs_more_evidence_blocked_reason_mismatch")

    for field in (
        "lesson_applied",
        "memory_write",
        "retention_write",
        "predictor_modified",
        "runtime_behavior_changed",
        "final_trial_trace_mutated",
    ):
        _require_false(trial_trace, field, errors)


def _supporting_evidence(dry_run_bridge_result: dict[str, Any]) -> dict[str, bool]:
    evidence = dry_run_bridge_result.get("supporting_evidence", {})
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
            "The generic dry-run correction bridge was connected to the existing dry-run correction into "
            "trial trace path."
        ),
        "what_was_reused": "The existing dry_run_correction_into_trial_trace module was reused.",
        "what_the_trial_trace_means": "The dry-run correction can be represented as a trial trace preview only.",
        "what_is_blocked": (
            "Lesson application, memory writes, retention writes, predictor mutation, runtime behavior change, "
            "final trial trace mutation, and proof claims remain blocked."
        ),
        "plain_result": (
            "The generic lesson pipeline now reaches the existing dry-run trial trace preview layer without "
            "creating a new trial trace channel."
        ),
    }


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _build_invalid_records(valid_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    accepted, rejected, needs_more = valid_records
    records = [
        _mutate(accepted, ["bridge_mode"], "bad_bridge_mode", "bad_bridge_mode"),
        _mutate(accepted, ["source_dry_run_bridge", "source_decision"], "unknown", "unknown_source_decision"),
        _mutate(accepted, ["source_dry_run_bridge", "legacy_status"], "rejected", "wrong_accepted_mapping"),
        _mutate(rejected, ["source_dry_run_bridge", "legacy_status"], "approved_for_preview", "wrong_rejected_mapping"),
        _mutate(
            needs_more,
            ["source_dry_run_bridge", "legacy_status"],
            "approved_for_preview",
            "wrong_needs_more_mapping",
        ),
        _mutate(
            accepted,
            ["source_dry_run_bridge", "dry_run_correction_created"],
            False,
            "accepted_dry_run_not_created",
        ),
        _mutate(
            accepted,
            ["trial_trace_bridge_result", "existing_trial_trace_module_called"],
            False,
            "accepted_trial_trace_module_not_called",
        ),
        _mutate(
            accepted,
            ["trial_trace_bridge_result", "trial_trace_preview_created"],
            False,
            "accepted_trial_trace_not_created",
        ),
        _mutate(accepted, ["trial_trace_bridge_result", "trial_trace_only"], False, "accepted_trial_trace_only_false"),
        _mutate(accepted, ["trial_trace_bridge_result", "lesson_applied"], True, "accepted_lesson_applied"),
        _mutate(accepted, ["trial_trace_bridge_result", "memory_write"], True, "accepted_memory_write"),
        _mutate(accepted, ["trial_trace_bridge_result", "retention_write"], True, "accepted_retention_write"),
        _mutate(accepted, ["trial_trace_bridge_result", "predictor_modified"], True, "accepted_predictor_modified"),
        _mutate(
            accepted,
            ["trial_trace_bridge_result", "runtime_behavior_changed"],
            True,
            "accepted_runtime_behavior_changed",
        ),
        _mutate(
            accepted,
            ["trial_trace_bridge_result", "final_trial_trace_mutated"],
            True,
            "accepted_final_trial_trace_mutated",
        ),
        _mutate(
            rejected,
            ["trial_trace_bridge_result", "trial_trace_preview_created"],
            True,
            "rejected_trial_trace_created",
        ),
        _mutate(
            needs_more,
            ["trial_trace_bridge_result", "trial_trace_preview_created"],
            True,
            "needs_more_trial_trace_created",
        ),
        _mutate(
            accepted,
            ["blocked_flags", "new_trial_trace_implementation_created"],
            True,
            "new_trial_trace_impl",
        ),
        _mutate(
            accepted,
            ["blocked_flags", "source_specific_trial_trace_channel_created"],
            True,
            "source_specific_channel",
        ),
        _mutate(
            accepted,
            ["supporting_evidence", "level0_flip_test_used_as_supporting_evidence"],
            False,
            "level0_missing",
        ),
        _mutate(accepted, ["supporting_evidence", "bidirectional_flip_passed"], False, "bidirectional_false"),
        _mutate(
            accepted,
            ["supporting_evidence", "one_way_caution_bias_rejected"],
            False,
            "caution_bias_false",
        ),
        _mutate(
            accepted,
            ["supporting_evidence", "level1_contrast_sample_set_used_as_candidate_source"],
            False,
            "level1_missing",
        ),
        _mutate(
            accepted,
            ["supporting_evidence", "success_failure_neutral_contrast_available"],
            False,
            "contrast_missing",
        ),
        _mutate(accepted, ["trial_trace_bridge_result", "trial_trace_summary"], "", "empty_trial_trace_summary"),
        _mutate(accepted, ["blocked_flags", "proof_of_learning_claim"], True, "proof_claim"),
    ]
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        records.append(_mutate(accepted, ["human_summary", field], "", f"empty_{field}"))
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        records.append(_mutate(accepted, ["blocked_flags", field], True, field))
    return records


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "trial_trace_bridge_result_count": len(validation_results),
        "valid_trial_trace_bridge_result_count": len(valid_results),
        "invalid_trial_trace_bridge_result_count": sum(1 for result in validation_results if not result["valid"]),
        "accepted_trial_trace_bridge_count": sum(1 for result in valid_results if result["accepted_trial_trace_bridge"]),
        "rejected_trial_trace_bridge_count": sum(1 for result in valid_results if result["rejected_trial_trace_bridge"]),
        "needs_more_evidence_trial_trace_bridge_count": sum(
            1 for result in valid_results if result["needs_more_evidence_trial_trace_bridge"]
        ),
        "trial_trace_preview_created_count": sum(1 for result in valid_results if result["trial_trace_preview_created"]),
        "trial_trace_blocked_count": sum(1 for result in valid_results if result["trial_trace_blocked"]),
        "existing_trial_trace_module_reused_count": sum(
            1 for result in valid_results if result["existing_trial_trace_module_reused"]
        ),
        "source_specific_trial_trace_channel_blocked_count": _count_error(
            validation_results, "source_specific_trial_trace_channel_created_enabled"
        ),
        "new_trial_trace_implementation_blocked_count": _count_error(
            validation_results, "new_trial_trace_implementation_created_enabled"
        ),
        "lesson_application_blocked_count": _count_error(validation_results, "lesson_applied_not_false")
        + _count_error(validation_results, "lesson_applied_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_not_false")
        + _count_error(validation_results, "memory_write_enabled"),
        "retention_write_blocked_count": _count_error(validation_results, "retention_write_not_false")
        + _count_error(validation_results, "retention_write_enabled"),
        "predictor_mutation_blocked_count": _count_error(validation_results, "predictor_modified_not_false")
        + _count_error(validation_results, "predictor_modified_enabled"),
        "runtime_behavior_change_blocked_count": _count_error(
            validation_results, "runtime_behavior_changed_not_false"
        )
        + _count_error(validation_results, "runtime_behavior_changed_enabled"),
        "final_trial_trace_mutation_blocked_count": _count_error(
            validation_results, "final_trial_trace_mutated_not_false"
        )
        + _count_error(validation_results, "final_trial_trace_mutated_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(
            validation_results, "proof_of_learning_claim_enabled"
        ),
    }
    summary["all_generic_lesson_dry_run_to_trial_trace_bridge_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["valid_trial_trace_bridge_result_count"] == 3
        and summary["accepted_trial_trace_bridge_count"] == 1
        and summary["rejected_trial_trace_bridge_count"] == 1
        and summary["needs_more_evidence_trial_trace_bridge_count"] == 1
        and summary["trial_trace_preview_created_count"] == 1
        and summary["trial_trace_blocked_count"] == 2
        and summary["existing_trial_trace_module_reused_count"] == 1
        and summary["source_specific_trial_trace_channel_blocked_count"] >= 1
        and summary["new_trial_trace_implementation_blocked_count"] >= 1
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
    mutated["trial_trace_bridge_id"] = f"{record.get('trial_trace_bridge_id')}:{suffix}"
    return mutated


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _bridge_id(decision: Any) -> str:
    suffix = str(decision or "unknown").replace(" ", "_")
    return f"{TRIAL_TRACE_BRIDGE_ID}:{suffix}"


if __name__ == "__main__":
    import json

    print(json.dumps(run_generic_lesson_dry_run_to_trial_trace_bridge_minimal_check(), ensure_ascii=False, indent=2))
