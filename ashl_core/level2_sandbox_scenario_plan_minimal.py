"""Plan a future Level 2 sandbox scenario without executing it."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .level2_sandbox_design_envelope_minimal import (
    TARGET_SCOPE,
    build_level2_sandbox_design_envelope,
    validate_level2_sandbox_design_envelope,
)


COMMAND = "run-level2-sandbox-scenario-plan-minimal-check"
FLOW = "level2_sandbox_scenario_plan_minimal_v0"
RECORD_TYPE = "level2_sandbox_scenario_plan_minimal"
SCENARIO_PLAN_STATUS = "planned_for_future_level2_sandbox_package_only"
SCENARIO_ID = "phase0_level2_scenario_plan_minimal_v0"
SCENARIO_KIND = "controlled_counterfactual_retry_sandbox_plan"
EXPECTED_OUTCOMES = {
    "front_symbol": "d",
    "preferred_sandbox_action": "check_before_retry",
    "retry_same_action_should_be_blocked_until_check": True,
    "audit_should_remain_present": True,
    "rollback_should_remain_available": True,
}
PLANNED_FAILURE_CLASSES = (
    "missing_or_invalid_level2_design_envelope",
    "missing_or_invalid_level1_review_conclusion",
    "missing_or_invalid_level2_readiness_precheck",
    "unexpected_sandbox_action",
    "retry_not_blocked_until_check",
    "audit_missing",
    "rollback_missing",
    "scope_escape_attempt",
    "runtime_or_memory_effect_attempt",
)
PLANNED_STOP_CONDITIONS = (
    "scope_escape_detected",
    "runtime_behavior_change_requested",
    "memory_or_retention_write_requested",
    "predictor_mutation_requested",
    "selected_or_final_action_requested",
    "production_promotion_requested",
    "proof_of_learning_claim_requested",
)
FORBIDDEN_BOOLEAN_FIELDS = (
    "level2_execution_allowed",
    "level2_application_allowed",
    "production_promotion_allowed",
    "runtime_behavior_change_allowed",
    "memory_write_allowed",
    "retained_jsonl_write_allowed",
    "retention_write_allowed",
    "predictor_mutation_allowed",
    "selected_action_allowed",
    "final_action_allowed",
    "direct_command_allowed",
    "proof_of_learning_claim_allowed",
)
REQUIRED_TRUE_FIELDS = (
    "requires_valid_level1_review_conclusion",
    "requires_valid_level2_readiness_precheck",
    "requires_valid_level2_design_envelope",
    "audit_recorded",
    "rollback_required_for_future_execution",
    "human_review_required_before_future_level2_application",
)
REQUIRED_FIELDS = (
    "record_type",
    "phase",
    "target_scope",
    "scenario_plan_status",
    "source_level2_design_envelope",
    "scenario_id",
    "scenario_kind",
    "scenario_description",
    "planned_inputs",
    "planned_expected_outcomes",
    "planned_failure_classes",
    "planned_stop_conditions",
    "notes",
) + REQUIRED_TRUE_FIELDS + FORBIDDEN_BOOLEAN_FIELDS


def build_level2_sandbox_scenario_plan(
    source_design_envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_design_envelope is None:
        source_design_envelope = build_level2_sandbox_design_envelope()

    source_is_dict = isinstance(source_design_envelope, dict)
    source = source_design_envelope if source_is_dict else {}
    source_validation = (
        validate_level2_sandbox_design_envelope(source) if source_is_dict else {"valid": False}
    )
    design_envelope_valid = source_validation.get("valid") is True

    return {
        "record_type": RECORD_TYPE,
        "phase": "phase0",
        "target_scope": TARGET_SCOPE,
        "scenario_plan_status": SCENARIO_PLAN_STATUS,
        "source_level2_design_envelope": {
            "record_type": source.get("record_type"),
            "target_scope": source.get("target_scope"),
            "design_envelope_status": source.get("design_envelope_status"),
            "valid_level2_design_envelope": design_envelope_valid,
        },
        "source_level2_design_envelope_record": deepcopy(source_design_envelope) if source_is_dict else None,
        "requires_valid_level1_review_conclusion": True,
        "requires_valid_level2_readiness_precheck": True,
        "requires_valid_level2_design_envelope": True,
        "level2_execution_allowed": False,
        "level2_application_allowed": False,
        "production_promotion_allowed": False,
        "runtime_behavior_change_allowed": False,
        "memory_write_allowed": False,
        "retained_jsonl_write_allowed": False,
        "retention_write_allowed": False,
        "predictor_mutation_allowed": False,
        "selected_action_allowed": False,
        "final_action_allowed": False,
        "direct_command_allowed": False,
        "proof_of_learning_claim_allowed": False,
        "scenario_id": SCENARIO_ID,
        "scenario_kind": SCENARIO_KIND,
        "scenario_description": (
            "Future Level 2 sandbox scenario plan for checking a reviewed lesson under controlled retry "
            "conditions without runtime or memory effects."
        ),
        "planned_inputs": {
            "reviewed_lesson_reference_required": True,
            "level1_application_evaluation_required": True,
            "human_review_summary_required": True,
            "level2_design_envelope_required": True,
            "sandbox_input_trace_required": True,
        },
        "planned_expected_outcomes": dict(EXPECTED_OUTCOMES),
        "planned_failure_classes": list(PLANNED_FAILURE_CLASSES),
        "planned_stop_conditions": list(PLANNED_STOP_CONDITIONS),
        "audit_recorded": True,
        "rollback_required_for_future_execution": True,
        "human_review_required_before_future_level2_application": True,
        "notes": [
            "This is a scenario plan only.",
            "It does not execute or apply Level 2 sandbox behavior.",
            (
                "It does not create memory, predictor, runtime, production, selected_action, final_action, "
                "or proof-of-learning capability."
            ),
        ],
    }


def validate_level2_sandbox_scenario_plan(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing_field:{field}")
    if record.get("record_type") != RECORD_TYPE:
        errors.append("record_type_not_level2_sandbox_scenario_plan_minimal")
    if record.get("phase") != "phase0":
        errors.append("phase_not_phase0")
    if record.get("target_scope") != TARGET_SCOPE:
        errors.append("target_scope_not_phase0_level2_sandbox_design_only")
    if record.get("scenario_plan_status") != SCENARIO_PLAN_STATUS:
        errors.append("scenario_plan_status_not_planned_for_future_level2_sandbox_package_only")
    for field in REQUIRED_TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in FORBIDDEN_BOOLEAN_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")

    source = record.get("source_level2_design_envelope")
    if not isinstance(source, dict):
        errors.append("source_level2_design_envelope_not_dict")
        source = {}
    if source.get("valid_level2_design_envelope") is not True:
        errors.append("valid_level2_design_envelope_not_true")
    if source.get("target_scope") != TARGET_SCOPE:
        errors.append("source_target_scope_not_phase0_level2_sandbox_design_only")

    if record.get("scenario_id") != SCENARIO_ID:
        errors.append("scenario_id_not_phase0_level2_scenario_plan_minimal_v0")
    if record.get("scenario_kind") != SCENARIO_KIND:
        errors.append("scenario_kind_not_controlled_counterfactual_retry_sandbox_plan")
    if not isinstance(record.get("scenario_description"), str) or not record.get("scenario_description", "").strip():
        errors.append("scenario_description_empty")

    planned_inputs = record.get("planned_inputs")
    if not isinstance(planned_inputs, dict):
        errors.append("planned_inputs_not_dict")
        planned_inputs = {}
    for field in (
        "reviewed_lesson_reference_required",
        "level1_application_evaluation_required",
        "human_review_summary_required",
        "level2_design_envelope_required",
        "sandbox_input_trace_required",
    ):
        if planned_inputs.get(field) is not True:
            errors.append(f"planned_input_{field}_not_true")

    expected = record.get("planned_expected_outcomes")
    if not isinstance(expected, dict):
        errors.append("planned_expected_outcomes_not_dict")
        expected = {}
    for key, value in EXPECTED_OUTCOMES.items():
        if expected.get(key) != value:
            errors.append(f"planned_expected_outcome_{key}_not_expected")

    if set(record.get("planned_failure_classes", [])) != set(PLANNED_FAILURE_CLASSES):
        errors.append("planned_failure_classes_not_explicit")
    if set(record.get("planned_stop_conditions", [])) != set(PLANNED_STOP_CONDITIONS):
        errors.append("planned_stop_conditions_not_explicit")
    notes = record.get("notes")
    if not isinstance(notes, list) or not all(isinstance(note, str) and note.strip() for note in notes):
        errors.append("notes_not_non_empty_strings")

    return {
        "valid": not errors,
        "error_codes": errors,
        "record_type": record.get("record_type"),
        "level2_design_envelope_checked": source.get("valid_level2_design_envelope") is True,
        "scenario_plan_design_only": (
            record.get("target_scope") == TARGET_SCOPE
            and record.get("scenario_plan_status") == SCENARIO_PLAN_STATUS
        ),
        "level2_execution_blocked": record.get("level2_execution_allowed") is False,
        "level2_application_blocked": record.get("level2_application_allowed") is False,
        "runtime_memory_predictor_blocked": (
            record.get("runtime_behavior_change_allowed") is False
            and record.get("memory_write_allowed") is False
            and record.get("retained_jsonl_write_allowed") is False
            and record.get("retention_write_allowed") is False
            and record.get("predictor_mutation_allowed") is False
        ),
        "proof_of_learning_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_level2_sandbox_scenario_plan_minimal_records() -> list[dict[str, Any]]:
    valid = build_level2_sandbox_scenario_plan()
    invalid = [
        _mutated(valid, ["requires_valid_level2_design_envelope"], False),
        _mutated(valid, ["source_level2_design_envelope", "valid_level2_design_envelope"], False),
        _mutated(valid, ["target_scope"], "production"),
        _mutated(valid, ["level2_execution_allowed"], True),
        _mutated(valid, ["level2_application_allowed"], True),
        _mutated(valid, ["runtime_behavior_change_allowed"], True),
        _mutated(valid, ["memory_write_allowed"], True),
        _mutated(valid, ["retained_jsonl_write_allowed"], True),
        _mutated(valid, ["retention_write_allowed"], True),
        _mutated(valid, ["predictor_mutation_allowed"], True),
        _mutated(valid, ["selected_action_allowed"], True),
        _mutated(valid, ["final_action_allowed"], True),
        _mutated(valid, ["production_promotion_allowed"], True),
        _mutated(valid, ["proof_of_learning_claim_allowed"], True),
        _mutated(valid, ["planned_expected_outcomes"], {}),
        _mutated(valid, ["planned_expected_outcomes", "front_symbol"], "."),
        _mutated(valid, ["planned_expected_outcomes", "preferred_sandbox_action"], "retry_same_action"),
        _mutated(valid, ["planned_expected_outcomes", "retry_same_action_should_be_blocked_until_check"], False),
        _mutated(valid, ["audit_recorded"], False),
        _mutated(valid, ["rollback_required_for_future_execution"], False),
        _mutated(valid, ["human_review_required_before_future_level2_application"], False),
    ]
    return [valid] + invalid


def check_level2_sandbox_scenario_plan_minimal_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    validation_results = [validate_level2_sandbox_scenario_plan(record) for record in records]
    valid_results = [result for result in validation_results if result.get("valid")]
    summary = {
        "level2_sandbox_scenario_plan_result_count": len(records),
        "valid_level2_sandbox_scenario_plan_count": len(valid_results),
        "invalid_level2_sandbox_scenario_plan_count": len(records) - len(valid_results),
        "level2_design_envelope_checked_count": sum(
            1 for result in valid_results if result.get("level2_design_envelope_checked") is True
        ),
        "scenario_plan_design_only_count": sum(
            1 for result in valid_results if result.get("scenario_plan_design_only") is True
        ),
        "level2_execution_blocked_count": sum(
            1 for result in valid_results if result.get("level2_execution_blocked") is True
        ),
        "level2_application_blocked_count": sum(
            1 for result in valid_results if result.get("level2_application_blocked") is True
        ),
        "runtime_memory_predictor_blocked_count": sum(
            1 for result in valid_results if result.get("runtime_memory_predictor_blocked") is True
        ),
        "proof_of_learning_blocked_count": sum(
            1 for result in valid_results if result.get("proof_of_learning_blocked") is True
        ),
    }
    summary["all_level2_sandbox_scenario_plan_checks_passed"] = (
        summary["valid_level2_sandbox_scenario_plan_count"] == 1
        and summary["invalid_level2_sandbox_scenario_plan_count"] >= 1
        and summary["level2_design_envelope_checked_count"] == 1
        and summary["scenario_plan_design_only_count"] == 1
        and summary["level2_execution_blocked_count"] == 1
        and summary["level2_application_blocked_count"] == 1
        and summary["runtime_memory_predictor_blocked_count"] == 1
        and summary["proof_of_learning_blocked_count"] == 1
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_level2_sandbox_scenario_plan_checks_passed"] else "failed",
        "scenario_plan_records": records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "planning_only": True,
            "level2_execution_added": False,
            "level2_application_added": False,
            "runtime_behavior_change_added": False,
            "memory_write_added": False,
            "retained_jsonl_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "production_promotion_added": False,
            "approval_replay_session_binding_added": False,
            "proof_of_learning_claimed": False,
        },
    }


def run_level2_sandbox_scenario_plan_minimal_check() -> dict[str, Any]:
    return check_level2_sandbox_scenario_plan_minimal_records(
        build_level2_sandbox_scenario_plan_minimal_records()
    )


def main() -> dict[str, Any]:
    return run_level2_sandbox_scenario_plan_minimal_check()


def _mutated(record: dict[str, Any], path: list[str], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: dict[str, Any] = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(main(), ensure_ascii=False, indent=2))
