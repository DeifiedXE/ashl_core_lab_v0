"""Minimal candidate-layer memory admission for one reviewed lesson."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import (
    INTERPRETED_LESSON_TEXT,
    PLAIN_LANGUAGE_SUMMARY,
    QINGYIN_STATUS,
    REPEATED_KEY,
    build_human_interpreted_lesson_candidate_from_bucket_signal,
    build_human_interpretation_review_decision,
    validate_human_interpreted_lesson_candidate,
    validate_human_interpretation_review_decision,
)
from .memory_admission_approval_boundary_minimal import (
    APPROVED_DECISION,
    build_memory_admission_approval_record,
    validate_memory_admission_approval_record,
)
from .memory_admission_package_design_minimal import (
    build_memory_admission_package_design,
    validate_memory_admission_package_design,
)
from .memory_readiness_design_for_approved_bucket_lesson_minimal import (
    build_memory_readiness_design_for_approved_bucket_lesson,
    validate_memory_readiness_design_for_approved_bucket_lesson,
)


COMMAND = "run-memory-admission-minimal-check"
FLOW = "memory_admission_minimal_v0"
PACKAGE_ID = "PKG-Phase0-MemoryAdmission-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b75"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b76"
LESSON_NAME = "check_before_retry_when_risky_or_failed"
TARGET_FORM = "reviewed_lesson_memory_candidate"
MEMORY_LAYER_TARGET = "candidate_layer_only"
DISALLOWED_TARGET_FORMS = (
    "core_memory",
    "long_term_memory",
    "archive_memory",
    "working_memory_snapshot",
    "retained_jsonl",
    "runtime_policy",
    "predictor_parameter",
    "production_rule",
)
EVIDENCE_CHAIN = (
    "level3_toy_minefield_variant_suite_stability_review",
    "bucket_derived_lesson_candidate_signal",
    "human_interpreted_lesson_candidate_from_bucket_signal",
    "human_interpretation_review_decision",
    "memory_readiness_design_for_approved_bucket_lesson",
    "memory_admission_package_design",
    "memory_admission_approval",
)
FALSE_ADMISSION_FIELDS = (
    "long_term_memory_write_performed",
    "retained_jsonl_write_performed",
    "runtime_influence_enabled",
    "predictor_influence_enabled",
    "qingyin_self_authored_lesson_text",
    "autonomous_learning_claim_allowed",
    "proof_of_learning_claim_allowed",
    "memory_write_allowed",
    "long_term_memory_write_allowed",
    "retained_jsonl_write_allowed",
    "retention_write_allowed",
    "runtime_influence_allowed",
    "predictor_influence_allowed",
    "predictor_mutation_allowed",
    "production_behavior_change_allowed",
    "selected_action_allowed",
    "final_action_allowed",
)
FALSE_CANDIDATE_FIELDS = (
    "is_long_term_memory",
    "is_core_memory",
    "is_archive_memory",
    "writes_jsonl",
    "runtime_read_enabled",
    "predictor_read_enabled",
    "human_approved_for_memory_write",
    "human_approved_for_runtime_influence",
    "human_approved_for_predictor_influence",
)


def build_memory_admission_record(
    interpreted_candidate: dict[str, Any] | None = None,
    review_decision: dict[str, Any] | None = None,
    memory_readiness_design: dict[str, Any] | None = None,
    memory_admission_package_design: dict[str, Any] | None = None,
    memory_admission_approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidate = deepcopy(interpreted_candidate) if interpreted_candidate is not None else (
        build_human_interpreted_lesson_candidate_from_bucket_signal()
    )
    review = deepcopy(review_decision) if review_decision is not None else build_human_interpretation_review_decision(candidate)
    readiness = deepcopy(memory_readiness_design) if memory_readiness_design is not None else (
        build_memory_readiness_design_for_approved_bucket_lesson(review)
    )
    package_design = (
        deepcopy(memory_admission_package_design)
        if memory_admission_package_design is not None
        else build_memory_admission_package_design(readiness)
    )
    approval = (
        deepcopy(memory_admission_approval)
        if memory_admission_approval is not None
        else build_memory_admission_approval_record(package_design)
    )
    _raise_if_invalid_sources(candidate, review, readiness, package_design, approval)
    return {
        "record_type": "memory_admission",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "admission_status": "admitted_as_reviewed_lesson_memory_candidate",
        "admission_target_form": TARGET_FORM,
        "memory_layer_target": MEMORY_LAYER_TARGET,
        "long_term_memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "runtime_influence_enabled": False,
        "predictor_influence_enabled": False,
        "source_lesson_name": LESSON_NAME,
        "source_repeated_key": REPEATED_KEY,
        "source_candidate_type": "human_interpreted_bucket_derived_lesson_candidate",
        "source_signal_type": "bucket_derived_lesson_candidate_signal",
        "source_signal_authorship": "qingyin_bucket_derived_system_detected",
        "interpretation_author_type": "human_or_human_gpt_assisted",
        "qingyin_self_authored_lesson_text": False,
        "admitted_lesson_text": INTERPRETED_LESSON_TEXT,
        "plain_language_summary": PLAIN_LANGUAGE_SUMMARY,
        "approval_record_type": "memory_admission_approval",
        "approval_decision": APPROVED_DECISION,
        "approval_source": "explicit_user_statement",
        "approval_actor": "user",
        "approver_role": "project_owner",
        "evidence_chain": list(EVIDENCE_CHAIN),
        "current_allowed_use": "candidate_record_only",
        "future_allowed_use_requires_separate_package": True,
        "future_runtime_influence_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_long_term_memory_write_requires_separate_boundary": True,
        "future_retained_jsonl_write_requires_separate_boundary": True,
        "repo_audit_acknowledged": True,
        "qingyin_current_status": QINGYIN_STATUS,
        "autonomous_learning_claim_allowed": False,
        "proof_of_learning_claim_allowed": False,
        "memory_admission_performed": True,
        "memory_write_allowed": False,
        "long_term_memory_write_allowed": False,
        "retained_jsonl_write_allowed": False,
        "retention_write_allowed": False,
        "runtime_influence_allowed": False,
        "predictor_influence_allowed": False,
        "predictor_mutation_allowed": False,
        "production_behavior_change_allowed": False,
        "selected_action_allowed": False,
        "final_action_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "rollback_action": "invalidate_memory_admission_record_only",
        "rollback_auto_rebuilds_influence": False,
        "source_human_interpreted_lesson_candidate": candidate,
        "source_human_interpretation_review_decision": review,
        "source_memory_readiness_design": readiness,
        "source_memory_admission_package_design": package_design,
        "source_memory_admission_approval": approval,
    }


def build_reviewed_lesson_memory_candidate_record(
    admission_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    admission = deepcopy(admission_record) if admission_record is not None else build_memory_admission_record()
    if not validate_memory_admission_record(admission)["valid"]:
        raise ValueError("invalid_memory_admission_record")
    return {
        "record_type": "reviewed_lesson_memory_candidate",
        "record_version": "v0",
        "candidate_status": "admitted_candidate_not_long_term_memory",
        "lesson_name": admission.get("source_lesson_name"),
        "lesson_text": admission.get("admitted_lesson_text"),
        "source_admission_record_type": admission.get("record_type"),
        "source_admission_status": admission.get("admission_status"),
        "memory_layer": MEMORY_LAYER_TARGET,
        "is_long_term_memory": False,
        "is_core_memory": False,
        "is_archive_memory": False,
        "writes_jsonl": False,
        "runtime_read_enabled": False,
        "predictor_read_enabled": False,
        "human_reviewed": True,
        "human_approved_for_admission": True,
        "human_approved_for_memory_write": False,
        "human_approved_for_runtime_influence": False,
        "human_approved_for_predictor_influence": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_memory_admission": admission,
    }


def validate_memory_admission_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "memory_admission",
        "record_version": "v0",
        "admission_status": "admitted_as_reviewed_lesson_memory_candidate",
        "admission_target_form": TARGET_FORM,
        "memory_layer_target": MEMORY_LAYER_TARGET,
        "source_candidate_type": "human_interpreted_bucket_derived_lesson_candidate",
        "source_signal_type": "bucket_derived_lesson_candidate_signal",
        "source_signal_authorship": "qingyin_bucket_derived_system_detected",
        "interpretation_author_type": "human_or_human_gpt_assisted",
        "approval_record_type": "memory_admission_approval",
        "approval_decision": APPROVED_DECISION,
        "approval_source": "explicit_user_statement",
        "approval_actor": "user",
        "approver_role": "project_owner",
        "current_allowed_use": "candidate_record_only",
        "qingyin_current_status": QINGYIN_STATUS,
        "rollback_action": "invalidate_memory_admission_record_only",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if record.get("record_version") != "v0":
        errors.append("record_version_not_v0")
    if record.get("admission_target_form") in DISALLOWED_TARGET_FORMS:
        errors.append("admission_target_form_disallowed")
    if record.get("memory_layer_target") in ("long_term_memory", "core_memory"):
        errors.append("memory_layer_target_disallowed")
    for field in ("source_lesson_name", "source_repeated_key", "admitted_lesson_text", "plain_language_summary"):
        if not isinstance(record.get(field), str) or not record.get(field).strip():
            errors.append(f"{field}_empty")
    if record.get("source_lesson_name") != LESSON_NAME:
        errors.append("source_lesson_name_not_expected")
    if record.get("source_repeated_key") != REPEATED_KEY:
        errors.append("source_repeated_key_not_expected")
    if record.get("memory_admission_performed") is not True:
        errors.append("memory_admission_performed_not_true")
    for field in FALSE_ADMISSION_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in (
        "future_allowed_use_requires_separate_package",
        "future_runtime_influence_requires_separate_boundary",
        "future_predictor_influence_requires_separate_boundary",
        "future_long_term_memory_write_requires_separate_boundary",
        "future_retained_jsonl_write_requires_separate_boundary",
        "repo_audit_acknowledged",
        "audit_recorded",
        "rollback_available",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    if record.get("rollback_auto_rebuilds_influence") is not False:
        errors.append("rollback_auto_rebuilds_influence_not_false")
    evidence_chain = record.get("evidence_chain")
    if not isinstance(evidence_chain, list) or not set(EVIDENCE_CHAIN).issubset(set(evidence_chain)):
        errors.append("evidence_chain_incomplete")
    _validate_embedded_sources(record, errors)
    return {
        "valid": not errors,
        "error_codes": errors,
        "approval_checked": _approval_checked(record),
        "admission_performed": record.get("memory_admission_performed") is True,
        "long_term_memory_write_blocked": record.get("long_term_memory_write_allowed") is False
        and record.get("long_term_memory_write_performed") is False,
        "retained_jsonl_write_blocked": record.get("retained_jsonl_write_allowed") is False
        and record.get("retained_jsonl_write_performed") is False,
        "runtime_influence_blocked": record.get("runtime_influence_allowed") is False
        and record.get("runtime_influence_enabled") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_allowed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
        "rollback_available": record.get("rollback_available") is True,
    }


def validate_reviewed_lesson_memory_candidate_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "reviewed_lesson_memory_candidate",
        "record_version": "v0",
        "candidate_status": "admitted_candidate_not_long_term_memory",
        "source_admission_record_type": "memory_admission",
        "source_admission_status": "admitted_as_reviewed_lesson_memory_candidate",
        "memory_layer": MEMORY_LAYER_TARGET,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    for field in ("lesson_name", "lesson_text"):
        if not isinstance(record.get(field), str) or not record.get(field).strip():
            errors.append(f"{field}_empty")
    for field in FALSE_CANDIDATE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in ("human_reviewed", "human_approved_for_admission", "audit_recorded", "rollback_available"):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    source = record.get("source_memory_admission")
    if not isinstance(source, dict):
        errors.append("source_memory_admission_missing")
    elif not validate_memory_admission_record(source)["valid"]:
        errors.append("source_memory_admission_invalid")
    return {
        "valid": not errors,
        "error_codes": errors,
        "candidate_record_created": record.get("record_type") == "reviewed_lesson_memory_candidate",
        "long_term_memory_write_blocked": record.get("is_long_term_memory") is False,
        "retained_jsonl_write_blocked": record.get("writes_jsonl") is False,
        "runtime_influence_blocked": record.get("runtime_read_enabled") is False,
        "predictor_mutation_blocked": record.get("predictor_read_enabled") is False,
        "rollback_available": record.get("rollback_available") is True,
    }


def run_memory_admission_minimal_check() -> dict[str, Any]:
    valid_admission = build_memory_admission_record()
    valid_candidate = build_reviewed_lesson_memory_candidate_record(valid_admission)
    invalid_admissions = _invalid_admission_records(valid_admission)
    invalid_candidates = _invalid_candidate_records(valid_candidate)
    admission_validations = [
        validate_memory_admission_record(record) for record in [valid_admission] + invalid_admissions
    ]
    candidate_validations = [
        validate_reviewed_lesson_memory_candidate_record(record) for record in [valid_candidate] + invalid_candidates
    ]
    valid_admission_results = [result for result in admission_validations if result["valid"]]
    valid_candidate_results = [result for result in candidate_validations if result["valid"]]
    summary = {
        "valid_memory_admission_count": len(valid_admission_results),
        "invalid_memory_admission_count": len(admission_validations) - len(valid_admission_results),
        "valid_reviewed_lesson_memory_candidate_count": len(valid_candidate_results),
        "invalid_reviewed_lesson_memory_candidate_count": len(candidate_validations) - len(valid_candidate_results),
        "approval_checked_count": sum(1 for result in valid_admission_results if result["approval_checked"]),
        "admission_performed_count": sum(1 for result in valid_admission_results if result["admission_performed"]),
        "candidate_record_created_count": sum(
            1 for result in valid_candidate_results if result["candidate_record_created"]
        ),
        "long_term_memory_write_blocked_count": sum(
            1 for result in valid_admission_results if result["long_term_memory_write_blocked"]
        ),
        "retained_jsonl_write_blocked_count": sum(
            1 for result in valid_admission_results if result["retained_jsonl_write_blocked"]
        ),
        "runtime_influence_blocked_count": sum(
            1 for result in valid_admission_results if result["runtime_influence_blocked"]
        ),
        "predictor_mutation_blocked_count": sum(
            1 for result in valid_admission_results if result["predictor_mutation_blocked"]
        ),
        "proof_claim_blocked_count": sum(1 for result in valid_admission_results if result["proof_claim_blocked"]),
        "rollback_available_count": sum(1 for result in valid_admission_results if result["rollback_available"]),
    }
    summary["all_memory_admission_minimal_checks_passed"] = _all_checks_passed(summary)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_memory_admission_minimal_checks_passed"] else "failed",
        "valid_memory_admission_record": valid_admission,
        "valid_reviewed_lesson_memory_candidate_record": valid_candidate,
        "invalid_memory_admission_records": invalid_admissions,
        "invalid_reviewed_lesson_memory_candidate_records": invalid_candidates,
        "memory_admission_validation_results": admission_validations,
        "reviewed_lesson_memory_candidate_validation_results": candidate_validations,
        "summary": summary,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package opens the minimal memory admission boundary for reviewed_lesson_memory_candidate "
                "records, while Long-term Memory write, retained JSONL write, runtime influence, predictor "
                "mutation, action selection, production promotion, and proof-of-learning remain blocked."
            ),
        },
        "safe_claim": (
            "ASHL Core can admit one approved human-interpreted, bucket-derived lesson as a "
            "reviewed_lesson_memory_candidate in the candidate layer, while keeping Long-term Memory write, "
            "retained JSONL write, runtime influence, predictor mutation, action selection, production "
            "promotion, and proof-of-learning blocked."
        ),
    }


def _raise_if_invalid_sources(
    candidate: dict[str, Any],
    review: dict[str, Any],
    readiness: dict[str, Any],
    package_design: dict[str, Any],
    approval: dict[str, Any],
) -> None:
    if not validate_human_interpreted_lesson_candidate(candidate)["valid"]:
        raise ValueError("invalid_human_interpreted_lesson_candidate")
    if not validate_human_interpretation_review_decision(review)["valid"]:
        raise ValueError("invalid_human_interpretation_review_decision")
    if review.get("review_decision") != "approved_for_future_memory_readiness_design_only":
        raise ValueError("review_decision_not_approved_for_memory_readiness")
    if not validate_memory_readiness_design_for_approved_bucket_lesson(readiness)["valid"]:
        raise ValueError("invalid_memory_readiness_design")
    if not validate_memory_admission_package_design(package_design)["valid"]:
        raise ValueError("invalid_memory_admission_package_design")
    if not validate_memory_admission_approval_record(approval)["valid"]:
        raise ValueError("invalid_memory_admission_approval")
    if approval.get("approval_decision") != APPROVED_DECISION:
        raise ValueError("memory_admission_approval_not_approved")
    if approval.get("future_memory_admission_package_may_proceed") is not True:
        raise ValueError("memory_admission_approval_may_not_proceed")


def _validate_embedded_sources(record: dict[str, Any], errors: list[str]) -> None:
    sources = [
        (
            "source_human_interpreted_lesson_candidate",
            validate_human_interpreted_lesson_candidate,
            "source_human_interpreted_lesson_candidate_invalid",
        ),
        (
            "source_human_interpretation_review_decision",
            validate_human_interpretation_review_decision,
            "source_human_interpretation_review_decision_invalid",
        ),
        (
            "source_memory_readiness_design",
            validate_memory_readiness_design_for_approved_bucket_lesson,
            "source_memory_readiness_design_invalid",
        ),
        (
            "source_memory_admission_package_design",
            validate_memory_admission_package_design,
            "source_memory_admission_package_design_invalid",
        ),
        (
            "source_memory_admission_approval",
            validate_memory_admission_approval_record,
            "source_memory_admission_approval_invalid",
        ),
    ]
    for field, validator, error in sources:
        source = record.get(field)
        if not isinstance(source, dict):
            errors.append(f"{field}_missing")
        elif not validator(source)["valid"]:
            errors.append(error)
    approval = record.get("source_memory_admission_approval")
    if isinstance(approval, dict):
        if approval.get("approval_decision") != APPROVED_DECISION:
            errors.append("source_memory_admission_approval_not_approved")
        if approval.get("future_memory_admission_package_may_proceed") is not True:
            errors.append("source_memory_admission_approval_may_not_proceed")


def _approval_checked(record: dict[str, Any]) -> bool:
    approval = record.get("source_memory_admission_approval")
    return (
        isinstance(approval, dict)
        and approval.get("record_type") == "memory_admission_approval"
        and approval.get("approval_decision") == APPROVED_DECISION
        and approval.get("future_memory_admission_package_may_proceed") is True
        and approval.get("approval_source") == "explicit_user_statement"
        and approval.get("approval_actor") == "user"
        and approval.get("approver_role") == "project_owner"
        and bool(approval.get("approval_text"))
        and approval.get("memory_write_allowed") is False
        and approval.get("retained_jsonl_write_allowed") is False
        and approval.get("runtime_influence_allowed") is False
        and approval.get("predictor_mutation_allowed") is False
        and approval.get("proof_of_learning_claim_allowed") is False
    )


def _invalid_admission_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalid = [
        _without(valid, "source_memory_admission_approval"),
        _mutated(valid, ["source_memory_admission_approval", "approval_decision"], "rejected_for_memory_admission"),
        _mutated(valid, ["source_memory_admission_approval", "approval_decision"], "needs_more_evidence_before_memory_admission"),
        _mutated(valid, ["source_memory_admission_approval", "approval_decision"], "needs_rewrite_before_memory_admission"),
        _without(valid, "source_memory_admission_package_design"),
        _mutated(valid, ["admission_target_form"], "long_term_memory"),
        _mutated(valid, ["admission_target_form"], "core_memory"),
        _mutated(valid, ["memory_layer_target"], "long_term_memory"),
        _mutated(valid, ["memory_layer_target"], "core_memory"),
        _mutated(valid, ["rollback_available"], False),
        _mutated(valid, ["rollback_auto_rebuilds_influence"], True),
    ]
    for field in FALSE_ADMISSION_FIELDS:
        invalid.append(_mutated(valid, [field], True))
    return invalid


def _invalid_candidate_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalid = [
        _without(valid, "source_memory_admission"),
        _mutated(valid, ["source_memory_admission", "long_term_memory_write_performed"], True),
        _mutated(valid, ["candidate_status"], "long_term_memory"),
        _mutated(valid, ["memory_layer"], "long_term_memory"),
        _mutated(valid, ["human_reviewed"], False),
        _mutated(valid, ["human_approved_for_admission"], False),
        _mutated(valid, ["rollback_available"], False),
    ]
    for field in FALSE_CANDIDATE_FIELDS:
        invalid.append(_mutated(valid, [field], True))
    return invalid


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["valid_memory_admission_count"] == 1
        and summary["invalid_memory_admission_count"] >= 1
        and summary["valid_reviewed_lesson_memory_candidate_count"] == 1
        and summary["invalid_reviewed_lesson_memory_candidate_count"] >= 1
        and summary["approval_checked_count"] == 1
        and summary["admission_performed_count"] == 1
        and summary["candidate_record_created_count"] == 1
        and summary["long_term_memory_write_blocked_count"] == 1
        and summary["retained_jsonl_write_blocked_count"] == 1
        and summary["runtime_influence_blocked_count"] == 1
        and summary["predictor_mutation_blocked_count"] == 1
        and summary["proof_claim_blocked_count"] == 1
        and summary["rollback_available_count"] == 1
    )


def _without(record: dict[str, Any], key: str) -> dict[str, Any]:
    clone = deepcopy(record)
    clone.pop(key, None)
    return clone


def _mutated(record: dict[str, Any], path: list[Any], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: Any = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(run_memory_admission_minimal_check(), indent=2))
