"""Minimal reviewed lesson memory write and controlled read boundary."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from .bucket_signal_human_interpretation_review_minimal import (
    INTERPRETED_LESSON_TEXT,
    PLAIN_LANGUAGE_SUMMARY,
    QINGYIN_STATUS,
    REPEATED_KEY,
)
from .memory_admission_minimal import (
    LESSON_NAME,
    build_memory_admission_record,
    build_reviewed_lesson_memory_candidate_record,
    validate_memory_admission_record,
    validate_reviewed_lesson_memory_candidate_record,
)
from .memory_write_approval_boundary_minimal import (
    APPROVED_DECISION,
    BLOCKED_DECISIONS,
    build_memory_write_approval_record,
    validate_memory_write_approval_record,
)


COMMAND = "run-memory-write-and-read-minimal-check"
FLOW = "memory_write_and_read_minimal_v0"
PACKAGE_ID = "PKG-Phase0-MemoryWriteAndRead-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b77"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b78"
MEMORY_RECORD_LAYER = "reviewed_lesson_memory_layer_minimal"
MEMORY_STATUS = "written_and_readable_by_controlled_memory_read_path"
WRITE_STATUS = "written_minimal_reviewed_lesson_memory_record"
WRITE_TARGET = "minimal_reviewed_lesson_memory_record"
READ_SCOPE = "controlled_memory_read_path_only"
READ_PURPOSE = "human_review_and_future_influence_design_only"
CURRENT_ALLOWED_USE = "controlled_memory_read_and_audit_only"
ROLLBACK_ACTION = "invalidate_minimal_memory_record_and_block_controlled_read"
FALSE_WRITE_FIELDS = (
    "long_term_memory_write_performed",
    "core_memory_write_performed",
    "archive_memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "runtime_influence_enabled",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "selected_action_allowed",
    "final_action_allowed",
    "direct_command_allowed",
    "production_behavior_change_allowed",
    "proof_of_learning_claim_allowed",
    "qingyin_self_authored_text",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)
FALSE_MEMORY_RECORD_FIELDS = (
    "is_core_memory",
    "is_archive_memory",
    "is_production_long_term_memory_runtime",
    "writes_jsonl",
    "runtime_influence_enabled",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "human_approved_for_runtime_influence",
    "human_approved_for_predictor_influence",
    "human_approved_for_production_behavior",
)
FALSE_READ_FIELDS = (
    "read_is_runtime_influence",
    "read_is_action_selection_input",
    "read_is_predictor_input",
    "read_is_production_input",
    "runtime_influence_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "selected_action_created",
    "final_action_created",
    "production_behavior_changed",
    "proof_of_learning_claim_allowed",
)
TRUE_WRITE_BOUNDARY_FIELDS = (
    "future_runtime_influence_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "future_retained_jsonl_write_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "future_action_selection_requires_separate_boundary",
    "repo_audit_acknowledged",
    "audit_recorded",
    "rollback_available",
)


def build_minimal_memory_write_record(
    memory_admission: dict[str, Any] | None = None,
    reviewed_lesson_memory_candidate: dict[str, Any] | None = None,
    memory_write_approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    admission = deepcopy(memory_admission) if memory_admission is not None else build_memory_admission_record()
    candidate = (
        deepcopy(reviewed_lesson_memory_candidate)
        if reviewed_lesson_memory_candidate is not None
        else build_reviewed_lesson_memory_candidate_record(admission)
    )
    approval = (
        deepcopy(memory_write_approval)
        if memory_write_approval is not None
        else build_memory_write_approval_record(admission, candidate)
    )
    _raise_if_invalid_sources(admission, candidate, approval)
    return {
        "record_type": "memory_write",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "write_status": WRITE_STATUS,
        "write_target": WRITE_TARGET,
        "memory_record_layer": MEMORY_RECORD_LAYER,
        "source_admission_record_type": admission.get("record_type"),
        "source_admission_status": admission.get("admission_status"),
        "source_candidate_record_type": candidate.get("record_type"),
        "source_candidate_status": candidate.get("candidate_status"),
        "source_approval_record_type": approval.get("record_type"),
        "source_approval_decision": approval.get("approval_decision"),
        "lesson_name": candidate.get("lesson_name") or LESSON_NAME,
        "repeated_key": admission.get("source_repeated_key") or REPEATED_KEY,
        "memory_text": candidate.get("lesson_text") or INTERPRETED_LESSON_TEXT,
        "plain_language_summary": admission.get("plain_language_summary") or PLAIN_LANGUAGE_SUMMARY,
        "source_signal_authorship": admission.get("source_signal_authorship"),
        "interpretation_author_type": admission.get("interpretation_author_type"),
        "qingyin_self_authored_text": False,
        "memory_write_performed": True,
        "minimal_memory_read_enabled": True,
        "controlled_memory_read_path_enabled": True,
        "long_term_memory_write_performed": False,
        "core_memory_write_performed": False,
        "archive_memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "runtime_influence_enabled": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "selected_action_allowed": False,
        "final_action_allowed": False,
        "direct_command_allowed": False,
        "production_behavior_change_allowed": False,
        "proof_of_learning_claim_allowed": False,
        "current_allowed_use": CURRENT_ALLOWED_USE,
        "future_runtime_influence_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_retained_jsonl_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_action_selection_requires_separate_boundary": True,
        "repo_audit_acknowledged": True,
        "qingyin_current_status": QINGYIN_STATUS,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "rollback_action": ROLLBACK_ACTION,
        "source_memory_admission": admission,
        "source_reviewed_lesson_memory_candidate": candidate,
        "source_memory_write_approval": approval,
    }


def validate_minimal_memory_write_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "memory_write",
        "record_version": "v0",
        "write_status": WRITE_STATUS,
        "write_target": WRITE_TARGET,
        "memory_record_layer": MEMORY_RECORD_LAYER,
        "source_admission_record_type": "memory_admission",
        "source_admission_status": "admitted_as_reviewed_lesson_memory_candidate",
        "source_candidate_record_type": "reviewed_lesson_memory_candidate",
        "source_candidate_status": "admitted_candidate_not_long_term_memory",
        "source_approval_record_type": "memory_write_approval",
        "source_approval_decision": APPROVED_DECISION,
        "source_signal_authorship": "qingyin_bucket_derived_system_detected",
        "interpretation_author_type": "human_or_human_gpt_assisted",
        "current_allowed_use": CURRENT_ALLOWED_USE,
        "qingyin_current_status": QINGYIN_STATUS,
        "rollback_action": ROLLBACK_ACTION,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    for field in ("lesson_name", "repeated_key", "memory_text", "plain_language_summary"):
        if not isinstance(record.get(field), str) or not record.get(field).strip():
            errors.append(f"{field}_empty")
    if record.get("lesson_name") != LESSON_NAME:
        errors.append("lesson_name_not_expected")
    if record.get("repeated_key") != REPEATED_KEY:
        errors.append("repeated_key_not_expected")
    if record.get("memory_write_performed") is not True:
        errors.append("memory_write_performed_not_true")
    if record.get("minimal_memory_read_enabled") is not True:
        errors.append("minimal_memory_read_enabled_not_true")
    if record.get("controlled_memory_read_path_enabled") is not True:
        errors.append("controlled_memory_read_path_enabled_not_true")
    for field in FALSE_WRITE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in TRUE_WRITE_BOUNDARY_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    _validate_embedded_sources(record, errors)
    return {
        "valid": not errors,
        "error_codes": errors,
        "approval_checked": _approval_source_valid(record.get("source_memory_write_approval")),
        "memory_write_performed": record.get("memory_write_performed") is True,
        "minimal_memory_read_enabled": record.get("minimal_memory_read_enabled") is True,
        "retained_jsonl_write_blocked": record.get("retained_jsonl_write_performed") is False,
        "retention_write_blocked": record.get("retention_write_performed") is False,
        "runtime_influence_blocked": record.get("runtime_influence_enabled") is False,
        "predictor_read_blocked": record.get("predictor_read_enabled") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "selected_action_blocked": record.get("selected_action_allowed") is False,
        "final_action_blocked": record.get("final_action_allowed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
        "rollback_available": record.get("rollback_available") is True,
    }


def build_minimal_reviewed_lesson_memory_record(
    memory_write_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    write_record = deepcopy(memory_write_record) if memory_write_record is not None else build_minimal_memory_write_record()
    if not validate_minimal_memory_write_record(write_record)["valid"]:
        raise ValueError("invalid_minimal_memory_write_record")
    return {
        "record_type": "minimal_reviewed_lesson_memory_record",
        "record_version": "v0",
        "memory_status": MEMORY_STATUS,
        "memory_layer": MEMORY_RECORD_LAYER,
        "lesson_name": write_record.get("lesson_name"),
        "repeated_key": write_record.get("repeated_key"),
        "memory_text": write_record.get("memory_text"),
        "source_memory_write_record_type": write_record.get("record_type"),
        "source_memory_write_status": write_record.get("write_status"),
        "is_core_memory": False,
        "is_archive_memory": False,
        "is_production_long_term_memory_runtime": False,
        "writes_jsonl": False,
        "controlled_memory_read_enabled": True,
        "runtime_influence_enabled": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "human_approved_for_memory_write": True,
        "human_approved_for_controlled_memory_read": True,
        "human_approved_for_runtime_influence": False,
        "human_approved_for_predictor_influence": False,
        "human_approved_for_production_behavior": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_memory_write": write_record,
    }


def validate_minimal_reviewed_lesson_memory_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "minimal_reviewed_lesson_memory_record",
        "record_version": "v0",
        "memory_status": MEMORY_STATUS,
        "memory_layer": MEMORY_RECORD_LAYER,
        "source_memory_write_record_type": "memory_write",
        "source_memory_write_status": WRITE_STATUS,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    for field in ("lesson_name", "repeated_key", "memory_text"):
        if not isinstance(record.get(field), str) or not record.get(field).strip():
            errors.append(f"{field}_empty")
    if record.get("controlled_memory_read_enabled") is not True:
        errors.append("controlled_memory_read_enabled_not_true")
    for field in FALSE_MEMORY_RECORD_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in (
        "human_approved_for_memory_write",
        "human_approved_for_controlled_memory_read",
        "audit_recorded",
        "rollback_available",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    source = record.get("source_memory_write")
    if not isinstance(source, dict):
        errors.append("source_memory_write_missing")
    elif not validate_minimal_memory_write_record(source)["valid"]:
        errors.append("source_memory_write_invalid")
    return {
        "valid": not errors,
        "error_codes": errors,
        "minimal_memory_record_created": record.get("record_type") == "minimal_reviewed_lesson_memory_record",
        "controlled_memory_read_enabled": record.get("controlled_memory_read_enabled") is True,
        "retained_jsonl_write_blocked": record.get("writes_jsonl") is False,
        "runtime_influence_blocked": record.get("runtime_influence_enabled") is False,
        "predictor_read_blocked": record.get("predictor_read_enabled") is False,
        "predictor_mutation_blocked": record.get("predictor_influence_enabled") is False,
        "rollback_available": record.get("rollback_available") is True,
    }


def build_controlled_memory_read_record(
    memory_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reviewed_memory = (
        deepcopy(memory_record) if memory_record is not None else build_minimal_reviewed_lesson_memory_record()
    )
    if not validate_minimal_reviewed_lesson_memory_record(reviewed_memory)["valid"]:
        raise ValueError("invalid_minimal_reviewed_lesson_memory_record")
    return {
        "record_type": "controlled_memory_read",
        "record_version": "v0",
        "read_status": "read_successful",
        "read_scope": READ_SCOPE,
        "read_purpose": READ_PURPOSE,
        "source_memory_record_type": reviewed_memory.get("record_type"),
        "source_memory_status": reviewed_memory.get("memory_status"),
        "source_memory_layer": reviewed_memory.get("memory_layer"),
        "retrieved_lesson_name": reviewed_memory.get("lesson_name"),
        "retrieved_repeated_key": reviewed_memory.get("repeated_key"),
        "retrieved_memory_text": reviewed_memory.get("memory_text"),
        "read_visible_to_qingyin_controlled_path": True,
        "read_is_runtime_influence": False,
        "read_is_action_selection_input": False,
        "read_is_predictor_input": False,
        "read_is_production_input": False,
        "runtime_influence_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "selected_action_created": False,
        "final_action_created": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_minimal_memory_record": reviewed_memory,
    }


def validate_controlled_memory_read_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "controlled_memory_read",
        "record_version": "v0",
        "read_status": "read_successful",
        "read_scope": READ_SCOPE,
        "read_purpose": READ_PURPOSE,
        "source_memory_record_type": "minimal_reviewed_lesson_memory_record",
        "source_memory_status": MEMORY_STATUS,
        "source_memory_layer": MEMORY_RECORD_LAYER,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    for field in ("retrieved_lesson_name", "retrieved_repeated_key", "retrieved_memory_text"):
        if not isinstance(record.get(field), str) or not record.get(field).strip():
            errors.append(f"{field}_empty")
    if record.get("read_visible_to_qingyin_controlled_path") is not True:
        errors.append("read_visible_to_qingyin_controlled_path_not_true")
    for field in FALSE_READ_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in ("audit_recorded", "rollback_available"):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    source = record.get("source_minimal_memory_record")
    if not isinstance(source, dict):
        errors.append("source_minimal_memory_record_missing")
    elif not validate_minimal_reviewed_lesson_memory_record(source)["valid"]:
        errors.append("source_minimal_memory_record_invalid")
    return {
        "valid": not errors,
        "error_codes": errors,
        "controlled_memory_read_performed": record.get("read_status") == "read_successful",
        "retrieved_memory_text_visible": isinstance(record.get("retrieved_memory_text"), str)
        and bool(record.get("retrieved_memory_text", "").strip()),
        "retained_jsonl_write_blocked": True,
        "retention_write_blocked": True,
        "runtime_influence_blocked": record.get("read_is_runtime_influence") is False
        and record.get("runtime_influence_enabled") is False,
        "predictor_read_blocked": record.get("read_is_predictor_input") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
        "rollback_available": record.get("rollback_available") is True,
    }


def run_memory_write_and_read_minimal_check() -> dict[str, Any]:
    valid_write = build_minimal_memory_write_record()
    valid_memory_record = build_minimal_reviewed_lesson_memory_record(valid_write)
    valid_read = build_controlled_memory_read_record(valid_memory_record)
    invalid_writes = _invalid_write_records(valid_write)
    invalid_memory_records = _invalid_memory_records(valid_memory_record)
    invalid_reads = _invalid_read_records(valid_read)
    write_results = [validate_minimal_memory_write_record(record) for record in [valid_write] + invalid_writes]
    memory_results = [
        validate_minimal_reviewed_lesson_memory_record(record)
        for record in [valid_memory_record] + invalid_memory_records
    ]
    read_results = [validate_controlled_memory_read_record(record) for record in [valid_read] + invalid_reads]
    valid_write_results = [result for result in write_results if result["valid"]]
    valid_memory_results = [result for result in memory_results if result["valid"]]
    valid_read_results = [result for result in read_results if result["valid"]]
    summary = {
        "valid_memory_write_count": len(valid_write_results),
        "invalid_memory_write_count": len(write_results) - len(valid_write_results),
        "valid_minimal_memory_record_count": len(valid_memory_results),
        "invalid_minimal_memory_record_count": len(memory_results) - len(valid_memory_results),
        "valid_controlled_memory_read_count": len(valid_read_results),
        "invalid_controlled_memory_read_count": len(read_results) - len(valid_read_results),
        "approval_checked_count": sum(1 for result in valid_write_results if result["approval_checked"]),
        "memory_write_performed_count": sum(1 for result in valid_write_results if result["memory_write_performed"]),
        "controlled_memory_read_performed_count": sum(
            1 for result in valid_read_results if result["controlled_memory_read_performed"]
        ),
        "retrieved_memory_text_visible_count": sum(
            1 for result in valid_read_results if result["retrieved_memory_text_visible"]
        ),
        "retained_jsonl_write_blocked_count": _count_true(
            valid_write_results + valid_memory_results + valid_read_results, "retained_jsonl_write_blocked"
        ),
        "retention_write_blocked_count": _count_true(
            valid_write_results + valid_read_results, "retention_write_blocked"
        ),
        "runtime_influence_blocked_count": _count_true(
            valid_write_results + valid_memory_results + valid_read_results, "runtime_influence_blocked"
        ),
        "predictor_read_blocked_count": _count_true(
            valid_write_results + valid_memory_results + valid_read_results, "predictor_read_blocked"
        ),
        "predictor_mutation_blocked_count": _count_true(
            valid_write_results + valid_memory_results + valid_read_results, "predictor_mutation_blocked"
        ),
        "selected_action_blocked_count": _count_true(
            valid_write_results + valid_read_results, "selected_action_blocked"
        ),
        "final_action_blocked_count": _count_true(valid_write_results + valid_read_results, "final_action_blocked"),
        "proof_claim_blocked_count": _count_true(valid_write_results + valid_read_results, "proof_claim_blocked"),
        "rollback_available_count": _count_true(
            valid_write_results + valid_memory_results + valid_read_results, "rollback_available"
        ),
    }
    summary["all_memory_write_and_read_minimal_checks_passed"] = _all_checks_passed(summary)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_memory_write_and_read_minimal_checks_passed"] else "failed",
        "valid_memory_write_record": valid_write,
        "valid_minimal_reviewed_lesson_memory_record": valid_memory_record,
        "valid_controlled_memory_read_record": valid_read,
        "invalid_memory_write_records": invalid_writes,
        "invalid_minimal_memory_records": invalid_memory_records,
        "invalid_controlled_memory_read_records": invalid_reads,
        "memory_write_validation_results": write_results,
        "minimal_memory_record_validation_results": memory_results,
        "controlled_memory_read_validation_results": read_results,
        "summary": summary,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package opens the minimal memory write and controlled memory read boundary for one "
                "approved reviewed_lesson_memory_candidate, while retained JSONL write, runtime influence, "
                "predictor mutation, action selection, production promotion, and proof-of-learning remain blocked."
            ),
        },
        "safe_claim": (
            "ASHL Core can write one approved human-interpreted, bucket-derived lesson as a minimal reviewed "
            "lesson memory record and read it through a controlled memory read path, while keeping retained "
            "JSONL write, runtime influence, predictor read/influence/mutation, action selection, production "
            "promotion, and proof-of-learning blocked."
        ),
    }


def _raise_if_invalid_sources(
    admission: dict[str, Any],
    candidate: dict[str, Any],
    approval: dict[str, Any],
) -> None:
    if not validate_memory_admission_record(admission)["valid"]:
        raise ValueError("invalid_memory_admission_source")
    if not validate_reviewed_lesson_memory_candidate_record(candidate)["valid"]:
        raise ValueError("invalid_reviewed_lesson_memory_candidate_source")
    if not validate_memory_write_approval_record(approval)["valid"]:
        raise ValueError("invalid_memory_write_approval_source")
    if approval.get("approval_decision") != APPROVED_DECISION:
        raise ValueError("memory_write_approval_not_approved")
    if approval.get("future_memory_write_package_may_proceed") is not True:
        raise ValueError("memory_write_approval_may_not_proceed")


def _validate_embedded_sources(record: dict[str, Any], errors: list[str]) -> None:
    _validate_source(record, "source_memory_admission", validate_memory_admission_record, errors)
    _validate_source(
        record,
        "source_reviewed_lesson_memory_candidate",
        validate_reviewed_lesson_memory_candidate_record,
        errors,
    )
    _validate_source(record, "source_memory_write_approval", validate_memory_write_approval_record, errors)
    approval = record.get("source_memory_write_approval")
    if isinstance(approval, dict):
        if approval.get("approval_decision") != APPROVED_DECISION:
            errors.append("source_memory_write_approval_not_approved")
        if approval.get("future_memory_write_package_may_proceed") is not True:
            errors.append("source_memory_write_approval_may_not_proceed")


def _validate_source(
    record: dict[str, Any],
    field: str,
    validator: Callable[[dict[str, Any]], dict[str, Any]],
    errors: list[str],
) -> None:
    source = record.get(field)
    if not isinstance(source, dict):
        errors.append(f"{field}_missing")
    elif not validator(source)["valid"]:
        errors.append(f"{field}_invalid")


def _approval_source_valid(approval: Any) -> bool:
    return (
        isinstance(approval, dict)
        and validate_memory_write_approval_record(approval)["valid"]
        and approval.get("approval_decision") == APPROVED_DECISION
        and approval.get("future_memory_write_package_may_proceed") is True
        and approval.get("approval_source") == "explicit_user_statement"
        and approval.get("approval_actor") == "user"
        and approval.get("approver_role") == "project_owner"
    )


def _invalid_write_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    records = [
        _without(valid, "source_memory_admission"),
        _without(valid, "source_reviewed_lesson_memory_candidate"),
        _without(valid, "source_memory_write_approval"),
        _mutated(valid, ["source_memory_write_approval", "approval_decision"], "rejected_for_memory_write"),
        _mutated(valid, ["source_memory_write_approval", "approval_decision"], "needs_more_evidence_before_memory_write"),
        _mutated(valid, ["source_memory_write_approval", "approval_decision"], "needs_retention_rule_before_memory_write"),
        _mutated(valid, ["source_memory_write_approval", "approval_decision"], "needs_rollback_rule_before_memory_write"),
        _mutated(valid, ["source_memory_write_approval", "approval_decision"], "needs_rewrite_before_memory_write"),
        _mutated(valid, ["source_memory_write_approval", "future_memory_write_package_may_proceed"], False),
        _mutated(valid, ["memory_record_layer"], "core_memory"),
        _mutated(valid, ["memory_record_layer"], "archive_memory"),
        _mutated(valid, ["memory_record_layer"], "production_long_term_memory_runtime"),
        _mutated(valid, ["controlled_memory_read_path_enabled"], False),
        _mutated(valid, ["rollback_available"], False),
        _mutated(valid, ["rollback_action"], "do_not_block_controlled_read"),
    ]
    for decision in BLOCKED_DECISIONS:
        blocked = build_memory_write_approval_record(approval_decision=decision)
        candidate = build_reviewed_lesson_memory_candidate_record(blocked["source_memory_admission"])
        write = deepcopy(valid)
        write["source_memory_write_approval"] = blocked
        write["source_reviewed_lesson_memory_candidate"] = candidate
        write["source_approval_decision"] = decision
        records.append(write)
    for field in FALSE_WRITE_FIELDS:
        records.append(_mutated(valid, [field], True))
    return records


def _invalid_memory_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    records = [
        _without(valid, "source_memory_write"),
        _mutated(valid, ["memory_status"], "not_readable"),
        _mutated(valid, ["controlled_memory_read_enabled"], False),
        _mutated(valid, ["human_approved_for_memory_write"], False),
        _mutated(valid, ["human_approved_for_controlled_memory_read"], False),
        _mutated(valid, ["rollback_available"], False),
    ]
    for field in FALSE_MEMORY_RECORD_FIELDS:
        records.append(_mutated(valid, [field], True))
    return records


def _invalid_read_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    records = [
        _without(valid, "source_minimal_memory_record"),
        _mutated(valid, ["read_status"], "read_failed"),
        _mutated(valid, ["read_scope"], "runtime_memory_read"),
        _mutated(valid, ["retrieved_memory_text"], ""),
        _mutated(valid, ["read_visible_to_qingyin_controlled_path"], False),
        _mutated(valid, ["rollback_available"], False),
    ]
    for field in FALSE_READ_FIELDS:
        records.append(_mutated(valid, [field], True))
    return records


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["valid_memory_write_count"] == 1
        and summary["invalid_memory_write_count"] >= 1
        and summary["valid_minimal_memory_record_count"] == 1
        and summary["invalid_minimal_memory_record_count"] >= 1
        and summary["valid_controlled_memory_read_count"] == 1
        and summary["invalid_controlled_memory_read_count"] >= 1
        and summary["approval_checked_count"] == 1
        and summary["memory_write_performed_count"] == 1
        and summary["controlled_memory_read_performed_count"] == 1
        and summary["retrieved_memory_text_visible_count"] == 1
        and summary["retained_jsonl_write_blocked_count"] == 3
        and summary["retention_write_blocked_count"] == 2
        and summary["runtime_influence_blocked_count"] == 3
        and summary["predictor_read_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["selected_action_blocked_count"] == 2
        and summary["final_action_blocked_count"] == 2
        and summary["proof_claim_blocked_count"] == 2
        and summary["rollback_available_count"] == 3
    )


def _count_true(results: list[dict[str, Any]], field: str) -> int:
    return sum(1 for result in results if result.get(field) is True)


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

    print(json.dumps(run_memory_write_and_read_minimal_check(), indent=2))
