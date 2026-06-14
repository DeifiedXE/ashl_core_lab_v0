"""Preview-only memory influence view from a controlled memory read."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS, REPEATED_KEY
from .memory_admission_minimal import LESSON_NAME
from .memory_write_and_read_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as SOURCE_BOUNDARY_INDEX_VERSION,
    MEMORY_RECORD_LAYER,
    MEMORY_STATUS,
    build_controlled_memory_read_record,
    validate_controlled_memory_read_record,
)


COMMAND = "run-memory-influence-preview-minimal-check"
FLOW = "memory_influence_preview_minimal_v0"
PACKAGE_ID = "PKG-Phase0-MemoryInfluencePreview-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = SOURCE_BOUNDARY_INDEX_VERSION
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b79"
PREVIEW_STATUS = "generated_no_runtime_effect"
PREVIEW_SCOPE = "controlled_preview_only"
PREVIEW_SOURCE = "controlled_memory_read"
PREFERRED_FUTURE_TENDENCY = "check_before_retry"
DISCOURAGED_FUTURE_TENDENCY = "retry_same_action_without_check"
SAFE_ALTERNATIVES = (
    "check_relevant_state",
    "choose_safer_alternative",
    "fallback",
    "stop_and_report",
)
FALSE_PREVIEW_FIELDS = (
    "preview_is_runtime_influence",
    "preview_is_predictor_input",
    "preview_is_action_selection",
    "preview_is_final_action",
    "preview_is_production_behavior",
    "runtime_influence_enabled",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "production_behavior_changed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
    "proof_of_learning_claim_allowed",
)
TRUE_BOUNDARY_FIELDS = (
    "future_runtime_influence_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "future_action_selection_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "repo_audit_acknowledged",
    "audit_recorded",
    "rollback_available",
)


def build_memory_influence_preview_record(
    controlled_memory_read: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_read = deepcopy(controlled_memory_read) if controlled_memory_read is not None else (
        build_controlled_memory_read_record()
    )
    if not validate_controlled_memory_read_record(source_read)["valid"]:
        raise ValueError("invalid_controlled_memory_read_source")
    source_memory = source_read.get("source_minimal_memory_record")
    if not isinstance(source_memory, dict):
        raise ValueError("missing_source_minimal_memory_record")
    _raise_if_source_memory_has_influence(source_memory)
    return {
        "record_type": "memory_influence_preview",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "preview_status": PREVIEW_STATUS,
        "preview_scope": PREVIEW_SCOPE,
        "preview_source": PREVIEW_SOURCE,
        "source_memory_record_type": source_read.get("source_memory_record_type"),
        "source_memory_status": source_read.get("source_memory_status"),
        "source_lesson_name": source_read.get("retrieved_lesson_name"),
        "source_repeated_key": source_read.get("retrieved_repeated_key"),
        "retrieved_memory_text": source_read.get("retrieved_memory_text"),
        "preview_interpretation": (
            "If a future influence boundary is opened, this memory would favor checking relevant state "
            "before retrying a risky or failed action."
        ),
        "preferred_future_tendency": PREFERRED_FUTURE_TENDENCY,
        "discouraged_future_tendency": DISCOURAGED_FUTURE_TENDENCY,
        "safe_alternatives": list(SAFE_ALTERNATIVES),
        "preview_is_runtime_influence": False,
        "preview_is_predictor_input": False,
        "preview_is_action_selection": False,
        "preview_is_final_action": False,
        "preview_is_production_behavior": False,
        "runtime_influence_enabled": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "production_behavior_changed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "future_runtime_influence_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_action_selection_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "repo_audit_acknowledged": True,
        "qingyin_current_status": QINGYIN_STATUS,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "proof_of_learning_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "rollback_action": "discard_preview_only",
        "source_controlled_memory_read": source_read,
    }


def validate_memory_influence_preview_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "memory_influence_preview",
        "record_version": "v0",
        "preview_status": PREVIEW_STATUS,
        "preview_scope": PREVIEW_SCOPE,
        "preview_source": PREVIEW_SOURCE,
        "source_memory_record_type": "minimal_reviewed_lesson_memory_record",
        "source_memory_status": MEMORY_STATUS,
        "source_lesson_name": LESSON_NAME,
        "source_repeated_key": REPEATED_KEY,
        "preferred_future_tendency": PREFERRED_FUTURE_TENDENCY,
        "discouraged_future_tendency": DISCOURAGED_FUTURE_TENDENCY,
        "qingyin_current_status": QINGYIN_STATUS,
        "rollback_action": "discard_preview_only",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    for field in ("source_lesson_name", "retrieved_memory_text", "preview_interpretation"):
        if not isinstance(record.get(field), str) or not record.get(field).strip():
            errors.append(f"{field}_empty")
    alternatives = record.get("safe_alternatives")
    if not isinstance(alternatives, list):
        errors.append("safe_alternatives_not_list")
        alternatives = []
    if "check_relevant_state" not in alternatives:
        errors.append("safe_alternatives_missing_check_relevant_state")
    if not {"choose_safer_alternative", "fallback", "stop_and_report"}.intersection(alternatives):
        errors.append("safe_alternatives_missing_non_retry_option")
    for field in FALSE_PREVIEW_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in TRUE_BOUNDARY_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    source_read = record.get("source_controlled_memory_read")
    if not isinstance(source_read, dict):
        errors.append("source_controlled_memory_read_missing")
    else:
        source_result = validate_controlled_memory_read_record(source_read)
        if not source_result["valid"]:
            errors.append("source_controlled_memory_read_invalid")
        source_memory = source_read.get("source_minimal_memory_record")
        if not isinstance(source_memory, dict):
            errors.append("source_minimal_memory_record_missing")
        elif _source_memory_has_influence(source_memory):
            errors.append("source_minimal_memory_record_influence_enabled")
    return {
        "valid": not errors,
        "error_codes": errors,
        "controlled_memory_read_checked": isinstance(source_read, dict)
        and validate_controlled_memory_read_record(source_read)["valid"],
        "retrieved_memory_text_checked": isinstance(record.get("retrieved_memory_text"), str)
        and bool(record.get("retrieved_memory_text", "").strip()),
        "preview_generated": record.get("preview_status") == PREVIEW_STATUS,
        "preferred_tendency_checked": record.get("preferred_future_tendency") == PREFERRED_FUTURE_TENDENCY,
        "runtime_influence_blocked": record.get("preview_is_runtime_influence") is False
        and record.get("runtime_influence_enabled") is False,
        "predictor_read_blocked": record.get("preview_is_predictor_input") is False
        and record.get("predictor_read_enabled") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "selected_action_blocked": record.get("preview_is_action_selection") is False
        and record.get("selected_action_created") is False,
        "final_action_blocked": record.get("preview_is_final_action") is False
        and record.get("final_action_created") is False,
        "retained_jsonl_write_blocked": record.get("retained_jsonl_write_performed") is False,
        "retention_write_blocked": record.get("retention_write_performed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
        "rollback_available": record.get("rollback_available") is True,
    }


def run_memory_influence_preview_minimal_check() -> dict[str, Any]:
    valid_preview = build_memory_influence_preview_record()
    invalid_previews = _invalid_preview_records(valid_preview)
    validations = [validate_memory_influence_preview_record(record) for record in [valid_preview] + invalid_previews]
    valid_results = [result for result in validations if result["valid"]]
    summary = {
        "valid_preview_count": len(valid_results),
        "invalid_preview_count": len(validations) - len(valid_results),
        "controlled_memory_read_checked_count": sum(1 for result in valid_results if result["controlled_memory_read_checked"]),
        "retrieved_memory_text_checked_count": sum(1 for result in valid_results if result["retrieved_memory_text_checked"]),
        "preview_generated_count": sum(1 for result in valid_results if result["preview_generated"]),
        "preferred_tendency_checked_count": sum(1 for result in valid_results if result["preferred_tendency_checked"]),
        "runtime_influence_blocked_count": sum(1 for result in valid_results if result["runtime_influence_blocked"]),
        "predictor_read_blocked_count": sum(1 for result in valid_results if result["predictor_read_blocked"]),
        "predictor_mutation_blocked_count": sum(1 for result in valid_results if result["predictor_mutation_blocked"]),
        "selected_action_blocked_count": sum(1 for result in valid_results if result["selected_action_blocked"]),
        "final_action_blocked_count": sum(1 for result in valid_results if result["final_action_blocked"]),
        "retained_jsonl_write_blocked_count": sum(1 for result in valid_results if result["retained_jsonl_write_blocked"]),
        "retention_write_blocked_count": sum(1 for result in valid_results if result["retention_write_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid_results if result["proof_claim_blocked"]),
        "rollback_available_count": sum(1 for result in valid_results if result["rollback_available"]),
    }
    summary["all_memory_influence_preview_minimal_checks_passed"] = _all_checks_passed(summary)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_memory_influence_preview_minimal_checks_passed"] else "failed",
        "valid_preview_record": valid_preview,
        "invalid_preview_records": invalid_previews,
        "validation_results": validations,
        "summary": summary,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package introduces a preview-only memory influence validation boundary from controlled "
                "memory read, while runtime influence, predictor input/mutation, action selection, production "
                "promotion, retained JSONL write, and proof-of-learning remain blocked."
            ),
        },
        "safe_claim": (
            "ASHL Core can generate a preview-only influence view from one controlled memory read, showing that "
            "the memory would favor check_before_retry in a future influence design, while keeping runtime "
            "influence, predictor read/influence/mutation, action selection, production promotion, retained JSONL "
            "write, retention write, and proof-of-learning blocked."
        ),
    }


def _raise_if_source_memory_has_influence(source_memory: dict[str, Any]) -> None:
    if _source_memory_has_influence(source_memory):
        raise ValueError("source_minimal_memory_record_influence_enabled")


def _source_memory_has_influence(source_memory: dict[str, Any]) -> bool:
    return not (
        source_memory.get("runtime_influence_enabled") is False
        and source_memory.get("predictor_read_enabled") is False
        and source_memory.get("predictor_influence_enabled") is False
        and source_memory.get("writes_jsonl") is False
        and source_memory.get("memory_layer") == MEMORY_RECORD_LAYER
    )


def _invalid_preview_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    records = [
        _without(valid, "source_controlled_memory_read"),
        _mutated(valid, ["source_controlled_memory_read", "read_status"], "read_failed"),
        _mutated(valid, ["source_controlled_memory_read", "retrieved_memory_text"], ""),
        _mutated(valid, ["retrieved_memory_text"], ""),
        _mutated(valid, ["preferred_future_tendency"], "retry_same_action"),
        _mutated(valid, ["discouraged_future_tendency"], "check_before_retry"),
        _mutated(valid, ["safe_alternatives"], ["retry_same_action"]),
        _mutated(valid, ["future_runtime_influence_requires_separate_boundary"], False),
        _mutated(valid, ["future_predictor_influence_requires_separate_boundary"], False),
        _mutated(valid, ["future_action_selection_requires_separate_boundary"], False),
        _mutated(valid, ["future_retention_requires_separate_boundary"], False),
        _mutated(valid, ["repo_audit_acknowledged"], False),
        _mutated(valid, ["audit_recorded"], False),
        _mutated(valid, ["rollback_available"], False),
        _mutated(valid, ["rollback_action"], "keep_preview"),
        _mutated(valid, ["source_controlled_memory_read", "source_minimal_memory_record", "runtime_influence_enabled"], True),
        _mutated(valid, ["source_controlled_memory_read", "source_minimal_memory_record", "predictor_read_enabled"], True),
        _mutated(valid, ["source_controlled_memory_read", "source_minimal_memory_record", "predictor_influence_enabled"], True),
        _mutated(valid, ["source_controlled_memory_read", "source_minimal_memory_record", "writes_jsonl"], True),
    ]
    for field in FALSE_PREVIEW_FIELDS:
        records.append(_mutated(valid, [field], True))
    return records


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["valid_preview_count"] == 1
        and summary["invalid_preview_count"] >= 1
        and summary["controlled_memory_read_checked_count"] == 1
        and summary["retrieved_memory_text_checked_count"] == 1
        and summary["preview_generated_count"] == 1
        and summary["preferred_tendency_checked_count"] == 1
        and summary["runtime_influence_blocked_count"] == 1
        and summary["predictor_read_blocked_count"] == 1
        and summary["predictor_mutation_blocked_count"] == 1
        and summary["selected_action_blocked_count"] == 1
        and summary["final_action_blocked_count"] == 1
        and summary["retained_jsonl_write_blocked_count"] == 1
        and summary["retention_write_blocked_count"] == 1
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

    print(json.dumps(run_memory_influence_preview_minimal_check(), indent=2))
