"""Audit the b99 sandbox-only final_action boundary."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_final_action_minimal import (
    build_sandbox_final_action_record,
    validate_sandbox_final_action_record,
)
from .test_tier_policy_minimal import (
    build_test_tier_policy_record,
    validate_test_tier_policy_record,
)


COMMAND = "run-b99-sandbox-final-action-boundary-audit-minimal-check"
FLOW = "b99_sandbox_final_action_boundary_audit_minimal_v0"
PACKAGE_ID = "PKG-Phase0-B99SandboxFinalActionBoundaryAudit-Minimal-v0"
BOUNDARY_INDEX = "2026-06-09-b99"
SANDBOX_SCOPE = "phase0_level3_sandbox_only"
FINAL_ACTION = "observe_or_alternative_probe"
EXECUTION_RESULT = "local_context_observed"
AUDITED_STEPS = ("test_tier_policy_b99", "sandbox_final_action_b99")

TRUE_FIELDS = (
    "final_action_created",
    "test_tier_policy_present",
    "test_tier_policy_workflow_only",
    "audit_recorded",
)
FALSE_FIELDS = (
    "boundary_change_required",
    "boundary_index_update_required",
    "direct_command_created",
    "direct_command_allowed",
    "production_behavior_changed",
    "persistent_rule_created",
    "persistent_trust_doubt_update_performed",
    "cross_session_feedback_persistence",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "test_tier_policy_runtime_capability",
    "test_tier_policy_boundary_change_required_by_itself",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)


def build_b99_sandbox_final_action_boundary_audit_record(
    sandbox_final_action_source: dict[str, Any] | None = None,
    test_tier_policy_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    final_action_source = (
        deepcopy(sandbox_final_action_source)
        if sandbox_final_action_source is not None
        else build_sandbox_final_action_record()
    )
    policy_source = (
        deepcopy(test_tier_policy_source)
        if test_tier_policy_source is not None
        else build_test_tier_policy_record()
    )
    return {
        "record_type": "b99_sandbox_final_action_boundary_audit",
        "record_version": "v0",
        "audit_status": "passed_sandbox_final_action_boundary_audit",
        "boundary_index_before": BOUNDARY_INDEX,
        "boundary_index_after": BOUNDARY_INDEX,
        "boundary_change_required": False,
        "boundary_index_update_required": False,
        "source_sandbox_final_action_record": final_action_source,
        "source_test_tier_policy_record": policy_source,
        "audited_steps": list(AUDITED_STEPS),
        "sandbox_scope": SANDBOX_SCOPE,
        "final_action_created": True,
        "final_action": FINAL_ACTION,
        "final_action_scope": "sandbox_only",
        "source_selected_action": FINAL_ACTION,
        "source_execution_result": EXECUTION_RESULT,
        "direct_command_created": False,
        "direct_command_allowed": False,
        "production_behavior_changed": False,
        "persistent_rule_created": False,
        "persistent_trust_doubt_update_performed": False,
        "cross_session_feedback_persistence": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "test_tier_policy_present": True,
        "test_tier_policy_workflow_only": True,
        "test_tier_policy_runtime_capability": False,
        "test_tier_policy_boundary_change_required_by_itself": False,
        "proof_of_learning_claim_allowed": False,
        "qingyin_current_status": "phase0_trace_checker_system",
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_b99_sandbox_final_action_boundary_audit_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    final_action_source = record.get("source_sandbox_final_action_record")
    policy_source = record.get("source_test_tier_policy_record")
    final_action_result = (
        validate_sandbox_final_action_record(final_action_source)
        if isinstance(final_action_source, dict)
        else {"valid": False}
    )
    policy_result = (
        validate_test_tier_policy_record(policy_source)
        if isinstance(policy_source, dict)
        else {"valid": False}
    )
    expected = {
        "record_type": "b99_sandbox_final_action_boundary_audit",
        "record_version": "v0",
        "audit_status": "passed_sandbox_final_action_boundary_audit",
        "boundary_index_before": BOUNDARY_INDEX,
        "boundary_index_after": BOUNDARY_INDEX,
        "sandbox_scope": SANDBOX_SCOPE,
        "final_action": FINAL_ACTION,
        "final_action_scope": "sandbox_only",
        "source_selected_action": FINAL_ACTION,
        "source_execution_result": EXECUTION_RESULT,
        "qingyin_current_status": "phase0_trace_checker_system",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    audited_steps = record.get("audited_steps", [])
    if not isinstance(audited_steps, list) or not set(AUDITED_STEPS).issubset(set(audited_steps)):
        errors.append("audited_steps_missing_required")
    if final_action_result["valid"] is not True:
        errors.append("missing_or_invalid_b99_final_action_source")
    if policy_result["valid"] is not True:
        errors.append("missing_or_invalid_b99_test_tier_policy_source")
    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "audited_step_count": len(set(audited_steps).intersection(AUDITED_STEPS))
        if isinstance(audited_steps, list)
        else 0,
        "missing_step_count": (
            len(set(AUDITED_STEPS) - set(audited_steps)) if isinstance(audited_steps, list) else len(AUDITED_STEPS)
        ),
        "boundary_unchanged_checked": (
            record.get("boundary_index_before") == BOUNDARY_INDEX
            and record.get("boundary_index_after") == BOUNDARY_INDEX
            and record.get("boundary_change_required") is False
            and record.get("boundary_index_update_required") is False
        ),
        "final_action_checked": (
            final_action_result["valid"] is True
            and record.get("final_action_created") is True
            and record.get("final_action") == FINAL_ACTION
        ),
        "sandbox_scope_checked": (
            record.get("sandbox_scope") == SANDBOX_SCOPE
            and record.get("final_action_scope") == "sandbox_only"
        ),
        "direct_command_blocked": (
            record.get("direct_command_created") is False
            and record.get("direct_command_allowed") is False
        ),
        "persistent_update_blocked": (
            record.get("persistent_rule_created") is False
            and record.get("persistent_trust_doubt_update_performed") is False
            and record.get("cross_session_feedback_persistence") is False
        ),
        "memory_write_blocked": (
            record.get("memory_write_performed") is False
            and record.get("retained_jsonl_write_performed") is False
        ),
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": (
            record.get("predictor_read_enabled") is False
            and record.get("predictor_influence_enabled") is False
            and record.get("predictor_mutation_performed") is False
        ),
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "test_policy_workflow_only_checked": (
            policy_result["valid"] is True
            and record.get("test_tier_policy_present") is True
            and record.get("test_tier_policy_workflow_only") is True
            and record.get("test_tier_policy_runtime_capability") is False
            and record.get("test_tier_policy_boundary_change_required_by_itself") is False
        ),
        "proof_claim_blocked": (
            record.get("proof_of_learning_claim_allowed") is False
            and record.get("autonomous_learning_claim_allowed") is False
            and record.get("autonomous_action_claim_allowed") is False
        ),
    }


def run_b99_sandbox_final_action_boundary_audit_minimal_check() -> dict[str, Any]:
    valid_audit = build_b99_sandbox_final_action_boundary_audit_record()
    valid_result = validate_b99_sandbox_final_action_boundary_audit_record(valid_audit)
    invalid_audits = _invalid_audits(valid_audit)
    invalid_results = [
        validate_b99_sandbox_final_action_boundary_audit_record(item) for item in invalid_audits
    ]
    summary = {
        "valid_audit_count": 1 if valid_result["valid"] else 0,
        "invalid_audit_count": sum(1 for result in invalid_results if not result["valid"]),
        "audited_step_count": valid_result["audited_step_count"],
        "missing_step_count": valid_result["missing_step_count"],
        "boundary_unchanged_checked_count": 1 if valid_result["boundary_unchanged_checked"] else 0,
        "final_action_checked_count": 1 if valid_result["final_action_checked"] else 0,
        "sandbox_scope_checked_count": 1 if valid_result["sandbox_scope_checked"] else 0,
        "direct_command_blocked_count": 1 if valid_result["direct_command_blocked"] else 0,
        "persistent_update_blocked_count": 1 if valid_result["persistent_update_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "production_behavior_blocked_count": 1 if valid_result["production_behavior_blocked"] else 0,
        "test_policy_workflow_only_checked_count": (
            1 if valid_result["test_policy_workflow_only_checked"] else 0
        ),
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_b99_sandbox_final_action_boundary_audit_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_audit_count"] == len(invalid_audits)
        and summary["valid_audit_count"] == 1
        and summary["missing_step_count"] == 0
        and summary["audited_step_count"] == 2
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_b99_sandbox_final_action_boundary_audit_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": False,
            "boundary_index_update_required": False,
            "boundary_index_version_before": BOUNDARY_INDEX,
            "boundary_index_version_after": BOUNDARY_INDEX,
            "rationale": (
                "This package audits existing b99 sandbox-only final_action behavior and workflow-only "
                "test-tier policy. It does not change permission scope, runtime behavior condition, "
                "persistence, memory, retention, predictor, direct command, production, or proof boundary."
            ),
        },
        "valid_audit": valid_audit,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can audit the b99 sandbox-only final_action boundary and confirm that the "
            "final_action remains sandbox-only while direct command, persistent updates, memory writes, "
            "retention writes, predictor mutation, production behavior, and proof-of-learning remain "
            "blocked; the test-tier policy is workflow-only and not a runtime capability."
        ),
    }


def _invalid_audits(valid_audit: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("source_sandbox_final_action_record", {}),
        ("source_test_tier_policy_record", {}),
        ("boundary_index_after", "2026-06-09-b100"),
        ("final_action_scope", "production"),
        ("final_action", "retry_same_action_without_check"),
        ("direct_command_created", True),
        ("direct_command_allowed", True),
        ("production_behavior_changed", True),
        ("persistent_rule_created", True),
        ("persistent_trust_doubt_update_performed", True),
        ("cross_session_feedback_persistence", True),
        ("memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_read_enabled", True),
        ("predictor_influence_enabled", True),
        ("predictor_mutation_performed", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
        ("test_tier_policy_runtime_capability", True),
        ("test_tier_policy_boundary_change_required_by_itself", True),
    ):
        bad = deepcopy(valid_audit)
        bad[field] = value
        invalids.append(bad)
    bad = deepcopy(valid_audit)
    bad["audited_steps"] = ["sandbox_final_action_b99"]
    invalids.append(bad)
    bad = deepcopy(valid_audit)
    bad["boundary_change_required"] = True
    invalids.append(bad)
    return invalids
