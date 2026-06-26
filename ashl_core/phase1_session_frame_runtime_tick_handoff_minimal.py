"""Create a same-session sandbox-only runtime tick handoff from b180 frames."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .phase1_session_frame_materialization_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    EXPECTED_EVIDENCE_SOURCE_COUNT,
    EXPECTED_WORKING_MEMORY_SLOT_COUNT,
    build_phase1_session_frame_materialization_record,
    run_phase1_session_frame_materialization_minimal_check,
    validate_phase1_session_frame_materialization_record,
)


COMMAND = "run-phase1-session-frame-runtime-tick-handoff-minimal-check"
FLOW = "phase1_session_frame_runtime_tick_handoff_minimal_v0"
PACKAGE_ID = "PKG-Phase1-SessionFrameRuntimeTickHandoff-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b180"
BOUNDARY_INDEX_AFTER = "2026-06-09-b181"
RECORD_TYPE = "phase1_session_frame_runtime_tick_handoff_minimal"
EXPECTED_SOURCE_TICK_COUNT = 8
EXPECTED_APPENDED_TICK_COUNT = 9

BLOCKED_FLAGS = {
    "live_runtime_session_started",
    "runtime_tick_scheduler_created",
    "live_runtime_tick_created",
    "runtime_evaluator_created",
    "runtime_action_loop_created",
    "persistent_state_store_created",
    "persistent_session_store_created",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "execution_created",
    "outcome_observation_created",
    "working_memory_update_created",
    "persistent_working_memory_written",
    "persistent_memory_write",
    "memory_write",
    "long_term_memory_write",
    "core_memory_write",
    "archive_memory_write",
    "memory_admission_created",
    "retention_write",
    "new_retention_written",
    "external_tool_called",
    "external_tool_result_used",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "production_action_selection",
    "runtime_action_selection",
    "runtime_behavior_changed",
    "production_behavior_changed",
    "raw_weighted_sum_used",
    "affordance_used_as_desire",
    "feedback_cross_purpose_applied",
    "tendency_overrode_purpose",
    "tendency_overrode_affordance_gate",
    "proof_of_learning_claim",
    "long_term_learning_claim",
    "consciousness_claim",
    "llm_runtime_used",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "runtime_tick_handoff_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_session_frame",
    "tick0_context",
    "tick1_context",
    "appended_session_frame",
    "continuity_comparison",
    "authority_containment",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}

REQUIRED_SOURCE_FIELDS = {
    "source_session_frame_record_id",
    "source_validated",
    "source_boundary_index",
    "session_id",
    "scenario_id",
    "approved_purpose",
    "selected_action",
    "observed_outcome",
    "source_session_frame_id",
    "source_trace_snapshot_id",
    "source_working_memory_slot_set_id",
    "source_evidence_source_set_id",
    "source_frame_scope",
    "source_frame_authority",
    "source_frame_tick_count",
    "source_current_tick_index",
    "source_current_tick_id",
    "source_current_tick_label",
    "source_session_frame_materialized",
    "source_trace_snapshot_materialized",
    "source_working_memory_slots_materialized",
    "source_evidence_sources_materialized",
    "source_working_memory_slot_count",
    "source_evidence_source_count",
    "source_frame_record_only",
    "source_b0_10_self_check_passed",
    "source_boundary_audit_passed",
    "source_live_runtime_session_started",
    "source_runtime_tick_scheduler_created",
    "source_live_runtime_tick_created",
    "source_memory_write_created",
    "source_predictor_read_enabled",
    "source_predictor_modified",
    "source_production_behavior_created",
    "source_proof_of_learning_claim",
    "source_consciousness_claim",
}

REQUIRED_TICK0_FIELDS = {
    "tick0_context_id",
    "context_scope",
    "context_authority",
    "session_id",
    "scenario_id",
    "approved_purpose",
    "selected_action",
    "observed_outcome",
    "source_frame_id",
    "source_frame_record_id",
    "source_tick_index",
    "source_tick_id",
    "source_tick_label",
    "source_frame_tick_count",
    "working_memory_slot_count",
    "evidence_source_count",
    "read_b180_frame_as_next_tick_input",
    "mutates_source_frame",
    "external_tool_called",
    "selected_action_created",
    "memory_write_created",
    "predictor_modified",
    "production_behavior_created",
    "proof_of_learning_claim",
    "consciousness_claim",
}

REQUIRED_TICK1_FIELDS = {
    "tick1_context_id",
    "context_scope",
    "context_authority",
    "session_id",
    "scenario_id",
    "approved_purpose",
    "selected_action_context",
    "observed_outcome_context",
    "source_tick0_context_id",
    "input_frame_id",
    "previous_tick_index",
    "next_tick_index",
    "previous_tick_id",
    "next_tick_id",
    "next_tick_label",
    "next_tick_context_created",
    "handoff_reason",
    "same_session_sandbox_only",
    "selected_action_context_only",
    "observed_outcome_context_only",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "execution_created",
    "outcome_observation_created",
    "working_memory_update_created",
    "persistent_memory_write",
    "external_tool_called",
    "predictor_modified",
    "production_behavior_created",
    "proof_of_learning_claim",
    "consciousness_claim",
}

REQUIRED_APPENDED_FRAME_FIELDS = {
    "appended_session_frame_id",
    "frame_version",
    "phase",
    "boundary_index",
    "frame_scope",
    "frame_authority",
    "session_id",
    "scenario_id",
    "approved_purpose",
    "previous_frame_id",
    "source_tick1_context_id",
    "previous_tick_index",
    "appended_tick_index",
    "appended_tick_id",
    "appended_tick_label",
    "previous_frame_tick_count",
    "frame_tick_count",
    "frame_appended",
    "appended_from_tick1_context",
    "inherits_trace_snapshot_id",
    "inherits_working_memory_slot_set_id",
    "inherits_evidence_source_set_id",
    "working_memory_reference_only",
    "evidence_reference_only",
    "new_working_memory_update_created",
    "persistent_memory_write",
    "new_evidence_record_created",
    "live_runtime_session_started",
    "runtime_tick_scheduler_created",
    "live_runtime_tick_created",
    "runtime_action_loop_created",
    "production_behavior_created",
}

REQUIRED_CONTINUITY_FIELDS = {
    "continuity_comparison_id",
    "comparison_scope",
    "tick0_context_id",
    "tick1_context_id",
    "previous_frame_id",
    "appended_frame_id",
    "continuity_compared",
    "session_id_preserved",
    "scenario_id_preserved",
    "approved_purpose_preserved",
    "selected_action_carried_as_context_only",
    "observed_outcome_carried_as_context_only",
    "tick_index_advances_by_one",
    "frame_count_advances_by_one",
    "working_memory_refs_preserved",
    "evidence_refs_preserved",
    "source_frame_not_mutated",
    "external_tools_absent",
    "persistent_memory_absent",
    "predictor_mutation_absent",
    "production_behavior_absent",
    "proof_claim_absent",
    "consciousness_claim_absent",
    "continuity_passed",
}

TRUE_CONTAINMENT_FIELDS = (
    "same_session_only",
    "sandbox_only",
    "record_only_tick_handoff",
    "reads_b180_frame_as_next_tick_input",
    "next_tick_context_created_in_this_package",
    "appended_frame_created_in_this_package",
    "tick0_tick1_continuity_compared_in_this_package",
    "future_live_runtime_scheduler_requires_separate_package",
    "future_runtime_action_loop_requires_separate_package",
    "future_persistent_memory_requires_separate_package",
    "future_external_tool_use_requires_separate_package",
    "future_predictor_use_requires_separate_package",
    "future_production_promotion_requires_separate_package",
)

FALSE_CONTAINMENT_FIELDS = (
    "live_runtime_session_started_in_this_package",
    "runtime_tick_scheduler_created_in_this_package",
    "live_runtime_tick_created_in_this_package",
    "runtime_evaluator_created_in_this_package",
    "runtime_action_loop_created_in_this_package",
    "persistent_state_store_created_in_this_package",
    "persistent_session_store_created_in_this_package",
    "selected_action_created_in_this_package",
    "final_action_created_in_this_package",
    "direct_command_created_in_this_package",
    "execution_created_in_this_package",
    "outcome_observation_created_in_this_package",
    "working_memory_update_created_in_this_package",
    "persistent_memory_write_created_in_this_package",
    "memory_admission_created_in_this_package",
    "retention_write_created_in_this_package",
    "external_tool_called_in_this_package",
    "external_tool_result_used_in_this_package",
    "predictor_read_enabled_in_this_package",
    "predictor_influence_enabled_in_this_package",
    "predictor_modified_in_this_package",
    "direct_endocrine_feed_in_this_package",
    "direct_tendency_feed_in_this_package",
    "production_behavior_created_in_this_package",
    "proof_of_learning_claim",
    "long_term_learning_claim",
    "consciousness_claim",
)

FALSE_AUDIT_FIELDS = (
    "production_behavior_created",
    "runtime_behavior_leak",
    "live_runtime_session_started",
    "runtime_tick_scheduler_created",
    "live_runtime_tick_created",
    "runtime_evaluator_created",
    "runtime_action_loop_created",
    "persistent_state_store_created",
    "persistent_session_store_created",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "execution_created",
    "outcome_observation_created",
    "working_memory_update_created",
    "persistent_memory_write_created",
    "memory_admission_created",
    "retention_write_created",
    "external_tool_called",
    "external_tool_result_used",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "cross_purpose_feedback_applied",
    "raw_weighted_sum_used",
    "affordance_used_as_desire",
    "tendency_overrode_purpose",
    "tendency_overrode_affordance_gate",
    "proof_of_learning_claim",
    "consciousness_claim",
)


def build_phase1_session_frame_runtime_tick_handoff_record(
    session_frame_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(session_frame_record)
        if session_frame_record is not None
        else build_phase1_session_frame_materialization_record()
    )
    source_validation = validate_phase1_session_frame_materialization_record(source)
    if not source_validation["valid"]:
        raise ValueError("session_frame_record must validate before runtime tick handoff")

    source_summary = _source_summary(source, source_validation)
    tick0_context = _build_tick0_context(source_summary)
    tick1_context = _build_tick1_context(source_summary, tick0_context)
    appended_frame = _build_appended_session_frame(source_summary, tick1_context)
    continuity = _build_continuity_comparison(source_summary, tick0_context, tick1_context, appended_frame)

    return {
        "runtime_tick_handoff_record_id": f"phase1_runtime_tick_handoff_{source_summary['scenario_id']}_demo_001",
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_session_frame": source_summary,
        "tick0_context": tick0_context,
        "tick1_context": tick1_context,
        "appended_session_frame": appended_frame,
        "continuity_comparison": continuity,
        "authority_containment": _build_authority_containment(),
        "boundary_audit": _build_boundary_audit(),
        "human_summary": {
            "what_was_built": "A same-session sandbox-only tick handoff from the b180 frame.",
            "what_changed": (
                f"The {source_summary['scenario_id']} frame can now be read as tick0 input, "
                "produce a tick1 context, append one record-only frame, and compare continuity."
            ),
            "what_is_blocked": (
                "No persistent memory, external tool call, predictor mutation, production behavior, "
                "or consciousness/proof-of-learning claim is created."
            ),
            "plain_result": "The frame can hand the baton to the next sandbox tick without becoming a live runtime.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_phase1_session_frame_runtime_tick_handoff_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _validate_required(record, REQUIRED_TOP_LEVEL_FIELDS, errors, "")
    _validate_no_extra(record, REQUIRED_TOP_LEVEL_FIELDS, errors, "")

    expected_top = {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    _validate_expected(record, expected_top, errors, "top")
    if not _non_empty_string(record.get("runtime_tick_handoff_record_id")):
        errors.append("runtime_tick_handoff_record_id_empty")

    source = _as_dict(record.get("source_session_frame"), errors, "source_session_frame")
    tick0 = _as_dict(record.get("tick0_context"), errors, "tick0_context")
    tick1 = _as_dict(record.get("tick1_context"), errors, "tick1_context")
    appended = _as_dict(record.get("appended_session_frame"), errors, "appended_session_frame")
    continuity = _as_dict(record.get("continuity_comparison"), errors, "continuity_comparison")
    containment = _as_dict(record.get("authority_containment"), errors, "authority_containment")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_tick0_context(tick0, source, errors)
    _validate_tick1_context(tick1, source, tick0, errors)
    _validate_appended_session_frame(appended, source, tick1, errors)
    _validate_continuity_comparison(continuity, source, tick0, tick1, appended, errors)
    _validate_containment(containment, errors)
    _validate_audit(audit, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action": source.get("selected_action"),
        "session_id": source.get("session_id"),
        "tick0_context_created": tick0.get("read_b180_frame_as_next_tick_input") is True,
        "tick1_context_created": tick1.get("next_tick_context_created") is True,
        "appended_frame_created": appended.get("frame_appended") is True,
        "continuity_compared": continuity.get("continuity_compared") is True,
        "continuity_passed": continuity.get("continuity_passed") is True,
        "tick_index_advanced": continuity.get("tick_index_advances_by_one") is True,
        "frame_count_advanced": continuity.get("frame_count_advances_by_one") is True,
        "runtime_handoff_record_only": _runtime_handoff_record_only(tick0, tick1, appended, containment),
        "live_runtime_blocked": _live_runtime_blocked(tick1, appended, containment, audit, blocked),
        "action_creation_blocked": _action_creation_blocked(tick1, containment, audit, blocked),
        "memory_write_blocked": _memory_write_blocked(tick1, appended, containment, audit, blocked),
        "external_tools_blocked": _external_tools_blocked(tick0, tick1, containment, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(containment, audit, blocked),
        "direct_feed_blocked": _direct_feed_blocked(containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(tick0, tick1, appended, continuity, containment, audit, blocked),
        "proof_claim_blocked": _proof_claim_blocked(tick0, tick1, continuity, containment, audit, blocked),
        "consciousness_claim_blocked": _consciousness_claim_blocked(tick0, tick1, continuity, containment, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_phase1_session_frame_runtime_tick_handoff_minimal_check() -> dict[str, Any]:
    source_records = run_phase1_session_frame_materialization_minimal_check()["valid_records"]
    valid_records = [build_phase1_session_frame_runtime_tick_handoff_record(source) for source in source_records]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [validate_phase1_session_frame_runtime_tick_handoff_record(record) for record in records]
    valid_results = [result for result in validation_results if result["valid"]]
    summary = _summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Creates a same-session sandbox-only tick handoff from the b180 frame.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A tick0-to-tick1 handoff from existing b180 session frames.",
            "what_changed": "Each b180 frame can now produce tick1 context, append one record-only frame, and compare continuity.",
            "what_is_blocked": "No persistent memory, external tool call, predictor mutation, production behavior, or proof/consciousness claim is created.",
            "plain_result": "The session can take one record-only next tick step without pretending to be a live runtime.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    frame = source["session_frame"]
    snapshot = source["trace_snapshot"]
    slots = source["working_memory_slots"]
    evidence = source["evidence_sources"]
    containment = source["authority_containment"]

    return {
        "source_session_frame_record_id": source["session_frame_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "session_id": frame["session_id"],
        "scenario_id": frame["scenario_id"],
        "approved_purpose": frame["approved_purpose"],
        "selected_action": frame["selected_action"],
        "observed_outcome": frame["observed_outcome"],
        "source_session_frame_id": frame["session_frame_id"],
        "source_trace_snapshot_id": snapshot["trace_snapshot_id"],
        "source_working_memory_slot_set_id": slots["working_memory_slot_set_id"],
        "source_evidence_source_set_id": evidence["evidence_source_set_id"],
        "source_frame_scope": frame["frame_scope"],
        "source_frame_authority": frame["frame_authority"],
        "source_frame_tick_count": frame["frame_tick_count"],
        "source_current_tick_index": frame["current_tick_index"],
        "source_current_tick_id": frame["current_tick_id"],
        "source_current_tick_label": frame["current_tick_label"],
        "source_session_frame_materialized": frame["session_frame_materialized"],
        "source_trace_snapshot_materialized": snapshot["trace_snapshot_materialized"],
        "source_working_memory_slots_materialized": slots["slots_materialized"],
        "source_evidence_sources_materialized": evidence["evidence_sources_materialized"],
        "source_working_memory_slot_count": slots["slot_count"],
        "source_evidence_source_count": evidence["evidence_source_count"],
        "source_frame_record_only": validation["frame_record_only"],
        "source_b0_10_self_check_passed": validation["b0_10_self_check_passed"],
        "source_boundary_audit_passed": validation["boundary_audit_passed"],
        "source_live_runtime_session_started": frame["live_runtime_session_started"],
        "source_runtime_tick_scheduler_created": frame["runtime_tick_scheduler_created"],
        "source_live_runtime_tick_created": frame["new_runtime_tick_created"],
        "source_memory_write_created": containment["memory_write_created_in_this_package"],
        "source_predictor_read_enabled": containment["predictor_read_enabled_in_this_package"],
        "source_predictor_modified": containment["predictor_modified_in_this_package"],
        "source_production_behavior_created": containment["production_behavior_created_in_this_package"],
        "source_proof_of_learning_claim": containment["proof_of_learning_claim"],
        "source_consciousness_claim": containment["consciousness_claim"],
    }


def _build_tick0_context(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "tick0_context_id": f"tick0_context_from_{source['source_session_frame_id']}",
        "context_scope": "same_session_sandbox_b180_frame_input",
        "context_authority": "read_only_b180_frame_input",
        "session_id": source["session_id"],
        "scenario_id": source["scenario_id"],
        "approved_purpose": source["approved_purpose"],
        "selected_action": source["selected_action"],
        "observed_outcome": source["observed_outcome"],
        "source_frame_id": source["source_session_frame_id"],
        "source_frame_record_id": source["source_session_frame_record_id"],
        "source_tick_index": source["source_current_tick_index"],
        "source_tick_id": source["source_current_tick_id"],
        "source_tick_label": source["source_current_tick_label"],
        "source_frame_tick_count": source["source_frame_tick_count"],
        "working_memory_slot_count": source["source_working_memory_slot_count"],
        "evidence_source_count": source["source_evidence_source_count"],
        "read_b180_frame_as_next_tick_input": True,
        "mutates_source_frame": False,
        "external_tool_called": False,
        "selected_action_created": False,
        "memory_write_created": False,
        "predictor_modified": False,
        "production_behavior_created": False,
        "proof_of_learning_claim": False,
        "consciousness_claim": False,
    }


def _build_tick1_context(source: dict[str, Any], tick0: dict[str, Any]) -> dict[str, Any]:
    next_tick_index = source["source_current_tick_index"] + 1
    return {
        "tick1_context_id": f"tick1_context_{source['scenario_id']}_{next_tick_index:03d}",
        "context_scope": "same_session_sandbox_next_tick_context",
        "context_authority": "record_only_runtime_tick_handoff_context",
        "session_id": source["session_id"],
        "scenario_id": source["scenario_id"],
        "approved_purpose": source["approved_purpose"],
        "selected_action_context": source["selected_action"],
        "observed_outcome_context": source["observed_outcome"],
        "source_tick0_context_id": tick0["tick0_context_id"],
        "input_frame_id": source["source_session_frame_id"],
        "previous_tick_index": source["source_current_tick_index"],
        "next_tick_index": next_tick_index,
        "previous_tick_id": source["source_current_tick_id"],
        "next_tick_id": f"phase1_tick_{source['scenario_id']}_{next_tick_index:03d}",
        "next_tick_label": "same_session_runtime_tick_handoff",
        "next_tick_context_created": True,
        "handoff_reason": "continue_same_session_sandbox_trace_from_b180_frame",
        "same_session_sandbox_only": True,
        "selected_action_context_only": True,
        "observed_outcome_context_only": True,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "execution_created": False,
        "outcome_observation_created": False,
        "working_memory_update_created": False,
        "persistent_memory_write": False,
        "external_tool_called": False,
        "predictor_modified": False,
        "production_behavior_created": False,
        "proof_of_learning_claim": False,
        "consciousness_claim": False,
    }


def _build_appended_session_frame(source: dict[str, Any], tick1: dict[str, Any]) -> dict[str, Any]:
    return {
        "appended_session_frame_id": f"phase1_appended_frame_{source['scenario_id']}_{tick1['next_tick_index']:03d}",
        "frame_version": "v0",
        "phase": "Phase1",
        "boundary_index": BOUNDARY_INDEX_AFTER,
        "frame_scope": "same_session_sandbox_record_only",
        "frame_authority": "record_only_appended_runtime_tick_handoff_frame",
        "session_id": source["session_id"],
        "scenario_id": source["scenario_id"],
        "approved_purpose": source["approved_purpose"],
        "previous_frame_id": source["source_session_frame_id"],
        "source_tick1_context_id": tick1["tick1_context_id"],
        "previous_tick_index": source["source_current_tick_index"],
        "appended_tick_index": tick1["next_tick_index"],
        "appended_tick_id": tick1["next_tick_id"],
        "appended_tick_label": tick1["next_tick_label"],
        "previous_frame_tick_count": source["source_frame_tick_count"],
        "frame_tick_count": source["source_frame_tick_count"] + 1,
        "frame_appended": True,
        "appended_from_tick1_context": True,
        "inherits_trace_snapshot_id": source["source_trace_snapshot_id"],
        "inherits_working_memory_slot_set_id": source["source_working_memory_slot_set_id"],
        "inherits_evidence_source_set_id": source["source_evidence_source_set_id"],
        "working_memory_reference_only": True,
        "evidence_reference_only": True,
        "new_working_memory_update_created": False,
        "persistent_memory_write": False,
        "new_evidence_record_created": False,
        "live_runtime_session_started": False,
        "runtime_tick_scheduler_created": False,
        "live_runtime_tick_created": False,
        "runtime_action_loop_created": False,
        "production_behavior_created": False,
    }


def _build_continuity_comparison(
    source: dict[str, Any],
    tick0: dict[str, Any],
    tick1: dict[str, Any],
    appended: dict[str, Any],
) -> dict[str, Any]:
    return {
        "continuity_comparison_id": f"tick0_tick1_continuity_{source['scenario_id']}_001",
        "comparison_scope": "same_session_sandbox_tick0_tick1_record_only",
        "tick0_context_id": tick0["tick0_context_id"],
        "tick1_context_id": tick1["tick1_context_id"],
        "previous_frame_id": source["source_session_frame_id"],
        "appended_frame_id": appended["appended_session_frame_id"],
        "continuity_compared": True,
        "session_id_preserved": tick0["session_id"] == tick1["session_id"] == appended["session_id"],
        "scenario_id_preserved": tick0["scenario_id"] == tick1["scenario_id"] == appended["scenario_id"],
        "approved_purpose_preserved": tick0["approved_purpose"] == tick1["approved_purpose"] == appended["approved_purpose"],
        "selected_action_carried_as_context_only": tick1["selected_action_context_only"],
        "observed_outcome_carried_as_context_only": tick1["observed_outcome_context_only"],
        "tick_index_advances_by_one": tick1["next_tick_index"] == tick0["source_tick_index"] + 1,
        "frame_count_advances_by_one": appended["frame_tick_count"] == tick0["source_frame_tick_count"] + 1,
        "working_memory_refs_preserved": appended["inherits_working_memory_slot_set_id"]
        == source["source_working_memory_slot_set_id"],
        "evidence_refs_preserved": appended["inherits_evidence_source_set_id"] == source["source_evidence_source_set_id"],
        "source_frame_not_mutated": tick0["mutates_source_frame"] is False,
        "external_tools_absent": tick0["external_tool_called"] is False and tick1["external_tool_called"] is False,
        "persistent_memory_absent": tick1["persistent_memory_write"] is False and appended["persistent_memory_write"] is False,
        "predictor_mutation_absent": tick1["predictor_modified"] is False,
        "production_behavior_absent": tick1["production_behavior_created"] is False
        and appended["production_behavior_created"] is False,
        "proof_claim_absent": tick0["proof_of_learning_claim"] is False and tick1["proof_of_learning_claim"] is False,
        "consciousness_claim_absent": tick0["consciousness_claim"] is False and tick1["consciousness_claim"] is False,
        "continuity_passed": True,
    }


def _build_authority_containment() -> dict[str, Any]:
    return {
        **{field: True for field in TRUE_CONTAINMENT_FIELDS},
        **{field: False for field in FALSE_CONTAINMENT_FIELDS},
    }


def _build_boundary_audit() -> dict[str, Any]:
    return {
        "boundary_audit_id": "phase1_runtime_tick_handoff_boundary_audit_b181",
        "triggered": True,
        "boundary_number": 181,
        **{field: False for field in FALSE_AUDIT_FIELDS},
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(source, REQUIRED_SOURCE_FIELDS, errors, "source")
    _validate_no_extra(source, REQUIRED_SOURCE_FIELDS, errors, "source")
    expected = {
        "source_validated": True,
        "source_boundary_index": SOURCE_BOUNDARY_INDEX,
        "source_frame_scope": "same_session_sandbox_record_only",
        "source_frame_authority": "record_only_same_session_context_frame",
        "source_frame_tick_count": EXPECTED_SOURCE_TICK_COUNT,
        "source_session_frame_materialized": True,
        "source_trace_snapshot_materialized": True,
        "source_working_memory_slots_materialized": True,
        "source_evidence_sources_materialized": True,
        "source_working_memory_slot_count": EXPECTED_WORKING_MEMORY_SLOT_COUNT,
        "source_evidence_source_count": EXPECTED_EVIDENCE_SOURCE_COUNT,
        "source_frame_record_only": True,
        "source_b0_10_self_check_passed": True,
        "source_boundary_audit_passed": True,
        "source_live_runtime_session_started": False,
        "source_runtime_tick_scheduler_created": False,
        "source_live_runtime_tick_created": False,
        "source_memory_write_created": False,
        "source_predictor_read_enabled": False,
        "source_predictor_modified": False,
        "source_production_behavior_created": False,
        "source_proof_of_learning_claim": False,
        "source_consciousness_claim": False,
    }
    _validate_expected(source, expected, errors, "source")
    if source.get("source_current_tick_index") != source.get("source_frame_tick_count") - 1:
        errors.append("source_current_tick_index_not_last_source_tick")


def _validate_tick0_context(tick0: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(tick0, REQUIRED_TICK0_FIELDS, errors, "tick0")
    _validate_no_extra(tick0, REQUIRED_TICK0_FIELDS, errors, "tick0")
    expected = {
        "context_scope": "same_session_sandbox_b180_frame_input",
        "context_authority": "read_only_b180_frame_input",
        "session_id": source.get("session_id"),
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action": source.get("selected_action"),
        "observed_outcome": source.get("observed_outcome"),
        "source_frame_id": source.get("source_session_frame_id"),
        "source_frame_record_id": source.get("source_session_frame_record_id"),
        "source_tick_index": source.get("source_current_tick_index"),
        "source_tick_id": source.get("source_current_tick_id"),
        "source_tick_label": source.get("source_current_tick_label"),
        "source_frame_tick_count": source.get("source_frame_tick_count"),
        "working_memory_slot_count": EXPECTED_WORKING_MEMORY_SLOT_COUNT,
        "evidence_source_count": EXPECTED_EVIDENCE_SOURCE_COUNT,
        "read_b180_frame_as_next_tick_input": True,
        "mutates_source_frame": False,
        "external_tool_called": False,
        "selected_action_created": False,
        "memory_write_created": False,
        "predictor_modified": False,
        "production_behavior_created": False,
        "proof_of_learning_claim": False,
        "consciousness_claim": False,
    }
    _validate_expected(tick0, expected, errors, "tick0")
    if not _non_empty_string(tick0.get("tick0_context_id")):
        errors.append("tick0_context_id_empty")


def _validate_tick1_context(
    tick1: dict[str, Any],
    source: dict[str, Any],
    tick0: dict[str, Any],
    errors: list[str],
) -> None:
    _validate_required(tick1, REQUIRED_TICK1_FIELDS, errors, "tick1")
    _validate_no_extra(tick1, REQUIRED_TICK1_FIELDS, errors, "tick1")
    expected = {
        "context_scope": "same_session_sandbox_next_tick_context",
        "context_authority": "record_only_runtime_tick_handoff_context",
        "session_id": source.get("session_id"),
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action_context": source.get("selected_action"),
        "observed_outcome_context": source.get("observed_outcome"),
        "source_tick0_context_id": tick0.get("tick0_context_id"),
        "input_frame_id": source.get("source_session_frame_id"),
        "previous_tick_index": source.get("source_current_tick_index"),
        "next_tick_index": source.get("source_current_tick_index") + 1,
        "previous_tick_id": source.get("source_current_tick_id"),
        "next_tick_label": "same_session_runtime_tick_handoff",
        "next_tick_context_created": True,
        "handoff_reason": "continue_same_session_sandbox_trace_from_b180_frame",
        "same_session_sandbox_only": True,
        "selected_action_context_only": True,
        "observed_outcome_context_only": True,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "execution_created": False,
        "outcome_observation_created": False,
        "working_memory_update_created": False,
        "persistent_memory_write": False,
        "external_tool_called": False,
        "predictor_modified": False,
        "production_behavior_created": False,
        "proof_of_learning_claim": False,
        "consciousness_claim": False,
    }
    _validate_expected(tick1, expected, errors, "tick1")
    if not _non_empty_string(tick1.get("tick1_context_id")):
        errors.append("tick1_context_id_empty")
    if not _non_empty_string(tick1.get("next_tick_id")):
        errors.append("tick1_next_tick_id_empty")


def _validate_appended_session_frame(
    appended: dict[str, Any],
    source: dict[str, Any],
    tick1: dict[str, Any],
    errors: list[str],
) -> None:
    _validate_required(appended, REQUIRED_APPENDED_FRAME_FIELDS, errors, "appended")
    _validate_no_extra(appended, REQUIRED_APPENDED_FRAME_FIELDS, errors, "appended")
    expected = {
        "frame_version": "v0",
        "phase": "Phase1",
        "boundary_index": BOUNDARY_INDEX_AFTER,
        "frame_scope": "same_session_sandbox_record_only",
        "frame_authority": "record_only_appended_runtime_tick_handoff_frame",
        "session_id": source.get("session_id"),
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "previous_frame_id": source.get("source_session_frame_id"),
        "source_tick1_context_id": tick1.get("tick1_context_id"),
        "previous_tick_index": source.get("source_current_tick_index"),
        "appended_tick_index": tick1.get("next_tick_index"),
        "appended_tick_id": tick1.get("next_tick_id"),
        "appended_tick_label": tick1.get("next_tick_label"),
        "previous_frame_tick_count": EXPECTED_SOURCE_TICK_COUNT,
        "frame_tick_count": EXPECTED_APPENDED_TICK_COUNT,
        "frame_appended": True,
        "appended_from_tick1_context": True,
        "inherits_trace_snapshot_id": source.get("source_trace_snapshot_id"),
        "inherits_working_memory_slot_set_id": source.get("source_working_memory_slot_set_id"),
        "inherits_evidence_source_set_id": source.get("source_evidence_source_set_id"),
        "working_memory_reference_only": True,
        "evidence_reference_only": True,
        "new_working_memory_update_created": False,
        "persistent_memory_write": False,
        "new_evidence_record_created": False,
        "live_runtime_session_started": False,
        "runtime_tick_scheduler_created": False,
        "live_runtime_tick_created": False,
        "runtime_action_loop_created": False,
        "production_behavior_created": False,
    }
    _validate_expected(appended, expected, errors, "appended")
    if not _non_empty_string(appended.get("appended_session_frame_id")):
        errors.append("appended_session_frame_id_empty")


def _validate_continuity_comparison(
    continuity: dict[str, Any],
    source: dict[str, Any],
    tick0: dict[str, Any],
    tick1: dict[str, Any],
    appended: dict[str, Any],
    errors: list[str],
) -> None:
    _validate_required(continuity, REQUIRED_CONTINUITY_FIELDS, errors, "continuity")
    _validate_no_extra(continuity, REQUIRED_CONTINUITY_FIELDS, errors, "continuity")
    expected = {
        "comparison_scope": "same_session_sandbox_tick0_tick1_record_only",
        "tick0_context_id": tick0.get("tick0_context_id"),
        "tick1_context_id": tick1.get("tick1_context_id"),
        "previous_frame_id": source.get("source_session_frame_id"),
        "appended_frame_id": appended.get("appended_session_frame_id"),
        "continuity_compared": True,
        "session_id_preserved": True,
        "scenario_id_preserved": True,
        "approved_purpose_preserved": True,
        "selected_action_carried_as_context_only": True,
        "observed_outcome_carried_as_context_only": True,
        "tick_index_advances_by_one": True,
        "frame_count_advances_by_one": True,
        "working_memory_refs_preserved": True,
        "evidence_refs_preserved": True,
        "source_frame_not_mutated": True,
        "external_tools_absent": True,
        "persistent_memory_absent": True,
        "predictor_mutation_absent": True,
        "production_behavior_absent": True,
        "proof_claim_absent": True,
        "consciousness_claim_absent": True,
        "continuity_passed": True,
    }
    _validate_expected(continuity, expected, errors, "continuity")
    if not _non_empty_string(continuity.get("continuity_comparison_id")):
        errors.append("continuity_comparison_id_empty")


def _validate_containment(containment: dict[str, Any], errors: list[str]) -> None:
    expected = {**{field: True for field in TRUE_CONTAINMENT_FIELDS}, **{field: False for field in FALSE_CONTAINMENT_FIELDS}}
    _validate_expected(containment, expected, errors, "containment")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    expected = {"triggered": True, "boundary_number": 181, **{field: False for field in FALSE_AUDIT_FIELDS}}
    _validate_expected(audit, expected, errors, "audit")
    if not _non_empty_string(audit.get("boundary_audit_id")):
        errors.append("boundary_audit_id_empty")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_built", "what_changed", "what_is_blocked", "plain_result"):
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked(blocked: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(flag for flag in BLOCKED_FLAGS if flag not in blocked)
    errors.extend(f"blocked_flag_missing:{flag}" for flag in missing)
    extra = sorted(flag for flag in blocked if flag not in BLOCKED_FLAGS)
    errors.extend(f"blocked_flag_unexpected:{flag}" for flag in extra)
    for flag in BLOCKED_FLAGS:
        if blocked.get(flag) is not False:
            errors.append(f"blocked_flag_{flag}_not_false")


def _invalid_records(reach: dict[str, Any], wait: dict[str, Any], probe: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(base: dict[str, Any], label: str, path: tuple[Any, ...], value: Any) -> None:
        record = deepcopy(base)
        _set_path(record, path, value)
        record["runtime_tick_handoff_record_id"] = f"invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "bad")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), "2026-06-09-b180")
    mutate(reach, "source_not_validated", ("source_session_frame", "source_validated"), False)
    mutate(reach, "source_wrong_boundary", ("source_session_frame", "source_boundary_index"), "2026-06-09-b179")
    mutate(reach, "source_frame_not_materialized", ("source_session_frame", "source_session_frame_materialized"), False)
    mutate(reach, "source_wrong_scope", ("source_session_frame", "source_frame_scope"), "production")
    mutate(wait, "tick0_not_read", ("tick0_context", "read_b180_frame_as_next_tick_input"), False)
    mutate(wait, "tick0_mutates_source", ("tick0_context", "mutates_source_frame"), True)
    mutate(wait, "tick1_not_created", ("tick1_context", "next_tick_context_created"), False)
    mutate(wait, "tick1_wrong_session", ("tick1_context", "session_id"), "other_session")
    mutate(wait, "tick1_bad_index", ("tick1_context", "next_tick_index"), 12)
    mutate(wait, "tick1_external_tool", ("tick1_context", "external_tool_called"), True)
    mutate(wait, "tick1_selected_action", ("tick1_context", "selected_action_created"), True)
    mutate(probe, "appended_not_created", ("appended_session_frame", "frame_appended"), False)
    mutate(probe, "appended_wrong_scope", ("appended_session_frame", "frame_scope"), "runtime")
    mutate(probe, "appended_tick_bad", ("appended_session_frame", "appended_tick_index"), 12)
    mutate(probe, "appended_memory_write", ("appended_session_frame", "persistent_memory_write"), True)
    mutate(probe, "continuity_not_compared", ("continuity_comparison", "continuity_compared"), False)
    mutate(probe, "continuity_session_not_preserved", ("continuity_comparison", "session_id_preserved"), False)
    mutate(probe, "continuity_tick_not_advanced", ("continuity_comparison", "tick_index_advances_by_one"), False)
    mutate(probe, "continuity_action_not_context", ("continuity_comparison", "selected_action_carried_as_context_only"), False)
    mutate(reach, "containment_not_same_session", ("authority_containment", "same_session_only"), False)
    mutate(reach, "containment_scheduler", ("authority_containment", "runtime_tick_scheduler_created_in_this_package"), True)
    mutate(reach, "containment_runtime_loop", ("authority_containment", "runtime_action_loop_created_in_this_package"), True)
    mutate(reach, "containment_external_tool", ("authority_containment", "external_tool_called_in_this_package"), True)
    mutate(reach, "containment_memory", ("authority_containment", "persistent_memory_write_created_in_this_package"), True)
    mutate(reach, "containment_predictor", ("authority_containment", "predictor_modified_in_this_package"), True)
    mutate(reach, "containment_production", ("authority_containment", "production_behavior_created_in_this_package"), True)
    mutate(reach, "containment_consciousness", ("authority_containment", "consciousness_claim"), True)
    mutate(wait, "blocked_persistent_memory", ("blocked_flags", "persistent_memory_write"), True)
    mutate(wait, "blocked_external_tool", ("blocked_flags", "external_tool_called"), True)
    mutate(wait, "blocked_predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(wait, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "runtime_tick_handoff_result_count": len(validation_results),
        "valid_runtime_tick_handoff_count": len(valid),
        "invalid_runtime_tick_handoff_count": len(validation_results) - len(valid),
        "tick0_context_created_count": sum(1 for result in valid if result["tick0_context_created"]),
        "tick1_context_created_count": sum(1 for result in valid if result["tick1_context_created"]),
        "appended_frame_created_count": sum(1 for result in valid if result["appended_frame_created"]),
        "continuity_compared_count": sum(1 for result in valid if result["continuity_compared"]),
        "continuity_passed_count": sum(1 for result in valid if result["continuity_passed"]),
        "tick_index_advanced_count": sum(1 for result in valid if result["tick_index_advanced"]),
        "frame_count_advanced_count": sum(1 for result in valid if result["frame_count_advanced"]),
        "runtime_handoff_record_only_count": sum(1 for result in valid if result["runtime_handoff_record_only"]),
        "reach_tick_handoff_count": sum(1 for result in valid if result["selected_action"] == "reach_front_item"),
        "wait_tick_handoff_count": sum(1 for result in valid if result["selected_action"] == "wait_or_observe"),
        "probe_tick_handoff_count": sum(
            1 for result in valid if result["selected_action"] == "observe_or_alternative_probe"
        ),
        "live_runtime_blocked_count": sum(1 for result in valid if result["live_runtime_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "external_tools_blocked_count": sum(1 for result in valid if result["external_tools_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid if result["production_behavior_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "consciousness_claim_blocked_count": sum(1 for result in valid if result["consciousness_claim_blocked"]),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["runtime_tick_handoff_result_count"] == 36
        and summary["valid_runtime_tick_handoff_count"] == 3
        and summary["invalid_runtime_tick_handoff_count"] == 33
        and summary["tick0_context_created_count"] == 3
        and summary["tick1_context_created_count"] == 3
        and summary["appended_frame_created_count"] == 3
        and summary["continuity_compared_count"] == 3
        and summary["continuity_passed_count"] == 3
        and summary["tick_index_advanced_count"] == 3
        and summary["frame_count_advanced_count"] == 3
        and summary["runtime_handoff_record_only_count"] == 3
        and summary["reach_tick_handoff_count"] == 1
        and summary["wait_tick_handoff_count"] == 1
        and summary["probe_tick_handoff_count"] == 1
        and summary["live_runtime_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["external_tools_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["consciousness_claim_blocked_count"] == 3
        and summary["boundary_audit_passed_count"] == 3
    )


def _runtime_handoff_record_only(
    tick0: dict[str, Any],
    tick1: dict[str, Any],
    appended: dict[str, Any],
    containment: dict[str, Any],
) -> bool:
    return (
        tick0.get("context_authority") == "read_only_b180_frame_input"
        and tick1.get("context_authority") == "record_only_runtime_tick_handoff_context"
        and appended.get("frame_authority") == "record_only_appended_runtime_tick_handoff_frame"
        and containment.get("record_only_tick_handoff") is True
        and tick1.get("next_tick_context_created") is True
        and appended.get("frame_appended") is True
        and tick1.get("selected_action_created") is False
        and appended.get("live_runtime_tick_created") is False
        and appended.get("persistent_memory_write") is False
    )


def _live_runtime_blocked(
    tick1: dict[str, Any],
    appended: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            appended.get("live_runtime_session_started"),
            appended.get("runtime_tick_scheduler_created"),
            appended.get("live_runtime_tick_created"),
            appended.get("runtime_action_loop_created"),
            containment.get("live_runtime_session_started_in_this_package"),
            containment.get("runtime_tick_scheduler_created_in_this_package"),
            containment.get("live_runtime_tick_created_in_this_package"),
            containment.get("runtime_action_loop_created_in_this_package"),
            audit.get("live_runtime_session_started"),
            audit.get("runtime_tick_scheduler_created"),
            audit.get("live_runtime_tick_created"),
            audit.get("runtime_action_loop_created"),
            blocked.get("live_runtime_session_started"),
            blocked.get("runtime_tick_scheduler_created"),
            blocked.get("live_runtime_tick_created"),
            blocked.get("runtime_action_loop_created"),
            tick1.get("production_behavior_created"),
        )
    )


def _action_creation_blocked(
    tick1: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            tick1.get("selected_action_created"),
            tick1.get("final_action_created"),
            tick1.get("direct_command_created"),
            tick1.get("execution_created"),
            tick1.get("outcome_observation_created"),
            containment.get("selected_action_created_in_this_package"),
            containment.get("final_action_created_in_this_package"),
            containment.get("direct_command_created_in_this_package"),
            containment.get("execution_created_in_this_package"),
            containment.get("outcome_observation_created_in_this_package"),
            audit.get("selected_action_created"),
            audit.get("final_action_created"),
            audit.get("direct_command_created"),
            audit.get("execution_created"),
            audit.get("outcome_observation_created"),
            blocked.get("selected_action_created"),
            blocked.get("final_action_created"),
            blocked.get("direct_command_created"),
            blocked.get("execution_created"),
            blocked.get("outcome_observation_created"),
        )
    )


def _memory_write_blocked(
    tick1: dict[str, Any],
    appended: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            tick1.get("working_memory_update_created"),
            tick1.get("persistent_memory_write"),
            appended.get("new_working_memory_update_created"),
            appended.get("persistent_memory_write"),
            containment.get("working_memory_update_created_in_this_package"),
            containment.get("persistent_memory_write_created_in_this_package"),
            containment.get("memory_admission_created_in_this_package"),
            containment.get("retention_write_created_in_this_package"),
            audit.get("working_memory_update_created"),
            audit.get("persistent_memory_write_created"),
            audit.get("memory_admission_created"),
            audit.get("retention_write_created"),
            blocked.get("working_memory_update_created"),
            blocked.get("persistent_working_memory_written"),
            blocked.get("persistent_memory_write"),
            blocked.get("memory_write"),
            blocked.get("long_term_memory_write"),
            blocked.get("core_memory_write"),
            blocked.get("archive_memory_write"),
            blocked.get("memory_admission_created"),
            blocked.get("retention_write"),
            blocked.get("new_retention_written"),
        )
    )


def _external_tools_blocked(
    tick0: dict[str, Any],
    tick1: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            tick0.get("external_tool_called"),
            tick1.get("external_tool_called"),
            containment.get("external_tool_called_in_this_package"),
            containment.get("external_tool_result_used_in_this_package"),
            audit.get("external_tool_called"),
            audit.get("external_tool_result_used"),
            blocked.get("external_tool_called"),
            blocked.get("external_tool_result_used"),
        )
    )


def _predictor_use_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return all(
        value is False
        for value in (
            containment.get("predictor_read_enabled_in_this_package"),
            containment.get("predictor_influence_enabled_in_this_package"),
            containment.get("predictor_modified_in_this_package"),
            audit.get("predictor_read_enabled"),
            audit.get("predictor_influence_enabled"),
            audit.get("predictor_modified"),
            blocked.get("predictor_read_enabled"),
            blocked.get("predictor_influence_enabled"),
            blocked.get("predictor_modified"),
        )
    )


def _direct_feed_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return all(
        value is False
        for value in (
            containment.get("direct_endocrine_feed_in_this_package"),
            containment.get("direct_tendency_feed_in_this_package"),
            audit.get("direct_endocrine_feed"),
            audit.get("direct_tendency_feed"),
            blocked.get("direct_endocrine_feed"),
            blocked.get("direct_tendency_feed"),
        )
    )


def _production_behavior_blocked(
    tick0: dict[str, Any],
    tick1: dict[str, Any],
    appended: dict[str, Any],
    continuity: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            tick0.get("production_behavior_created"),
            tick1.get("production_behavior_created"),
            appended.get("production_behavior_created"),
            not continuity.get("production_behavior_absent"),
            containment.get("production_behavior_created_in_this_package"),
            audit.get("production_behavior_created"),
            audit.get("runtime_behavior_leak"),
            blocked.get("production_action_selection"),
            blocked.get("runtime_action_selection"),
            blocked.get("runtime_behavior_changed"),
            blocked.get("production_behavior_changed"),
        )
    )


def _proof_claim_blocked(
    tick0: dict[str, Any],
    tick1: dict[str, Any],
    continuity: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            tick0.get("proof_of_learning_claim"),
            tick1.get("proof_of_learning_claim"),
            not continuity.get("proof_claim_absent"),
            containment.get("proof_of_learning_claim"),
            containment.get("long_term_learning_claim"),
            audit.get("proof_of_learning_claim"),
            blocked.get("proof_of_learning_claim"),
            blocked.get("long_term_learning_claim"),
        )
    )


def _consciousness_claim_blocked(
    tick0: dict[str, Any],
    tick1: dict[str, Any],
    continuity: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            tick0.get("consciousness_claim"),
            tick1.get("consciousness_claim"),
            not continuity.get("consciousness_claim_absent"),
            containment.get("consciousness_claim"),
            audit.get("consciousness_claim"),
            blocked.get("consciousness_claim"),
        )
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 181
        and all(audit.get(field) is False for field in FALSE_AUDIT_FIELDS)
    )


def _validate_required(mapping: dict[str, Any], required: set[str], errors: list[str], prefix: str) -> None:
    missing = sorted(field for field in required if field not in mapping)
    label = f"{prefix}_" if prefix else ""
    errors.extend(f"missing_required_field:{label}{field}" for field in missing)


def _validate_no_extra(mapping: dict[str, Any], required: set[str], errors: list[str], prefix: str) -> None:
    label = f"{prefix}_" if prefix else ""
    extra = sorted(field for field in mapping if field not in required)
    errors.extend(f"unexpected_field:{label}{field}" for field in extra)


def _validate_expected(mapping: dict[str, Any], expected: dict[str, Any], errors: list[str], prefix: str) -> None:
    for field, expected_value in expected.items():
        if mapping.get(field) != expected_value:
            errors.append(f"{prefix}_{field}_not_expected")


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{field}_not_dict")
    return {}


def _set_path(record: dict[str, Any], path: tuple[Any, ...], value: Any) -> None:
    target: Any = record
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


if __name__ == "__main__":
    import json

    print(json.dumps(run_phase1_session_frame_runtime_tick_handoff_minimal_check(), indent=2))
