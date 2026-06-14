"""Design-only memory readiness record for approved bucket-derived lessons."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import (
    BOUNDARY_VERSION,
    INTERPRETED_LESSON_TEXT,
    QINGYIN_STATUS,
    REPEATED_KEY,
    build_human_interpretation_review_decision,
    validate_human_interpretation_review_decision,
    validate_human_interpreted_lesson_candidate,
)


COMMAND = "run-memory-readiness-design-for-approved-bucket-lesson-minimal-check"
FLOW = "memory_readiness_design_for_approved_bucket_lesson_minimal_v0"
PACKAGE_ID = "PKG-Phase0-Memory-Readiness-Design-Approved-Bucket-Lesson-Minimal-v0"
APPROVED_REVIEW_DECISION = "approved_for_future_memory_readiness_design_only"
REQUIRED_BEFORE_MEMORY_WRITE = (
    "explicit_future_memory_admission_package",
    "explicit_human_memory_admission_approval",
    "memory_layer_target_selection",
    "retention_and_rollback_rule",
    "cross_session_influence_rebuild_rule",
    "runtime_influence_boundary",
    "predictor_influence_boundary",
    "audit_and_revocation_path",
)
FALSE_PERMISSION_FIELDS = (
    "memory_write_allowed",
    "retained_jsonl_write_allowed",
    "retention_write_allowed",
    "runtime_influence_allowed",
    "predictor_influence_allowed",
    "production_behavior_change_allowed",
    "selected_action_allowed",
    "final_action_allowed",
    "proof_of_learning_claim_allowed",
)


def build_memory_readiness_design_for_approved_bucket_lesson(
    review_decision: dict[str, Any] | None = None,
) -> dict[str, Any]:
    review = (
        deepcopy(review_decision)
        if review_decision is not None
        else build_human_interpretation_review_decision()
    )
    review_validation = validate_human_interpretation_review_decision(review)
    if not review_validation["valid"]:
        raise ValueError("invalid_human_interpretation_review_decision")
    if review.get("review_decision") != APPROVED_REVIEW_DECISION:
        raise ValueError("review_decision_not_approved_for_memory_readiness_design")
    if review.get("memory_readiness_design_allowed") is not True:
        raise ValueError("memory_readiness_design_not_allowed")
    candidate = review.get("source_interpreted_candidate")
    if not isinstance(candidate, dict):
        raise ValueError("missing_source_interpreted_candidate")
    candidate_validation = validate_human_interpreted_lesson_candidate(candidate)
    if not candidate_validation["valid"]:
        raise ValueError("invalid_source_interpreted_candidate")
    return {
        "record_type": "memory_readiness_design_for_approved_bucket_lesson",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "source_review_record_type": review.get("record_type"),
        "source_review_decision": review.get("review_decision"),
        "source_candidate_type": review.get("target_record_type"),
        "source_signal_authorship": candidate.get("source_signal_authorship"),
        "interpretation_author_type": candidate.get("interpretation_author_type"),
        "lesson_name": "check_before_retry_when_risky_or_failed",
        "repeated_key": candidate.get("source_repeated_key"),
        "interpreted_lesson_text": candidate.get("interpreted_lesson_text"),
        "readiness_design_status": "memory_readiness_design_recorded",
        "memory_admission_status": "not_admitted_to_memory",
        "memory_write_status": "not_written",
        "current_allowed_use": "future_memory_readiness_design_only",
        "proposed_future_memory_form": "reviewed_lesson_memory_candidate",
        "proposed_future_memory_scope": "future_sandbox_influence_design_only",
        "proposed_runtime_influence": "blocked",
        "proposed_predictor_influence": "blocked",
        "required_before_any_memory_write": list(REQUIRED_BEFORE_MEMORY_WRITE),
        "repo_audit_acknowledged": True,
        "qingyin_current_status": QINGYIN_STATUS,
        "qingyin_self_authored_lesson_text": False,
        "autonomous_learning_claim_allowed": False,
        "memory_write_allowed": False,
        "retained_jsonl_write_allowed": False,
        "retention_write_allowed": False,
        "runtime_influence_allowed": False,
        "predictor_influence_allowed": False,
        "production_behavior_change_allowed": False,
        "selected_action_allowed": False,
        "final_action_allowed": False,
        "proof_of_learning_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_review_decision_record": review,
    }


def validate_memory_readiness_design_for_approved_bucket_lesson(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "memory_readiness_design_for_approved_bucket_lesson":
        errors.append("record_type_not_memory_readiness_design_for_approved_bucket_lesson")
    if record.get("record_version") != "v0":
        errors.append("record_version_not_v0")
    if record.get("source_review_record_type") != "human_interpretation_review_decision":
        errors.append("source_review_record_type_not_human_interpretation_review_decision")
    if record.get("source_review_decision") != APPROVED_REVIEW_DECISION:
        errors.append("source_review_decision_not_approved")
    if record.get("source_candidate_type") != "human_interpreted_lesson_candidate_from_bucket_signal":
        errors.append("source_candidate_type_not_bucket_interpreted_candidate")
    if record.get("source_signal_authorship") != "qingyin_bucket_derived_system_detected":
        errors.append("source_signal_authorship_not_qingyin_bucket_derived_system_detected")
    if record.get("interpretation_author_type") != "human_or_human_gpt_assisted":
        errors.append("interpretation_author_type_not_human_or_human_gpt_assisted")
    if record.get("lesson_name") != "check_before_retry_when_risky_or_failed":
        errors.append("lesson_name_not_expected")
    if record.get("repeated_key") != REPEATED_KEY:
        errors.append("repeated_key_not_expected")
    if record.get("interpreted_lesson_text") != INTERPRETED_LESSON_TEXT:
        errors.append("interpreted_lesson_text_not_expected")
    if record.get("readiness_design_status") != "memory_readiness_design_recorded":
        errors.append("readiness_design_status_not_recorded")
    if record.get("memory_admission_status") != "not_admitted_to_memory":
        errors.append("memory_admission_status_not_not_admitted")
    if record.get("memory_write_status") != "not_written":
        errors.append("memory_write_status_not_not_written")
    if record.get("current_allowed_use") != "future_memory_readiness_design_only":
        errors.append("current_allowed_use_not_design_only")
    if record.get("proposed_future_memory_form") != "reviewed_lesson_memory_candidate":
        errors.append("proposed_future_memory_form_not_reviewed_lesson_memory_candidate")
    if record.get("proposed_future_memory_scope") != "future_sandbox_influence_design_only":
        errors.append("proposed_future_memory_scope_not_future_sandbox_influence_design_only")
    if record.get("proposed_runtime_influence") != "blocked":
        errors.append("proposed_runtime_influence_not_blocked")
    if record.get("proposed_predictor_influence") != "blocked":
        errors.append("proposed_predictor_influence_not_blocked")
    requirements = record.get("required_before_any_memory_write")
    if not isinstance(requirements, list):
        errors.append("required_before_any_memory_write_not_list")
        requirements = []
    missing = sorted(set(REQUIRED_BEFORE_MEMORY_WRITE) - set(requirements))
    errors.extend(f"missing_required_before_memory_write:{item}" for item in missing)
    if record.get("repo_audit_acknowledged") is not True:
        errors.append("repo_audit_acknowledged_not_true")
    if record.get("qingyin_current_status") != QINGYIN_STATUS:
        errors.append("qingyin_current_status_not_phase0_trace_checker_system")
    if record.get("qingyin_self_authored_lesson_text") is not False:
        errors.append("qingyin_self_authored_lesson_text_not_false")
    if record.get("autonomous_learning_claim_allowed") is not False:
        errors.append("autonomous_learning_claim_allowed_not_false")
    for field in FALSE_PERMISSION_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if record.get("audit_recorded") is not True:
        errors.append("audit_recorded_not_true")
    if record.get("rollback_available") is not True:
        errors.append("rollback_available_not_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "approved_review_checked": record.get("source_review_decision") == APPROVED_REVIEW_DECISION,
        "bucket_signal_source_checked": record.get("source_signal_authorship") == "qingyin_bucket_derived_system_detected",
        "repo_audit_acknowledged": record.get("repo_audit_acknowledged") is True,
        "memory_write_blocked": record.get("memory_write_allowed") is False,
        "retained_jsonl_write_blocked": record.get("retained_jsonl_write_allowed") is False,
        "runtime_influence_blocked": record.get("runtime_influence_allowed") is False,
        "predictor_influence_blocked": record.get("predictor_influence_allowed") is False,
        "future_requirements_recorded": not missing and isinstance(record.get("required_before_any_memory_write"), list),
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_memory_readiness_design_for_approved_bucket_lesson_minimal_check() -> dict[str, Any]:
    valid = build_memory_readiness_design_for_approved_bucket_lesson()
    invalid = _invalid_records(valid)
    validations = [validate_memory_readiness_design_for_approved_bucket_lesson(record) for record in [valid] + invalid]
    valid_results = [result for result in validations if result["valid"]]
    summary = {
        "valid_memory_readiness_design_count": len(valid_results),
        "invalid_memory_readiness_design_count": len(validations) - len(valid_results),
        "approved_review_checked_count": sum(1 for result in valid_results if result["approved_review_checked"]),
        "bucket_signal_source_checked_count": sum(1 for result in valid_results if result["bucket_signal_source_checked"]),
        "repo_audit_acknowledged_count": sum(1 for result in valid_results if result["repo_audit_acknowledged"]),
        "memory_write_blocked_count": sum(1 for result in valid_results if result["memory_write_blocked"]),
        "retained_jsonl_write_blocked_count": sum(
            1 for result in valid_results if result["retained_jsonl_write_blocked"]
        ),
        "runtime_influence_blocked_count": sum(1 for result in valid_results if result["runtime_influence_blocked"]),
        "predictor_influence_blocked_count": sum(1 for result in valid_results if result["predictor_influence_blocked"]),
        "future_requirements_recorded_count": sum(
            1 for result in valid_results if result["future_requirements_recorded"]
        ),
        "proof_claim_blocked_count": sum(1 for result in valid_results if result["proof_claim_blocked"]),
    }
    summary["all_memory_readiness_design_for_approved_bucket_lesson_checks_passed"] = _all_checks_passed(summary)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_memory_readiness_design_for_approved_bucket_lesson_checks_passed"] else "failed",
        "valid_record": valid,
        "invalid_records": invalid,
        "validation_results": validations,
        "summary": summary,
        "boundary": {
            "boundary_change_required": False,
            "boundary_index_update_required": False,
            "boundary_index_version_before": BOUNDARY_VERSION,
            "boundary_index_version_after": BOUNDARY_VERSION,
            "rationale": (
                "This package records design-only readiness constraints without changing memory write "
                "permission, runtime influence, predictor influence, persistence, retention, or action-selection boundaries."
            ),
        },
        "safe_claim": (
            "ASHL Core can record memory-readiness design constraints for one approved human-interpreted, "
            "bucket-derived lesson candidate, while keeping memory admission, memory write, retained JSONL "
            "write, runtime influence, predictor mutation, action selection, production promotion, and "
            "proof-of-learning blocked."
        ),
    }


def _invalid_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    records = [
        _mutated(valid, ["source_review_decision"], "rejected"),
        _mutated(valid, ["source_review_decision"], "needs_more_evidence"),
        _mutated(valid, ["source_review_decision"], "needs_rewrite"),
        _mutated(valid, ["source_signal_authorship"], "manual_note"),
        _mutated(valid, ["interpretation_author_type"], "qingyin"),
        _mutated(valid, ["repo_audit_acknowledged"], False),
        _mutated(valid, ["memory_admission_status"], "admitted"),
        _mutated(valid, ["memory_write_status"], "written"),
        _mutated(valid, ["current_allowed_use"], "memory_write"),
        _mutated(valid, ["proposed_future_memory_form"], "Long-term Memory"),
        _mutated(valid, ["proposed_runtime_influence"], "allowed"),
        _mutated(valid, ["proposed_predictor_influence"], "allowed"),
        _mutated(valid, ["required_before_any_memory_write"], list(REQUIRED_BEFORE_MEMORY_WRITE[:-1])),
        _mutated(valid, ["qingyin_self_authored_lesson_text"], True),
        _mutated(valid, ["autonomous_learning_claim_allowed"], True),
        _mutated(valid, ["audit_recorded"], False),
        _mutated(valid, ["rollback_available"], False),
    ]
    for field in FALSE_PERMISSION_FIELDS:
        records.append(_mutated(valid, [field], True))
    return records


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["valid_memory_readiness_design_count"] == 1
        and summary["invalid_memory_readiness_design_count"] >= 1
        and summary["approved_review_checked_count"] == 1
        and summary["bucket_signal_source_checked_count"] == 1
        and summary["repo_audit_acknowledged_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["retained_jsonl_write_blocked_count"] == 1
        and summary["runtime_influence_blocked_count"] == 1
        and summary["predictor_influence_blocked_count"] == 1
        and summary["future_requirements_recorded_count"] == 1
        and summary["proof_claim_blocked_count"] == 1
    )


def _mutated(record: dict[str, Any], path: list[Any], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: Any = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(run_memory_readiness_design_for_approved_bucket_lesson_minimal_check(), indent=2))
