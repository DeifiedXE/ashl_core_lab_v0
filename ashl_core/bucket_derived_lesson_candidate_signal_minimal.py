"""Bucket-derived lesson candidate signal without lesson text generation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .level3_toy_minefield_variant_suite_stability_minimal import (
    CONCLUSION_PASSED,
    PACKAGE_ID as SOURCE_PACKAGE_ID,
    STABILITY_STABLE,
    build_level3_toy_minefield_variant_suite_stability_review,
    validate_level3_toy_minefield_variant_suite_stability_review,
)


COMMAND = "run-bucket-derived-lesson-candidate-signal-minimal-check"
FLOW = "bucket_derived_lesson_candidate_signal_minimal_v0"
PACKAGE_ID = "PKG-Phase0-Bucket-Derived-Lesson-Candidate-Signal-Minimal-v0"
BOUNDARY_VERSION = "2026-06-09-b74"
REQUIRED_SUPPORTING_CONTEXTS = (
    "safe_path_variant",
    "risky_repeat_trap_variant",
    "blocked_path_fallback_variant",
)
SUPPORTING_EVIDENCE_TYPES = (
    "level3_variant_trace",
    "level3_variant_observation",
    "level3_variant_evaluation",
    "level3_variant_stability_summary",
    "level3_variant_review_conclusion",
)
FALSE_PERMISSION_FIELDS = (
    "memory_write_allowed",
    "retained_jsonl_write_allowed",
    "runtime_influence_allowed",
    "predictor_influence_allowed",
    "production_behavior_change_allowed",
    "selected_action_allowed",
    "final_action_allowed",
    "proof_of_learning_claim_allowed",
)
SAFE_CLAIM = (
    "ASHL Core can detect a structured bucket-derived lesson candidate signal from bounded Phase0 "
    "Level 3 sandbox evidence, pending human interpretation and review, without writing memory or "
    "changing runtime behavior."
)


def build_bucket_derived_lesson_candidate_signal(
    source_variant_suite: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_variant_suite is None:
        source_variant_suite = build_level3_toy_minefield_variant_suite_stability_review()
    source_valid = validate_level3_toy_minefield_variant_suite_stability_review(source_variant_suite).get("valid") is True
    stability = source_variant_suite.get("stability_summary", {})
    conclusion = source_variant_suite.get("review_conclusion", {})
    contexts = list(stability.get("passed_variant_ids", REQUIRED_SUPPORTING_CONTEXTS))
    return {
        "record_type": "bucket_derived_lesson_candidate_signal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "candidate_signal_status": "pending_human_interpretation",
        "signal_source_type": "qingyin_bucket_derived_system_detected",
        "qingyin_generated_text": False,
        "text_lesson_candidate_created": False,
        "human_interpretation_required": True,
        "source_scope": "phase0_level3_toy_minefield_variant_suite_only",
        "source_package_id": SOURCE_PACKAGE_ID,
        "source_variant_suite_valid": source_valid,
        "source_review_status": "concluded_level3_variant_review_passed"
        if conclusion.get("review_conclusion_status") == CONCLUSION_PASSED
        else conclusion.get("review_conclusion_status"),
        "source_stability_status": stability.get("stability_status"),
        "repeated_key": "retry_same_risky_action_without_check",
        "occurrence_count": len(contexts),
        "minimum_signal_threshold": 3,
        "supporting_contexts": contexts,
        "supporting_evidence_types": list(SUPPORTING_EVIDENCE_TYPES),
        "suggested_human_interpretation": None,
        "generated_lesson_text": None,
        "memory_write_allowed": False,
        "retained_jsonl_write_allowed": False,
        "runtime_influence_allowed": False,
        "predictor_influence_allowed": False,
        "production_behavior_change_allowed": False,
        "selected_action_allowed": False,
        "final_action_allowed": False,
        "proof_of_learning_claim_allowed": False,
        "task_queue_completed_status_is_approval": False,
        "passing_tests_are_approval": False,
        "codex_generated_candidate_text_is_qingyin_authored": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_variant_suite": deepcopy(source_variant_suite),
    }


def validate_bucket_derived_lesson_candidate_signal(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "bucket_derived_lesson_candidate_signal":
        errors.append("record_type_not_bucket_derived_lesson_candidate_signal")
    if record.get("record_version") != "v0":
        errors.append("record_version_not_v0")
    if record.get("candidate_signal_status") != "pending_human_interpretation":
        errors.append("candidate_signal_status_not_pending_human_interpretation")
    if record.get("signal_source_type") != "qingyin_bucket_derived_system_detected":
        errors.append("signal_source_type_not_qingyin_bucket_derived_system_detected")
    if record.get("qingyin_generated_text") is not False:
        errors.append("qingyin_generated_text_not_false")
    if record.get("text_lesson_candidate_created") is not False:
        errors.append("text_lesson_candidate_created_not_false")
    if record.get("human_interpretation_required") is not True:
        errors.append("human_interpretation_required_not_true")
    if record.get("source_scope") != "phase0_level3_toy_minefield_variant_suite_only":
        errors.append("source_scope_not_level3_variant_suite_only")
    if record.get("source_variant_suite_valid") is not True:
        errors.append("source_variant_suite_valid_not_true")
    if record.get("source_review_status") != "concluded_level3_variant_review_passed":
        errors.append("source_review_status_not_passed")
    if record.get("source_stability_status") != STABILITY_STABLE:
        errors.append("source_stability_status_not_stable")
    if not isinstance(record.get("repeated_key"), str) or not record.get("repeated_key", "").strip():
        errors.append("repeated_key_empty")
    if not isinstance(record.get("minimum_signal_threshold"), int) or record.get("minimum_signal_threshold") < 2:
        errors.append("minimum_signal_threshold_too_low")
    if not isinstance(record.get("occurrence_count"), int) or record.get("occurrence_count") < record.get(
        "minimum_signal_threshold", 999
    ):
        errors.append("occurrence_count_below_threshold")
    contexts = record.get("supporting_contexts", [])
    if not set(REQUIRED_SUPPORTING_CONTEXTS).issubset(set(contexts if isinstance(contexts, list) else [])):
        errors.append("supporting_contexts_missing_required_variants")
    if record.get("supporting_evidence_types") != list(SUPPORTING_EVIDENCE_TYPES):
        errors.append("supporting_evidence_types_not_expected")
    if record.get("generated_lesson_text") is not None:
        errors.append("generated_lesson_text_not_null")
    if record.get("suggested_human_interpretation") is not None:
        errors.append("suggested_human_interpretation_not_null")
    for field in FALSE_PERMISSION_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in (
        "task_queue_completed_status_is_approval",
        "passing_tests_are_approval",
        "codex_generated_candidate_text_is_qingyin_authored",
    ):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if record.get("audit_recorded") is not True:
        errors.append("audit_recorded_not_true")
    if record.get("rollback_available") is not True:
        errors.append("rollback_available_not_true")
    return {"valid": not errors, "error_codes": errors}


def run_bucket_derived_lesson_candidate_signal_minimal_check() -> dict[str, Any]:
    valid = build_bucket_derived_lesson_candidate_signal()
    invalid = _invalid_records(valid)
    validation_results = [validate_bucket_derived_lesson_candidate_signal(record) for record in [valid] + invalid]
    valid_results = [result for result in validation_results if result["valid"]]
    summary = {
        "valid_signal_count": len(valid_results),
        "invalid_signal_count": len(validation_results) - len(valid_results),
        "source_bucket_checked_count": 1 if valid.get("source_variant_suite_valid") is True else 0,
        "repeated_key_checked_count": 1 if valid.get("repeated_key") else 0,
        "threshold_checked_count": 1
        if valid.get("occurrence_count", 0) >= valid.get("minimum_signal_threshold", 999)
        else 0,
        "supporting_context_checked_count": 1
        if set(REQUIRED_SUPPORTING_CONTEXTS).issubset(set(valid.get("supporting_contexts", [])))
        else 0,
        "human_interpretation_required_count": 1 if valid.get("human_interpretation_required") is True else 0,
        "memory_write_blocked_count": 1 if valid.get("memory_write_allowed") is False else 0,
        "runtime_influence_blocked_count": 1 if valid.get("runtime_influence_allowed") is False else 0,
        "proof_claim_blocked_count": 1 if valid.get("proof_of_learning_claim_allowed") is False else 0,
    }
    summary["all_bucket_derived_lesson_candidate_signal_checks_passed"] = (
        summary["valid_signal_count"] == 1
        and summary["invalid_signal_count"] >= 1
        and summary["source_bucket_checked_count"] == 1
        and summary["repeated_key_checked_count"] == 1
        and summary["threshold_checked_count"] == 1
        and summary["supporting_context_checked_count"] == 1
        and summary["human_interpretation_required_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["runtime_influence_blocked_count"] == 1
        and summary["proof_claim_blocked_count"] == 1
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_bucket_derived_lesson_candidate_signal_checks_passed"] else "failed",
        "valid_record": valid,
        "invalid_records": invalid,
        "validation_results": validation_results,
        "summary": summary,
        "safe_claim": SAFE_CLAIM,
        "boundary": {
            "boundary_change_required": False,
            "boundary_index_update_required": False,
            "boundary_index_version_before": BOUNDARY_VERSION,
            "boundary_index_version_after": BOUNDARY_VERSION,
            "boundary_change_rationale": (
                "This package creates a structured signal from existing Level 3 sandbox evidence only. "
                "It does not create lesson text, write memory, write retained JSONL, mutate predictors, "
                "change runtime behavior, select actions, promote production behavior, or claim proof of learning."
            ),
        },
    }


def _invalid_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _mutated(valid, ["generated_lesson_text"], "Check before retrying risky actions."),
        _mutated(valid, ["suggested_human_interpretation"], "Human-readable lesson text fixture."),
        _mutated(valid, ["qingyin_generated_text"], True),
        _mutated(valid, ["text_lesson_candidate_created"], True),
        _mutated(valid, ["human_interpretation_required"], False),
        _mutated(valid, ["occurrence_count"], 2),
        _mutated(valid, ["supporting_contexts"], ["safe_path_variant"]),
        _mutated(valid, ["source_scope"], "phase0_level3_toy_minefield_sandbox_only"),
        _mutated(valid, ["source_variant_suite_valid"], False),
        _mutated(valid, ["memory_write_allowed"], True),
        _mutated(valid, ["retained_jsonl_write_allowed"], True),
        _mutated(valid, ["runtime_influence_allowed"], True),
        _mutated(valid, ["predictor_influence_allowed"], True),
        _mutated(valid, ["production_behavior_change_allowed"], True),
        _mutated(valid, ["selected_action_allowed"], True),
        _mutated(valid, ["final_action_allowed"], True),
        _mutated(valid, ["proof_of_learning_claim_allowed"], True),
        _mutated(valid, ["task_queue_completed_status_is_approval"], True),
        _mutated(valid, ["passing_tests_are_approval"], True),
        _mutated(valid, ["codex_generated_candidate_text_is_qingyin_authored"], True),
        _mutated(valid, ["audit_recorded"], False),
        _mutated(valid, ["rollback_available"], False),
    ]


def _mutated(record: dict[str, Any], path: list[Any], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: Any = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(run_bucket_derived_lesson_candidate_signal_minimal_check(), indent=2))
