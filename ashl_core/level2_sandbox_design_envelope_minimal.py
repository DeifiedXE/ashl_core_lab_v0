"""Define a design-only envelope for a future Level 2 sandbox package."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .level1_sandbox_review_conclusion_and_level2_readiness_precheck_minimal import (
    CONCLUSION_PASSED,
    PRECHECK_READY,
    build_level1_sandbox_review_conclusion_and_level2_readiness_precheck,
    validate_level1_sandbox_review_conclusion_and_level2_readiness_precheck,
)


COMMAND = "run-level2-sandbox-design-envelope-minimal-check"
FLOW = "level2_sandbox_design_envelope_minimal_v0"
RECORD_TYPE = "level2_sandbox_design_envelope"
VERSION = "minimal_v0"
TARGET_SCOPE = "phase0_level2_sandbox_design_only"
DESIGN_STATUS = "defined_for_future_package_only"
SAFE_CLAIM = (
    "ASHL Core can define a design-only envelope for a future Phase0 Level 2 sandbox package, "
    "requiring valid Level 1 review conclusion and Level 2 readiness precheck, while Level 2 "
    "application/execution, runtime behavior change, memory or retained JSONL writes, retention "
    "writes, predictor mutation, selected_action, final_action, production promotion, and "
    "proof-of-learning claims remain blocked."
)

ALLOWED_FUTURE_LEVEL2_CAPABILITIES = (
    "multi_step_sandbox_trace",
    "bounded_counterfactual_check",
    "sandbox_only_failure_reason_comparison",
    "sandbox_only_expected_vs_actual_outcome_comparison",
)
FORBIDDEN_CAPABILITIES = (
    "production_behavior_change",
    "runtime_behavior_change",
    "memory_write",
    "retained_jsonl_write",
    "retention_write",
    "predictor_mutation",
    "selected_action",
    "final_action",
    "direct_action_command",
    "proof_of_learning_claim",
    "level2_execution_now",
    "level2_application_now",
)
REQUIRED_FUTURE_INPUTS = (
    "valid_level1_review_conclusion",
    "valid_level2_readiness_precheck",
    "explicit_future_level2_package_scope",
    "stop_conditions_defined",
    "rollback_plan_defined",
    "audit_plan_defined",
)
STOP_CONDITIONS = (
    "missing_valid_level1_review_conclusion",
    "missing_valid_level2_readiness_precheck",
    "attempted_runtime_behavior_change",
    "attempted_memory_or_retention_write",
    "attempted_predictor_mutation",
    "attempted_selected_or_final_action",
    "attempted_proof_of_learning_claim",
    "attempted_production_promotion",
)
FORBIDDEN_BOOLEAN_FIELDS = (
    "level2_execution_allowed",
    "level2_application_allowed",
    "production_behavior_change_allowed",
    "runtime_behavior_change_allowed",
    "memory_write_created",
    "retained_jsonl_write_created",
    "retention_write_created",
    "predictor_mutation_created",
    "selected_action_created",
    "final_action_created",
    "direct_action_command_created",
    "proof_of_learning_claim_created",
    "task_queue_completed_status_is_approval",
    "passing_tests_are_approval",
    "codex_generated_status_is_approval",
)
REQUIRED_FIELDS = (
    "record_type",
    "version",
    "source_level1_review_conclusion",
    "source_level2_readiness_precheck",
    "target_scope",
    "design_envelope_status",
    "allowed_future_level2_capabilities",
    "forbidden_capabilities",
    "required_future_inputs",
    "stop_conditions",
    "audit_required",
    "rollback_required",
    "human_review_required_before_future_level2_application",
    "safe_claim",
) + FORBIDDEN_BOOLEAN_FIELDS


def build_level2_sandbox_design_envelope(
    source_review_precheck: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_review_precheck is None:
        source_review_precheck = build_level1_sandbox_review_conclusion_and_level2_readiness_precheck()

    source_is_dict = isinstance(source_review_precheck, dict)
    source = source_review_precheck if source_is_dict else {}
    source_validation = (
        validate_level1_sandbox_review_conclusion_and_level2_readiness_precheck(source)
        if source_is_dict
        else {"valid": False}
    )
    source_level1_valid = (
        source_validation.get("valid") is True
        and source.get("level1_review_conclusion_status") == CONCLUSION_PASSED
    )
    source_level2_precheck_valid = (
        source_validation.get("valid") is True
        and source.get("level2_readiness_precheck_status") == PRECHECK_READY
        and source.get("level2_application_allowed") is False
        and source.get("level2_execution_allowed") is False
    )

    return {
        "record_type": RECORD_TYPE,
        "version": VERSION,
        "source_level1_review_conclusion": {
            "record_type": source.get("record_type"),
            "level1_review_conclusion_status": source.get("level1_review_conclusion_status"),
            "valid_level1_review_conclusion": source_level1_valid,
        },
        "source_level2_readiness_precheck": {
            "level2_readiness_precheck_status": source.get("level2_readiness_precheck_status"),
            "valid_level2_readiness_precheck": source_level2_precheck_valid,
            "level2_application_allowed": source.get("level2_application_allowed") is True,
            "level2_execution_allowed": source.get("level2_execution_allowed") is True,
        },
        "source_review_precheck_record": deepcopy(source_review_precheck) if source_is_dict else None,
        "target_scope": TARGET_SCOPE,
        "level2_execution_allowed": False,
        "level2_application_allowed": False,
        "design_envelope_status": DESIGN_STATUS,
        "allowed_future_level2_capabilities": list(ALLOWED_FUTURE_LEVEL2_CAPABILITIES),
        "forbidden_capabilities": list(FORBIDDEN_CAPABILITIES),
        "required_future_inputs": list(REQUIRED_FUTURE_INPUTS),
        "stop_conditions": list(STOP_CONDITIONS),
        "audit_required": True,
        "rollback_required": True,
        "human_review_required_before_future_level2_application": True,
        "production_behavior_change_allowed": False,
        "runtime_behavior_change_allowed": False,
        "memory_write_created": False,
        "retained_jsonl_write_created": False,
        "retention_write_created": False,
        "predictor_mutation_created": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_action_command_created": False,
        "proof_of_learning_claim_created": False,
        "task_queue_completed_status_is_approval": False,
        "passing_tests_are_approval": False,
        "codex_generated_status_is_approval": False,
        "safe_claim": SAFE_CLAIM,
    }


def validate_level2_sandbox_design_envelope(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing_field:{field}")
    if record.get("record_type") != RECORD_TYPE:
        errors.append("record_type_not_level2_sandbox_design_envelope")
    if record.get("version") != VERSION:
        errors.append("version_not_minimal_v0")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_phase0_level2_sandbox_design_only")
    if record.get("design_envelope_status") != DESIGN_STATUS:
        errors.append("design_envelope_status_not_defined_for_future_package_only")
    for field in FORBIDDEN_BOOLEAN_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if record.get("audit_required") is not True:
        errors.append("audit_required_not_true")
    if record.get("rollback_required") is not True:
        errors.append("rollback_required_not_true")
    if record.get("human_review_required_before_future_level2_application") is not True:
        errors.append("human_review_required_before_future_level2_application_not_true")

    source_level1 = record.get("source_level1_review_conclusion")
    if not isinstance(source_level1, dict):
        errors.append("source_level1_review_conclusion_not_dict")
        source_level1 = {}
    if source_level1.get("valid_level1_review_conclusion") is not True:
        errors.append("valid_level1_review_conclusion_not_true")
    if source_level1.get("level1_review_conclusion_status") != CONCLUSION_PASSED:
        errors.append("level1_review_conclusion_status_not_passed")

    source_level2 = record.get("source_level2_readiness_precheck")
    if not isinstance(source_level2, dict):
        errors.append("source_level2_readiness_precheck_not_dict")
        source_level2 = {}
    if source_level2.get("valid_level2_readiness_precheck") is not True:
        errors.append("valid_level2_readiness_precheck_not_true")
    if source_level2.get("level2_readiness_precheck_status") != PRECHECK_READY:
        errors.append("level2_readiness_precheck_status_not_ready")
    if source_level2.get("level2_application_allowed") is not False:
        errors.append("source_level2_application_allowed_not_false")
    if source_level2.get("level2_execution_allowed") is not False:
        errors.append("source_level2_execution_allowed_not_false")

    if set(record.get("allowed_future_level2_capabilities", [])) != set(ALLOWED_FUTURE_LEVEL2_CAPABILITIES):
        errors.append("allowed_future_level2_capabilities_not_explicit")
    if set(record.get("forbidden_capabilities", [])) != set(FORBIDDEN_CAPABILITIES):
        errors.append("forbidden_capabilities_not_explicit")
    if set(record.get("required_future_inputs", [])) != set(REQUIRED_FUTURE_INPUTS):
        errors.append("required_future_inputs_not_explicit")
    if set(record.get("stop_conditions", [])) != set(STOP_CONDITIONS):
        errors.append("stop_conditions_not_explicit")
    if record.get("safe_claim") != SAFE_CLAIM:
        errors.append("safe_claim_not_allowed")

    return {
        "valid": not errors,
        "error_codes": errors,
        "record_type": record.get("record_type"),
        "level2_execution_allowed": record.get("level2_execution_allowed") is True,
        "level2_application_allowed": record.get("level2_application_allowed") is True,
        "forbidden_capabilities_blocked": all(record.get(field) is False for field in FORBIDDEN_BOOLEAN_FIELDS),
        "audit_required": record.get("audit_required") is True,
        "rollback_required": record.get("rollback_required") is True,
        "human_review_required": record.get("human_review_required_before_future_level2_application") is True,
    }


def run_level2_sandbox_design_envelope_minimal_check() -> dict[str, Any]:
    records = _demo_records()
    validation_results = [validate_level2_sandbox_design_envelope(record) for record in records]
    valid_results = [result for result in validation_results if result.get("valid")]
    summary = {
        "level2_sandbox_design_envelope_result_count": len(records),
        "valid_level2_sandbox_design_envelope_count": len(valid_results),
        "invalid_level2_sandbox_design_envelope_count": len(records) - len(valid_results),
        "level2_execution_allowed_count": sum(
            1 for result in valid_results if result.get("level2_execution_allowed") is True
        ),
        "level2_application_allowed_count": sum(
            1 for result in valid_results if result.get("level2_application_allowed") is True
        ),
        "forbidden_capability_blocked_count": sum(
            1 for result in valid_results if result.get("forbidden_capabilities_blocked") is True
        ),
        "audit_required_count": sum(1 for result in valid_results if result.get("audit_required") is True),
        "rollback_required_count": sum(1 for result in valid_results if result.get("rollback_required") is True),
        "human_review_required_count": sum(1 for result in valid_results if result.get("human_review_required") is True),
    }
    summary["all_level2_sandbox_design_envelope_checks_passed"] = (
        summary["valid_level2_sandbox_design_envelope_count"] == 1
        and summary["invalid_level2_sandbox_design_envelope_count"] >= 1
        and summary["level2_execution_allowed_count"] == 0
        and summary["level2_application_allowed_count"] == 0
        and summary["forbidden_capability_blocked_count"] == 1
        and summary["audit_required_count"] == 1
        and summary["rollback_required_count"] == 1
        and summary["human_review_required_count"] == 1
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_level2_sandbox_design_envelope_checks_passed"] else "failed",
        "design_envelope_results": records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "design_only": True,
            "level2_execution_allowed": False,
            "level2_application_allowed": False,
            "runtime_behavior_change_added": False,
            "memory_write_added": False,
            "retained_jsonl_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_action_command_created": False,
            "production_promotion_added": False,
            "approval_replay_session_binding_added": False,
            "proof_of_learning_claimed": False,
        },
    }


def _demo_records() -> list[dict[str, Any]]:
    valid = build_level2_sandbox_design_envelope()
    missing_level1 = _mutated(valid, ["source_level1_review_conclusion", "valid_level1_review_conclusion"], False)
    missing_precheck = _mutated(valid, ["source_level2_readiness_precheck", "valid_level2_readiness_precheck"], False)
    invalid = [
        missing_level1,
        missing_precheck,
        _mutated(valid, ["target_scope"], "production"),
        _mutated(valid, ["level2_execution_allowed"], True),
        _mutated(valid, ["level2_application_allowed"], True),
        _mutated(valid, ["production_behavior_change_allowed"], True),
        _mutated(valid, ["runtime_behavior_change_allowed"], True),
        _mutated(valid, ["memory_write_created"], True),
        _mutated(valid, ["retained_jsonl_write_created"], True),
        _mutated(valid, ["retention_write_created"], True),
        _mutated(valid, ["predictor_mutation_created"], True),
        _mutated(valid, ["selected_action_created"], True),
        _mutated(valid, ["final_action_created"], True),
        _mutated(valid, ["direct_action_command_created"], True),
        _mutated(valid, ["proof_of_learning_claim_created"], True),
        _mutated(valid, ["stop_conditions"], []),
        _mutated(valid, ["audit_required"], False),
        _mutated(valid, ["rollback_required"], False),
        _mutated(valid, ["human_review_required_before_future_level2_application"], False),
        _mutated(valid, ["task_queue_completed_status_is_approval"], True),
        _mutated(valid, ["passing_tests_are_approval"], True),
        _mutated(valid, ["codex_generated_status_is_approval"], True),
    ]
    return [valid] + invalid


def _mutated(record: dict[str, Any], path: list[str], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: dict[str, Any] = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(run_level2_sandbox_design_envelope_minimal_check(), ensure_ascii=False, indent=2))
