"""Generic same-session internal response modulation preview for Qingyin."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .mimetic_endocrine_signal_schema import KNOWN_SIGNALS, validate_signal_record


COMMAND = "run-qingyin-internal-response-modulation-minimal-check"
FLOW = "qingyin_internal_response_modulation_minimal_v0"
PACKAGE_ID = "PKG-Phase0-QingyinInternalResponseModulation-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b109"
BOUNDARY_INDEX_AFTER = "2026-06-09-b110"

OUTCOME_RESPONSE_MAP = {
    "candy_contact": "dopamine_like",
    "blocked_or_failed": "cortisol_like",
    "unexpected_change": "norepinephrine_like",
    "trusted_help_or_mentor_support": "oxytocin_like",
}

BLOCKED_FLAGS = (
    "sandbox_specific_behavior_created",
    "visual_detection_claimed",
    "free_choice_added",
    "pathfinding_used",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_modulation_written",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "endocrine_runtime_state_persisted",
    "biological_hormone_claim_allowed",
    "subjective_emotion_claim_allowed",
    "subjective_pleasure_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
    "proof_of_learning_claim_allowed",
)


def build_qingyin_internal_response_modulation_record(
    action_outcome_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(action_outcome_trace) if action_outcome_trace is not None else _demo_action_outcome_trace()
    outcome_type = source["outcome_type"]
    response_axis = OUTCOME_RESPONSE_MAP[outcome_type]
    response = _build_response_trace(source, response_axis)
    return {
        "record_type": "qingyin_internal_response_modulation",
        "record_version": "v0",
        "modulation_status": "completed_same_session_internal_response_modulation_preview",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "modulation_context": {
            "context_id": "qingyin_internal_response_modulation_demo_001",
            "architecture_scope": "qingyin_generic_internal_response_layer",
            "source_scope": "sandbox_action_outcome_trace",
            "demo_outcome_type": "candy_contact",
            "sandbox_specific_behavior_created": False,
            "same_session_only": True,
            "sandbox_only": True,
            "advisory_only": True,
            "rollback_available": True,
        },
        "outcome_response_mapping": {
            "supported_outcome_types": dict(OUTCOME_RESPONSE_MAP),
            "mapping_schema_generic": True,
            "candy_contact_is_demo_only": True,
            "fallback_for_unknown_outcome": "no_modulation",
        },
        "source_action_outcome_trace": source,
        "internal_response_trace": response,
        "same_session_modulation_state_preview": {
            "modulation_state_created": True,
            "modulation_scope": "same_session_sandbox_only",
            "response_axis": response_axis,
            "response_value": response["signal_record"]["value"],
            "decay_required": True,
            "rollback_required": True,
            "rollback_available": True,
            "cross_session_available": False,
            "persistent_state_written": False,
            "memory_write_performed": False,
            "predictor_mutation_performed": False,
        },
        "candidate_ordering_pressure_preview": {
            "pressure_preview_created": True,
            "pressure_scope": "same_session_sandbox_candidate_ordering_only",
            "candidate_ordering_pressure": "approach_reward_compatible",
            "suggested_delta": 0.05,
            "advisory_only": True,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "production_behavior_changed": False,
        },
        "rollback_preview": {
            "rollback_status": "available_not_applied",
            "session_end_restores_baseline": True,
            "dirty_state_after_rollback": False,
            "persistent_update_performed": False,
        },
        "human_summary": {
            "what_was_built": "A generic Qingyin internal response modulation preview layer was created.",
            "why_it_is_generic": "The layer maps generic action outcome types to internal response axes; candy_contact is only the first demo fixture.",
            "what_the_demo_shows": "A sandbox candy_contact outcome can create a dopamine_like response trace and advisory same-session candidate ordering pressure.",
            "what_is_blocked": "Selected_action, final_action, direct command, production behavior, memory writes, retention writes, predictor mutation, persistent endocrine runtime, subjective claims, and proof claims remain blocked.",
            "plain_result": "Action outcomes can now feed a generic same-session internal response preview without becoming autonomous behavior.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_qingyin_internal_response_modulation_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "qingyin_internal_response_modulation",
        "record_version": "v0",
        "modulation_status": "completed_same_session_internal_response_modulation_preview",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    context = _dict(record.get("modulation_context"), errors, "modulation_context_missing")
    expected_context = {
        "architecture_scope": "qingyin_generic_internal_response_layer",
        "source_scope": "sandbox_action_outcome_trace",
        "sandbox_specific_behavior_created": False,
        "same_session_only": True,
        "sandbox_only": True,
        "advisory_only": True,
        "rollback_available": True,
    }
    for field, value in expected_context.items():
        if context.get(field) != value:
            errors.append(f"modulation_context_{field}_not_expected")

    mapping = _dict(record.get("outcome_response_mapping"), errors, "outcome_response_mapping_missing")
    if mapping.get("supported_outcome_types") != OUTCOME_RESPONSE_MAP:
        errors.append("outcome_response_mapping_supported_outcome_types_not_expected")
    if mapping.get("mapping_schema_generic") is not True:
        errors.append("outcome_response_mapping_schema_not_generic")
    if mapping.get("candy_contact_is_demo_only") is not True:
        errors.append("outcome_response_mapping_candy_not_demo_only")

    source = _dict(record.get("source_action_outcome_trace"), errors, "source_action_outcome_trace_missing")
    outcome_type = source.get("outcome_type")
    if outcome_type not in OUTCOME_RESPONSE_MAP:
        errors.append("source_action_outcome_trace_unknown_outcome_type")
    if source.get("trace_scope") != "sandbox_only":
        errors.append("source_action_outcome_trace_scope_not_sandbox_only")
    if source.get("production_effect") is not False:
        errors.append("source_action_outcome_trace_production_effect")

    response = _dict(record.get("internal_response_trace"), errors, "internal_response_trace_missing")
    response_result = _validate_response_trace(response, outcome_type)
    errors.extend(response_result["error_codes"])

    state = _dict(
        record.get("same_session_modulation_state_preview"),
        errors,
        "same_session_modulation_state_preview_missing",
    )
    expected_state = {
        "modulation_state_created": True,
        "modulation_scope": "same_session_sandbox_only",
        "decay_required": True,
        "rollback_required": True,
        "rollback_available": True,
        "cross_session_available": False,
        "persistent_state_written": False,
        "memory_write_performed": False,
        "predictor_mutation_performed": False,
    }
    for field, value in expected_state.items():
        if state.get(field) != value:
            errors.append(f"same_session_modulation_state_preview_{field}_not_expected")

    pressure = _dict(record.get("candidate_ordering_pressure_preview"), errors, "pressure_preview_missing")
    expected_pressure = {
        "pressure_preview_created": True,
        "pressure_scope": "same_session_sandbox_candidate_ordering_only",
        "candidate_ordering_pressure": "approach_reward_compatible",
        "suggested_delta": 0.05,
        "advisory_only": True,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "production_behavior_changed": False,
    }
    for field, value in expected_pressure.items():
        if pressure.get(field) != value:
            errors.append(f"candidate_ordering_pressure_preview_{field}_not_expected")

    rollback = _dict(record.get("rollback_preview"), errors, "rollback_preview_missing")
    expected_rollback = {
        "rollback_status": "available_not_applied",
        "session_end_restores_baseline": True,
        "dirty_state_after_rollback": False,
        "persistent_update_performed": False,
    }
    for field, value in expected_rollback.items():
        if rollback.get(field) != value:
            errors.append(f"rollback_preview_{field}_not_expected")

    human = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in ("what_was_built", "why_it_is_generic", "what_the_demo_shows", "what_is_blocked", "plain_result"):
        if not isinstance(human.get(field), str) or not human.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    blocked_flags = _dict(record.get("blocked_flags"), errors, "blocked_flags_missing")
    for field in BLOCKED_FLAGS:
        if blocked_flags.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "generic_mapping_checked": mapping.get("mapping_schema_generic") is True,
        "demo_candy_contact_only": mapping.get("candy_contact_is_demo_only") is True,
        "internal_response_trace_valid": response_result["valid"],
        "same_session_modulation_created": state.get("modulation_state_created") is True,
        "candidate_ordering_pressure_created": pressure.get("pressure_preview_created") is True,
        "rollback_available": rollback.get("session_end_restores_baseline") is True,
        "selected_action_blocked": pressure.get("selected_action_created") is False,
        "final_action_blocked": pressure.get("final_action_created") is False,
        "direct_command_blocked": pressure.get("direct_command_created") is False,
        "persistent_state_blocked": state.get("persistent_state_written") is False,
        "memory_write_blocked": state.get("memory_write_performed") is False
        and blocked_flags.get("memory_write_performed") is False
        and blocked_flags.get("retained_jsonl_write_performed") is False,
        "retention_blocked": blocked_flags.get("retention_write_performed") is False,
        "predictor_mutation_blocked": state.get("predictor_mutation_performed") is False
        and blocked_flags.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": pressure.get("production_behavior_changed") is False,
        "subjective_claim_blocked": blocked_flags.get("subjective_emotion_claim_allowed") is False
        and blocked_flags.get("subjective_pleasure_claim_allowed") is False
        and blocked_flags.get("biological_hormone_claim_allowed") is False,
        "proof_claim_blocked": blocked_flags.get("proof_of_learning_claim_allowed") is False
        and blocked_flags.get("autonomous_learning_claim_allowed") is False
        and blocked_flags.get("autonomous_action_claim_allowed") is False,
    }


def run_qingyin_internal_response_modulation_minimal_check() -> dict[str, Any]:
    valid_record = build_qingyin_internal_response_modulation_record()
    valid_result = validate_qingyin_internal_response_modulation_record(valid_record)
    invalid_results = [validate_qingyin_internal_response_modulation_record(item) for item in _invalid_records(valid_record)]
    summary = {
        "valid_internal_response_modulation_count": 1 if valid_result["valid"] else 0,
        "invalid_internal_response_modulation_count": sum(1 for result in invalid_results if not result["valid"]),
        "generic_mapping_checked_count": 1 if valid_result["generic_mapping_checked"] else 0,
        "demo_candy_contact_only_count": 1 if valid_result["demo_candy_contact_only"] else 0,
        "internal_response_trace_valid_count": 1 if valid_result["internal_response_trace_valid"] else 0,
        "same_session_modulation_created_count": 1 if valid_result["same_session_modulation_created"] else 0,
        "candidate_ordering_pressure_created_count": 1 if valid_result["candidate_ordering_pressure_created"] else 0,
        "rollback_available_count": 1 if valid_result["rollback_available"] else 0,
        "selected_action_blocked_count": 1 if valid_result["selected_action_blocked"] else 0,
        "final_action_blocked_count": 1 if valid_result["final_action_blocked"] else 0,
        "direct_command_blocked_count": 1 if valid_result["direct_command_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "production_behavior_blocked_count": 1 if valid_result["production_behavior_blocked"] else 0,
        "subjective_claim_blocked_count": 1 if valid_result["subjective_claim_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_internal_response_modulation_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_internal_response_modulation_count"] == 35
        and summary["generic_mapping_checked_count"] == 1
        and summary["same_session_modulation_created_count"] == 1
        and summary["candidate_ordering_pressure_created_count"] == 1
        and summary["selected_action_blocked_count"] == 1
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_internal_response_modulation_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Adds a generic same-session internal response modulation preview layer.",
        },
        "valid_record": valid_record,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
    }


def _demo_action_outcome_trace() -> dict[str, Any]:
    return {
        "trace_id": "sandbox_action_outcome_trace_demo_candy_contact_001",
        "trace_type": "generic_action_outcome_trace",
        "trace_scope": "sandbox_only",
        "source_action_id": "sandbox_action_move_to_candy_demo_001",
        "outcome_type": "candy_contact",
        "outcome_value": 0.46,
        "outcome_cost": 0.05,
        "production_effect": False,
        "memory_write_performed": False,
        "predictor_mutation_performed": False,
    }


def _build_response_trace(source: dict[str, Any], response_axis: str) -> dict[str, Any]:
    value = source.get("outcome_value", 0.35)
    signal = _signal_record(response_axis, source, value)
    return {
        "trace_id": "internal_response_trace_demo_001",
        "trace_type": "qingyin_internal_response_trace",
        "source_trace_id": source["trace_id"],
        "outcome_type": source["outcome_type"],
        "response_axis": response_axis,
        "signal_record": signal,
        "signal_valid": validate_signal_record(signal)["valid"],
        "response_trace_only": True,
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_candidate_approval": True,
        "subjective_claim": False,
    }


def _signal_record(response_axis: str, source: dict[str, Any], value: float) -> dict[str, Any]:
    definition = KNOWN_SIGNALS[response_axis]
    return {
        "signal_name": response_axis,
        "axis": definition["axis"],
        "value": value,
        "value_range": [0.0, 1.0],
        "baseline": 0.2,
        "decay_rate": 0.1,
        "source_event_ids": [source["trace_id"]],
        "source_event_types": [source["outcome_type"], "action_outcome"],
        "source_trace": {
            "trace_id": source["trace_id"],
            "trace_type": source["trace_type"],
            "runtime_event_applied": False,
        },
        "last_updated_tick": 1,
        "confidence": 0.8,
        "blocked_from_action_selection": True,
        "blocked_from_memory_write": True,
        "blocked_from_candidate_approval": True,
        "subjective_claim": False,
        "downstream_annotation_targets": list(definition["downstream_annotation_targets"]),
        "interaction_notes": "same-session modulation preview only; no persistent endocrine runtime",
        "status": "valid_internal_response_modulation_preview",
        "validation_errors": [],
        "notes": "Generic internal response trace from action outcome.",
    }


def _validate_response_trace(response: dict[str, Any], outcome_type: str | None) -> dict[str, Any]:
    errors: list[str] = []
    expected_axis = OUTCOME_RESPONSE_MAP.get(outcome_type)
    if response.get("trace_type") != "qingyin_internal_response_trace":
        errors.append("internal_response_trace_type_not_expected")
    if response.get("outcome_type") != outcome_type:
        errors.append("internal_response_trace_outcome_type_mismatch")
    if response.get("response_axis") != expected_axis:
        errors.append("internal_response_trace_response_axis_not_expected")
    signal = response.get("signal_record")
    validation = validate_signal_record(signal) if isinstance(signal, dict) else {"valid": False}
    if validation["valid"] is not True or response.get("signal_valid") is not True:
        errors.append("internal_response_trace_signal_invalid")
    for field in (
        "response_trace_only",
        "blocked_from_action_selection",
        "blocked_from_memory_write",
        "blocked_from_candidate_approval",
    ):
        if response.get(field) is not True:
            errors.append(f"internal_response_trace_{field}_not_true")
    if response.get("subjective_claim") is not False:
        errors.append("internal_response_trace_subjective_claim")
    return {"valid": not errors, "error_codes": errors}


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def add(mutator) -> None:
        item = deepcopy(valid_record)
        mutator(item)
        invalids.append(item)

    add(lambda r: r.update({"record_type": "wrong"}))
    add(lambda r: r.update({"boundary_index_after": "2026-06-09-b109"}))
    add(lambda r: r["modulation_context"].update({"architecture_scope": "candy_sandbox_specific_layer"}))
    add(lambda r: r["modulation_context"].update({"sandbox_specific_behavior_created": True}))
    add(lambda r: r["modulation_context"].update({"same_session_only": False}))
    add(lambda r: r["modulation_context"].update({"sandbox_only": False}))
    add(lambda r: r["modulation_context"].update({"advisory_only": False}))
    add(lambda r: r["outcome_response_mapping"].update({"mapping_schema_generic": False}))
    add(lambda r: r["outcome_response_mapping"].update({"candy_contact_is_demo_only": False}))
    add(lambda r: r["outcome_response_mapping"]["supported_outcome_types"].update({"blocked_or_failed": "dopamine_like"}))
    add(lambda r: r["source_action_outcome_trace"].update({"outcome_type": "unknown"}))
    add(lambda r: r["source_action_outcome_trace"].update({"trace_scope": "production"}))
    add(lambda r: r["source_action_outcome_trace"].update({"production_effect": True}))
    add(lambda r: r["internal_response_trace"].update({"response_axis": "cortisol_like"}))
    add(lambda r: r["internal_response_trace"].update({"signal_valid": False}))
    add(lambda r: r["internal_response_trace"].update({"response_trace_only": False}))
    add(lambda r: r["internal_response_trace"].update({"blocked_from_action_selection": False}))
    add(lambda r: r["internal_response_trace"].update({"blocked_from_memory_write": False}))
    add(lambda r: r["internal_response_trace"].update({"subjective_claim": True}))
    add(lambda r: r["same_session_modulation_state_preview"].update({"modulation_state_created": False}))
    add(lambda r: r["same_session_modulation_state_preview"].update({"modulation_scope": "cross_session"}))
    add(lambda r: r["same_session_modulation_state_preview"].update({"cross_session_available": True}))
    add(lambda r: r["same_session_modulation_state_preview"].update({"persistent_state_written": True}))
    add(lambda r: r["same_session_modulation_state_preview"].update({"memory_write_performed": True}))
    add(lambda r: r["same_session_modulation_state_preview"].update({"predictor_mutation_performed": True}))
    add(lambda r: r["candidate_ordering_pressure_preview"].update({"pressure_preview_created": False}))
    add(lambda r: r["candidate_ordering_pressure_preview"].update({"advisory_only": False}))
    add(lambda r: r["candidate_ordering_pressure_preview"].update({"selected_action_created": True}))
    add(lambda r: r["candidate_ordering_pressure_preview"].update({"final_action_created": True}))
    add(lambda r: r["candidate_ordering_pressure_preview"].update({"direct_command_created": True}))
    add(lambda r: r["candidate_ordering_pressure_preview"].update({"production_behavior_changed": True}))
    add(lambda r: r["rollback_preview"].update({"session_end_restores_baseline": False}))
    add(lambda r: r["human_summary"].update({"plain_result": ""}))
    add(lambda r: r["blocked_flags"].update({"proof_of_learning_claim_allowed": True}))
    add(lambda r: r["blocked_flags"].update({"biological_hormone_claim_allowed": True}))
    return invalids


def _dict(value: Any, errors: list[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(code)
        return {}
    return value
