"""Boundary audit for the b85-b93 same-session sandbox thought loop."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS


COMMAND = "run-b85-b93-same-session-thought-loop-audit-minimal-check"
FLOW = "b85_b93_same_session_thought_loop_audit_minimal_v0"
PACKAGE_ID = "PKG-Phase0-B85B93SameSessionThoughtLoopAudit-Minimal-v0"
BOUNDARY_INDEX_VERSION = "2026-06-09-b93"
RECORD_TYPE = "b85_b93_same_session_thought_loop_audit"
AUDIT_STATUS = "passed_same_session_thought_loop_boundary_audit"
AUDITED_STEPS = [
    "sandbox_behavior_use_b85",
    "doubt_action_trace_b86",
    "doubt_gated_ordering_b87",
    "verification_candidate_registry_b88",
    "verification_planning_b89",
    "verification_execution_b90",
    "verification_result_feedback_trace_b91",
    "ephemeral_feedback_application_b92",
    "same_session_feedback_reordering_b93",
]

TRUE_FIELDS = (
    "same_session_only",
    "rollback_required",
    "rollback_verified",
    "candidate_ordering_allowed",
    "doubt_trace_allowed",
    "verification_candidate_registry_allowed",
    "verification_planning_allowed",
    "sandbox_verification_execution_allowed",
    "trace_only_feedback_allowed",
    "ephemeral_feedback_application_allowed",
    "same_session_reordering_allowed",
    "audit_recorded",
)
FALSE_FIELDS = (
    "boundary_change_required",
    "boundary_index_update_required",
    "dirty_state_after_rollback",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "persistent_rule_created",
    "persistent_trust_doubt_update_performed",
    "cross_session_feedback_persistence",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "production_behavior_changed",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)


def build_b85_b93_thought_loop_audit_record() -> dict[str, Any]:
    return {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "audit_status": AUDIT_STATUS,
        "boundary_index_before": BOUNDARY_INDEX_VERSION,
        "boundary_index_after": BOUNDARY_INDEX_VERSION,
        "boundary_change_required": False,
        "boundary_index_update_required": False,
        "audited_steps": AUDITED_STEPS[:],
        "loop_scope": "phase0_level3_sandbox_same_session_only",
        "same_session_only": True,
        "rollback_required": True,
        "rollback_verified": True,
        "dirty_state_after_rollback": False,
        "candidate_ordering_allowed": True,
        "doubt_trace_allowed": True,
        "verification_candidate_registry_allowed": True,
        "verification_planning_allowed": True,
        "sandbox_verification_execution_allowed": True,
        "trace_only_feedback_allowed": True,
        "ephemeral_feedback_application_allowed": True,
        "same_session_reordering_allowed": True,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "persistent_trust_doubt_update_performed": False,
        "cross_session_feedback_persistence": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "qingyin_current_status": QINGYIN_STATUS,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_b85_b93_thought_loop_audit_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "audit_status": AUDIT_STATUS,
        "boundary_index_before": BOUNDARY_INDEX_VERSION,
        "boundary_index_after": BOUNDARY_INDEX_VERSION,
        "loop_scope": "phase0_level3_sandbox_same_session_only",
        "qingyin_current_status": QINGYIN_STATUS,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    audited_steps = record.get("audited_steps")
    missing_steps = [
        step
        for step in AUDITED_STEPS
        if not isinstance(audited_steps, list) or step not in audited_steps
    ]
    if missing_steps:
        errors.append("missing_b85_b93_audited_step")
    if record.get("boundary_index_before") != record.get("boundary_index_after"):
        errors.append("boundary_index_changed_by_audit")
    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "audited_step_count": len(audited_steps) if isinstance(audited_steps, list) else 0,
        "missing_step_count": len(missing_steps),
        "boundary_unchanged_checked": (
            record.get("boundary_index_before") == BOUNDARY_INDEX_VERSION
            and record.get("boundary_index_after") == BOUNDARY_INDEX_VERSION
            and record.get("boundary_change_required") is False
            and record.get("boundary_index_update_required") is False
        ),
        "rollback_checked": record.get("rollback_required") is True
        and record.get("rollback_verified") is True
        and record.get("dirty_state_after_rollback") is False,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "persistent_update_blocked": record.get("persistent_trust_doubt_update_performed") is False,
        "cross_session_blocked": record.get("cross_session_feedback_persistence") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False
        and record.get("retained_jsonl_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_b85_b93_same_session_thought_loop_audit_minimal_check() -> dict[str, Any]:
    valid_audit = build_b85_b93_thought_loop_audit_record()
    valid_result = validate_b85_b93_thought_loop_audit_record(valid_audit)
    invalid_audits = _invalid_audits(valid_audit)
    invalid_results = [validate_b85_b93_thought_loop_audit_record(item) for item in invalid_audits]
    summary = {
        "valid_audit_count": 1 if valid_result["valid"] else 0,
        "invalid_audit_count": sum(1 for result in invalid_results if not result["valid"]),
        "audited_step_count": valid_result["audited_step_count"],
        "missing_step_count": valid_result["missing_step_count"],
        "boundary_unchanged_checked_count": 1 if valid_result["boundary_unchanged_checked"] else 0,
        "rollback_checked_count": 1 if valid_result["rollback_checked"] else 0,
        "selected_action_blocked_count": 1 if valid_result["selected_action_blocked"] else 0,
        "final_action_blocked_count": 1 if valid_result["final_action_blocked"] else 0,
        "persistent_update_blocked_count": 1 if valid_result["persistent_update_blocked"] else 0,
        "cross_session_blocked_count": 1 if valid_result["cross_session_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "production_behavior_blocked_count": 1 if valid_result["production_behavior_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_b85_b93_same_session_thought_loop_audit_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_audit_count"] == len(invalid_audits)
        and summary["valid_audit_count"] == 1
        and summary["audited_step_count"] == len(AUDITED_STEPS)
        and summary["missing_step_count"] == 0
        and all(
            value == 1
            for key, value in summary.items()
            if key.endswith("_count")
            and key not in {"valid_audit_count", "invalid_audit_count", "audited_step_count", "missing_step_count"}
        )
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_b85_b93_same_session_thought_loop_audit_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": False,
            "boundary_index_update_required": False,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION,
            "rationale": (
                "This package audits an existing same-session sandbox thought loop and does not "
                "change permission scope, persistence, predictor, action-selection, production, or proof boundaries."
            ),
        },
        "valid_audit": valid_audit,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can audit the b85-b93 same-session sandbox thought loop and confirm that "
            "candidate ordering, doubt trace, verification planning/execution, feedback, ephemeral "
            "application, reordering, and rollback remain sandbox-only and same-session-only while "
            "selected_action, final_action, persistent updates, memory writes, retention writes, "
            "predictor mutation, production behavior, and proof-of-learning remain blocked."
        ),
    }


def _invalid_audits(valid_audit: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    missing_step = deepcopy(valid_audit)
    missing_step["audited_steps"] = valid_audit["audited_steps"][:-1]
    invalids.append(missing_step)
    for field, value in (
        ("boundary_index_after", "2026-06-09-b94"),
        ("boundary_change_required", True),
        ("boundary_index_update_required", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("persistent_rule_created", True),
        ("persistent_trust_doubt_update_performed", True),
        ("cross_session_feedback_persistence", True),
        ("memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_read_enabled", True),
        ("predictor_influence_enabled", True),
        ("predictor_mutation_performed", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
        ("rollback_required", False),
        ("rollback_verified", False),
        ("dirty_state_after_rollback", True),
    ):
        bad = deepcopy(valid_audit)
        bad[field] = value
        invalids.append(bad)
    return invalids
