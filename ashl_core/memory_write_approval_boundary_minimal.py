"""Explicit approval boundary for future memory write packages."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS, REPEATED_KEY
from .memory_admission_minimal import (
    LESSON_NAME,
    build_memory_admission_record,
    build_reviewed_lesson_memory_candidate_record,
    validate_memory_admission_record,
    validate_reviewed_lesson_memory_candidate_record,
)


COMMAND = "run-memory-write-approval-boundary-minimal-check"
FLOW = "memory_write_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-MemoryWriteApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b76"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b77"
APPROVED_DECISION = "approved_for_future_memory_write_package"
BLOCKED_DECISIONS = (
    "rejected_for_memory_write",
    "needs_more_evidence_before_memory_write",
    "needs_retention_rule_before_memory_write",
    "needs_rollback_rule_before_memory_write",
    "needs_rewrite_before_memory_write",
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
    "memory_write_performed",
    "long_term_memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "runtime_influence_allowed",
    "predictor_influence_allowed",
    "predictor_mutation_allowed",
    "production_behavior_change_allowed",
    "selected_action_allowed",
    "final_action_allowed",
    "proof_of_learning_claim_allowed",
)


def build_memory_write_approval_record(
    source_admission: dict[str, Any] | None = None,
    source_candidate: dict[str, Any] | None = None,
    approval_decision: str = APPROVED_DECISION,
) -> dict[str, Any]:
    admission = deepcopy(source_admission) if source_admission is not None else build_memory_admission_record()
    candidate = (
        deepcopy(source_candidate)
        if source_candidate is not None
        else build_reviewed_lesson_memory_candidate_record(admission)
    )
    if not validate_memory_admission_record(admission)["valid"]:
        raise ValueError("invalid_memory_admission_source")
    if not validate_reviewed_lesson_memory_candidate_record(candidate)["valid"]:
        raise ValueError("invalid_reviewed_lesson_memory_candidate_source")
    if approval_decision not in ALLOWED_DECISIONS:
        raise ValueError("invalid_approval_decision")
    may_proceed = approval_decision == APPROVED_DECISION
    return {
        "record_type": "memory_write_approval",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "source_admission_record_type": admission.get("record_type"),
        "source_admission_status": admission.get("admission_status"),
        "source_candidate_record_type": candidate.get("record_type"),
        "source_candidate_status": candidate.get("candidate_status"),
        "target_lesson_name": admission.get("source_lesson_name") or LESSON_NAME,
        "target_repeated_key": admission.get("source_repeated_key") or REPEATED_KEY,
        "target_candidate_source": "human_interpreted_bucket_derived_lesson_candidate",
        "approval_decision": approval_decision,
        "approval_purpose": "future_memory_write_package_only",
        "approval_source": "explicit_user_statement",
        "approval_actor": "user",
        "approver_role": "project_owner",
        "approval_text": (
            "I approve proceeding to a future memory write package for the reviewed lesson memory candidate "
            "check_before_retry_when_risky_or_failed, while not approving runtime influence, predictor mutation, "
            "selected_action, final_action, production behavior, or proof-of-learning."
        ),
        "codex_self_approval_allowed": False,
        "ai_self_approval_allowed": False,
        "fixture_approval_is_real_approval": False,
        "task_queue_status_is_approval": False,
        "passing_tests_are_approval": False,
        "implicit_chat_command_is_approval": False,
        "future_memory_write_package_may_proceed": may_proceed,
        "memory_write_performed": False,
        "long_term_memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "runtime_influence_allowed": False,
        "predictor_influence_allowed": False,
        "predictor_mutation_allowed": False,
        "production_behavior_change_allowed": False,
        "selected_action_allowed": False,
        "final_action_allowed": False,
        "proof_of_learning_claim_allowed": False,
        "requires_separate_future_memory_write_package": True,
        "requires_explicit_target_layer_selection": True,
        "requires_retention_rule": True,
        "requires_rollback_rule": True,
        "requires_cross_session_influence_rule": True,
        "requires_separate_runtime_influence_boundary": True,
        "requires_separate_predictor_influence_boundary": True,
        "repo_audit_acknowledged": True,
        "qingyin_current_status": QINGYIN_STATUS,
        "qingyin_self_authored_lesson_text": False,
        "autonomous_learning_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_memory_admission": admission,
        "source_reviewed_lesson_memory_candidate": candidate,
    }


def validate_memory_write_approval_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "memory_write_approval",
        "record_version": "v0",
        "source_admission_record_type": "memory_admission",
        "source_admission_status": "admitted_as_reviewed_lesson_memory_candidate",
        "source_candidate_record_type": "reviewed_lesson_memory_candidate",
        "source_candidate_status": "admitted_candidate_not_long_term_memory",
        "target_candidate_source": "human_interpreted_bucket_derived_lesson_candidate",
        "approval_purpose": "future_memory_write_package_only",
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
        if record.get("future_memory_write_package_may_proceed") is not True:
            errors.append("approved_decision_may_proceed_not_true")
    elif record.get("future_memory_write_package_may_proceed") is not False:
        errors.append("blocked_decision_may_proceed_not_false")
    admission = record.get("source_memory_admission")
    if not isinstance(admission, dict):
        errors.append("source_memory_admission_missing")
    elif not validate_memory_admission_record(admission)["valid"]:
        errors.append("source_memory_admission_invalid")
    candidate = record.get("source_reviewed_lesson_memory_candidate")
    if not isinstance(candidate, dict):
        errors.append("source_reviewed_lesson_memory_candidate_missing")
    elif not validate_reviewed_lesson_memory_candidate_record(candidate)["valid"]:
        errors.append("source_reviewed_lesson_memory_candidate_invalid")
    for field in FALSE_APPROVAL_SOURCE_FIELDS + FALSE_PERMISSION_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in (
        "requires_separate_future_memory_write_package",
        "requires_explicit_target_layer_selection",
        "requires_retention_rule",
        "requires_rollback_rule",
        "requires_cross_session_influence_rule",
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
        and record.get("future_memory_write_package_may_proceed") is True,
        "blocked_decision_checked": decision in BLOCKED_DECISIONS
        and record.get("future_memory_write_package_may_proceed") is False,
        "explicit_user_statement_checked": record.get("approval_source") == "explicit_user_statement",
        "project_owner_checked": record.get("approver_role") == "project_owner",
        "source_admission_checked": isinstance(admission, dict)
        and validate_memory_admission_record(admission)["valid"],
        "source_candidate_checked": isinstance(candidate, dict)
        and validate_reviewed_lesson_memory_candidate_record(candidate)["valid"],
        "codex_self_approval_blocked": record.get("codex_self_approval_allowed") is False,
        "ai_self_approval_blocked": record.get("ai_self_approval_allowed") is False,
        "fixture_approval_blocked": record.get("fixture_approval_is_real_approval") is False,
        "task_queue_approval_blocked": record.get("task_queue_status_is_approval") is False,
        "passing_tests_approval_blocked": record.get("passing_tests_are_approval") is False,
        "memory_write_performed_blocked": record.get("memory_write_performed") is False,
        "long_term_memory_write_blocked": record.get("long_term_memory_write_performed") is False,
        "retained_jsonl_write_blocked": record.get("retained_jsonl_write_performed") is False,
        "retention_write_blocked": record.get("retention_write_performed") is False,
        "runtime_influence_blocked": record.get("runtime_influence_allowed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_allowed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_memory_write_approval_boundary_minimal_check() -> dict[str, Any]:
    valid_records = [build_memory_write_approval_record(approval_decision=decision) for decision in ALLOWED_DECISIONS]
    invalid_records = _invalid_records(valid_records[0])
    validations = [validate_memory_write_approval_record(record) for record in valid_records + invalid_records]
    valid_results = [result for result in validations if result["valid"]]
    summary = {
        "valid_approval_count": len(valid_results),
        "invalid_approval_count": len(validations) - len(valid_results),
        "approved_decision_checked_count": sum(1 for result in valid_results if result["approved_decision_checked"]),
        "blocked_decision_checked_count": sum(1 for result in valid_results if result["blocked_decision_checked"]),
        "explicit_user_statement_checked_count": sum(1 for result in valid_results if result["explicit_user_statement_checked"]),
        "project_owner_checked_count": sum(1 for result in valid_results if result["project_owner_checked"]),
        "source_admission_checked_count": sum(1 for result in valid_results if result["source_admission_checked"]),
        "source_candidate_checked_count": sum(1 for result in valid_results if result["source_candidate_checked"]),
        "codex_self_approval_blocked_count": sum(1 for result in valid_results if result["codex_self_approval_blocked"]),
        "ai_self_approval_blocked_count": sum(1 for result in valid_results if result["ai_self_approval_blocked"]),
        "fixture_approval_blocked_count": sum(1 for result in valid_results if result["fixture_approval_blocked"]),
        "task_queue_approval_blocked_count": sum(1 for result in valid_results if result["task_queue_approval_blocked"]),
        "passing_tests_approval_blocked_count": sum(1 for result in valid_results if result["passing_tests_approval_blocked"]),
        "memory_write_performed_blocked_count": sum(1 for result in valid_results if result["memory_write_performed_blocked"]),
        "long_term_memory_write_blocked_count": sum(1 for result in valid_results if result["long_term_memory_write_blocked"]),
        "retained_jsonl_write_blocked_count": sum(1 for result in valid_results if result["retained_jsonl_write_blocked"]),
        "retention_write_blocked_count": sum(1 for result in valid_results if result["retention_write_blocked"]),
        "runtime_influence_blocked_count": sum(1 for result in valid_results if result["runtime_influence_blocked"]),
        "predictor_mutation_blocked_count": sum(1 for result in valid_results if result["predictor_mutation_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid_results if result["proof_claim_blocked"]),
    }
    summary["all_memory_write_approval_boundary_checks_passed"] = _all_checks_passed(summary)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_memory_write_approval_boundary_checks_passed"] else "failed",
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
                "This package introduces an explicit human approval validation boundary for future memory write "
                "packages, while memory write, retained JSONL write, runtime influence, predictor mutation, action "
                "selection, production promotion, and proof-of-learning remain blocked."
            ),
        },
        "safe_claim": (
            "ASHL Core can validate explicit human approval to proceed with a future memory write package for one "
            "reviewed_lesson_memory_candidate, while keeping memory write, retained JSONL write, runtime influence, "
            "predictor mutation, action selection, production promotion, and proof-of-learning blocked."
        ),
    }


def _invalid_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalid = [
        _without(valid, "source_memory_admission"),
        _mutated(valid, ["source_memory_admission", "long_term_memory_write_performed"], True),
        _without(valid, "source_reviewed_lesson_memory_candidate"),
        _mutated(valid, ["source_reviewed_lesson_memory_candidate", "writes_jsonl"], True),
        _mutated(valid, ["approval_source"], "task_queue"),
        _mutated(valid, ["approval_actor"], "codex"),
        _mutated(valid, ["approver_role"], "assistant"),
        _mutated(valid, ["approval_text"], ""),
        _mutated(valid, ["approval_decision"], "write_memory_now"),
        _mutated(valid, ["future_memory_write_package_may_proceed"], False),
        _mutated(build_memory_write_approval_record(approval_decision="rejected_for_memory_write"), ["future_memory_write_package_may_proceed"], True),
        _mutated(build_memory_write_approval_record(approval_decision="needs_more_evidence_before_memory_write"), ["future_memory_write_package_may_proceed"], True),
        _mutated(build_memory_write_approval_record(approval_decision="needs_retention_rule_before_memory_write"), ["future_memory_write_package_may_proceed"], True),
        _mutated(build_memory_write_approval_record(approval_decision="needs_rollback_rule_before_memory_write"), ["future_memory_write_package_may_proceed"], True),
        _mutated(build_memory_write_approval_record(approval_decision="needs_rewrite_before_memory_write"), ["future_memory_write_package_may_proceed"], True),
        _mutated(valid, ["requires_separate_future_memory_write_package"], False),
        _mutated(valid, ["requires_explicit_target_layer_selection"], False),
        _mutated(valid, ["requires_retention_rule"], False),
        _mutated(valid, ["requires_rollback_rule"], False),
        _mutated(valid, ["requires_cross_session_influence_rule"], False),
        _mutated(valid, ["requires_separate_runtime_influence_boundary"], False),
        _mutated(valid, ["requires_separate_predictor_influence_boundary"], False),
        _mutated(valid, ["repo_audit_acknowledged"], False),
        _mutated(valid, ["qingyin_self_authored_lesson_text"], True),
        _mutated(valid, ["autonomous_learning_claim_allowed"], True),
        _mutated(valid, ["audit_recorded"], False),
        _mutated(valid, ["rollback_available"], False),
    ]
    for field in FALSE_APPROVAL_SOURCE_FIELDS + FALSE_PERMISSION_FIELDS:
        invalid.append(_mutated(valid, [field], True))
    return invalid


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["valid_approval_count"] == 6
        and summary["invalid_approval_count"] >= 1
        and summary["approved_decision_checked_count"] == 1
        and summary["blocked_decision_checked_count"] == 5
        and summary["explicit_user_statement_checked_count"] == 6
        and summary["project_owner_checked_count"] == 6
        and summary["source_admission_checked_count"] == 6
        and summary["source_candidate_checked_count"] == 6
        and summary["codex_self_approval_blocked_count"] == 6
        and summary["ai_self_approval_blocked_count"] == 6
        and summary["fixture_approval_blocked_count"] == 6
        and summary["task_queue_approval_blocked_count"] == 6
        and summary["passing_tests_approval_blocked_count"] == 6
        and summary["memory_write_performed_blocked_count"] == 6
        and summary["long_term_memory_write_blocked_count"] == 6
        and summary["retained_jsonl_write_blocked_count"] == 6
        and summary["retention_write_blocked_count"] == 6
        and summary["runtime_influence_blocked_count"] == 6
        and summary["predictor_mutation_blocked_count"] == 6
        and summary["proof_claim_blocked_count"] == 6
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

    print(json.dumps(run_memory_write_approval_boundary_minimal_check(), indent=2))
