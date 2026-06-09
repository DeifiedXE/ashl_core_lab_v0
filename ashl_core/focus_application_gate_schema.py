"""Schema checker for Focus Application Gate v0 records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-focus-application-gate-schema-check"
FLOW = "focus_application_gate_schema_v0"

REQUIRED_FIELDS = {
    "gate_record_id",
    "source_ranking_trace_id",
    "gate_set_name",
    "gates",
    "active_focus_id",
    "focus_applied",
    "attention_control",
    "source_trace",
    "safety_flags",
}

REQUIRED_GATES = {
    "focus_application_candidate_gate",
    "focus_lock_prevention_gate",
    "mentor_interrupt_gate",
    "endocrine_boundary_gate",
    "perception_to_action_boundary_gate",
    "runtime_permission_gate",
}

ALLOWED_GATE_STATUSES = {
    "review_only",
    "blocked",
    "not_implemented",
    "future_required",
}

GATE_REQUIRED_REASON_CODES = {
    "focus_application_candidate_gate": {
        "ranking_trace_is_not_active_focus",
        "rank_position_1_not_selected_focus",
        "highest_total_score_not_selected_focus",
    },
    "focus_lock_prevention_gate": {
        "attention_intensity_cap_recorded",
        "attention_duration_limit_recorded",
        "forced_decay_recorded",
        "interruptible_recorded",
    },
    "mentor_interrupt_gate": {
        "external_mentor_interrupt_unconditional_priority_recorded",
    },
    "endocrine_boundary_gate": {
        "no_endocrine_runtime_controls_focus",
        "norepinephrine_like_interrupt_future_only",
        "cortisol_like_forced_diffusion_future_only",
    },
    "perception_to_action_boundary_gate": {
        "perception_to_action_boundary_review_required_before_action_influence",
        "no_focus_to_action_bridge",
    },
    "runtime_permission_gate": {
        "runtime_focus_selector_not_enabled",
        "runtime_ranking_not_enabled",
        "active_focus_not_enabled",
        "focus_applied_not_enabled",
        "attention_control_not_enabled",
    },
}

ALLOWED_REASON_CODES = set().union(*GATE_REQUIRED_REASON_CODES.values()) | {
    "cooldown_decay_interrupt_fields_recorded",
}

REQUIRED_SOURCE_TRACE_FIELDS = {
    "boundary_review",
    "ranking_trace_schema",
    "design_layer",
}

REQUIRED_SAFETY_FLAGS = {
    "blocked_from_action_selection",
    "blocked_from_memory_write",
    "blocked_from_endocrine_control",
    "runtime_focus_selector",
    "runtime_ranking",
    "active_focus_enabled",
    "focus_applied",
    "attention_control",
    "focus_to_action_bridge",
    "perception_to_action_bridge",
    "endocrine_runtime",
    "object_recognition",
    "object_tracking",
    "semantic_vision",
    "action_selection_influence",
    "memory_write",
    "endocrine_control",
    "predictor_modified",
}


def build_valid_focus_application_gate_record() -> dict[str, Any]:
    return {
        "case_name": "valid_focus_application_gate_record",
        "gate_record_id": "focus_application_gate_demo:001",
        "source_ranking_trace_id": "focus_candidate_ranking_trace:001",
        "gate_set_name": "focus_application_boundary_review_v0",
        "gates": [
            _build_gate(
                "focus_application_candidate_gate",
                [
                    "ranking_trace_is_not_active_focus",
                    "rank_position_1_not_selected_focus",
                    "highest_total_score_not_selected_focus",
                ],
            ),
            _build_gate(
                "focus_lock_prevention_gate",
                [
                    "attention_intensity_cap_recorded",
                    "attention_duration_limit_recorded",
                    "forced_decay_recorded",
                    "interruptible_recorded",
                    "cooldown_decay_interrupt_fields_recorded",
                ],
            ),
            _build_gate(
                "mentor_interrupt_gate",
                ["external_mentor_interrupt_unconditional_priority_recorded"],
            ),
            _build_gate(
                "endocrine_boundary_gate",
                [
                    "no_endocrine_runtime_controls_focus",
                    "norepinephrine_like_interrupt_future_only",
                    "cortisol_like_forced_diffusion_future_only",
                ],
            ),
            _build_gate(
                "perception_to_action_boundary_gate",
                [
                    "perception_to_action_boundary_review_required_before_action_influence",
                    "no_focus_to_action_bridge",
                ],
            ),
            _build_gate(
                "runtime_permission_gate",
                [
                    "runtime_focus_selector_not_enabled",
                    "runtime_ranking_not_enabled",
                    "active_focus_not_enabled",
                    "focus_applied_not_enabled",
                    "attention_control_not_enabled",
                ],
            ),
        ],
        "active_focus_id": None,
        "focus_applied": False,
        "attention_control": False,
        "source_trace": {
            "boundary_review": "focus_application_boundary_review_v0",
            "ranking_trace_schema": "focus_candidate_ranking_trace_schema",
            "design_layer": "focus_application_gate_schema_v0",
        },
        "safety_flags": {
            "blocked_from_action_selection": True,
            "blocked_from_memory_write": True,
            "blocked_from_endocrine_control": True,
            "runtime_focus_selector": False,
            "runtime_ranking": False,
            "active_focus_enabled": False,
            "focus_applied": False,
            "attention_control": False,
            "focus_to_action_bridge": False,
            "perception_to_action_bridge": False,
            "endocrine_runtime": False,
            "object_recognition": False,
            "object_tracking": False,
            "semantic_vision": False,
            "action_selection_influence": False,
            "memory_write": False,
            "endocrine_control": False,
            "predictor_modified": False,
        },
        "notes": [
            "Review-only gates do not authorize active_focus, focus_applied, attention_control, or runtime focus.",
            "Every gate passed value is false in v0.",
        ],
    }


def build_demo_focus_application_gate_records() -> list[dict[str, Any]]:
    valid = build_valid_focus_application_gate_record()

    active_focus = deepcopy(valid)
    active_focus["case_name"] = "active_focus_non_null_gate_record"
    active_focus["gate_record_id"] = "focus_application_gate_demo:active_focus:001"
    active_focus["active_focus_id"] = "focus_candidate_from_change_trace:001"

    focus_applied = deepcopy(valid)
    focus_applied["case_name"] = "focus_applied_gate_record"
    focus_applied["gate_record_id"] = "focus_application_gate_demo:focus_applied:001"
    focus_applied["focus_applied"] = True

    attention_control = deepcopy(valid)
    attention_control["case_name"] = "attention_control_gate_record"
    attention_control["gate_record_id"] = "focus_application_gate_demo:attention_control:001"
    attention_control["attention_control"] = True

    missing_gate = deepcopy(valid)
    missing_gate["case_name"] = "missing_required_gate_record"
    missing_gate["gate_record_id"] = "focus_application_gate_demo:missing_gate:001"
    missing_gate["gates"] = [
        gate for gate in missing_gate["gates"]
        if gate["gate_name"] != "runtime_permission_gate"
    ]

    runtime_permission = deepcopy(valid)
    runtime_permission["case_name"] = "runtime_permission_enabled_gate_record"
    runtime_permission["gate_record_id"] = "focus_application_gate_demo:runtime_permission:001"
    runtime_permission["safety_flags"]["runtime_focus_selector"] = True

    return [valid, active_focus, focus_applied, attention_control, missing_gate, runtime_permission]


def validate_focus_application_gate_record(gate_record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in gate_record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    gates = gate_record.get("gates")
    if not isinstance(gates, list):
        errors.append("gates_not_list")
        gates = []
    gate_results = [_validate_gate(gate) for gate in gates]
    for result in gate_results:
        errors.extend(result["error_codes"])
    gate_names = [
        gate.get("gate_name")
        for gate in gates
        if isinstance(gate, dict)
    ]
    missing_gates = sorted(gate for gate in REQUIRED_GATES if gate not in gate_names)
    errors.extend(f"missing_required_gate:{gate}" for gate in missing_gates)

    if gate_record.get("active_focus_id") is not None:
        errors.append("active_focus_id_non_null")
    if gate_record.get("focus_applied") is not False:
        errors.append("focus_applied_enabled")
    if gate_record.get("attention_control") is not False:
        errors.append("attention_control_enabled")

    _validate_source_trace(gate_record, errors)
    safety_flags = _validate_safety_flags(gate_record, errors)

    all_required_gates_present = not missing_gates
    all_gates_passed = all(
        isinstance(gate, dict) and gate.get("passed") is True
        for gate in gates
    ) if gates else False
    if all_gates_passed:
        errors.append("all_gates_passed_enabled")

    return {
        "case_name": gate_record.get("case_name"),
        "gate_record_id": gate_record.get("gate_record_id"),
        "valid": not errors,
        "error_codes": errors,
        "gate_count": len(gates),
        "required_gate_count": len(REQUIRED_GATES),
        "all_required_gates_present": all_required_gates_present,
        "all_gates_passed": all_gates_passed,
        "active_focus_is_null": gate_record.get("active_focus_id") is None,
        "focus_applied": gate_record.get("focus_applied") is True,
        "attention_control": gate_record.get("attention_control") is True,
        "runtime_focus_selector": safety_flags.get("runtime_focus_selector") is True,
        "runtime_ranking": safety_flags.get("runtime_ranking") is True,
        "active_focus_enabled": safety_flags.get("active_focus_enabled") is True,
        "focus_to_action_bridge": safety_flags.get("focus_to_action_bridge") is True,
        "perception_to_action_bridge": safety_flags.get("perception_to_action_bridge") is True,
        "endocrine_runtime": safety_flags.get("endocrine_runtime") is True,
        "action_selection_influence": safety_flags.get("action_selection_influence") is True,
        "memory_write": safety_flags.get("memory_write") is True,
        "endocrine_control": safety_flags.get("endocrine_control") is True,
        "predictor_modified": safety_flags.get("predictor_modified") is True,
        "object_recognition": safety_flags.get("object_recognition") is True,
        "object_tracking": safety_flags.get("object_tracking") is True,
        "semantic_vision": safety_flags.get("semantic_vision") is True,
    }


def run_focus_application_gate_schema_check() -> dict[str, Any]:
    gate_records = build_demo_focus_application_gate_records()
    validation_results = [validate_focus_application_gate_record(record) for record in gate_records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(validation_results, summary) else "failed",
        "gate_records": gate_records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker validates review-only focus_application_gate records.",
            "Gate records do not authorize active_focus, focus_applied, attention_control, runtime ranking, or runtime focus selection.",
            "Every gate passed value must remain false in v0.",
            "No focus-to-action bridge, perception-to-action bridge, endocrine runtime, action selection influence, or memory write is added.",
        ],
    }


def _build_gate(gate_name: str, reason_codes: list[str]) -> dict[str, Any]:
    return {
        "gate_name": gate_name,
        "status": "review_only",
        "passed": False,
        "required_for_future_runtime": True,
        "reason_codes": reason_codes,
        "notes": "Design-only gate; no runtime focus application implemented.",
    }


def _validate_gate(gate: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(gate, dict):
        return {"gate_name": None, "valid": False, "error_codes": ["gate_not_dict"]}

    gate_name = gate.get("gate_name")
    if gate_name not in REQUIRED_GATES:
        errors.append(f"unknown_gate:{gate_name}")
    status = gate.get("status")
    if status not in ALLOWED_GATE_STATUSES:
        errors.append(f"unknown_gate_status:{status}")
    if status in {"runtime_enabled", "active", "applied"}:
        errors.append(f"runtime_like_gate_status:{status}")
    if gate.get("passed") is not False:
        errors.append("gate_passed_true")
    if gate.get("required_for_future_runtime") is not True:
        errors.append("gate_not_required_for_future_runtime")

    reason_codes = gate.get("reason_codes")
    if not isinstance(reason_codes, list):
        errors.append("gate_reason_codes_not_list")
        reason_codes = []
    for reason_code in reason_codes:
        if reason_code not in ALLOWED_REASON_CODES:
            errors.append(f"unknown_gate_reason_code:{reason_code}")

    required_reasons = GATE_REQUIRED_REASON_CODES.get(gate_name, set())
    missing_reasons = sorted(reason for reason in required_reasons if reason not in reason_codes)
    errors.extend(f"missing_gate_reason_code:{reason}" for reason in missing_reasons)
    return {"gate_name": gate_name, "valid": not errors, "error_codes": errors}


def _validate_source_trace(gate_record: dict[str, Any], errors: list[str]) -> None:
    source_trace = gate_record.get("source_trace")
    if not isinstance(source_trace, dict) or not source_trace:
        errors.append("missing_source_trace")
        return
    missing = sorted(field for field in REQUIRED_SOURCE_TRACE_FIELDS if field not in source_trace)
    errors.extend(f"missing_source_trace_field:{field}" for field in missing)
    if source_trace.get("boundary_review") != "focus_application_boundary_review_v0":
        errors.append("invalid_boundary_review")
    if source_trace.get("ranking_trace_schema") != "focus_candidate_ranking_trace_schema":
        errors.append("invalid_ranking_trace_schema")
    if source_trace.get("design_layer") != "focus_application_gate_schema_v0":
        errors.append("invalid_design_layer")


def _validate_safety_flags(gate_record: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    safety_flags = gate_record.get("safety_flags")
    if not isinstance(safety_flags, dict):
        errors.append("safety_flags_not_dict")
        safety_flags = {}
    for flag in sorted(REQUIRED_SAFETY_FLAGS):
        if flag not in safety_flags:
            errors.append(f"missing_safety_flag:{flag}")

    if safety_flags.get("blocked_from_action_selection") is not True:
        errors.append("action_selection_not_blocked")
    if safety_flags.get("blocked_from_memory_write") is not True:
        errors.append("memory_write_not_blocked")
    if safety_flags.get("blocked_from_endocrine_control") is not True:
        errors.append("endocrine_control_not_blocked")

    false_required_flags = {
        "runtime_focus_selector": "runtime_focus_selector_enabled",
        "runtime_ranking": "runtime_ranking_enabled",
        "active_focus_enabled": "active_focus_enabled",
        "focus_applied": "focus_applied_flag_enabled",
        "attention_control": "attention_control_flag_enabled",
        "focus_to_action_bridge": "focus_to_action_bridge_enabled",
        "perception_to_action_bridge": "perception_to_action_bridge_enabled",
        "endocrine_runtime": "endocrine_runtime_enabled",
        "object_recognition": "object_recognition_enabled",
        "object_tracking": "object_tracking_enabled",
        "semantic_vision": "semantic_vision_enabled",
        "action_selection_influence": "action_selection_influence_enabled",
        "memory_write": "memory_write_enabled",
        "endocrine_control": "endocrine_control_enabled",
        "predictor_modified": "predictor_modified_enabled",
    }
    for flag, error_code in false_required_flags.items():
        if safety_flags.get(flag) not in {False, 0}:
            errors.append(error_code)
    return safety_flags


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid_results = [result for result in validation_results if result["valid"]]
    return {
        "gate_record_count": len(validation_results),
        "valid_gate_record_count": len(valid_results),
        "invalid_gate_record_count": sum(1 for result in validation_results if not result["valid"]),
        "gate_count": sum(result["gate_count"] for result in valid_results),
        "required_gate_count": len(REQUIRED_GATES),
        "missing_required_gate_blocked_count": _count_error_prefix(validation_results, "missing_required_gate:"),
        "active_focus_non_null_blocked_count": _count_error(validation_results, "active_focus_id_non_null"),
        "focus_applied_blocked_count": _count_error(validation_results, "focus_applied_enabled"),
        "attention_control_blocked_count": _count_error(validation_results, "attention_control_enabled"),
        "runtime_permission_enabled_blocked_count": _count_error(validation_results, "runtime_focus_selector_enabled"),
        "runtime_focus_selector_count": sum(1 for result in valid_results if result["runtime_focus_selector"]),
        "runtime_ranking_count": sum(1 for result in valid_results if result["runtime_ranking"]),
        "active_focus_enabled_count": sum(1 for result in valid_results if result["active_focus_enabled"]),
        "focus_to_action_bridge_count": sum(1 for result in valid_results if result["focus_to_action_bridge"]),
        "perception_to_action_bridge_count": sum(1 for result in valid_results if result["perception_to_action_bridge"]),
        "endocrine_runtime_count": sum(1 for result in valid_results if result["endocrine_runtime"]),
        "action_selection_influence_count": sum(1 for result in valid_results if result["action_selection_influence"]),
        "memory_write_count": sum(1 for result in valid_results if result["memory_write"]),
        "endocrine_control_count": sum(1 for result in valid_results if result["endocrine_control"]),
        "predictor_modified_count": sum(1 for result in valid_results if result["predictor_modified"]),
        "object_recognition_count": sum(1 for result in valid_results if result["object_recognition"]),
        "object_tracking_count": sum(1 for result in valid_results if result["object_tracking"]),
        "semantic_vision_count": sum(1 for result in valid_results if result["semantic_vision"]),
    }


def _all_checks_passed(validation_results: list[dict[str, Any]], summary: dict[str, int]) -> bool:
    cases = {result["case_name"]: result for result in validation_results}
    return (
        summary["gate_record_count"] == 6
        and summary["valid_gate_record_count"] == 1
        and summary["invalid_gate_record_count"] == 5
        and summary["gate_count"] == 6
        and summary["required_gate_count"] == 6
        and cases["valid_focus_application_gate_record"]["valid"] is True
        and cases["active_focus_non_null_gate_record"]["valid"] is False
        and cases["focus_applied_gate_record"]["valid"] is False
        and cases["attention_control_gate_record"]["valid"] is False
        and cases["missing_required_gate_record"]["valid"] is False
        and cases["runtime_permission_enabled_gate_record"]["valid"] is False
        and summary["missing_required_gate_blocked_count"] >= 1
        and summary["active_focus_non_null_blocked_count"] >= 1
        and summary["focus_applied_blocked_count"] >= 1
        and summary["attention_control_blocked_count"] >= 1
        and summary["runtime_permission_enabled_blocked_count"] >= 1
        and summary["runtime_focus_selector_count"] == 0
        and summary["runtime_ranking_count"] == 0
        and summary["active_focus_enabled_count"] == 0
        and summary["focus_to_action_bridge_count"] == 0
        and summary["perception_to_action_bridge_count"] == 0
        and summary["endocrine_runtime_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["object_recognition_count"] == 0
        and summary["object_tracking_count"] == 0
        and summary["semantic_vision_count"] == 0
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "focus_application_gate_schema_enabled": True,
        "schema_check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "review_only_gates": True,
        "all_gates_passed_allowed": False,
        "runtime_focus_selector_added": False,
        "runtime_ranking_added": False,
        "active_focus_selection_added": False,
        "focus_application_added": False,
        "attention_control_added": False,
        "focus_to_action_bridge_added": False,
        "perception_to_action_bridge_added": False,
        "endocrine_runtime_added": False,
        "action_selection_modified": False,
        "vision_used_for_action_selection": False,
        "visual_memory_write": False,
        "long_term_memory_write": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "predictor_modified": False,
        "global_predictor_modified": False,
        "object_recognition_enabled": False,
        "object_tracking_enabled": False,
        "semantic_vision_claimed": False,
        "llm_vision_used": False,
        "llm_reasoning_used": False,
        "llm_planning_used": False,
        "consciousness_claimed": False,
        "subjective_visual_experience_claimed": False,
        "runtime_focus_selector_count": summary["runtime_focus_selector_count"],
        "runtime_ranking_count": summary["runtime_ranking_count"],
        "active_focus_enabled_count": summary["active_focus_enabled_count"],
        "focus_to_action_bridge_count": summary["focus_to_action_bridge_count"],
        "perception_to_action_bridge_count": summary["perception_to_action_bridge_count"],
        "endocrine_runtime_count": summary["endocrine_runtime_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "memory_write_count": summary["memory_write_count"],
        "endocrine_control_count": summary["endocrine_control_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "object_recognition_count": summary["object_recognition_count"],
        "object_tracking_count": summary["object_tracking_count"],
        "semantic_vision_count": summary["semantic_vision_count"],
    }


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_error_prefix(validation_results: list[dict[str, Any]], prefix: str) -> int:
    return sum(
        1 for result in validation_results
        if any(error_code.startswith(prefix) for error_code in result["error_codes"])
    )
