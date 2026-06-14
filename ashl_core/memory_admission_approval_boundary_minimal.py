"""Explicit approval boundary for future memory admission packages."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS, REPEATED_KEY
from .memory_admission_package_design_minimal import (
    build_memory_admission_package_design,
    validate_memory_admission_package_design,
)


COMMAND = "run-memory-admission-approval-boundary-minimal-check"
FLOW = "memory_admission_approval_boundary_minimal_v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b74"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b75"
PACKAGE_ID = "PKG-Phase0-MemoryAdmissionApprovalBoundary-Minimal-v0"
LESSON_NAME = "check_before_retry_when_risky_or_failed"
TARGET_CANDIDATE_SOURCE = "human_interpreted_bucket_derived_lesson_candidate"
APPROVED_DECISION = "approved_for_future_memory_admission_package"
BLOCKED_DECISIONS = (
    "rejected_for_memory_admission",
    "needs_more_evidence_before_memory_admission",
    "needs_rewrite_before_memory_admission",
)
ALLOWED_DECISIONS = (APPROVED_DECISION,) + BLOCKED_DECISIONS
FALSE_APPROVAL_SOURCE_FIELDS = (
    "codex_self_approval_allowed",
    "ai_self_approval_allowed",
    "fixture_approval_is_real_approval",
    "task_queue_status_is_approval",
    "passing_tests_are_approval",
    "implicit_chat_command_is_approval",
)
FALSE_PERMISSION_FIELDS = (
    "memory_admission_performed",
    "memory_write_allowed",
    "retained_jsonl_write_allowed",
    "retention_write_allowed",
    "runtime_influence_allowed",
    "predictor_influence_allowed",
    "predictor_mutation_allowed",
    "production_behavior_change_allowed",
    "selected_action_allowed",
    "final_action_allowed",
    "proof_of_learning_claim_allowed",
)


def build_memory_admission_approval_record(
    source_design: dict[str, Any] | None = None,
    approval_decision: str = APPROVED_DECISION,
) -> dict[str, Any]:
    source = deepcopy(source_design) if source_design is not None else build_memory_admission_package_design()
    source_validation = validate_memory_admission_package_design(source)
    if not source_validation["valid"]:
        raise ValueError("invalid_memory_admission_package_design_source")
    if approval_decision not in ALLOWED_DECISIONS:
        raise ValueError("invalid_approval_decision")
    may_proceed = approval_decision == APPROVED_DECISION
    return {
        "record_type": "memory_admission_approval",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "source_design_record_type": source.get("record_type"),
        "source_design_status": source.get("design_status"),
        "target_lesson_name": source.get("source_lesson_name") or LESSON_NAME,
        "target_repeated_key": source.get("source_repeated_key") or REPEATED_KEY,
        "target_candidate_source": TARGET_CANDIDATE_SOURCE,
        "approval_decision": approval_decision,
        "approval_purpose": "future_memory_admission_package_only",
        "approval_source": "explicit_user_statement",
        "approval_actor": "user",
        "approver_role": "project_owner",
        "approval_text": (
            "I approve proceeding with a future memory admission package for this reviewed "
            "bucket-derived lesson candidate, without approving memory write, retained JSONL write, "
            "runtime influence, predictor mutation, production behavior, or proof-of-learning."
        ),
        "codex_self_approval_allowed": False,
        "ai_self_approval_allowed": False,
        "fixture_approval_is_real_approval": False,
        "task_queue_status_is_approval": False,
        "passing_tests_are_approval": False,
        "implicit_chat_command_is_approval": False,
        "future_memory_admission_package_may_proceed": may_proceed,
        "memory_admission_performed": False,
        "memory_write_allowed": False,
        "retained_jsonl_write_allowed": False,
        "retention_write_allowed": False,
        "runtime_influence_allowed": False,
        "predictor_influence_allowed": False,
        "predictor_mutation_allowed": False,
        "production_behavior_change_allowed": False,
        "selected_action_allowed": False,
        "final_action_allowed": False,
        "proof_of_learning_claim_allowed": False,
        "requires_separate_future_memory_admission_package": True,
        "requires_separate_future_memory_write_boundary": True,
        "requires_separate_runtime_influence_boundary": True,
        "requires_separate_predictor_influence_boundary": True,
        "repo_audit_acknowledged": True,
        "qingyin_current_status": QINGYIN_STATUS,
        "qingyin_self_authored_lesson_text": False,
        "autonomous_learning_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_memory_admission_package_design": source,
    }


def validate_memory_admission_approval_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "memory_admission_approval":
        errors.append("record_type_not_memory_admission_approval")
    if record.get("record_version") != "v0":
        errors.append("record_version_not_v0")
    source = record.get("source_memory_admission_package_design")
    if not isinstance(source, dict):
        errors.append("source_memory_admission_package_design_missing")
    elif not validate_memory_admission_package_design(source)["valid"]:
        errors.append("source_memory_admission_package_design_invalid")
    expected = {
        "source_design_record_type": "memory_admission_package_design",
        "source_design_status": "future_memory_admission_package_design_recorded",
        "target_candidate_source": TARGET_CANDIDATE_SOURCE,
        "approval_purpose": "future_memory_admission_package_only",
        "approval_source": "explicit_user_statement",
        "approval_actor": "user",
        "approver_role": "project_owner",
        "qingyin_current_status": QINGYIN_STATUS,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    for field in ("target_lesson_name", "target_repeated_key", "approval_text"):
        if not isinstance(record.get(field), str) or not record.get(field).strip():
            errors.append(f"{field}_empty")
    decision = record.get("approval_decision")
    if decision not in ALLOWED_DECISIONS:
        errors.append("approval_decision_not_allowed")
    elif decision == APPROVED_DECISION:
        if record.get("future_memory_admission_package_may_proceed") is not True:
            errors.append("approved_decision_may_proceed_not_true")
    elif record.get("future_memory_admission_package_may_proceed") is not False:
        errors.append("blocked_decision_may_proceed_not_false")
    for field in FALSE_APPROVAL_SOURCE_FIELDS + FALSE_PERMISSION_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in (
        "requires_separate_future_memory_admission_package",
        "requires_separate_future_memory_write_boundary",
        "requires_separate_runtime_influence_boundary",
        "requires_separate_predictor_influence_boundary",
        "repo_audit_acknowledged",
        "audit_recorded",
        "rollback_available",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    if record.get("qingyin_self_authored_lesson_text") is not False:
        errors.append("qingyin_self_authored_lesson_text_not_false")
    if record.get("autonomous_learning_claim_allowed") is not False:
        errors.append("autonomous_learning_claim_allowed_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "approved_decision_checked": decision == APPROVED_DECISION
        and record.get("future_memory_admission_package_may_proceed") is True,
        "blocked_decision_checked": decision in BLOCKED_DECISIONS
        and record.get("future_memory_admission_package_may_proceed") is False,
        "explicit_user_statement_checked": record.get("approval_source") == "explicit_user_statement",
        "project_owner_checked": record.get("approver_role") == "project_owner",
        "codex_self_approval_blocked": record.get("codex_self_approval_allowed") is False,
        "ai_self_approval_blocked": record.get("ai_self_approval_allowed") is False,
        "fixture_approval_blocked": record.get("fixture_approval_is_real_approval") is False,
        "task_queue_approval_blocked": record.get("task_queue_status_is_approval") is False,
        "passing_tests_approval_blocked": record.get("passing_tests_are_approval") is False,
        "memory_admission_performed_blocked": record.get("memory_admission_performed") is False,
        "memory_write_blocked": record.get("memory_write_allowed") is False,
        "retained_jsonl_write_blocked": record.get("retained_jsonl_write_allowed") is False,
        "runtime_influence_blocked": record.get("runtime_influence_allowed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_allowed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_memory_admission_approval_boundary_minimal_check() -> dict[str, Any]:
    valid_records = [build_memory_admission_approval_record(approval_decision=decision) for decision in ALLOWED_DECISIONS]
    invalid_records = _invalid_records(valid_records[0])
    validations = [validate_memory_admission_approval_record(record) for record in valid_records + invalid_records]
    valid_results = [result for result in validations if result["valid"]]
    summary = {
        "valid_approval_count": len(valid_results),
        "invalid_approval_count": len(validations) - len(valid_results),
        "approved_decision_checked_count": sum(1 for result in valid_results if result["approved_decision_checked"]),
        "blocked_decision_checked_count": sum(1 for result in valid_results if result["blocked_decision_checked"]),
        "explicit_user_statement_checked_count": sum(
            1 for result in valid_results if result["explicit_user_statement_checked"]
        ),
        "project_owner_checked_count": sum(1 for result in valid_results if result["project_owner_checked"]),
        "codex_self_approval_blocked_count": sum(
            1 for result in valid_results if result["codex_self_approval_blocked"]
        ),
        "ai_self_approval_blocked_count": sum(1 for result in valid_results if result["ai_self_approval_blocked"]),
        "fixture_approval_blocked_count": sum(1 for result in valid_results if result["fixture_approval_blocked"]),
        "task_queue_approval_blocked_count": sum(
            1 for result in valid_results if result["task_queue_approval_blocked"]
        ),
        "passing_tests_approval_blocked_count": sum(
            1 for result in valid_results if result["passing_tests_approval_blocked"]
        ),
        "memory_admission_performed_blocked_count": sum(
            1 for result in valid_results if result["memory_admission_performed_blocked"]
        ),
        "memory_write_blocked_count": sum(1 for result in valid_results if result["memory_write_blocked"]),
        "retained_jsonl_write_blocked_count": sum(
            1 for result in valid_results if result["retained_jsonl_write_blocked"]
        ),
        "runtime_influence_blocked_count": sum(1 for result in valid_results if result["runtime_influence_blocked"]),
        "predictor_mutation_blocked_count": sum(
            1 for result in valid_results if result["predictor_mutation_blocked"]
        ),
        "proof_claim_blocked_count": sum(1 for result in valid_results if result["proof_claim_blocked"]),
    }
    summary["all_memory_admission_approval_boundary_checks_passed"] = _all_checks_passed(summary)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_memory_admission_approval_boundary_checks_passed"] else "failed",
        "valid_record": valid_records[0],
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "validation_results": validations,
        "summary": summary,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package introduces an explicit human approval validation boundary for future memory "
                "admission packages, while memory admission, memory write, retained JSONL write, runtime "
                "influence, predictor mutation, action selection, production promotion, and proof-of-learning "
                "remain blocked."
            ),
        },
        "safe_claim": (
            "ASHL Core can validate explicit human approval to proceed with a future memory admission package "
            "for one approved human-interpreted, bucket-derived lesson candidate, while keeping memory admission, "
            "memory write, retained JSONL write, runtime influence, predictor mutation, action selection, "
            "production promotion, and proof-of-learning blocked."
        ),
    }


def _invalid_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    records = [
        _without(valid, "source_memory_admission_package_design"),
        _mutated(valid, ["source_memory_admission_package_design", "memory_write_allowed"], True),
        _mutated(valid, ["approval_source"], "codex_report"),
        _mutated(valid, ["approval_actor"], "codex"),
        _mutated(valid, ["approver_role"], "assistant"),
        _mutated(valid, ["approval_text"], ""),
        _mutated(valid, ["target_candidate_source"], "other"),
        _mutated(valid, ["approval_decision"], "write_memory"),
        _mutated(valid, ["future_memory_admission_package_may_proceed"], False),
        _mutated(build_memory_admission_approval_record(approval_decision="rejected_for_memory_admission"), ["future_memory_admission_package_may_proceed"], True),
        _mutated(build_memory_admission_approval_record(approval_decision="needs_more_evidence_before_memory_admission"), ["future_memory_admission_package_may_proceed"], True),
        _mutated(build_memory_admission_approval_record(approval_decision="needs_rewrite_before_memory_admission"), ["future_memory_admission_package_may_proceed"], True),
        _mutated(valid, ["requires_separate_future_memory_admission_package"], False),
        _mutated(valid, ["requires_separate_future_memory_write_boundary"], False),
        _mutated(valid, ["requires_separate_runtime_influence_boundary"], False),
        _mutated(valid, ["requires_separate_predictor_influence_boundary"], False),
        _mutated(valid, ["repo_audit_acknowledged"], False),
        _mutated(valid, ["qingyin_self_authored_lesson_text"], True),
        _mutated(valid, ["autonomous_learning_claim_allowed"], True),
        _mutated(valid, ["audit_recorded"], False),
        _mutated(valid, ["rollback_available"], False),
    ]
    for field in FALSE_APPROVAL_SOURCE_FIELDS + FALSE_PERMISSION_FIELDS:
        records.append(_mutated(valid, [field], True))
    return records


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["valid_approval_count"] == 4
        and summary["invalid_approval_count"] >= 1
        and summary["approved_decision_checked_count"] == 1
        and summary["blocked_decision_checked_count"] == 3
        and summary["explicit_user_statement_checked_count"] == 4
        and summary["project_owner_checked_count"] == 4
        and summary["codex_self_approval_blocked_count"] == 4
        and summary["ai_self_approval_blocked_count"] == 4
        and summary["fixture_approval_blocked_count"] == 4
        and summary["task_queue_approval_blocked_count"] == 4
        and summary["passing_tests_approval_blocked_count"] == 4
        and summary["memory_admission_performed_blocked_count"] == 4
        and summary["memory_write_blocked_count"] == 4
        and summary["retained_jsonl_write_blocked_count"] == 4
        and summary["runtime_influence_blocked_count"] == 4
        and summary["predictor_mutation_blocked_count"] == 4
        and summary["proof_claim_blocked_count"] == 4
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

    print(json.dumps(run_memory_admission_approval_boundary_minimal_check(), indent=2))
