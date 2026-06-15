"""Boundary approval and trace-only doubt pressure checks for future sandbox selected_action."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-sandbox-selected-action-approval-and-doubt-pressure-trace-minimal-check"
FLOW = "sandbox_selected_action_approval_and_doubt_pressure_trace_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxSelectedActionApprovalAndDoubtPressureTrace-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b93"
BOUNDARY_INDEX_AFTER = "2026-06-09-b94"


APPROVAL_FALSE_FIELDS = (
    "implementation_in_this_package",
    "selected_action_created",
    "final_action_created",
    "final_action_allowed",
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
APPROVAL_TRUE_FIELDS = (
    "required_source_loop_audited",
    "required_source_loop_same_session_only",
    "required_source_loop_rollback_verified",
    "selected_action_allowed_in_future_package",
    "future_final_action_requires_separate_boundary",
    "future_direct_command_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "future_memory_write_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "future_production_promotion_requires_separate_boundary",
    "audit_recorded",
    "rollback_available",
)
PRESSURE_FALSE_FIELDS = (
    "pressure_effect_applied_to_runtime",
    "pressure_effect_persisted",
    "never_try_state_allowed",
    "permanent_action_ban_allowed",
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
    "llm_used",
)
PRESSURE_TRUE_FIELDS = (
    "trace_only",
    "paranoia_guard_enabled",
    "verification_budget_required",
    "stop_condition_required",
    "low_risk_action_still_allowed",
    "audit_recorded",
    "rollback_available",
)
SUMMARY_FALSE_FIELDS = (
    "selected_action_created",
    "pressure_runtime_effect_applied",
    "pressure_persisted",
    "final_action_created",
    "direct_command_created",
    "persistent_rule_created",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "production_behavior_changed",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)
SUMMARY_TRUE_FIELDS = (
    "boundary_change_required",
    "boundary_index_update_required",
    "selected_action_approval_boundary_created",
    "cortisol_like_pressure_trace_created",
    "paranoia_guard_passed",
    "future_selected_action_requires_separate_implementation_package",
    "future_pressure_runtime_application_requires_separate_boundary",
    "audit_recorded",
)


def build_sandbox_selected_action_approval_record() -> dict[str, Any]:
    return {
        "record_type": "sandbox_selected_action_approval_boundary",
        "record_version": "v0",
        "approval_status": "approved_for_future_sandbox_selected_action_package_only",
        "approval_scope": "future_sandbox_only_selected_action_from_ranked_candidate_ordering",
        "source_boundary_index": BOUNDARY_INDEX_BEFORE,
        "required_source_loop": "b85_b93_same_session_thought_loop",
        "required_source_loop_audited": True,
        "required_source_loop_same_session_only": True,
        "required_source_loop_rollback_verified": True,
        "allowed_next_package": "Sandbox Selected Action Minimal v0",
        "allowed_future_behavior": "convert_top_ranked_sandbox_candidate_to_selected_action",
        "implementation_in_this_package": False,
        "selected_action_created": False,
        "selected_action_allowed_in_future_package": True,
        "final_action_created": False,
        "final_action_allowed": False,
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
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "future_final_action_requires_separate_boundary": True,
        "future_direct_command_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "audit_recorded": True,
        "rollback_available": True,
    }


def validate_sandbox_selected_action_approval_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_selected_action_approval_boundary",
        "record_version": "v0",
        "approval_status": "approved_for_future_sandbox_selected_action_package_only",
        "approval_scope": "future_sandbox_only_selected_action_from_ranked_candidate_ordering",
        "source_boundary_index": BOUNDARY_INDEX_BEFORE,
        "required_source_loop": "b85_b93_same_session_thought_loop",
        "allowed_next_package": "Sandbox Selected Action Minimal v0",
        "allowed_future_behavior": "convert_top_ranked_sandbox_candidate_to_selected_action",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    for field in APPROVAL_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in APPROVAL_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "source_loop_checked": record.get("required_source_loop_audited") is True
        and record.get("required_source_loop_same_session_only") is True,
        "rollback_checked": record.get("required_source_loop_rollback_verified") is True
        and record.get("rollback_available") is True,
        "future_selected_action_approval_checked": record.get("selected_action_allowed_in_future_package") is True
        and record.get("implementation_in_this_package") is False,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False and record.get("final_action_allowed") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False
        and record.get("retained_jsonl_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_cortisol_like_doubt_pressure_trace() -> dict[str, Any]:
    return {
        "record_type": "cortisol_like_doubt_pressure_trace",
        "record_version": "v0",
        "trace_status": "valid_trace_only_pressure_signal",
        "pressure_signal_name": "cortisol_like_doubt_pressure",
        "pressure_source": "expected_actual_mismatch_plus_recent_uncertainty",
        "pressure_before": 0.20,
        "pressure_after": 0.45,
        "pressure_delta": 0.25,
        "doubt_weight_before": 0.61,
        "doubt_weight_after_pressure_preview": 0.71,
        "strategy_shift_weight_before": 0.50,
        "strategy_shift_weight_after_pressure_preview": 0.60,
        "direct_retry_weight_before": 0.35,
        "direct_retry_weight_after_pressure_preview": 0.30,
        "pressure_effect_applied_to_runtime": False,
        "pressure_effect_persisted": False,
        "trace_only": True,
        "paranoia_guard_enabled": True,
        "paranoia_guard_status": "passed",
        "verification_budget_required": True,
        "stop_condition_required": True,
        "low_risk_action_still_allowed": True,
        "never_try_state_allowed": False,
        "permanent_action_ban_allowed": False,
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
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "llm_used": False,
        "audit_recorded": True,
        "rollback_available": True,
    }


def validate_cortisol_like_doubt_pressure_trace(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "cortisol_like_doubt_pressure_trace",
        "record_version": "v0",
        "trace_status": "valid_trace_only_pressure_signal",
        "pressure_signal_name": "cortisol_like_doubt_pressure",
        "pressure_source": "expected_actual_mismatch_plus_recent_uncertainty",
        "paranoia_guard_status": "passed",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if record.get("pressure_after", 0) <= record.get("pressure_before", 0):
        errors.append("pressure_after_not_greater_than_before")
    if round(record.get("pressure_after", 0) - record.get("pressure_before", 0), 2) != record.get("pressure_delta"):
        errors.append("pressure_delta_mismatch")
    if record.get("doubt_weight_after_pressure_preview", 0) < record.get("doubt_weight_before", 0):
        errors.append("doubt_weight_not_increased")
    if record.get("strategy_shift_weight_after_pressure_preview", 0) < record.get("strategy_shift_weight_before", 0):
        errors.append("strategy_shift_weight_not_increased")
    if record.get("direct_retry_weight_after_pressure_preview", 1) > record.get("direct_retry_weight_before", 0):
        errors.append("direct_retry_weight_not_lowered")
    for field in PRESSURE_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in PRESSURE_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "paranoia_guard_checked": record.get("paranoia_guard_enabled") is True
        and record.get("paranoia_guard_status") == "passed",
        "low_risk_action_allowed_checked": record.get("low_risk_action_still_allowed") is True
        and record.get("never_try_state_allowed") is False
        and record.get("permanent_action_ban_allowed") is False,
        "pressure_runtime_application_blocked": record.get("pressure_effect_applied_to_runtime") is False,
        "pressure_persistence_blocked": record.get("pressure_effect_persisted") is False,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False
        and record.get("retained_jsonl_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_combined_boundary_summary() -> dict[str, Any]:
    return {
        "record_type": "selected_action_approval_and_pressure_trace_boundary_summary",
        "record_version": "v0",
        "summary_status": "combined_boundary_validated",
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "selected_action_approval_boundary_created": True,
        "selected_action_created": False,
        "cortisol_like_pressure_trace_created": True,
        "pressure_runtime_effect_applied": False,
        "pressure_persisted": False,
        "paranoia_guard_passed": True,
        "future_selected_action_requires_separate_implementation_package": True,
        "future_pressure_runtime_application_requires_separate_boundary": True,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_combined_boundary_summary(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "selected_action_approval_and_pressure_trace_boundary_summary",
        "record_version": "v0",
        "summary_status": "combined_boundary_validated",
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    for field in SUMMARY_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in SUMMARY_FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "pressure_runtime_application_blocked": record.get("pressure_runtime_effect_applied") is False,
        "pressure_persistence_blocked": record.get("pressure_persisted") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_sandbox_selected_action_approval_and_doubt_pressure_trace_minimal_check() -> dict[str, Any]:
    approval = build_sandbox_selected_action_approval_record()
    pressure = build_cortisol_like_doubt_pressure_trace()
    summary_record = build_combined_boundary_summary()
    approval_result = validate_sandbox_selected_action_approval_record(approval)
    pressure_result = validate_cortisol_like_doubt_pressure_trace(pressure)
    summary_result = validate_combined_boundary_summary(summary_record)
    invalid_approvals = _invalid_approval_records(approval)
    invalid_pressures = _invalid_pressure_records(pressure)
    invalid_summaries = _invalid_summary_records(summary_record)
    invalid_approval_results = [validate_sandbox_selected_action_approval_record(record) for record in invalid_approvals]
    invalid_pressure_results = [validate_cortisol_like_doubt_pressure_trace(record) for record in invalid_pressures]
    invalid_summary_results = [validate_combined_boundary_summary(record) for record in invalid_summaries]
    summary = {
        "valid_selected_action_approval_count": 1 if approval_result["valid"] else 0,
        "invalid_selected_action_approval_count": sum(1 for result in invalid_approval_results if not result["valid"]),
        "valid_pressure_trace_count": 1 if pressure_result["valid"] else 0,
        "invalid_pressure_trace_count": sum(1 for result in invalid_pressure_results if not result["valid"]),
        "valid_combined_summary_count": 1 if summary_result["valid"] else 0,
        "invalid_combined_summary_count": sum(1 for result in invalid_summary_results if not result["valid"]),
        "source_loop_checked_count": 1 if approval_result["source_loop_checked"] else 0,
        "rollback_checked_count": 1 if approval_result["rollback_checked"] else 0,
        "paranoia_guard_checked_count": 1 if pressure_result["paranoia_guard_checked"] else 0,
        "low_risk_action_allowed_checked_count": 1 if pressure_result["low_risk_action_allowed_checked"] else 0,
        "future_selected_action_approval_checked_count": 1
        if approval_result["future_selected_action_approval_checked"]
        else 0,
        "selected_action_blocked_count": 1
        if approval_result["selected_action_blocked"]
        and pressure_result["selected_action_blocked"]
        and summary_result["selected_action_blocked"]
        else 0,
        "final_action_blocked_count": 1
        if approval_result["final_action_blocked"]
        and pressure_result["final_action_blocked"]
        and summary_result["final_action_blocked"]
        else 0,
        "pressure_runtime_application_blocked_count": 1
        if pressure_result["pressure_runtime_application_blocked"]
        and summary_result["pressure_runtime_application_blocked"]
        else 0,
        "pressure_persistence_blocked_count": 1
        if pressure_result["pressure_persistence_blocked"] and summary_result["pressure_persistence_blocked"]
        else 0,
        "memory_write_blocked_count": 1
        if approval_result["memory_write_blocked"]
        and pressure_result["memory_write_blocked"]
        and summary_result["memory_write_blocked"]
        else 0,
        "retention_blocked_count": 1
        if approval_result["retention_blocked"] and pressure_result["retention_blocked"] and summary_result["retention_blocked"]
        else 0,
        "predictor_mutation_blocked_count": 1
        if approval_result["predictor_mutation_blocked"]
        and pressure_result["predictor_mutation_blocked"]
        and summary_result["predictor_mutation_blocked"]
        else 0,
        "production_behavior_blocked_count": 1
        if approval_result["production_behavior_blocked"]
        and pressure_result["production_behavior_blocked"]
        and summary_result["production_behavior_blocked"]
        else 0,
        "proof_claim_blocked_count": 1
        if approval_result["proof_claim_blocked"]
        and pressure_result["proof_claim_blocked"]
        and summary_result["proof_claim_blocked"]
        else 0,
    }
    summary["all_sandbox_selected_action_approval_and_doubt_pressure_trace_checks_passed"] = (
        approval_result["valid"]
        and pressure_result["valid"]
        and summary_result["valid"]
        and summary["invalid_selected_action_approval_count"] == len(invalid_approvals)
        and summary["invalid_pressure_trace_count"] == len(invalid_pressures)
        and summary["invalid_combined_summary_count"] == len(invalid_summaries)
        and all(value == 1 for key, value in summary.items() if key.endswith("_count") and key.startswith("valid_"))
        and all(
            value == 1
            for key, value in summary.items()
            if key.endswith("_count") and "invalid" not in key and not key.startswith("valid_")
        )
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok"
        if summary["all_sandbox_selected_action_approval_and_doubt_pressure_trace_checks_passed"]
        else "failed",
        "package_id": PACKAGE_ID,
        "selected_action_approval": approval,
        "pressure_trace": pressure,
        "combined_summary": summary_record,
        "validation": {
            "selected_action_approval": approval_result,
            "pressure_trace": pressure_result,
            "combined_summary": summary_result,
        },
        "invalid_results": {
            "selected_action_approval": invalid_approval_results,
            "pressure_trace": invalid_pressure_results,
            "combined_summary": invalid_summary_results,
        },
        "summary": summary,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "rationale": (
                "Creates an explicit approval boundary for a future sandbox-only selected_action package "
                "and introduces a trace-only cortisol-like doubt pressure validation boundary; no selected_action, "
                "final_action, direct command, predictor mutation, production behavior, memory write, retained JSONL "
                "write, retention write, persistent update, or proof-of-learning is created."
            ),
        },
        "safe_claim": (
            "ASHL Core can validate an explicit approval boundary for a future sandbox-only selected_action package "
            "and produce a trace-only cortisol-like doubt pressure signal with paranoia guard, while no selected_action "
            "is created yet and final_action, direct command, persistent updates, memory writes, retention writes, "
            "predictor mutation, production behavior, pressure persistence, pressure runtime application, and "
            "proof-of-learning remain blocked."
        ),
    }


def _invalid_approval_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("required_source_loop_audited", False),
        ("required_source_loop_rollback_verified", False),
        ("implementation_in_this_package", True),
        ("selected_action_created", True),
        ("final_action_allowed", True),
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
        ("future_final_action_requires_separate_boundary", False),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _invalid_pressure_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("pressure_after", 0.20),
        ("doubt_weight_after_pressure_preview", 0.50),
        ("strategy_shift_weight_after_pressure_preview", 0.40),
        ("direct_retry_weight_after_pressure_preview", 0.40),
        ("pressure_effect_applied_to_runtime", True),
        ("pressure_effect_persisted", True),
        ("trace_only", False),
        ("never_try_state_allowed", True),
        ("permanent_action_ban_allowed", True),
        ("paranoia_guard_enabled", False),
        ("paranoia_guard_status", "missing"),
        ("low_risk_action_still_allowed", False),
        ("verification_budget_required", False),
        ("stop_condition_required", False),
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
        ("llm_used", True),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


def _invalid_summary_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("boundary_index_before", "2026-06-09-b92"),
        ("boundary_index_after", BOUNDARY_INDEX_BEFORE),
        ("boundary_change_required", False),
        ("boundary_index_update_required", False),
        ("selected_action_approval_boundary_created", False),
        ("selected_action_created", True),
        ("cortisol_like_pressure_trace_created", False),
        ("pressure_runtime_effect_applied", True),
        ("pressure_persisted", True),
        ("paranoia_guard_passed", False),
        ("future_selected_action_requires_separate_implementation_package", False),
        ("future_pressure_runtime_application_requires_separate_boundary", False),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("memory_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_read_enabled", True),
        ("predictor_influence_enabled", True),
        ("predictor_mutation_performed", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
    ):
        bad = deepcopy(valid_record)
        bad[field] = value
        invalids.append(bad)
    return invalids


if __name__ == "__main__":
    import json

    print(json.dumps(run_sandbox_selected_action_approval_and_doubt_pressure_trace_minimal_check(), ensure_ascii=False, indent=2))
