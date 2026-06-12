"""Observe the outcome of a Level 1 sandbox lesson application record."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .level1_sandbox_lesson_application_minimal import (
    build_level1_sandbox_lesson_application,
    validate_level1_sandbox_lesson_application,
)


COMMAND = "run-level1-sandbox-lesson-application-outcome-observation-minimal-check"
FLOW = "level1_sandbox_lesson_application_outcome_observation_minimal_v0"
RECORD_TYPE = "level1_sandbox_lesson_application_outcome_observation"
SCHEMA_VERSION = "level1_sandbox_lesson_application_outcome_observation_minimal_v0"
TARGET_SCOPE = "phase0_level1_sandbox_only"
SOURCE_RECORD_TYPE = "level1_sandbox_lesson_application"
SAFE_CAPABILITY_CLAIM = (
    "ASHL Core can observe the outcome of one reviewed lesson application inside the "
    "Phase0 Level 1 toy sandbox scope only, with explicit user approval, audit, and "
    "rollback, while production/runtime behavior, memory, retention, predictor mutation, "
    "action selection, and proof of learning remain blocked."
)

FORBIDDEN_FLAGS = (
    "production_behavior_changed",
    "runtime_behavior_changed",
    "memory_written",
    "retention_written",
    "predictor_modified",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "generalized_behavior_changed",
    "proof_of_learning_claimed",
)

FORBIDDEN_WORDING = (chr(0x876F) + chr(0x8840) + "?", "?" + chr(0x822A) + "??")


def build_level1_sandbox_lesson_application_outcome_observation(
    source_application_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_application_record is None:
        source_application_record = build_level1_sandbox_lesson_application()

    validation = validate_level1_sandbox_lesson_application(source_application_record)
    audit = source_application_record.get("audit", {})
    rollback = source_application_record.get("rollback", {})
    return {
        "record_type": RECORD_TYPE,
        "schema_version": SCHEMA_VERSION,
        "target_scope": TARGET_SCOPE,
        "source_application": deepcopy(source_application_record),
        "source_application_record_type": source_application_record.get("record_type"),
        "source_application_valid": validation.get("valid") is True,
        "outcome_observed": True,
        "observed_front_symbol": source_application_record.get("front_symbol"),
        "observed_sandbox_action": source_application_record.get("preferred_sandbox_action"),
        "observed_blocks_retry_same_action_until_check": source_application_record.get(
            "blocks_retry_same_action_until_check"
        )
        is True,
        "sandbox_effect_visible": validation.get("sandbox_effect_applied") is True,
        "audit_record_present": isinstance(audit, dict)
        and audit.get("application_audit_recorded") is True
        and audit.get("source_readiness_checked") is True
        and audit.get("source_approval_checked") is True,
        "rollback_record_present": isinstance(rollback, dict) and rollback.get("rollback_available") is True,
        "production_behavior_changed": False,
        "runtime_behavior_changed": False,
        "memory_written": False,
        "retention_written": False,
        "predictor_modified": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "generalized_behavior_changed": False,
        "proof_of_learning_claimed": False,
        "safe_capability_claim": SAFE_CAPABILITY_CLAIM,
        "approval_wording_boundary": "implicit chat command is not application approval",
    }


def check_level1_sandbox_lesson_application_outcome_observation(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != RECORD_TYPE:
        errors.append("record_type_not_level1_sandbox_lesson_application_outcome_observation")
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version_not_level1_sandbox_lesson_application_outcome_observation_minimal_v0")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_phase0_level1_sandbox_only")
    if record.get("source_application_record_type") != SOURCE_RECORD_TYPE:
        errors.append("source_application_record_type_not_level1_sandbox_lesson_application")
    if record.get("source_application_valid") is not True:
        errors.append("source_application_valid_not_true")
    if record.get("outcome_observed") is not True:
        errors.append("outcome_observed_not_true")
    if record.get("observed_front_symbol") != "d":
        errors.append("observed_front_symbol_not_d")
    if record.get("observed_sandbox_action") != "check_before_retry":
        errors.append("observed_sandbox_action_not_check_before_retry")
    if record.get("observed_blocks_retry_same_action_until_check") is not True:
        errors.append("observed_blocks_retry_same_action_until_check_not_true")
    if record.get("sandbox_effect_visible") is not True:
        errors.append("sandbox_effect_visible_not_true")
    if record.get("audit_record_present") is not True:
        errors.append("audit_record_present_not_true")
    if record.get("rollback_record_present") is not True:
        errors.append("rollback_record_present_not_true")

    source_application = record.get("source_application")
    if not isinstance(source_application, dict):
        errors.append("source_application_missing")
        source_application = {}
    source_validation = validate_level1_sandbox_lesson_application(source_application)
    if not source_validation.get("valid"):
        errors.append("source_application_invalid")
    if source_application.get("target_scope") != TARGET_SCOPE:
        errors.append("source_application_target_scope_not_phase0_level1_sandbox_only")
    if source_application.get("front_symbol") != "d":
        errors.append("source_application_front_symbol_not_d")
    if source_application.get("preferred_sandbox_action") != "check_before_retry":
        errors.append("source_application_preferred_sandbox_action_not_check_before_retry")
    if source_application.get("blocks_retry_same_action_until_check") is not True:
        errors.append("source_application_retry_block_not_true")

    for flag in FORBIDDEN_FLAGS:
        if record.get(flag) is not False:
            errors.append(f"{flag}_not_false")

    text = repr(record)
    for forbidden in FORBIDDEN_WORDING:
        if forbidden in text:
            errors.append(f"forbidden_wording_present:{forbidden}")
    if "implicit chat command is not application approval" not in record.get("approval_wording_boundary", ""):
        errors.append("approval_wording_boundary_missing")

    safe_claim = record.get("safe_capability_claim")
    if not isinstance(safe_claim, str) or not safe_claim.strip():
        errors.append("safe_capability_claim_empty")
    else:
        for forbidden_claim in (
            "proof of learning",
            "memory was updated",
            "runtime behavior changed",
            "production behavior changed",
        ):
            if forbidden_claim in safe_claim and "remain blocked" not in safe_claim:
                errors.append("safe_capability_claim_overclaims")

    return {
        "valid": not errors,
        "error_codes": errors,
        "record_type": record.get("record_type"),
        "source_application_checked": source_validation.get("valid") is True,
        "sandbox_effect_observed": (
            record.get("observed_front_symbol") == "d"
            and record.get("observed_sandbox_action") == "check_before_retry"
            and record.get("observed_blocks_retry_same_action_until_check") is True
            and record.get("sandbox_effect_visible") is True
        ),
        "audit_record_confirmed": record.get("audit_record_present") is True,
        "rollback_record_confirmed": record.get("rollback_record_present") is True,
        "blocked_boundary_confirmed": all(record.get(flag) is False for flag in FORBIDDEN_FLAGS),
        "safe_capability_claim": safe_claim,
    }


def build_demo_level1_sandbox_lesson_application_outcome_observation_records() -> list[dict[str, Any]]:
    valid_record = build_level1_sandbox_lesson_application_outcome_observation()
    invalid = [
        _without(valid_record, "source_application"),
        _mutated(valid_record, ["source_application", "target_scope"], "production"),
        _mutated(valid_record, ["source_application", "front_symbol"], "."),
        _mutated(valid_record, ["target_scope"], "production"),
        _mutated(valid_record, ["observed_front_symbol"], "."),
        _mutated(valid_record, ["observed_sandbox_action"], "retry_same_action"),
        _mutated(valid_record, ["observed_blocks_retry_same_action_until_check"], False),
        _mutated(valid_record, ["sandbox_effect_visible"], False),
        _mutated(valid_record, ["audit_record_present"], False),
        _mutated(valid_record, ["rollback_record_present"], False),
        _mutated(valid_record, ["source_application_valid"], False),
        _mutated(valid_record, ["source_application_record_type"], "wrong"),
        _mutated(valid_record, ["approval_wording_boundary"], FORBIDDEN_WORDING[0]),
        _mutated(valid_record, ["approval_wording_boundary"], FORBIDDEN_WORDING[1]),
    ]
    for flag in FORBIDDEN_FLAGS:
        invalid.append(_mutated(valid_record, [flag], True))
    return [valid_record] + invalid


def run_level1_sandbox_lesson_application_outcome_observation_minimal_check() -> dict[str, Any]:
    records = build_demo_level1_sandbox_lesson_application_outcome_observation_records()
    validation_results = [check_level1_sandbox_lesson_application_outcome_observation(record) for record in records]
    valid_results = [item for item in validation_results if item.get("valid")]
    summary = {
        "level1_sandbox_outcome_observation_result_count": len(records),
        "valid_level1_sandbox_outcome_observation_count": len(valid_results),
        "invalid_level1_sandbox_outcome_observation_count": len(records) - len(valid_results),
        "source_application_checked_count": sum(
            1 for item in valid_results if item.get("source_application_checked") is True
        ),
        "sandbox_effect_observed_count": sum(1 for item in valid_results if item.get("sandbox_effect_observed") is True),
        "audit_record_confirmed_count": sum(1 for item in valid_results if item.get("audit_record_confirmed") is True),
        "rollback_record_confirmed_count": sum(
            1 for item in valid_results if item.get("rollback_record_confirmed") is True
        ),
        "blocked_boundary_confirmed_count": sum(
            1 for item in valid_results if item.get("blocked_boundary_confirmed") is True
        ),
    }
    summary["all_level1_sandbox_lesson_application_outcome_observation_checks_passed"] = (
        summary["valid_level1_sandbox_outcome_observation_count"] == 1
        and summary["invalid_level1_sandbox_outcome_observation_count"] >= 1
        and summary["source_application_checked_count"] == 1
        and summary["sandbox_effect_observed_count"] == 1
        and summary["audit_record_confirmed_count"] == 1
        and summary["rollback_record_confirmed_count"] == 1
        and summary["blocked_boundary_confirmed_count"] == 1
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok"
        if summary["all_level1_sandbox_lesson_application_outcome_observation_checks_passed"]
        else "failed",
        "observation_results": records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "outcome_observation_only": True,
            "sandbox_only_scope": True,
            "production_behavior_changed": False,
            "runtime_behavior_changed": False,
            "memory_write": False,
            "retention_write": False,
            "predictor_mutation": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "generalized_behavior_changed": False,
            "proof_of_learning_claimed": False,
        },
    }


def _mutated(record: dict[str, Any], path: list[str], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: dict[str, Any] = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


def _without(record: dict[str, Any], field: str) -> dict[str, Any]:
    clone = deepcopy(record)
    clone.pop(field, None)
    return clone


if __name__ == "__main__":
    import json

    print(
        json.dumps(
            run_level1_sandbox_lesson_application_outcome_observation_minimal_check(),
            ensure_ascii=False,
            indent=2,
        )
    )
