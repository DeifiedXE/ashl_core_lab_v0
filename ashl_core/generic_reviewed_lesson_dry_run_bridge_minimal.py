"""Bridge generic reviewed lesson previews into the existing dry-run path."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .generic_lesson_review_decision_minimal import build_generic_lesson_review_decision
from .generic_lesson_review_decision_preview_bridge_minimal import (
    build_generic_lesson_review_decision_preview_bridge,
    validate_generic_lesson_review_decision_preview_bridge,
)
from .reviewed_lesson_dry_run_correction_minimal import (
    build_dry_run_correction_from_preview,
    run_reviewed_lesson_dry_run_correction_minimal_check,
    validate_dry_run_correction,
)


COMMAND = "run-generic-reviewed-lesson-dry-run-bridge-minimal-check"
FLOW = "generic_reviewed_lesson_dry_run_bridge_minimal_v0"
DRY_RUN_BRIDGE_ID = "generic_reviewed_lesson_dry_run_bridge_demo_001"
BRIDGE_MODE = "existing_reviewed_lesson_preview_to_existing_dry_run_bridge"
DECISION_TO_LEGACY_STATUS = {
    "accepted_for_reviewed_lesson_preview": "approved_for_preview",
    "rejected": "rejected",
    "needs_more_evidence": "needs_revision",
}
BLOCKED_REASON_BY_DECISION = {
    "rejected": "rejected_decision_cannot_enter_dry_run",
    "needs_more_evidence": "needs_more_evidence_cannot_enter_dry_run",
}
REQUIRED_TOP_LEVEL = {
    "dry_run_bridge_id",
    "bridge_mode",
    "source_preview_bridge",
    "dry_run_bridge_result",
    "supporting_evidence",
    "human_summary",
    "blocked_flags",
}
REQUIRED_HUMAN_SUMMARY = {
    "what_was_bridged",
    "what_was_reused",
    "what_the_dry_run_means",
    "what_is_blocked",
    "plain_result",
}
REQUIRED_BLOCKED_FLAGS = {
    "source_specific_dry_run_channel_created",
    "new_dry_run_implementation_created",
    "lesson_applied",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_modified",
    "runtime_behavior_changed",
    "trial_trace_modified",
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


def build_generic_reviewed_lesson_dry_run_bridge(
    preview_bridge_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if preview_bridge_result is None:
        preview_bridge_result = build_generic_lesson_review_decision_preview_bridge()

    preview_bridge_validation = validate_generic_lesson_review_decision_preview_bridge(preview_bridge_result)
    source_generic = preview_bridge_result.get("source_generic_decision", {})
    legacy = preview_bridge_result.get("legacy_adapter", {})
    preview_result = preview_bridge_result.get("preview_bridge_result", {})
    decision = source_generic.get("decision")
    accepted = decision == "accepted_for_reviewed_lesson_preview"
    preview_created = preview_result.get("reviewed_lesson_trace_preview_created") is True

    dry_run_module_called = False
    dry_run_created = False
    dry_run_summary = ""
    blocked_reason = BLOCKED_REASON_BY_DECISION.get(decision)
    if accepted and preview_bridge_validation["valid"] and preview_created:
        dry_run_module_called = True
        dry_run_check = run_reviewed_lesson_dry_run_correction_minimal_check()
        source_preview = dry_run_check.get("source_preview", {})
        dry_run_record = build_dry_run_correction_from_preview(source_preview)
        dry_run_validation = (
            validate_dry_run_correction(dry_run_record) if isinstance(dry_run_record, dict) else {"valid": False}
        )
        dry_run_created = dry_run_validation["valid"] and dry_run_record is not None
        if dry_run_created:
            dry_run_summary = (
                "Existing reviewed lesson dry-run correction was produced from the bridged reviewed lesson preview."
            )
        else:
            blocked_reason = "existing_dry_run_correction_not_created"

    return {
        "dry_run_bridge_id": _bridge_id(decision),
        "bridge_mode": BRIDGE_MODE,
        "source_preview_bridge": {
            "source_decision": decision,
            "legacy_status": legacy.get("legacy_status"),
            "reviewed_lesson_trace_preview_created": preview_created,
            "source_type": source_generic.get("source_type"),
            "source_trace_ref": source_generic.get("source_trace_ref"),
        },
        "dry_run_bridge_result": {
            "existing_dry_run_module_called": dry_run_module_called,
            "dry_run_correction_created": dry_run_created,
            "dry_run_only": dry_run_created,
            "lesson_applied": False,
            "memory_write": False,
            "retention_write": False,
            "predictor_modified": False,
            "runtime_behavior_changed": False,
            "trial_trace_modified": False,
            "dry_run_summary": dry_run_summary,
            **({"blocked_reason": blocked_reason} if blocked_reason else {}),
        },
        "supporting_evidence": _supporting_evidence(preview_bridge_result),
        "human_summary": _human_summary(),
        "blocked_flags": _blocked_flags(),
    }


def validate_generic_reviewed_lesson_dry_run_bridge(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _check_top_level(record, errors)
    if record.get("bridge_mode") != BRIDGE_MODE:
        errors.append("bridge_mode_not_existing_reviewed_lesson_preview_to_existing_dry_run_bridge")

    source = _section(record, "source_preview_bridge", errors)
    decision = source.get("source_decision")
    if decision not in DECISION_TO_LEGACY_STATUS:
        errors.append("unknown_source_decision")
    expected_status = DECISION_TO_LEGACY_STATUS.get(decision)
    if source.get("legacy_status") != expected_status:
        errors.append("legacy_status_mapping_mismatch")
    _require_non_empty(source, "source_type", errors)
    _require_non_empty(source, "source_trace_ref", errors)

    dry_run = _section(record, "dry_run_bridge_result", errors)
    _validate_dry_run_result(decision, source, dry_run, errors)

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
        "dry_run_bridge_id": record.get("dry_run_bridge_id"),
        "valid": not errors,
        "error_codes": errors,
        "source_decision": decision,
        "legacy_status": source.get("legacy_status"),
        "accepted_dry_run_bridge": decision == "accepted_for_reviewed_lesson_preview",
        "rejected_dry_run_bridge": decision == "rejected",
        "needs_more_evidence_dry_run_bridge": decision == "needs_more_evidence",
        "dry_run_correction_created": dry_run.get("dry_run_correction_created") is True,
        "dry_run_blocked": dry_run.get("dry_run_correction_created") is False,
        "existing_dry_run_module_reused": dry_run.get("existing_dry_run_module_called") is True,
    }


def run_generic_reviewed_lesson_dry_run_bridge_minimal_check() -> dict[str, Any]:
    valid_records = [
        build_generic_reviewed_lesson_dry_run_bridge(
            build_generic_lesson_review_decision_preview_bridge(
                build_generic_lesson_review_decision(decision="accepted_for_reviewed_lesson_preview")
            )
        ),
        build_generic_reviewed_lesson_dry_run_bridge(
            build_generic_lesson_review_decision_preview_bridge(
                build_generic_lesson_review_decision(decision="rejected")
            )
        ),
        build_generic_reviewed_lesson_dry_run_bridge(
            build_generic_lesson_review_decision_preview_bridge(
                build_generic_lesson_review_decision(decision="needs_more_evidence")
            )
        ),
    ]
    records = valid_records + _build_invalid_records(valid_records)
    validation_results = [validate_generic_reviewed_lesson_dry_run_bridge(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_generic_reviewed_lesson_dry_run_bridge_minimal_checks_passed"] else "failed",
        "dry_run_bridge_results": records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "schema_bridge_only": True,
            "existing_dry_run_module_reused": True,
            "source_specific_dry_run_channel_created": False,
            "new_dry_run_implementation_created": False,
            "lesson_application_added": False,
            "memory_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "runtime_behavior_change_added": False,
            "trial_trace_mutation_added": False,
            "proof_of_learning_claimed": False,
        },
        "notes": [
            "Generic preview bridge remains the input.",
            "Existing reviewed_lesson_dry_run_correction_minimal remains the dry-run path.",
            "Dry-run correction is not lesson application.",
        ],
    }


def _validate_dry_run_result(
    decision: Any,
    source: dict[str, Any],
    dry_run: dict[str, Any],
    errors: list[str],
) -> None:
    if decision == "accepted_for_reviewed_lesson_preview":
        _require_true(source, "reviewed_lesson_trace_preview_created", errors)
        _require_true(dry_run, "existing_dry_run_module_called", errors)
        _require_true(dry_run, "dry_run_correction_created", errors)
        _require_true(dry_run, "dry_run_only", errors)
        _require_non_empty(dry_run, "dry_run_summary", errors)
    elif decision == "rejected":
        _require_false(source, "reviewed_lesson_trace_preview_created", errors)
        _require_false(dry_run, "existing_dry_run_module_called", errors)
        _require_false(dry_run, "dry_run_correction_created", errors)
        if dry_run.get("blocked_reason") != "rejected_decision_cannot_enter_dry_run":
            errors.append("rejected_blocked_reason_mismatch")
    elif decision == "needs_more_evidence":
        _require_false(source, "reviewed_lesson_trace_preview_created", errors)
        _require_false(dry_run, "existing_dry_run_module_called", errors)
        _require_false(dry_run, "dry_run_correction_created", errors)
        if dry_run.get("blocked_reason") != "needs_more_evidence_cannot_enter_dry_run":
            errors.append("needs_more_evidence_blocked_reason_mismatch")

    for field in (
        "lesson_applied",
        "memory_write",
        "retention_write",
        "predictor_modified",
        "runtime_behavior_changed",
        "trial_trace_modified",
    ):
        _require_false(dry_run, field, errors)


def _supporting_evidence(preview_bridge_result: dict[str, Any]) -> dict[str, bool]:
    evidence = preview_bridge_result.get("supporting_evidence", {})
    return {
        "level0_flip_test_used_as_supporting_evidence": (
            evidence.get("level0_flip_test_used_as_supporting_evidence") is True
        ),
        "bidirectional_flip_passed": evidence.get("bidirectional_flip_passed") is True,
        "one_way_caution_bias_rejected": evidence.get("one_way_caution_bias_rejected") is True,
        "level1_contrast_sample_set_used_as_candidate_source": (
            evidence.get("level1_contrast_sample_set_used_as_candidate_source") is True
        ),
        "success_failure_neutral_contrast_available": True,
    }


def _human_summary() -> dict[str, str]:
    return {
        "what_was_bridged": "The bridged reviewed lesson preview was connected to the existing dry-run correction path.",
        "what_was_reused": "The existing reviewed_lesson_dry_run_correction_minimal module was reused.",
        "what_the_dry_run_means": "The lesson can be simulated in dry-run only; it has not been applied.",
        "what_is_blocked": (
            "Lesson application, memory writes, retention writes, predictor mutation, runtime behavior change, "
            "trial trace mutation, and proof claims remain blocked."
        ),
        "plain_result": (
            "The generic review path now reaches the existing reviewed lesson dry-run correction layer without "
            "creating a new dry-run channel."
        ),
    }


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _build_invalid_records(valid_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    accepted, rejected, needs_more = valid_records
    records = [
        _mutate(accepted, ["bridge_mode"], "bad_bridge_mode", "bad_bridge_mode"),
        _mutate(accepted, ["source_preview_bridge", "source_decision"], "unknown", "unknown_source_decision"),
        _mutate(accepted, ["source_preview_bridge", "legacy_status"], "rejected", "wrong_accepted_mapping"),
        _mutate(rejected, ["source_preview_bridge", "legacy_status"], "approved_for_preview", "wrong_rejected_mapping"),
        _mutate(
            needs_more,
            ["source_preview_bridge", "legacy_status"],
            "approved_for_preview",
            "wrong_needs_more_mapping",
        ),
        _mutate(
            accepted,
            ["source_preview_bridge", "reviewed_lesson_trace_preview_created"],
            False,
            "accepted_preview_not_created",
        ),
        _mutate(
            accepted,
            ["dry_run_bridge_result", "existing_dry_run_module_called"],
            False,
            "accepted_dry_run_module_not_called",
        ),
        _mutate(
            accepted,
            ["dry_run_bridge_result", "dry_run_correction_created"],
            False,
            "accepted_dry_run_not_created",
        ),
        _mutate(accepted, ["dry_run_bridge_result", "dry_run_only"], False, "accepted_dry_run_only_false"),
        _mutate(accepted, ["dry_run_bridge_result", "lesson_applied"], True, "accepted_lesson_applied"),
        _mutate(accepted, ["dry_run_bridge_result", "memory_write"], True, "accepted_memory_write"),
        _mutate(accepted, ["dry_run_bridge_result", "retention_write"], True, "accepted_retention_write"),
        _mutate(accepted, ["dry_run_bridge_result", "predictor_modified"], True, "accepted_predictor_modified"),
        _mutate(
            accepted,
            ["dry_run_bridge_result", "runtime_behavior_changed"],
            True,
            "accepted_runtime_behavior_changed",
        ),
        _mutate(accepted, ["dry_run_bridge_result", "trial_trace_modified"], True, "accepted_trial_trace_modified"),
        _mutate(rejected, ["dry_run_bridge_result", "dry_run_correction_created"], True, "rejected_dry_run_created"),
        _mutate(
            needs_more,
            ["dry_run_bridge_result", "dry_run_correction_created"],
            True,
            "needs_more_dry_run_created",
        ),
        _mutate(accepted, ["blocked_flags", "new_dry_run_implementation_created"], True, "new_dry_run_impl"),
        _mutate(
            accepted,
            ["blocked_flags", "source_specific_dry_run_channel_created"],
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
        _mutate(accepted, ["dry_run_bridge_result", "dry_run_summary"], "", "empty_dry_run_summary"),
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
        "dry_run_bridge_result_count": len(validation_results),
        "valid_dry_run_bridge_result_count": len(valid_results),
        "invalid_dry_run_bridge_result_count": sum(1 for result in validation_results if not result["valid"]),
        "accepted_dry_run_bridge_count": sum(1 for result in valid_results if result["accepted_dry_run_bridge"]),
        "rejected_dry_run_bridge_count": sum(1 for result in valid_results if result["rejected_dry_run_bridge"]),
        "needs_more_evidence_dry_run_bridge_count": sum(
            1 for result in valid_results if result["needs_more_evidence_dry_run_bridge"]
        ),
        "dry_run_correction_created_count": sum(1 for result in valid_results if result["dry_run_correction_created"]),
        "dry_run_blocked_count": sum(1 for result in valid_results if result["dry_run_blocked"]),
        "existing_dry_run_module_reused_count": sum(
            1 for result in valid_results if result["existing_dry_run_module_reused"]
        ),
        "source_specific_dry_run_channel_blocked_count": _count_error(
            validation_results, "source_specific_dry_run_channel_created_enabled"
        ),
        "new_dry_run_implementation_blocked_count": _count_error(
            validation_results, "new_dry_run_implementation_created_enabled"
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
        "trial_trace_mutation_blocked_count": _count_error(validation_results, "trial_trace_modified_not_false")
        + _count_error(validation_results, "trial_trace_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(
            validation_results, "proof_of_learning_claim_enabled"
        ),
    }
    summary["all_generic_reviewed_lesson_dry_run_bridge_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["valid_dry_run_bridge_result_count"] == 3
        and summary["accepted_dry_run_bridge_count"] == 1
        and summary["rejected_dry_run_bridge_count"] == 1
        and summary["needs_more_evidence_dry_run_bridge_count"] == 1
        and summary["dry_run_correction_created_count"] == 1
        and summary["dry_run_blocked_count"] == 2
        and summary["existing_dry_run_module_reused_count"] == 1
        and summary["source_specific_dry_run_channel_blocked_count"] >= 1
        and summary["new_dry_run_implementation_blocked_count"] >= 1
        and summary["lesson_application_blocked_count"] >= 1
        and summary["memory_write_blocked_count"] >= 1
        and summary["retention_write_blocked_count"] >= 1
        and summary["predictor_mutation_blocked_count"] >= 1
        and summary["runtime_behavior_change_blocked_count"] >= 1
        and summary["trial_trace_mutation_blocked_count"] >= 1
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
    mutated["dry_run_bridge_id"] = f"{record.get('dry_run_bridge_id')}:{suffix}"
    return mutated


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _bridge_id(decision: Any) -> str:
    suffix = str(decision or "unknown").replace(" ", "_")
    return f"{DRY_RUN_BRIDGE_ID}:{suffix}"


if __name__ == "__main__":
    import json

    print(json.dumps(run_generic_reviewed_lesson_dry_run_bridge_minimal_check(), ensure_ascii=False, indent=2))
