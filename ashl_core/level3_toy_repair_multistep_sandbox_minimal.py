"""Deterministic Level 3 toy repair multi-step sandbox trace."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS


COMMAND = "run-level3-toy-repair-multistep-sandbox-minimal-check"
FLOW = "level3_toy_repair_multistep_sandbox_minimal_v0"
PACKAGE_ID = "PKG-Phase0-Level3ToyRepairMultistepSandbox-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b82"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b83"
SANDBOX_LEVEL = "phase0_level3"
SANDBOX_ID = "toy_repair_multistep_sandbox_v0"
SANDBOX_SCOPE = "phase0_level3_toy_repair_sandbox_only"
SCENARIO_ID = "toy_device_hidden_fault_repair_v0"
DEVICE_ID = "toy_device_alpha"
FAILURE_KEY = "quick_fix_failed_due_to_hidden_fault"
ALLOWED_ACTION_SET = [
    "inspect_device",
    "attempt_quick_fix",
    "attempt_same_quick_fix_again",
    "attempt_safe_repair",
    "fallback_stop_and_report",
    "wait",
]
FALSE_TRACE_FIELDS = (
    "memory_read_used",
    "memory_runtime_influence_used",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "predictor_mutation_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "production_behavior_changed",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
    "real_repair_environment_used",
    "real_tool_used",
    "free_form_action_allowed",
    "natural_language_command_allowed",
)
TRUE_TRACE_FIELDS = (
    "blocked_invalid_repeat_without_check",
    "check_before_retry_observed",
    "safe_alternative_used_after_check",
    "temporary_sandbox_state_used",
    "audit_recorded",
    "rollback_available",
)


def build_level3_toy_repair_scenario() -> dict[str, Any]:
    return {
        "record_type": "level3_toy_repair_scenario",
        "record_version": "v0",
        "sandbox_level": SANDBOX_LEVEL,
        "sandbox_id": SANDBOX_ID,
        "sandbox_scope": SANDBOX_SCOPE,
        "scenario_id": SCENARIO_ID,
        "device_id": DEVICE_ID,
        "initial_state": {
            "device_id": DEVICE_ID,
            "device_state": "broken",
            "visible_fault": "loose_panel",
            "hidden_fault": "crossed_wire",
            "repair_attempted": False,
            "last_failed_action": None,
            "inspection_performed": False,
            "safe_repair_available": True,
            "tick": 0,
        },
        "allowed_action_set": list(ALLOWED_ACTION_SET),
        "memory_runtime_influence_used": False,
        "real_repair_environment_used": False,
        "real_tool_used": False,
    }


def build_level3_toy_repair_multistep_trace(invalid_repeat_without_inspection: bool = False) -> dict[str, Any]:
    steps = [
        {
            "step_index": 0,
            "sandbox_step_action": "attempt_quick_fix",
            "result": "failed",
            "failure_key": FAILURE_KEY,
            "device_state_after": "still_broken",
            "risk_marked": True,
        },
    ]
    if invalid_repeat_without_inspection:
        steps.append(
            {
                "step_index": 1,
                "sandbox_step_action": "attempt_same_quick_fix_again",
                "result": "blocked_invalid_repeat_without_inspection",
                "same_failed_action_retried_without_check": True,
            }
        )
    else:
        steps.extend(
            [
                {
                    "step_index": 1,
                    "sandbox_step_action": "inspect_device",
                    "result": "inspection_found_hidden_fault",
                    "inspection_performed": True,
                    "check_before_retry_observed": True,
                },
                {
                    "step_index": 2,
                    "sandbox_step_action": "attempt_safe_repair",
                    "result": "safe_repair_succeeded",
                    "device_state_after": "safe_stabilized",
                },
            ]
        )
    return {
        "record_type": "level3_toy_repair_multistep_trace",
        "record_version": "v0",
        "sandbox_level": SANDBOX_LEVEL,
        "sandbox_id": SANDBOX_ID,
        "sandbox_scope": SANDBOX_SCOPE,
        "scenario_id": SCENARIO_ID,
        "device_id": DEVICE_ID,
        "allowed_action_set": list(ALLOWED_ACTION_SET),
        "steps": steps,
        "blocked_invalid_repeat_without_check": True,
        "check_before_retry_observed": not invalid_repeat_without_inspection,
        "same_failed_action_retried_without_check": invalid_repeat_without_inspection,
        "safe_alternative_used_after_check": not invalid_repeat_without_inspection,
        "temporary_sandbox_state_used": True,
        "memory_read_used": False,
        "memory_runtime_influence_used": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "predictor_mutation_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "real_repair_environment_used": False,
        "real_tool_used": False,
        "free_form_action_allowed": False,
        "natural_language_command_allowed": False,
        "qingyin_current_status": QINGYIN_STATUS,
        "audit_recorded": True,
        "rollback_available": True,
        "source_scenario": build_level3_toy_repair_scenario(),
    }


def validate_level3_toy_repair_multistep_trace(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "level3_toy_repair_multistep_trace",
        "record_version": "v0",
        "sandbox_level": SANDBOX_LEVEL,
        "sandbox_id": SANDBOX_ID,
        "sandbox_scope": SANDBOX_SCOPE,
        "scenario_id": SCENARIO_ID,
        "device_id": DEVICE_ID,
        "qingyin_current_status": QINGYIN_STATUS,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    if record.get("allowed_action_set") != ALLOWED_ACTION_SET:
        errors.append("allowed_action_set_not_closed_expected_set")
    steps = record.get("steps", [])
    if not isinstance(steps, list) or not steps:
        errors.append("steps_missing")
        steps = []
    actions = [step.get("sandbox_step_action") for step in steps if isinstance(step, dict)]
    if any(action not in ALLOWED_ACTION_SET for action in actions):
        errors.append("step_action_not_in_allowed_action_set")
    quick_fix_index = _first_index(steps, "attempt_quick_fix")
    inspect_index = _first_index(steps, "inspect_device")
    safe_repair_index = _first_index(steps, "attempt_safe_repair")
    if quick_fix_index is None:
        errors.append("attempt_quick_fix_missing")
    elif steps[quick_fix_index].get("result") != "failed" or steps[quick_fix_index].get("failure_key") != FAILURE_KEY:
        errors.append("attempt_quick_fix_failure_not_expected")
    if inspect_index is None:
        errors.append("inspect_device_missing")
    if safe_repair_index is None:
        errors.append("attempt_safe_repair_missing")
    if (
        quick_fix_index is not None
        and inspect_index is not None
        and safe_repair_index is not None
        and not (quick_fix_index < inspect_index < safe_repair_index)
    ):
        errors.append("inspect_not_between_failed_quick_fix_and_safe_repair")
    if record.get("same_failed_action_retried_without_check") is not False:
        errors.append("same_failed_action_retried_without_check_not_false")
    for field in FALSE_TRACE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in TRUE_TRACE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "invalid_repeat_blocked": record.get("blocked_invalid_repeat_without_check") is True,
        "check_before_retry_observed": record.get("check_before_retry_observed") is True,
        "safe_repair_after_check": record.get("safe_alternative_used_after_check") is True,
        "memory_influence_blocked": record.get("memory_runtime_influence_used") is False,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "retained_jsonl_write_blocked": record.get("retained_jsonl_write_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_level3_toy_repair_observation(trace: dict[str, Any] | None = None) -> dict[str, Any]:
    source = deepcopy(trace) if trace is not None else build_level3_toy_repair_multistep_trace()
    return {
        "record_type": "level3_toy_repair_observation",
        "record_version": "v0",
        "source_trace_record_type": source.get("record_type"),
        "observation_status": "observed_valid_check_before_retry_repair_trace",
        "sandbox_scope": source.get("sandbox_scope"),
        "observed_failure_key": FAILURE_KEY,
        "observed_check_before_retry": source.get("check_before_retry_observed") is True,
        "observed_safe_alternative_after_check": source.get("safe_alternative_used_after_check") is True,
        "observed_invalid_repeat_blocked": source.get("blocked_invalid_repeat_without_check") is True,
        "observed_memory_runtime_influence": source.get("memory_runtime_influence_used") is True,
        "observed_selected_action": source.get("selected_action_created") is True,
        "observed_final_action": source.get("final_action_created") is True,
        "audit_recorded": source.get("audit_recorded") is True,
        "rollback_available": source.get("rollback_available") is True,
        "source_trace": source,
    }


def validate_level3_toy_repair_observation(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "level3_toy_repair_observation",
        "record_version": "v0",
        "source_trace_record_type": "level3_toy_repair_multistep_trace",
        "observation_status": "observed_valid_check_before_retry_repair_trace",
        "sandbox_scope": SANDBOX_SCOPE,
        "observed_failure_key": FAILURE_KEY,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    source = record.get("source_trace")
    if not isinstance(source, dict):
        errors.append("source_trace_missing")
    elif not validate_level3_toy_repair_multistep_trace(source)["valid"]:
        errors.append("source_trace_invalid")
    for field in ("observed_check_before_retry", "observed_safe_alternative_after_check", "observed_invalid_repeat_blocked", "audit_recorded", "rollback_available"):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in ("observed_memory_runtime_influence", "observed_selected_action", "observed_final_action"):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {"valid": not errors, "error_codes": errors}


def build_level3_toy_repair_evaluation(observation: dict[str, Any] | None = None) -> dict[str, Any]:
    source = deepcopy(observation) if observation is not None else build_level3_toy_repair_observation()
    return {
        "record_type": "level3_toy_repair_evaluation",
        "record_version": "v0",
        "source_observation_record_type": source.get("record_type"),
        "evaluation_status": "passed_expected_toy_repair_check_before_retry_behavior",
        "sandbox_scope": source.get("sandbox_scope"),
        "expected_behavior": "inspect_before_retry_after_failed_or_risky_repair",
        "observed_behavior": "inspection_occurred_before_safe_repair",
        "invalid_repeat_without_check_rejected": source.get("observed_invalid_repeat_blocked") is True,
        "memory_runtime_influence_used": source.get("observed_memory_runtime_influence") is True,
        "selected_action_created": source.get("observed_selected_action") is True,
        "final_action_created": source.get("observed_final_action") is True,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "audit_recorded": source.get("audit_recorded") is True,
        "rollback_available": source.get("rollback_available") is True,
        "source_observation": source,
    }


def validate_level3_toy_repair_evaluation(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "level3_toy_repair_evaluation",
        "record_version": "v0",
        "source_observation_record_type": "level3_toy_repair_observation",
        "evaluation_status": "passed_expected_toy_repair_check_before_retry_behavior",
        "sandbox_scope": SANDBOX_SCOPE,
        "expected_behavior": "inspect_before_retry_after_failed_or_risky_repair",
        "observed_behavior": "inspection_occurred_before_safe_repair",
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    source = record.get("source_observation")
    if not isinstance(source, dict):
        errors.append("source_observation_missing")
    elif not validate_level3_toy_repair_observation(source)["valid"]:
        errors.append("source_observation_invalid")
    for field in ("invalid_repeat_without_check_rejected", "audit_recorded", "rollback_available"):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in (
        "memory_runtime_influence_used",
        "selected_action_created",
        "final_action_created",
        "predictor_mutation_performed",
        "production_behavior_changed",
        "proof_of_learning_claim_allowed",
    ):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {"valid": not errors, "error_codes": errors}


def build_level3_toy_repair_human_review_summary(evaluation: dict[str, Any] | None = None) -> dict[str, Any]:
    source = deepcopy(evaluation) if evaluation is not None else build_level3_toy_repair_evaluation()
    return {
        "record_type": "level3_toy_repair_human_review_summary",
        "record_version": "v0",
        "summary_status": "ready_for_human_review",
        "source_evaluation_record_type": source.get("record_type"),
        "safe_claim": (
            "ASHL Core can run, observe, evaluate, and summarize a deterministic Phase0 Level 3 toy repair "
            "multi-step sandbox trace where a failed risky repair requires inspection before retry."
        ),
        "not_learning_proof": True,
        "not_memory_influence": True,
        "not_action_selection": True,
        "not_production_behavior": True,
        "human_summary": (
            "The toy repair sandbox shows that after a failed quick repair, the valid trace inspects the device "
            "before attempting a safer repair. This is sandbox-only trace evidence, not selected_action, "
            "final_action, production behavior, memory influence, or proof of learning."
        ),
        "source_evaluation": source,
    }


def validate_level3_toy_repair_human_review_summary(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "level3_toy_repair_human_review_summary",
        "record_version": "v0",
        "summary_status": "ready_for_human_review",
        "source_evaluation_record_type": "level3_toy_repair_evaluation",
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    source = record.get("source_evaluation")
    if not isinstance(source, dict):
        errors.append("source_evaluation_missing")
    elif not validate_level3_toy_repair_evaluation(source)["valid"]:
        errors.append("source_evaluation_invalid")
    for field in ("safe_claim", "human_summary"):
        if not isinstance(record.get(field), str) or not record.get(field, "").strip():
            errors.append(f"{field}_empty")
    for field in ("not_learning_proof", "not_memory_influence", "not_action_selection", "not_production_behavior"):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    return {"valid": not errors, "error_codes": errors}


def run_level3_toy_repair_multistep_sandbox_minimal_check() -> dict[str, Any]:
    valid_trace = build_level3_toy_repair_multistep_trace()
    valid_observation = build_level3_toy_repair_observation(valid_trace)
    valid_evaluation = build_level3_toy_repair_evaluation(valid_observation)
    valid_summary = build_level3_toy_repair_human_review_summary(valid_evaluation)
    invalid_traces = _invalid_traces(valid_trace)
    invalid_observations = _invalid_observations(valid_observation)
    invalid_evaluations = _invalid_evaluations(valid_evaluation)
    invalid_summaries = _invalid_summaries(valid_summary)
    trace_results = [validate_level3_toy_repair_multistep_trace(item) for item in [valid_trace] + invalid_traces]
    observation_results = [validate_level3_toy_repair_observation(item) for item in [valid_observation] + invalid_observations]
    evaluation_results = [validate_level3_toy_repair_evaluation(item) for item in [valid_evaluation] + invalid_evaluations]
    summary_results = [validate_level3_toy_repair_human_review_summary(item) for item in [valid_summary] + invalid_summaries]
    valid_trace_results = [result for result in trace_results if result["valid"]]
    summary = {
        "valid_trace_count": len(valid_trace_results),
        "invalid_trace_count": len(trace_results) - len(valid_trace_results),
        "valid_observation_count": sum(1 for result in observation_results if result["valid"]),
        "invalid_observation_count": sum(1 for result in observation_results if not result["valid"]),
        "valid_evaluation_count": sum(1 for result in evaluation_results if result["valid"]),
        "invalid_evaluation_count": sum(1 for result in evaluation_results if not result["valid"]),
        "valid_summary_count": sum(1 for result in summary_results if result["valid"]),
        "invalid_summary_count": sum(1 for result in summary_results if not result["valid"]),
        "invalid_repeat_blocked_count": sum(1 for result in valid_trace_results if result["invalid_repeat_blocked"]),
        "check_before_retry_observed_count": sum(1 for result in valid_trace_results if result["check_before_retry_observed"]),
        "safe_repair_after_check_count": sum(1 for result in valid_trace_results if result["safe_repair_after_check"]),
        "memory_influence_blocked_count": sum(1 for result in valid_trace_results if result["memory_influence_blocked"]),
        "selected_action_blocked_count": sum(1 for result in valid_trace_results if result["selected_action_blocked"]),
        "final_action_blocked_count": sum(1 for result in valid_trace_results if result["final_action_blocked"]),
        "predictor_mutation_blocked_count": sum(1 for result in valid_trace_results if result["predictor_mutation_blocked"]),
        "retained_jsonl_write_blocked_count": sum(
            1 for result in valid_trace_results if result["retained_jsonl_write_blocked"]
        ),
        "production_behavior_blocked_count": sum(1 for result in valid_trace_results if result["production_behavior_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid_trace_results if result["proof_claim_blocked"]),
    }
    summary["all_level3_toy_repair_multistep_sandbox_minimal_checks_passed"] = _all_checks_passed(summary)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_level3_toy_repair_multistep_sandbox_minimal_checks_passed"] else "failed",
        "valid_trace": valid_trace,
        "valid_observation": valid_observation,
        "valid_evaluation": valid_evaluation,
        "valid_summary": valid_summary,
        "invalid_traces": invalid_traces,
        "validation_results": {
            "traces": trace_results,
            "observations": observation_results,
            "evaluations": evaluation_results,
            "summaries": summary_results,
        },
        "summary": summary,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package introduces a second deterministic Phase0 Level 3 sandbox-only multi-step "
                "scenario family, Toy Repair, while memory influence, selected_action, final_action, predictor "
                "mutation, production promotion, retained JSONL write, retention write, and proof-of-learning remain blocked."
            ),
        },
        "safe_claim": (
            "ASHL Core can run, observe, evaluate, and summarize a deterministic Phase0 Level 3 toy repair "
            "multi-step sandbox trace where a failed or risky repair requires inspection before retry, while "
            "memory influence, selected_action, final_action, predictor mutation, production promotion, retained "
            "JSONL write, retention write, and proof-of-learning remain blocked."
        ),
    }


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary.get("valid_trace_count") == 1
        and summary.get("invalid_trace_count", 0) >= 1
        and summary.get("valid_observation_count") == 1
        and summary.get("valid_evaluation_count") == 1
        and summary.get("valid_summary_count") == 1
        and summary.get("invalid_repeat_blocked_count") == 1
        and summary.get("check_before_retry_observed_count") == 1
        and summary.get("safe_repair_after_check_count") == 1
        and summary.get("memory_influence_blocked_count") == 1
        and summary.get("selected_action_blocked_count") == 1
        and summary.get("final_action_blocked_count") == 1
        and summary.get("predictor_mutation_blocked_count") == 1
        and summary.get("retained_jsonl_write_blocked_count") == 1
        and summary.get("production_behavior_blocked_count") == 1
        and summary.get("proof_claim_blocked_count") == 1
    )


def _first_index(steps: list[Any], action: str) -> int | None:
    for index, step in enumerate(steps):
        if isinstance(step, dict) and step.get("sandbox_step_action") == action:
            return index
    return None


def _invalid_traces(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalids = [build_level3_toy_repair_multistep_trace(invalid_repeat_without_inspection=True)]

    def changed(field: str, value: Any) -> None:
        record = deepcopy(valid)
        record[field] = value
        invalids.append(record)

    missing_inspection = deepcopy(valid)
    missing_inspection["steps"] = [step for step in missing_inspection["steps"] if step.get("sandbox_step_action") != "inspect_device"]
    invalids.append(missing_inspection)
    safe_before_inspect = deepcopy(valid)
    safe_before_inspect["steps"][1], safe_before_inspect["steps"][2] = safe_before_inspect["steps"][2], safe_before_inspect["steps"][1]
    invalids.append(safe_before_inspect)
    free_form = deepcopy(valid)
    free_form["allowed_action_set"] = valid["allowed_action_set"] + ["say_anything"]
    invalids.append(free_form)
    for field in FALSE_TRACE_FIELDS:
        changed(field, True)
    changed("blocked_invalid_repeat_without_check", False)
    changed("check_before_retry_observed", False)
    changed("safe_alternative_used_after_check", False)
    changed("temporary_sandbox_state_used", False)
    return invalids


def _invalid_observations(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalids = []
    for field in ("observed_check_before_retry", "observed_safe_alternative_after_check", "observed_invalid_repeat_blocked"):
        record = deepcopy(valid)
        record[field] = False
        invalids.append(record)
    record = deepcopy(valid)
    record["observed_memory_runtime_influence"] = True
    invalids.append(record)
    return invalids


def _invalid_evaluations(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalids = []
    for field in (
        "invalid_repeat_without_check_rejected",
        "memory_runtime_influence_used",
        "selected_action_created",
        "final_action_created",
        "predictor_mutation_performed",
        "production_behavior_changed",
        "proof_of_learning_claim_allowed",
    ):
        record = deepcopy(valid)
        record[field] = False if field == "invalid_repeat_without_check_rejected" else True
        invalids.append(record)
    return invalids


def _invalid_summaries(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalids = []
    for field in ("not_learning_proof", "not_memory_influence", "not_action_selection", "not_production_behavior"):
        record = deepcopy(valid)
        record[field] = False
        invalids.append(record)
    record = deepcopy(valid)
    record["human_summary"] = ""
    invalids.append(record)
    return invalids


if __name__ == "__main__":
    import json

    print(json.dumps(run_level3_toy_repair_multistep_sandbox_minimal_check(), indent=2, sort_keys=True))
