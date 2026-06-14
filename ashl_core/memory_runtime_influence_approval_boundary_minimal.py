"""Explicit approval boundary for future memory runtime influence packages."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS, REPEATED_KEY
from .memory_admission_minimal import LESSON_NAME
from .memory_influence_preview_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as SOURCE_BOUNDARY_INDEX_VERSION,
    PREFERRED_FUTURE_TENDENCY,
    DISCOURAGED_FUTURE_TENDENCY,
    PREVIEW_SCOPE,
    PREVIEW_STATUS,
    build_memory_influence_preview_record,
    validate_memory_influence_preview_record,
)


COMMAND = "run-memory-runtime-influence-approval-boundary-minimal-check"
FLOW = "memory_runtime_influence_approval_boundary_minimal_v0"
PACKAGE_ID = "PKG-Phase0-MemoryRuntimeInfluenceApprovalBoundary-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = SOURCE_BOUNDARY_INDEX_VERSION
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b80"
APPROVED_DECISION = "approved_for_future_memory_runtime_influence_package"
BLOCKED_DECISIONS = (
    "rejected_for_runtime_influence",
    "needs_more_evidence_before_runtime_influence",
    "needs_stronger_safety_envelope_before_runtime_influence",
    "needs_rewrite_before_runtime_influence",
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
    "runtime_influence_performed",
    "predictor_mutation_allowed",
    "selected_action_allowed",
    "final_action_allowed",
    "production_behavior_change_allowed",
    "retained_jsonl_write_allowed",
    "retention_write_allowed",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)
TRUE_REQUIREMENT_FIELDS = (
    "requires_bounded_safety_envelope",
    "requires_rollback_to_baseline",
    "requires_no_selected_action",
    "requires_no_final_action",
    "requires_no_predictor_mutation",
    "requires_no_production_behavior",
    "repo_audit_acknowledged",
    "audit_recorded",
    "rollback_available",
)


def build_memory_runtime_influence_approval_record(
    source_preview: dict[str, Any] | None = None,
    approval_decision: str = APPROVED_DECISION,
) -> dict[str, Any]:
    preview = deepcopy(source_preview) if source_preview is not None else build_memory_influence_preview_record()
    if not validate_memory_influence_preview_record(preview)["valid"]:
        raise ValueError("invalid_memory_influence_preview_source")
    if approval_decision not in ALLOWED_DECISIONS:
        raise ValueError("invalid_approval_decision")
    may_proceed = approval_decision == APPROVED_DECISION
    return {
        "record_type": "memory_runtime_influence_approval",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "source_preview_record_type": preview.get("record_type"),
        "source_preview_status": preview.get("preview_status"),
        "source_preview_scope": preview.get("preview_scope"),
        "source_preferred_future_tendency": preview.get("preferred_future_tendency"),
        "source_discouraged_future_tendency": preview.get("discouraged_future_tendency"),
        "target_lesson_name": preview.get("source_lesson_name") or LESSON_NAME,
        "target_repeated_key": preview.get("source_repeated_key") or REPEATED_KEY,
        "approval_decision": approval_decision,
        "approval_purpose": "future_memory_runtime_influence_package_only",
        "approval_source": "explicit_user_statement",
        "approval_actor": "user",
        "approver_role": "project_owner",
        "approval_text": (
            "I approve proceeding with a future memory runtime influence package for the reviewed lesson "
            "memory record check_before_retry_when_risky_or_failed, while not approving selected_action, "
            "final_action, predictor mutation, production behavior, retained JSONL write, or proof-of-learning."
        ),
        "future_memory_runtime_influence_package_may_proceed": may_proceed,
        "runtime_influence_performed": False,
        "codex_self_approval_allowed": False,
        "ai_self_approval_allowed": False,
        "fixture_approval_is_real_approval": False,
        "task_queue_status_is_approval": False,
        "passing_tests_are_approval": False,
        "implicit_chat_command_is_approval": False,
        "predictor_mutation_allowed": False,
        "selected_action_allowed": False,
        "final_action_allowed": False,
        "production_behavior_change_allowed": False,
        "retained_jsonl_write_allowed": False,
        "retention_write_allowed": False,
        "proof_of_learning_claim_allowed": False,
        "requires_bounded_safety_envelope": True,
        "requires_rollback_to_baseline": True,
        "requires_no_selected_action": True,
        "requires_no_final_action": True,
        "requires_no_predictor_mutation": True,
        "requires_no_production_behavior": True,
        "repo_audit_acknowledged": True,
        "qingyin_current_status": QINGYIN_STATUS,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_memory_influence_preview": preview,
    }


def validate_memory_runtime_influence_approval_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "memory_runtime_influence_approval",
        "record_version": "v0",
        "source_preview_record_type": "memory_influence_preview",
        "source_preview_status": PREVIEW_STATUS,
        "source_preview_scope": PREVIEW_SCOPE,
        "source_preferred_future_tendency": PREFERRED_FUTURE_TENDENCY,
        "source_discouraged_future_tendency": DISCOURAGED_FUTURE_TENDENCY,
        "target_lesson_name": LESSON_NAME,
        "target_repeated_key": REPEATED_KEY,
        "approval_purpose": "future_memory_runtime_influence_package_only",
        "approval_source": "explicit_user_statement",
        "approval_actor": "user",
        "approver_role": "project_owner",
        "qingyin_current_status": QINGYIN_STATUS,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if not isinstance(record.get("approval_text"), str) or not record.get("approval_text", "").strip():
        errors.append("approval_text_empty")
    decision = record.get("approval_decision")
    if decision not in ALLOWED_DECISIONS:
        errors.append("approval_decision_not_allowed")
    elif decision == APPROVED_DECISION:
        if record.get("future_memory_runtime_influence_package_may_proceed") is not True:
            errors.append("approved_decision_may_proceed_not_true")
    elif record.get("future_memory_runtime_influence_package_may_proceed") is not False:
        errors.append("blocked_decision_may_proceed_not_false")
    source = record.get("source_memory_influence_preview")
    if not isinstance(source, dict):
        errors.append("source_memory_influence_preview_missing")
    elif not validate_memory_influence_preview_record(source)["valid"]:
        errors.append("source_memory_influence_preview_invalid")
    for field in FALSE_APPROVAL_SOURCE_FIELDS + FALSE_PERMISSION_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in TRUE_REQUIREMENT_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "approved_decision_checked": decision == APPROVED_DECISION
        and record.get("future_memory_runtime_influence_package_may_proceed") is True,
        "blocked_decision_checked": decision in BLOCKED_DECISIONS
        and record.get("future_memory_runtime_influence_package_may_proceed") is False,
        "source_preview_checked": isinstance(source, dict)
        and validate_memory_influence_preview_record(source)["valid"],
        "explicit_user_statement_checked": record.get("approval_source") == "explicit_user_statement",
        "project_owner_checked": record.get("approver_role") == "project_owner",
        "codex_self_approval_blocked": record.get("codex_self_approval_allowed") is False,
        "ai_self_approval_blocked": record.get("ai_self_approval_allowed") is False,
        "fixture_approval_blocked": record.get("fixture_approval_is_real_approval") is False,
        "task_queue_approval_blocked": record.get("task_queue_status_is_approval") is False,
        "passing_tests_approval_blocked": record.get("passing_tests_are_approval") is False,
        "runtime_influence_blocked": record.get("runtime_influence_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_allowed") is False,
        "selected_action_blocked": record.get("selected_action_allowed") is False,
        "final_action_blocked": record.get("final_action_allowed") is False,
        "production_behavior_blocked": record.get("production_behavior_change_allowed") is False,
        "retained_jsonl_write_blocked": record.get("retained_jsonl_write_allowed") is False,
        "retention_write_blocked": record.get("retention_write_allowed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
        "rollback_available": record.get("rollback_available") is True,
    }


def run_memory_runtime_influence_approval_boundary_minimal_check() -> dict[str, Any]:
    valid_records = [
        build_memory_runtime_influence_approval_record(approval_decision=decision)
        for decision in ALLOWED_DECISIONS
    ]
    invalid_records = _invalid_records(valid_records[0])
    validations = [validate_memory_runtime_influence_approval_record(record) for record in valid_records + invalid_records]
    valid_results = [result for result in validations if result["valid"]]
    summary = {
        "valid_approval_count": len(valid_results),
        "invalid_approval_count": len(validations) - len(valid_results),
        "approved_decision_checked_count": sum(1 for result in valid_results if result["approved_decision_checked"]),
        "blocked_decision_checked_count": sum(1 for result in valid_results if result["blocked_decision_checked"]),
        "source_preview_checked_count": sum(1 for result in valid_results if result["source_preview_checked"]),
        "explicit_user_statement_checked_count": sum(
            1 for result in valid_results if result["explicit_user_statement_checked"]
        ),
        "project_owner_checked_count": sum(1 for result in valid_results if result["project_owner_checked"]),
        "codex_self_approval_blocked_count": sum(1 for result in valid_results if result["codex_self_approval_blocked"]),
        "ai_self_approval_blocked_count": sum(1 for result in valid_results if result["ai_self_approval_blocked"]),
        "fixture_approval_blocked_count": sum(1 for result in valid_results if result["fixture_approval_blocked"]),
        "task_queue_approval_blocked_count": sum(1 for result in valid_results if result["task_queue_approval_blocked"]),
        "passing_tests_approval_blocked_count": sum(
            1 for result in valid_results if result["passing_tests_approval_blocked"]
        ),
        "runtime_influence_blocked_count": sum(1 for result in valid_results if result["runtime_influence_blocked"]),
        "predictor_mutation_blocked_count": sum(1 for result in valid_results if result["predictor_mutation_blocked"]),
        "selected_action_blocked_count": sum(1 for result in valid_results if result["selected_action_blocked"]),
        "final_action_blocked_count": sum(1 for result in valid_results if result["final_action_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid_results if result["production_behavior_blocked"]),
        "retained_jsonl_write_blocked_count": sum(
            1 for result in valid_results if result["retained_jsonl_write_blocked"]
        ),
        "retention_write_blocked_count": sum(1 for result in valid_results if result["retention_write_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid_results if result["proof_claim_blocked"]),
        "rollback_available_count": sum(1 for result in valid_results if result["rollback_available"]),
    }
    summary["all_memory_runtime_influence_approval_boundary_checks_passed"] = _all_checks_passed(summary)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_memory_runtime_influence_approval_boundary_checks_passed"] else "failed",
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
                "Introduces explicit human approval validation for future memory runtime influence packages, "
                "while runtime influence, predictor mutation, action selection, production promotion, retained "
                "JSONL write, and proof-of-learning remain blocked."
            ),
        },
        "safe_claim": (
            "ASHL Core can validate explicit human approval to proceed with a future memory runtime influence "
            "package, while runtime influence, predictor mutation, action selection, production promotion, "
            "retained JSONL write, and proof-of-learning remain blocked."
        ),
    }


def _invalid_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    records = [
        _without(valid, "source_memory_influence_preview"),
        _mutated(valid, ["source_memory_influence_preview", "preview_is_runtime_influence"], True),
        _mutated(valid, ["approval_source"], "task_queue"),
        _mutated(valid, ["approval_actor"], "codex"),
        _mutated(valid, ["approver_role"], "assistant"),
        _mutated(valid, ["approval_text"], ""),
        _mutated(valid, ["approval_decision"], "apply_runtime_influence_now"),
        _mutated(valid, ["future_memory_runtime_influence_package_may_proceed"], False),
        _mutated(build_memory_runtime_influence_approval_record(approval_decision="rejected_for_runtime_influence"), ["future_memory_runtime_influence_package_may_proceed"], True),
        _mutated(build_memory_runtime_influence_approval_record(approval_decision="needs_more_evidence_before_runtime_influence"), ["future_memory_runtime_influence_package_may_proceed"], True),
        _mutated(build_memory_runtime_influence_approval_record(approval_decision="needs_stronger_safety_envelope_before_runtime_influence"), ["future_memory_runtime_influence_package_may_proceed"], True),
        _mutated(build_memory_runtime_influence_approval_record(approval_decision="needs_rewrite_before_runtime_influence"), ["future_memory_runtime_influence_package_may_proceed"], True),
    ]
    for field in FALSE_APPROVAL_SOURCE_FIELDS + FALSE_PERMISSION_FIELDS:
        records.append(_mutated(valid, [field], True))
    for field in TRUE_REQUIREMENT_FIELDS:
        records.append(_mutated(valid, [field], False))
    return records


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["valid_approval_count"] == 5
        and summary["invalid_approval_count"] >= 1
        and summary["approved_decision_checked_count"] == 1
        and summary["blocked_decision_checked_count"] == 4
        and summary["source_preview_checked_count"] == 5
        and summary["explicit_user_statement_checked_count"] == 5
        and summary["project_owner_checked_count"] == 5
        and summary["codex_self_approval_blocked_count"] == 5
        and summary["ai_self_approval_blocked_count"] == 5
        and summary["fixture_approval_blocked_count"] == 5
        and summary["task_queue_approval_blocked_count"] == 5
        and summary["passing_tests_approval_blocked_count"] == 5
        and summary["runtime_influence_blocked_count"] == 5
        and summary["predictor_mutation_blocked_count"] == 5
        and summary["selected_action_blocked_count"] == 5
        and summary["final_action_blocked_count"] == 5
        and summary["production_behavior_blocked_count"] == 5
        and summary["retained_jsonl_write_blocked_count"] == 5
        and summary["retention_write_blocked_count"] == 5
        and summary["proof_claim_blocked_count"] == 5
        and summary["rollback_available_count"] == 5
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

    print(json.dumps(run_memory_runtime_influence_approval_boundary_minimal_check(), indent=2))
