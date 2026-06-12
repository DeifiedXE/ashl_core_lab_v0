"""Apply one reviewed lesson inside the Phase0 Level 1 sandbox scope only."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .level1_explicit_lesson_application_approval_minimal import (
    APPROVED,
    build_level1_explicit_lesson_application_approval,
    validate_level1_explicit_lesson_application_approval,
)
from .reviewed_lesson_sandbox_application_readiness_minimal import (
    READY_AFTER_APPROVAL_STATUS,
    build_reviewed_lesson_sandbox_application_readiness,
    validate_reviewed_lesson_sandbox_application_readiness,
)


COMMAND = "run-level1-sandbox-lesson-application-minimal-check"
FLOW = "level1_sandbox_lesson_application_minimal_v0"
VERSION = "level1_sandbox_lesson_application_minimal_v0"
RECORD_TYPE = "level1_sandbox_lesson_application"
STATUS = "applied_in_phase0_level1_sandbox_only"
TARGET_SCOPE = "phase0_level1_sandbox_only"
APPROVAL_TEXT = "I explicitly approve a future Phase0 Level 1 sandbox-only lesson application package."

REQUIRED_BLOCKED_BOUNDARIES = {
    "lesson_applied_to_production",
    "runtime_lesson_application",
    "production_behavior_change",
    "runtime_behavior_changed",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_modified",
    "production_action_selection",
    "runtime_action_selection",
    "selected_action",
    "selected_action_created",
    "final_action",
    "final_action_created",
    "direct_action_command",
    "direct_action_command_created",
    "persistent_policy_written",
    "generalized_behavior_change",
    "proof_of_learning_claim",
    "proof_of_learning_claimed",
}


def build_level1_sandbox_lesson_application(
    readiness_record: dict[str, Any] | None = None,
    approval_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if readiness_record is None:
        readiness_record = build_ready_level1_sandbox_application_readiness_fixture()
    if approval_record is None:
        approval_record = build_level1_explicit_lesson_application_approval(
            approval_decision=APPROVED,
            approval_source="explicit_user_statement",
            approval_text=APPROVAL_TEXT,
        )

    approval = approval_record.get("human_application_approval", {})
    return {
        "record_type": RECORD_TYPE,
        "version": VERSION,
        "target_scope": TARGET_SCOPE,
        "application_status": STATUS,
        "readiness_record": deepcopy(readiness_record),
        "approval_record": deepcopy(approval_record),
        "approval_source": approval.get("approval_source"),
        "approval_actor": approval.get("approval_actor"),
        "approver_role": approval.get("approver_role"),
        "approval_text": approval.get("approval_text"),
        "test_user_statement_fixture": approval.get("test_user_statement_fixture") is True,
        "front_symbol": "d",
        "preferred_sandbox_action": "check_before_retry",
        "blocks_retry_same_action_until_check": True,
        "audit": {
            "application_audit_recorded": True,
            "source_readiness_checked": True,
            "source_approval_checked": True,
            "sandbox_scope_checked": True,
            "production_boundary_checked": True,
        },
        "rollback": {
            "rollback_available": True,
            "rollback_scope": "phase0_level1_sandbox_application_record_only",
            "rollback_does_not_touch_memory": True,
            "rollback_does_not_touch_retention": True,
            "rollback_does_not_touch_predictor": True,
            "rollback_does_not_touch_runtime_behavior": True,
        },
        "blocked_boundaries": {field: False for field in sorted(REQUIRED_BLOCKED_BOUNDARIES)},
    }


def build_ready_level1_sandbox_application_readiness_fixture() -> dict[str, Any]:
    record = build_reviewed_lesson_sandbox_application_readiness()
    record = deepcopy(record)
    record["missing_requirements"]["explicit_human_application_approval"] = False
    record["missing_requirements"]["sandbox_application_package_exists"] = True
    record["readiness_result"]["readiness_status"] = READY_AFTER_APPROVAL_STATUS
    record["readiness_result"]["ready_for_application"] = True
    record["readiness_result"]["ready_for_sandbox_application_package"] = True
    record["readiness_result"]["allowed_to_apply_lesson"] = True
    return record


def validate_level1_sandbox_lesson_application(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != RECORD_TYPE:
        errors.append("record_type_not_level1_sandbox_lesson_application")
    if record.get("version") != VERSION:
        errors.append("version_not_level1_sandbox_lesson_application_minimal_v0")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_phase0_level1_sandbox_only")
    if record.get("application_status") != STATUS:
        errors.append("application_status_not_applied_in_phase0_level1_sandbox_only")

    readiness = record.get("readiness_record")
    if not isinstance(readiness, dict):
        errors.append("readiness_record_missing")
        readiness = {}
    readiness_validation = validate_reviewed_lesson_sandbox_application_readiness(readiness)
    if not readiness_validation.get("valid"):
        errors.append("readiness_record_invalid")
    readiness_result = readiness.get("readiness_result", {})
    readiness_scope = readiness.get("application_scope", {})
    if readiness_result.get("ready_for_application") is not True:
        errors.append("readiness_not_ready_for_application")
    if readiness_result.get("allowed_to_apply_lesson") is not True:
        errors.append("readiness_not_allowed_to_apply_lesson")
    if readiness_scope.get("target_scope") != TARGET_SCOPE:
        errors.append("readiness_target_scope_not_phase0_level1_sandbox_only")

    approval_record = record.get("approval_record")
    if not isinstance(approval_record, dict):
        errors.append("approval_record_missing")
        approval_record = {}
    approval_validation = validate_level1_explicit_lesson_application_approval(approval_record)
    if not approval_validation.get("valid"):
        errors.append("approval_record_invalid")
    approval = approval_record.get("human_application_approval", {})
    approval_result = approval_record.get("approval_result", {})
    if approval.get("approval_decision") != APPROVED:
        errors.append("approval_decision_not_approved")
    if approval.get("approval_source") != "explicit_user_statement":
        errors.append("approval_source_not_explicit_user_statement")
    if approval.get("approval_actor") != "user":
        errors.append("approval_actor_not_user")
    if approval.get("approver_role") != "project_owner":
        errors.append("approver_role_not_project_owner")
    if not isinstance(approval.get("approval_text"), str) or not approval.get("approval_text", "").strip():
        errors.append("approval_text_empty")
    if approval.get("codex_self_approval_allowed") is not False:
        errors.append("codex_self_approval_not_blocked")
    if approval.get("ai_self_approval_allowed") is not False:
        errors.append("ai_self_approval_not_blocked")
    if approval.get("demo_fixture_is_real_approval") is not False:
        errors.append("demo_fixture_treated_as_real_approval")
    if approval_result.get("explicit_user_statement_present") is not True:
        errors.append("explicit_user_statement_not_present")

    if record.get("approval_source") != "explicit_user_statement":
        errors.append("record_approval_source_not_explicit_user_statement")
    if record.get("approval_actor") != "user":
        errors.append("record_approval_actor_not_user")
    if record.get("approver_role") != "project_owner":
        errors.append("record_approver_role_not_project_owner")
    if not isinstance(record.get("approval_text"), str) or not record.get("approval_text", "").strip():
        errors.append("record_approval_text_empty")

    if record.get("front_symbol") != "d":
        errors.append("front_symbol_not_d")
    if record.get("preferred_sandbox_action") != "check_before_retry":
        errors.append("preferred_sandbox_action_not_check_before_retry")
    if record.get("blocks_retry_same_action_until_check") is not True:
        errors.append("blocks_retry_same_action_until_check_not_true")

    audit = record.get("audit")
    if not isinstance(audit, dict):
        errors.append("audit_missing")
        audit = {}
    for field in (
        "application_audit_recorded",
        "source_readiness_checked",
        "source_approval_checked",
        "sandbox_scope_checked",
        "production_boundary_checked",
    ):
        if audit.get(field) is not True:
            errors.append(f"{field}_not_true")

    rollback = record.get("rollback")
    if not isinstance(rollback, dict):
        errors.append("rollback_missing")
        rollback = {}
    if rollback.get("rollback_available") is not True:
        errors.append("rollback_available_not_true")
    if rollback.get("rollback_scope") != "phase0_level1_sandbox_application_record_only":
        errors.append("rollback_scope_not_record_only")
    for field in (
        "rollback_does_not_touch_memory",
        "rollback_does_not_touch_retention",
        "rollback_does_not_touch_predictor",
        "rollback_does_not_touch_runtime_behavior",
    ):
        if rollback.get(field) is not True:
            errors.append(f"{field}_not_true")

    blocked = record.get("blocked_boundaries")
    if not isinstance(blocked, dict):
        errors.append("blocked_boundaries_missing")
        blocked = {}
    for field in sorted(REQUIRED_BLOCKED_BOUNDARIES):
        if field not in blocked:
            errors.append(f"missing_blocked_boundary:{field}")
        elif blocked.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "valid": not errors,
        "error_codes": errors,
        "record_type": record.get("record_type"),
        "application_status": record.get("application_status"),
        "target_scope": record.get("target_scope"),
        "sandbox_effect_applied": (
            record.get("front_symbol") == "d"
            and record.get("preferred_sandbox_action") == "check_before_retry"
            and record.get("blocks_retry_same_action_until_check") is True
        ),
        "readiness_checked": readiness_validation.get("valid") is True,
        "approval_checked": approval_validation.get("valid") is True,
        "audit_recorded": audit.get("application_audit_recorded") is True,
        "rollback_available": rollback.get("rollback_available") is True,
        "production_behavior_blocked": blocked.get("production_behavior_change") is False,
        "runtime_behavior_blocked": blocked.get("runtime_behavior_changed") is False,
        "memory_write_blocked": blocked.get("memory_write") is False,
        "retention_write_blocked": blocked.get("retention_write") is False,
        "predictor_mutation_blocked": blocked.get("predictor_modified") is False,
        "final_action_blocked": blocked.get("final_action_created") is False,
        "proof_of_learning_claim_blocked": blocked.get("proof_of_learning_claimed") is False,
    }


def run_level1_sandbox_lesson_application_minimal_check() -> dict[str, Any]:
    valid_record = build_level1_sandbox_lesson_application()
    records = [valid_record] + _build_invalid_records(valid_record)
    validation_results = [validate_level1_sandbox_lesson_application(record) for record in records]
    valid_results = [item for item in validation_results if item["valid"]]
    summary = {
        "level1_sandbox_application_result_count": len(records),
        "valid_level1_sandbox_application_count": len(valid_results),
        "invalid_level1_sandbox_application_count": len(records) - len(valid_results),
        "sandbox_effect_applied_count": sum(1 for item in valid_results if item["sandbox_effect_applied"]),
        "readiness_checked_count": sum(1 for item in valid_results if item["readiness_checked"]),
        "approval_checked_count": sum(1 for item in valid_results if item["approval_checked"]),
        "audit_recorded_count": sum(1 for item in valid_results if item["audit_recorded"]),
        "rollback_available_count": sum(1 for item in valid_results if item["rollback_available"]),
        "memory_write_blocked_count": sum(1 for item in valid_results if item["memory_write_blocked"]),
        "retention_write_blocked_count": sum(1 for item in valid_results if item["retention_write_blocked"]),
        "predictor_mutation_blocked_count": sum(1 for item in valid_results if item["predictor_mutation_blocked"]),
        "runtime_behavior_blocked_count": sum(1 for item in valid_results if item["runtime_behavior_blocked"]),
        "final_action_blocked_count": sum(1 for item in valid_results if item["final_action_blocked"]),
        "proof_of_learning_claim_blocked_count": sum(
            1 for item in valid_results if item["proof_of_learning_claim_blocked"]
        ),
    }
    summary["all_level1_sandbox_lesson_application_minimal_checks_passed"] = (
        summary["valid_level1_sandbox_application_count"] == 1
        and summary["invalid_level1_sandbox_application_count"] >= 1
        and summary["sandbox_effect_applied_count"] == 1
        and summary["readiness_checked_count"] == 1
        and summary["approval_checked_count"] == 1
        and summary["audit_recorded_count"] == 1
        and summary["rollback_available_count"] == 1
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_level1_sandbox_lesson_application_minimal_checks_passed"] else "failed",
        "application_results": records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "sandbox_only_application": True,
            "production_lesson_application": False,
            "runtime_lesson_application": False,
            "memory_write": False,
            "retention_write": False,
            "predictor_mutation": False,
            "runtime_behavior_change": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_action_command_created": False,
            "proof_of_learning_claimed": False,
        },
    }


def _build_invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalid: list[dict[str, Any]] = []
    invalid.append(_without(valid_record, "readiness_record"))
    invalid.append(_mutated(valid_record, ["readiness_record", "readiness_mode"], "bad"))
    invalid.append(_mutated(valid_record, ["readiness_record", "readiness_result", "ready_for_application"], False))
    invalid.append(_mutated(valid_record, ["readiness_record", "readiness_result", "allowed_to_apply_lesson"], False))
    invalid.append(_without(valid_record, "approval_record"))
    invalid.append(_mutated(valid_record, ["approval_record", "human_application_approval", "approval_decision"], "rejected_for_application"))
    invalid.append(_mutated(valid_record, ["approval_record", "human_application_approval", "approval_decision"], "needs_more_evidence_before_application"))
    invalid.append(_mutated(valid_record, ["approval_record", "human_application_approval", "approval_source"], "test_fixture"))
    invalid.append(_mutated(valid_record, ["approval_record", "human_application_approval", "approval_source"], "codex_generated"))
    invalid.append(_mutated(valid_record, ["approval_record", "human_application_approval", "approval_source"], "ai_generated"))
    invalid.append(_mutated(valid_record, ["approval_record", "human_application_approval", "approval_actor"], "codex"))
    invalid.append(_mutated(valid_record, ["approval_record", "human_application_approval", "approval_actor"], "ai"))
    invalid.append(_mutated(valid_record, ["approval_record", "human_application_approval", "approver_role"], "codex"))
    invalid.append(_mutated(valid_record, ["approval_record", "human_application_approval", "approver_role"], "ai"))
    invalid.append(_mutated(valid_record, ["approval_record", "human_application_approval", "approval_text"], ""))
    invalid.append(_mutated(valid_record, ["approval_record", "human_application_approval", "demo_fixture_is_real_approval"], True))
    invalid.append(_mutated(valid_record, ["target_scope"], "production"))
    invalid.append(_mutated(valid_record, ["front_symbol"], "."))
    invalid.append(_mutated(valid_record, ["preferred_sandbox_action"], "retry_same_action"))
    invalid.append(_mutated(valid_record, ["blocks_retry_same_action_until_check"], False))
    for field in (
        "application_audit_recorded",
        "source_readiness_checked",
        "source_approval_checked",
        "sandbox_scope_checked",
        "production_boundary_checked",
    ):
        invalid.append(_mutated(valid_record, ["audit", field], False))
    invalid.append(_without(valid_record, "audit"))
    invalid.append(_mutated(valid_record, ["rollback", "rollback_available"], False))
    invalid.append(_mutated(valid_record, ["rollback", "rollback_scope"], "runtime"))
    for field in (
        "rollback_does_not_touch_memory",
        "rollback_does_not_touch_retention",
        "rollback_does_not_touch_predictor",
        "rollback_does_not_touch_runtime_behavior",
    ):
        invalid.append(_mutated(valid_record, ["rollback", field], False))
    invalid.append(_without(valid_record, "rollback"))
    for field in sorted(REQUIRED_BLOCKED_BOUNDARIES):
        invalid.append(_mutated(valid_record, ["blocked_boundaries", field], True))
    return invalid


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

    print(json.dumps(run_level1_sandbox_lesson_application_minimal_check(), ensure_ascii=False, indent=2))
