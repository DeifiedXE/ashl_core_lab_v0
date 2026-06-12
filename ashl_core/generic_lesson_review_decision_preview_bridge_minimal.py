"""Bridge generic lesson review decisions into existing reviewed lesson preview."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .generic_lesson_review_decision_minimal import (
    ALLOWED_SOURCE_TYPES,
    build_generic_lesson_review_decision,
    validate_generic_lesson_review_decision,
)
from .lesson_candidate_from_failure_reason import validate_lesson_candidate_record
from .lesson_candidate_human_review_decision_schema import validate_lesson_candidate_human_review_decision
from .phase0_level0_obstacle_memory_flip_test_minimal import build_phase0_level0_obstacle_memory_flip_result
from .reviewed_lesson_trace_preview import (
    build_reviewed_lesson_trace_preview,
    validate_reviewed_lesson_trace_preview,
)


COMMAND = "run-generic-lesson-review-decision-preview-bridge-minimal-check"
FLOW = "generic_lesson_review_decision_preview_bridge_minimal_v0"
BRIDGE_ID = "generic_lesson_review_decision_preview_bridge_demo_001"
BRIDGE_MODE = "generic_decision_to_existing_reviewed_lesson_preview_bridge"
GENERIC_TO_LEGACY_STATUS = {
    "accepted_for_reviewed_lesson_preview": "approved_for_preview",
    "rejected": "rejected",
    "needs_more_evidence": "needs_revision",
}
BLOCKED_REASON_BY_DECISION = {
    "rejected": "rejected_decision_cannot_enter_preview",
    "needs_more_evidence": "needs_more_evidence_cannot_enter_preview",
}
ADAPTER_IDS = {
    "source_evidence_summary_id": "evidence_summary_phase0_level1_contrast_001",
    "source_review_gate_result_id": "review_gate_phase0_level1_contrast_001",
    "source_lesson_candidate_id": "lesson_candidate_phase0_level1_danger_check_001",
    "source_failure_reason_id": "failure_reason_phase0_level1_retry_into_danger_001",
    "source_pair_id": "outcome_pair_phase0_level1_contrast_001",
    "action_intent_id": "action_intent_phase0_level1_check_before_retry_001",
}
REQUIRED_TOP_LEVEL = {
    "bridge_result_id",
    "bridge_mode",
    "source_generic_decision",
    "legacy_adapter",
    "preview_bridge_result",
    "supporting_evidence",
    "human_summary",
    "blocked_flags",
}
REQUIRED_HUMAN_SUMMARY = {
    "what_was_bridged",
    "mapping",
    "what_was_reused",
    "what_is_blocked",
    "plain_result",
}
REQUIRED_BLOCKED_FLAGS = {
    "source_specific_review_channel_created",
    "new_reviewed_lesson_preview_implementation",
    "lesson_applied",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_modified",
    "runtime_behavior_changed",
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


def build_generic_lesson_review_decision_preview_bridge(
    generic_decision: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if generic_decision is None:
        generic_decision = build_generic_lesson_review_decision()

    generic_validation = validate_generic_lesson_review_decision(generic_decision)
    decision = generic_decision.get("human_review_decision", {}).get("decision")
    legacy_status = GENERIC_TO_LEGACY_STATUS.get(decision, "unknown")
    legacy_candidate = _build_legacy_lesson_candidate()
    legacy_decision = _build_legacy_human_review_decision(legacy_status)
    candidate_validation = validate_lesson_candidate_record(legacy_candidate)
    legacy_validation = validate_lesson_candidate_human_review_decision(legacy_decision)
    legacy_validator_passed = (
        generic_validation["valid"] and candidate_validation["valid"] and legacy_validation["valid"]
    )

    preview = None
    preview_validation: dict[str, Any] | None = None
    existing_preview_called = decision == "accepted_for_reviewed_lesson_preview"
    preview_created = False
    blocked_reason = BLOCKED_REASON_BY_DECISION.get(decision)
    if existing_preview_called:
        preview = build_reviewed_lesson_trace_preview(legacy_candidate, legacy_decision)
        preview_validation = validate_reviewed_lesson_trace_preview(preview)
        preview_created = preview_validation["valid"] and preview.get("preview_status", {}).get("created") is True
        if not preview_created:
            blocked_reason = "existing_reviewed_lesson_preview_not_created"

    source = generic_decision.get("source", {})
    allowed = generic_decision.get("allowed_next_layer", {})
    return {
        "bridge_result_id": _bridge_id(decision),
        "bridge_mode": BRIDGE_MODE,
        "source_generic_decision": {
            "decision": decision,
            "source_type": source.get("source_type"),
            "source_trace_ref": source.get("source_trace_ref"),
            "may_enter_reviewed_lesson_preview": allowed.get("may_enter_reviewed_lesson_preview") is True,
            "may_enter_lesson_dry_run": allowed.get("may_enter_lesson_dry_run") is True,
            "may_apply_lesson": allowed.get("may_apply_lesson") is True,
        },
        "legacy_adapter": {
            "legacy_status": legacy_status,
            **ADAPTER_IDS,
            "legacy_validator_passed": legacy_validator_passed,
        },
        "preview_bridge_result": {
            "existing_reviewed_lesson_preview_called": existing_preview_called,
            "reviewed_lesson_trace_preview_created": preview_created,
            "preview_only": preview_created,
            "lesson_applied": False,
            "dry_run_created": False,
            "runtime_behavior_changed": False,
            **({"blocked_reason": blocked_reason} if blocked_reason else {}),
        },
        "supporting_evidence": _supporting_evidence(),
        "human_summary": _human_summary(decision, legacy_status),
        "blocked_flags": _blocked_flags(),
    }


def validate_generic_lesson_review_decision_preview_bridge(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _check_top_level(record, errors)
    if record.get("bridge_mode") != BRIDGE_MODE:
        errors.append("bridge_mode_not_generic_decision_to_existing_reviewed_lesson_preview_bridge")

    source = _section(record, "source_generic_decision", errors)
    decision = source.get("decision")
    if decision not in GENERIC_TO_LEGACY_STATUS:
        errors.append("unknown_generic_decision")
    if source.get("source_type") not in ALLOWED_SOURCE_TYPES:
        errors.append("unknown_source_type")
    _require_non_empty(source, "source_trace_ref", errors)

    legacy = _section(record, "legacy_adapter", errors)
    expected_status = GENERIC_TO_LEGACY_STATUS.get(decision)
    if legacy.get("legacy_status") != expected_status:
        errors.append("legacy_status_mapping_mismatch")
    for field in ADAPTER_IDS:
        _require_non_empty(legacy, field, errors)
    if decision == "accepted_for_reviewed_lesson_preview":
        _require_true(legacy, "legacy_validator_passed", errors)

    preview = _section(record, "preview_bridge_result", errors)
    _validate_preview_result(decision, source, preview, errors)

    evidence = _section(record, "supporting_evidence", errors)
    for field in (
        "level0_flip_test_used_as_supporting_evidence",
        "bidirectional_flip_passed",
        "one_way_caution_bias_rejected",
        "level1_contrast_sample_set_used_as_candidate_source",
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
        "bridge_result_id": record.get("bridge_result_id"),
        "valid": not errors,
        "error_codes": errors,
        "decision": decision,
        "legacy_status": legacy.get("legacy_status"),
        "accepted_bridge": decision == "accepted_for_reviewed_lesson_preview",
        "rejected_bridge": decision == "rejected",
        "needs_more_evidence_bridge": decision == "needs_more_evidence",
        "reviewed_lesson_trace_preview_created": preview.get("reviewed_lesson_trace_preview_created") is True,
        "preview_blocked": preview.get("reviewed_lesson_trace_preview_created") is False,
        "existing_preview_reused": preview.get("existing_reviewed_lesson_preview_called") is True,
    }


def run_generic_lesson_review_decision_preview_bridge_minimal_check() -> dict[str, Any]:
    valid_records = [
        build_generic_lesson_review_decision_preview_bridge(
            build_generic_lesson_review_decision(decision="accepted_for_reviewed_lesson_preview")
        ),
        build_generic_lesson_review_decision_preview_bridge(
            build_generic_lesson_review_decision(decision="rejected")
        ),
        build_generic_lesson_review_decision_preview_bridge(
            build_generic_lesson_review_decision(decision="needs_more_evidence")
        ),
    ]
    records = valid_records + _build_invalid_records(valid_records)
    validation_results = [validate_generic_lesson_review_decision_preview_bridge(record) for record in records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_generic_lesson_review_decision_preview_bridge_minimal_checks_passed"] else "failed",
        "preview_bridge_results": records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "schema_bridge_only": True,
            "existing_reviewed_lesson_preview_reused": True,
            "source_specific_review_channel_created": False,
            "new_reviewed_lesson_preview_implementation": False,
            "lesson_application_added": False,
            "dry_run_created": False,
            "memory_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "runtime_behavior_change_added": False,
            "proof_of_learning_claimed": False,
        },
        "notes": [
            "Generic decision is the shared review gate.",
            "Existing reviewed_lesson_trace_preview remains the preview path.",
            "The bridge only adapts schemas.",
        ],
    }


def _build_legacy_lesson_candidate() -> dict[str, Any]:
    return {
        "lesson_candidate_id": ADAPTER_IDS["source_lesson_candidate_id"],
        "source_failure_reason_id": ADAPTER_IDS["source_failure_reason_id"],
        "source_pair_id": ADAPTER_IDS["source_pair_id"],
        "action_intent_id": ADAPTER_IDS["action_intent_id"],
        "candidate_type": "precondition_or_correction",
        "proposed_correction": {
            "correction_type": "check_before_retry",
            "description": "Check before retrying in the controlled Level 1 danger fixture.",
            "target_action_type": "retry_same_action",
            "candidate_description_only": True,
            "correction_applied": False,
        },
        "applicability": {
            "source_category": "phase0_level1_retry_into_danger_contrast",
            "requires_human_review": True,
            "generalization_allowed": False,
            "persistent_candidate_allowed": False,
        },
        "confidence": {
            "value": 0.0,
            "basis": "single_demo_failure_reason",
            "runtime_confidence": False,
        },
        "source_trace": {
            "source": "lesson_candidate_from_failure_reason",
            "failure_reason_source": "failure_reason_from_outcome_pair",
            "source_failure_reason_id": ADAPTER_IDS["source_failure_reason_id"],
        },
        "review_boundary": {
            "review_required": True,
            "approved": False,
            "rejected": False,
            "lesson_application_allowed": False,
            "persistent_learning_allowed": False,
            "memory_write_allowed": False,
            "predictor_mutation_allowed": False,
        },
        "safety_flags": {
            "trace_only": True,
            "blocked_from_action_selection": True,
            "blocked_from_action_behavior_change": True,
            "blocked_from_lesson_application": True,
            "blocked_from_memory_write": True,
            "blocked_from_predictor_mutation": True,
            "blocked_from_persistent_rule_write": True,
            "approved_lesson": False,
            "lesson_applied": False,
            "action_selection_influence": False,
            "action_behavior_changed": False,
            "lesson_application_runtime": False,
            "memory_write": False,
            "predictor_modified": False,
            "persistent_rule_write": False,
            "endocrine_control": False,
            "autonomy_enabled": False,
        },
    }


def _build_legacy_human_review_decision(status: str) -> dict[str, Any]:
    allows_preview = status == "approved_for_preview"
    return {
        "review_decision_id": f"human_review_decision:{ADAPTER_IDS['source_evidence_summary_id']}:{status}",
        **ADAPTER_IDS,
        "decision": {
            "status": status,
            "reviewed_by_human": True,
            "approved_for_lesson_application": False,
            "approved_for_persistent_learning": False,
            "approved_for_memory_write": False,
            "approved_for_predictor_mutation": False,
        },
        "reviewer_trace": {
            "reviewer_type": "human",
            "review_mode": "manual",
            "review_timestamp": None,
            "reviewer_id": "human_mentor",
        },
        "review_reason": {
            "reason_code": "generic_decision_bridge",
            "description": "Generic lesson review decision was adapted for existing reviewed lesson preview.",
            "uses_evidence_summary": True,
        },
        "decision_scope": {
            "allows_preview": allows_preview,
            "allows_application": False,
            "allows_action_selection_influence": False,
            "allows_memory_write": False,
            "allows_persistent_rule_write": False,
            "allows_predictor_mutation": False,
        },
        "boundary_summary": {
            "lesson_applied": False,
            "behavior_preview_created": False,
            "action_selection_influence": False,
            "memory_write": False,
            "predictor_modified": False,
            "persistent_rule_write": False,
            "autonomy_enabled": False,
            "lesson_application_runtime": False,
        },
        "source_trace": {
            "source": "lesson_candidate_human_review_decision_schema",
            "evidence_summary_source": "lesson_candidate_review_evidence_summary",
            "lesson_candidate_source": "lesson_candidate_from_failure_reason",
        },
        "safety_flags": {
            "trace_only_decision": True,
            "blocked_from_lesson_application": True,
            "blocked_from_action_selection": True,
            "blocked_from_action_behavior_change": True,
            "blocked_from_memory_write": True,
            "blocked_from_predictor_mutation": True,
            "blocked_from_persistent_rule_write": True,
        },
    }


def _supporting_evidence() -> dict[str, bool]:
    level0 = build_phase0_level0_obstacle_memory_flip_result()
    flip = level0.get("flip_check", {})
    return {
        "level0_flip_test_used_as_supporting_evidence": True,
        "bidirectional_flip_passed": flip.get("bidirectional_flip_passed") is True,
        "one_way_caution_bias_rejected": flip.get("one_way_caution_bias_rejected") is True,
        "level1_contrast_sample_set_used_as_candidate_source": True,
    }


def _human_summary(decision: Any, legacy_status: str) -> dict[str, str]:
    return {
        "what_was_bridged": "A generic lesson review decision was bridged into the existing reviewed lesson preview path.",
        "mapping": f"{decision} was mapped to legacy {legacy_status}.",
        "what_was_reused": "The existing reviewed_lesson_trace_preview path was reused rather than reimplemented.",
        "what_is_blocked": (
            "Lesson application, memory writes, retention writes, predictor mutation, runtime behavior change, "
            "and proof claims remain blocked."
        ),
        "plain_result": "The generic decision gate can now feed the existing reviewed lesson preview pipeline.",
    }


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _bridge_id(decision: Any) -> str:
    suffix = str(decision or "unknown").replace(" ", "_")
    return f"{BRIDGE_ID}:{suffix}"


def _validate_preview_result(
    decision: Any,
    source: dict[str, Any],
    preview: dict[str, Any],
    errors: list[str],
) -> None:
    if decision == "accepted_for_reviewed_lesson_preview":
        _require_true(source, "may_enter_reviewed_lesson_preview", errors)
        _require_true(source, "may_enter_lesson_dry_run", errors)
        _require_false(source, "may_apply_lesson", errors)
        _require_true(preview, "existing_reviewed_lesson_preview_called", errors)
        _require_true(preview, "reviewed_lesson_trace_preview_created", errors)
        _require_true(preview, "preview_only", errors)
        _require_false(preview, "lesson_applied", errors)
        _require_false(preview, "dry_run_created", errors)
        _require_false(preview, "runtime_behavior_changed", errors)
    elif decision == "rejected":
        _require_false(preview, "existing_reviewed_lesson_preview_called", errors)
        _require_false(preview, "reviewed_lesson_trace_preview_created", errors)
        if preview.get("blocked_reason") != "rejected_decision_cannot_enter_preview":
            errors.append("rejected_blocked_reason_mismatch")
    elif decision == "needs_more_evidence":
        _require_false(preview, "existing_reviewed_lesson_preview_called", errors)
        _require_false(preview, "reviewed_lesson_trace_preview_created", errors)
        if preview.get("blocked_reason") != "needs_more_evidence_cannot_enter_preview":
            errors.append("needs_more_evidence_blocked_reason_mismatch")
    for field in ("lesson_applied", "dry_run_created", "runtime_behavior_changed"):
        _require_false(preview, field, errors)


def _build_invalid_records(valid_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    accepted, rejected, needs_more = valid_records
    records = [
        _mutate(accepted, ["bridge_mode"], "bad_bridge_mode", "bad_bridge_mode"),
        _mutate(accepted, ["source_generic_decision", "decision"], "unknown", "unknown_generic_decision"),
        _mutate(accepted, ["legacy_adapter", "legacy_status"], "rejected", "wrong_accepted_mapping"),
        _mutate(rejected, ["legacy_adapter", "legacy_status"], "approved_for_preview", "wrong_rejected_mapping"),
        _mutate(needs_more, ["legacy_adapter", "legacy_status"], "approved_for_preview", "wrong_needs_more_mapping"),
        _mutate(accepted, ["preview_bridge_result", "existing_reviewed_lesson_preview_called"], False, "accepted_preview_not_called"),
        _mutate(accepted, ["preview_bridge_result", "reviewed_lesson_trace_preview_created"], False, "accepted_preview_not_created"),
        _mutate(rejected, ["preview_bridge_result", "reviewed_lesson_trace_preview_created"], True, "rejected_preview_created"),
        _mutate(needs_more, ["preview_bridge_result", "reviewed_lesson_trace_preview_created"], True, "needs_more_preview_created"),
        _mutate(accepted, ["source_generic_decision", "may_apply_lesson"], True, "accepted_may_apply_lesson"),
        _mutate(accepted, ["preview_bridge_result", "lesson_applied"], True, "preview_lesson_applied"),
        _mutate(accepted, ["preview_bridge_result", "dry_run_created"], True, "preview_dry_run_created"),
        _mutate(accepted, ["preview_bridge_result", "runtime_behavior_changed"], True, "runtime_behavior_changed"),
        _mutate(accepted, ["legacy_adapter", "legacy_validator_passed"], False, "legacy_validator_failed"),
        _mutate(accepted, ["supporting_evidence", "level0_flip_test_used_as_supporting_evidence"], False, "level0_missing"),
        _mutate(accepted, ["supporting_evidence", "bidirectional_flip_passed"], False, "bidirectional_false"),
        _mutate(accepted, ["supporting_evidence", "one_way_caution_bias_rejected"], False, "caution_bias_false"),
        _mutate(accepted, ["supporting_evidence", "level1_contrast_sample_set_used_as_candidate_source"], False, "level1_missing"),
    ]
    for field in ADAPTER_IDS:
        records.append(_mutate(accepted, ["legacy_adapter", field], "", f"empty_{field}"))
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        records.append(_mutate(accepted, ["human_summary", field], "", f"empty_{field}"))
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        records.append(_mutate(accepted, ["blocked_flags", field], True, field))
    return records


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "preview_bridge_result_count": len(validation_results),
        "valid_preview_bridge_result_count": len(valid_results),
        "invalid_preview_bridge_result_count": sum(1 for result in validation_results if not result["valid"]),
        "accepted_bridge_count": sum(1 for result in valid_results if result["accepted_bridge"]),
        "rejected_bridge_count": sum(1 for result in valid_results if result["rejected_bridge"]),
        "needs_more_evidence_bridge_count": sum(1 for result in valid_results if result["needs_more_evidence_bridge"]),
        "reviewed_lesson_trace_preview_created_count": sum(
            1 for result in valid_results if result["reviewed_lesson_trace_preview_created"]
        ),
        "preview_blocked_count": sum(1 for result in valid_results if result["preview_blocked"]),
        "legacy_approved_for_preview_mapping_count": _count_valid_legacy_status(valid_results, "approved_for_preview"),
        "legacy_rejected_mapping_count": _count_valid_legacy_status(valid_results, "rejected"),
        "legacy_needs_revision_mapping_count": _count_valid_legacy_status(valid_results, "needs_revision"),
        "existing_preview_reused_count": sum(1 for result in valid_results if result["existing_preview_reused"]),
        "source_specific_channel_blocked_count": _count_error(
            validation_results, "source_specific_review_channel_created_enabled"
        ),
        "new_preview_implementation_blocked_count": _count_error(
            validation_results, "new_reviewed_lesson_preview_implementation_enabled"
        ),
        "lesson_application_blocked_count": _count_error(validation_results, "lesson_applied_enabled")
        + _count_error(validation_results, "lesson_applied_not_false")
        + _count_error(validation_results, "may_apply_lesson_not_false"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "retention_write_blocked_count": _count_error(validation_results, "retention_write_enabled"),
        "predictor_mutation_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "runtime_behavior_change_blocked_count": _count_error(validation_results, "runtime_behavior_changed_enabled")
        + _count_error(validation_results, "runtime_behavior_changed_not_false"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
    }
    summary["all_generic_lesson_review_decision_preview_bridge_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["valid_preview_bridge_result_count"] == 3
        and summary["accepted_bridge_count"] == 1
        and summary["rejected_bridge_count"] == 1
        and summary["needs_more_evidence_bridge_count"] == 1
        and summary["reviewed_lesson_trace_preview_created_count"] == 1
        and summary["preview_blocked_count"] == 2
        and summary["legacy_approved_for_preview_mapping_count"] == 1
        and summary["legacy_rejected_mapping_count"] == 1
        and summary["legacy_needs_revision_mapping_count"] == 1
        and summary["existing_preview_reused_count"] == 1
        and summary["source_specific_channel_blocked_count"] == 1
        and summary["new_preview_implementation_blocked_count"] == 1
        and summary["lesson_application_blocked_count"] >= 3
        and summary["memory_write_blocked_count"] == 1
        and summary["retention_write_blocked_count"] == 1
        and summary["predictor_mutation_blocked_count"] == 1
        and summary["runtime_behavior_change_blocked_count"] >= 2
        and summary["proof_of_learning_claim_blocked_count"] == 1
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
    mutated["bridge_result_id"] = f"{record.get('bridge_result_id')}:{suffix}"
    return mutated


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_legacy_status(valid_results: list[dict[str, Any]], status: str) -> int:
    return sum(1 for result in valid_results if result.get("legacy_status") == status)


if __name__ == "__main__":
    import json

    print(json.dumps(run_generic_lesson_review_decision_preview_bridge_minimal_check(), ensure_ascii=False, indent=2))
