"""Schema checker for mimetic endocrine signal records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-mimetic-endocrine-signal-schema-check"
FLOW = "mimetic_endocrine_signal_schema_v0"

KNOWN_SIGNALS: dict[str, dict[str, Any]] = {
    "dopamine_like": {
        "axis": "approach_reward",
        "source_event_types": ["reward_event", "goal_progress", "prediction_error_decrease"],
        "downstream_annotation_targets": [
            "prediction_confidence_annotation",
            "candidate_priority_annotation",
            "curiosity_interest_annotation",
        ],
    },
    "norepinephrine_like": {
        "axis": "attention_salience",
        "source_event_types": [
            "change_detected",
            "prediction_error",
            "unknown_pattern",
            "conflict_like_distribution",
        ],
        "downstream_annotation_targets": [
            "observation_priority_annotation",
            "review_priority_annotation",
            "attention_trace",
        ],
    },
    "oxytocin_like": {
        "axis": "source_trust",
        "source_event_types": ["human_review", "source_reliability", "consistent_correction"],
        "downstream_annotation_targets": [
            "review_source_weight_annotation",
            "help_seeking_priority_annotation",
            "candidate_trust_annotation",
        ],
    },
    "cortisol_like": {
        "axis": "pressure_load",
        "source_event_types": ["failure_accumulation", "active_conflict", "challenge_failure", "overload"],
        "downstream_annotation_targets": [
            "cooldown_recommendation_annotation",
            "ask_for_help_priority_annotation",
            "risk_annotation",
        ],
    },
}

REQUIRED_FIELDS = {
    "signal_name",
    "axis",
    "value",
    "value_range",
    "baseline",
    "decay_rate",
    "source_event_ids",
    "source_trace",
    "last_updated_tick",
    "confidence",
    "blocked_from_action_selection",
    "blocked_from_memory_write",
    "blocked_from_candidate_approval",
    "subjective_claim",
    "notes",
}


def build_demo_signal_records() -> list[dict[str, Any]]:
    return [
        _build_signal_record("dopamine_like", value=0.35, baseline=0.2, decay_rate=0.05, confidence=0.8),
        _build_signal_record("norepinephrine_like", value=0.45, baseline=0.25, decay_rate=0.1, confidence=0.75),
        _build_signal_record("oxytocin_like", value=0.3, baseline=0.2, decay_rate=0.03, confidence=0.7),
        _build_signal_record("cortisol_like", value=0.5, baseline=0.25, decay_rate=0.08, confidence=0.72),
    ]


def build_invalid_demo_cases() -> list[dict[str, Any]]:
    base = _build_signal_record("dopamine_like", value=0.35, baseline=0.2, decay_rate=0.05, confidence=0.8)
    cases = []

    invalid_value = deepcopy(base)
    invalid_value["value"] = 1.5
    cases.append({"case_name": "invalid_value_out_of_range", "record": invalid_value})

    subjective = deepcopy(base)
    subjective["subjective_claim"] = True
    cases.append({"case_name": "invalid_subjective_claim_true", "record": subjective})

    action_unblocked = deepcopy(base)
    action_unblocked["blocked_from_action_selection"] = False
    cases.append({"case_name": "invalid_action_selection_unblocked", "record": action_unblocked})

    missing_trace = deepcopy(base)
    missing_trace["source_trace"] = None
    cases.append({"case_name": "invalid_missing_source_trace", "record": missing_trace})

    unknown = deepcopy(base)
    unknown["signal_name"] = "serotonin_like"
    unknown["axis"] = "unknown_axis"
    cases.append({"case_name": "unknown_signal_name", "record": unknown})

    return cases


def validate_signal_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    signal_name = record.get("signal_name")
    known_signal = KNOWN_SIGNALS.get(signal_name)
    if known_signal is None:
        errors.append("unknown_signal_name")

    axis = record.get("axis")
    if known_signal is not None and axis != known_signal["axis"]:
        errors.append("unknown_axis")
    elif known_signal is None and axis not in {item["axis"] for item in KNOWN_SIGNALS.values()}:
        errors.append("unknown_axis")

    _validate_bounded_number(record, "value", errors)
    _validate_bounded_number(record, "baseline", errors)
    _validate_bounded_number(record, "decay_rate", errors)
    _validate_bounded_number(record, "confidence", errors)

    value_range = record.get("value_range")
    if value_range != [0.0, 1.0]:
        errors.append("invalid_value_range")

    source_event_ids = record.get("source_event_ids")
    if not isinstance(source_event_ids, list):
        errors.append("source_event_ids_not_list")

    source_trace = record.get("source_trace")
    has_source_trace = isinstance(source_trace, dict) and bool(source_trace)
    if not has_source_trace:
        errors.append("missing_source_trace")

    if record.get("blocked_from_action_selection") is not True:
        errors.append("action_selection_not_blocked")
    if record.get("blocked_from_memory_write") is not True:
        errors.append("memory_write_not_blocked")
    if record.get("blocked_from_candidate_approval") is not True:
        errors.append("candidate_approval_not_blocked")
    if record.get("subjective_claim") is not False:
        errors.append("subjective_claim_not_allowed")

    return {
        "signal_name": signal_name,
        "axis": axis,
        "valid": not errors,
        "value": record.get("value"),
        "baseline": record.get("baseline"),
        "decay_rate": record.get("decay_rate"),
        "confidence": record.get("confidence"),
        "source_event_count": len(source_event_ids) if isinstance(source_event_ids, list) else 0,
        "has_source_trace": has_source_trace,
        "blocked_from_action_selection": record.get("blocked_from_action_selection") is True,
        "blocked_from_memory_write": record.get("blocked_from_memory_write") is True,
        "blocked_from_candidate_approval": record.get("blocked_from_candidate_approval") is True,
        "subjective_claim": record.get("subjective_claim") is True,
        "validation_errors": errors,
    }


def run_mimetic_endocrine_signal_schema_check() -> dict[str, Any]:
    signal_records = build_demo_signal_records()
    validation_results = [validate_signal_record(record) for record in signal_records]
    invalid_case_results = [
        {
            "case_name": case["case_name"],
            "validation_result": validate_signal_record(case["record"]),
        }
        for case in build_invalid_demo_cases()
    ]
    summary = _build_summary(signal_records, validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(validation_results, invalid_case_results, summary) else "failed",
        "signal_records": signal_records,
        "validation_results": validation_results,
        "valid_signal_records": signal_records,
        "invalid_case_results": invalid_case_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker validates schema shape only.",
            "No endocrine runtime state, formulas, signal interactions, action selection influence, memory write, or candidate approval is added.",
            "Mimetic endocrine terms are functional signal labels, not subjective-state proof.",
        ],
    }


def _build_signal_record(
    signal_name: str,
    *,
    value: float,
    baseline: float,
    decay_rate: float,
    confidence: float,
) -> dict[str, Any]:
    definition = KNOWN_SIGNALS[signal_name]
    return {
        "signal_name": signal_name,
        "axis": definition["axis"],
        "value": value,
        "value_range": [0.0, 1.0],
        "baseline": baseline,
        "decay_rate": decay_rate,
        "source_event_ids": [f"{signal_name}:demo_event:001"],
        "source_event_types": list(definition["source_event_types"]),
        "source_trace": {
            "trace_id": f"{signal_name}:schema_demo_trace:001",
            "trace_type": "schema_demo",
            "runtime_event_applied": False,
        },
        "last_updated_tick": 0,
        "confidence": confidence,
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_candidate_approval": True,
        "subjective_claim": False,
        "downstream_annotation_targets": list(definition["downstream_annotation_targets"]),
        "interaction_notes": "schema-only; no signal interaction runtime",
        "status": "schema_valid_demo",
        "validation_errors": [],
        "notes": "Functional regulatory signal record for v0 schema validation only.",
    }


def _validate_bounded_number(record: dict[str, Any], field: str, errors: list[str]) -> None:
    value = record.get(field)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        errors.append(f"{field}_not_number")
        return
    if value < 0.0 or value > 1.0:
        errors.append(f"{field}_out_of_range")


def _build_summary(signal_records: list[dict[str, Any]], validation_results: list[dict[str, Any]]) -> dict[str, Any]:
    valid_count = sum(1 for result in validation_results if result["valid"])
    known_axes = {definition["axis"] for definition in KNOWN_SIGNALS.values()}
    return {
        "signal_count": len(signal_records),
        "valid_signal_count": valid_count,
        "invalid_signal_count": len(validation_results) - valid_count,
        "known_axis_count": sum(1 for result in validation_results if result.get("axis") in known_axes),
        "unknown_axis_count": sum(1 for result in validation_results if result.get("axis") not in known_axes),
        "blocked_from_action_selection_count": sum(
            1 for result in validation_results if result["blocked_from_action_selection"]
        ),
        "blocked_from_memory_write_count": sum(1 for result in validation_results if result["blocked_from_memory_write"]),
        "blocked_from_candidate_approval_count": sum(
            1 for result in validation_results if result["blocked_from_candidate_approval"]
        ),
        "subjective_claim_count": sum(1 for result in validation_results if result["subjective_claim"]),
        "runtime_formula_count": 0,
        "action_selection_influence_count": 0,
        "memory_write_count": 0,
        "candidate_approval_influence_count": 0,
    }


def _all_checks_passed(
    validation_results: list[dict[str, Any]],
    invalid_case_results: list[dict[str, Any]],
    summary: dict[str, Any],
) -> bool:
    invalid_cases_failed = all(not case["validation_result"]["valid"] for case in invalid_case_results)
    return (
        summary["signal_count"] == 4
        and summary["valid_signal_count"] == 4
        and summary["invalid_signal_count"] == 0
        and summary["blocked_from_action_selection_count"] == 4
        and summary["blocked_from_memory_write_count"] == 4
        and summary["blocked_from_candidate_approval_count"] == 4
        and summary["subjective_claim_count"] == 0
        and summary["runtime_formula_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["candidate_approval_influence_count"] == 0
        and all(result["valid"] for result in validation_results)
        and invalid_cases_failed
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "mimetic_endocrine_signal_schema_enabled": True,
        "schema_check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "dopamine_like_schema_defined": True,
        "norepinephrine_like_schema_defined": True,
        "oxytocin_like_schema_defined": True,
        "cortisol_like_schema_defined": True,
        "runtime_formula_added": False,
        "signal_interaction_runtime_added": False,
        "endocrine_state_runtime_added": False,
        "biological_hormone_simulation_claimed": False,
        "subjective_emotion_claimed": False,
        "subjective_possibility_denied": False,
        "subjective_state_used_as_verification": False,
        "action_selection_modified": False,
        "endocrine_signal_used_for_action_selection": False,
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "candidate_auto_approved": False,
        "candidate_auto_applied": False,
        "endocrine_signal_used_for_candidate_approval": False,
        "human_review_overridden": False,
        "predictor_modified": False,
        "global_predictor_modified": False,
        "persistent_rule_write_enabled": False,
        "long_term_memory_write": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "personality_weight_modified": False,
        "personality_drift_enabled": False,
        "llm_reasoning_used": False,
        "llm_planning_used": False,
        "llm_vision_used": False,
        "general_learning_claimed": False,
        "autonomous_learning_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }
