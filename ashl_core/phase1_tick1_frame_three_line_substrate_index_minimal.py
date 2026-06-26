"""Index the b181 tick1 frame into read-only thought/action/memory lines."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .phase1_session_frame_runtime_tick_handoff_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    EXPECTED_APPENDED_TICK_COUNT,
    build_phase1_session_frame_runtime_tick_handoff_record,
    run_phase1_session_frame_runtime_tick_handoff_minimal_check,
    validate_phase1_session_frame_runtime_tick_handoff_record,
)


COMMAND = "run-phase1-tick1-frame-three-line-substrate-index-minimal-check"
FLOW = "phase1_tick1_frame_three_line_substrate_index_minimal_v0"
PACKAGE_ID = "PKG-Phase1-Tick1FrameThreeLineSubstrateIndex-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b181"
BOUNDARY_INDEX_AFTER = "2026-06-09-b182"
RECORD_TYPE = "phase1_tick1_frame_three_line_substrate_index_minimal"
EXPECTED_LINE_COUNT = 3

BLOCKED_FLAGS = {
    "live_runtime_session_started",
    "runtime_tick_scheduler_created",
    "live_runtime_tick_created",
    "runtime_action_loop_created",
    "candidate_input_created",
    "candidate_ordering_created",
    "candidate_reordering_created",
    "candidate_scores_changed",
    "next_cycle_candidate_ordering_changed",
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
    "proof_of_learning_claim",
    "long_term_learning_claim",
    "consciousness_claim",
    "llm_runtime_used",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "tick1_three_line_substrate_index_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_runtime_tick_handoff",
    "tick1_frame_reference",
    "thought_line_index",
    "action_line_index",
    "memory_line_index",
    "cross_line_continuity_index",
    "authority_containment",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}

REQUIRED_SOURCE_FIELDS = {
    "source_runtime_tick_handoff_record_id",
    "source_validated",
    "source_boundary_index",
    "session_id",
    "scenario_id",
    "approved_purpose",
    "selected_action_context",
    "observed_outcome_context",
    "source_tick1_context_id",
    "source_appended_session_frame_id",
    "source_continuity_comparison_id",
    "source_tick1_context_created",
    "source_appended_frame_created",
    "source_continuity_passed",
    "source_previous_tick_index",
    "source_next_tick_index",
    "source_frame_tick_count",
    "source_handoff_reason",
    "source_working_memory_slot_set_id",
    "source_evidence_source_set_id",
    "source_working_memory_refs_preserved",
    "source_evidence_refs_preserved",
    "source_record_only",
    "source_live_runtime_blocked",
    "source_action_creation_blocked",
    "source_memory_write_blocked",
    "source_external_tools_blocked",
    "source_predictor_use_blocked",
    "source_production_behavior_blocked",
    "source_proof_claim_blocked",
    "source_consciousness_claim_blocked",
    "source_boundary_audit_passed",
}

REQUIRED_FRAME_REFERENCE_FIELDS = {
    "tick1_frame_reference_id",
    "reference_scope",
    "reference_authority",
    "session_id",
    "scenario_id",
    "approved_purpose",
    "tick1_context_id",
    "appended_frame_id",
    "appended_tick_index",
    "frame_tick_count",
    "continuity_comparison_id",
    "tick1_frame_reference_created",
    "source_frame_not_mutated",
    "record_reference_only",
    "live_runtime_tick_created",
    "action_selection_created",
    "memory_write_created",
    "external_tool_called",
    "production_behavior_created",
}

REQUIRED_THOUGHT_FIELDS = {
    "thought_line_index_id",
    "line_name",
    "line_scope",
    "line_authority",
    "indexed_fields",
    "approved_purpose_context",
    "handoff_reason_context",
    "observed_outcome_context",
    "continuity_context_id",
    "thought_line_index_created",
    "candidate_input_created",
    "thought_runtime_started",
    "llm_runtime_used",
    "proof_of_learning_claim",
    "consciousness_claim",
}

REQUIRED_ACTION_FIELDS = {
    "action_line_index_id",
    "line_name",
    "line_scope",
    "line_authority",
    "indexed_fields",
    "selected_action_context",
    "selected_action_context_only",
    "previous_tick_index",
    "appended_tick_index",
    "appended_frame_id",
    "action_line_index_created",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "execution_created",
    "outcome_observation_created",
}

REQUIRED_MEMORY_FIELDS = {
    "memory_line_index_id",
    "line_name",
    "line_scope",
    "line_authority",
    "indexed_fields",
    "working_memory_slot_set_id",
    "evidence_source_set_id",
    "working_memory_refs_preserved",
    "evidence_refs_preserved",
    "working_memory_reference_only",
    "evidence_reference_only",
    "memory_line_index_created",
    "working_memory_update_created",
    "persistent_memory_write",
    "retention_write",
    "memory_admission_created",
}

REQUIRED_CROSS_LINE_FIELDS = {
    "cross_line_continuity_index_id",
    "index_scope",
    "tick1_context_id",
    "appended_frame_id",
    "thought_line_index_id",
    "action_line_index_id",
    "memory_line_index_id",
    "lane_count",
    "thought_line_record_only",
    "action_line_record_only",
    "memory_line_record_only",
    "all_lanes_record_only",
    "continuity_passed",
    "session_id_preserved",
    "scenario_id_preserved",
    "approved_purpose_preserved",
    "tick1_frame_indexed",
    "candidate_input_created",
    "action_authority_created",
    "memory_authority_created",
    "production_behavior_created",
}

TRUE_CONTAINMENT_FIELDS = (
    "same_session_only",
    "sandbox_only",
    "record_only_three_line_index",
    "reads_b181_tick1_frame_only",
    "tick1_frame_reference_created_in_this_package",
    "thought_line_index_created_in_this_package",
    "action_line_index_created_in_this_package",
    "memory_line_index_created_in_this_package",
    "cross_line_continuity_index_created_in_this_package",
    "future_candidate_input_requires_separate_package",
    "future_action_selection_requires_separate_package",
    "future_memory_write_requires_separate_package",
    "future_external_tool_use_requires_separate_package",
    "future_predictor_use_requires_separate_package",
    "future_production_promotion_requires_separate_package",
)

FALSE_CONTAINMENT_FIELDS = (
    "live_runtime_session_started_in_this_package",
    "runtime_tick_scheduler_created_in_this_package",
    "live_runtime_tick_created_in_this_package",
    "runtime_action_loop_created_in_this_package",
    "candidate_input_created_in_this_package",
    "candidate_ordering_created_in_this_package",
    "candidate_reordering_created_in_this_package",
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
    "llm_runtime_used",
)

FALSE_AUDIT_FIELDS = (
    "production_behavior_created",
    "runtime_behavior_leak",
    "live_runtime_session_started",
    "runtime_tick_scheduler_created",
    "live_runtime_tick_created",
    "runtime_action_loop_created",
    "candidate_input_created",
    "candidate_ordering_created",
    "candidate_reordering_created",
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
    "proof_of_learning_claim",
    "long_term_learning_claim",
    "consciousness_claim",
    "llm_runtime_used",
)


def build_phase1_tick1_frame_three_line_substrate_index_record(
    runtime_tick_handoff_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(runtime_tick_handoff_record)
        if runtime_tick_handoff_record is not None
        else build_phase1_session_frame_runtime_tick_handoff_record()
    )
    source_validation = validate_phase1_session_frame_runtime_tick_handoff_record(source)
    if not source_validation["valid"]:
        raise ValueError("runtime_tick_handoff_record must validate before tick1 three-line indexing")

    source_summary = _source_summary(source, source_validation)
    frame_reference = _build_tick1_frame_reference(source_summary)
    thought_line = _build_thought_line_index(source_summary)
    action_line = _build_action_line_index(source_summary)
    memory_line = _build_memory_line_index(source_summary)
    cross_line = _build_cross_line_continuity_index(source_summary, frame_reference, thought_line, action_line, memory_line)

    return {
        "tick1_three_line_substrate_index_record_id": f"phase1_tick1_three_line_index_{source_summary['scenario_id']}_demo_001",
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_runtime_tick_handoff": source_summary,
        "tick1_frame_reference": frame_reference,
        "thought_line_index": thought_line,
        "action_line_index": action_line,
        "memory_line_index": memory_line,
        "cross_line_continuity_index": cross_line,
        "authority_containment": _build_authority_containment(),
        "boundary_audit": _build_boundary_audit(),
        "human_summary": {
            "what_was_built": "A read-only three-line index for the b181 tick1 frame.",
            "what_changed": (
                f"The {source_summary['scenario_id']} tick1 frame now has named thought, action, "
                "and memory lanes for the next sandbox package to read."
            ),
            "what_is_blocked": (
                "No candidate input, action selection, execution, memory write, external tool call, "
                "production behavior, or proof/consciousness claim is created."
            ),
            "plain_result": "The next step can see what tick1 knows in three lanes, but cannot act from it yet.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_phase1_tick1_frame_three_line_substrate_index_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    _validate_required(record, REQUIRED_TOP_LEVEL_FIELDS, errors, "")
    _validate_no_extra(record, REQUIRED_TOP_LEVEL_FIELDS, errors, "")
    _validate_expected(
        record,
        {
            "record_type": RECORD_TYPE,
            "record_version": "v0",
            "package_id": PACKAGE_ID,
            "boundary_index_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
        },
        errors,
        "top",
    )
    if not _non_empty_string(record.get("tick1_three_line_substrate_index_record_id")):
        errors.append("tick1_three_line_substrate_index_record_id_empty")

    source = _as_dict(record.get("source_runtime_tick_handoff"), errors, "source_runtime_tick_handoff")
    frame_reference = _as_dict(record.get("tick1_frame_reference"), errors, "tick1_frame_reference")
    thought = _as_dict(record.get("thought_line_index"), errors, "thought_line_index")
    action = _as_dict(record.get("action_line_index"), errors, "action_line_index")
    memory = _as_dict(record.get("memory_line_index"), errors, "memory_line_index")
    cross = _as_dict(record.get("cross_line_continuity_index"), errors, "cross_line_continuity_index")
    containment = _as_dict(record.get("authority_containment"), errors, "authority_containment")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_frame_reference(frame_reference, source, errors)
    _validate_thought_line(thought, source, errors)
    _validate_action_line(action, source, frame_reference, errors)
    _validate_memory_line(memory, source, errors)
    _validate_cross_line(cross, source, frame_reference, thought, action, memory, errors)
    _validate_containment(containment, errors)
    _validate_audit(audit, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "selected_action_context": source.get("selected_action_context"),
        "observed_outcome_context": source.get("observed_outcome_context"),
        "tick1_frame_reference_created": frame_reference.get("tick1_frame_reference_created") is True,
        "thought_line_index_created": thought.get("thought_line_index_created") is True,
        "action_line_index_created": action.get("action_line_index_created") is True,
        "memory_line_index_created": memory.get("memory_line_index_created") is True,
        "cross_line_continuity_index_created": cross.get("tick1_frame_indexed") is True,
        "lane_count_valid": cross.get("lane_count") == EXPECTED_LINE_COUNT,
        "all_lanes_record_only": cross.get("all_lanes_record_only") is True,
        "three_line_index_record_only": _three_line_index_record_only(frame_reference, thought, action, memory, cross, containment),
        "live_runtime_blocked": _live_runtime_blocked(frame_reference, containment, audit, blocked),
        "candidate_input_blocked": _candidate_input_blocked(thought, cross, containment, audit, blocked),
        "action_creation_blocked": _action_creation_blocked(action, containment, audit, blocked),
        "memory_write_blocked": _memory_write_blocked(frame_reference, memory, containment, audit, blocked),
        "external_tools_blocked": _external_tools_blocked(frame_reference, containment, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(containment, audit, blocked),
        "direct_feed_blocked": _direct_feed_blocked(containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(frame_reference, cross, containment, audit, blocked),
        "proof_claim_blocked": _proof_claim_blocked(thought, containment, audit, blocked),
        "consciousness_claim_blocked": _consciousness_claim_blocked(thought, containment, audit, blocked),
        "llm_runtime_blocked": _llm_runtime_blocked(thought, containment, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_phase1_tick1_frame_three_line_substrate_index_minimal_check() -> dict[str, Any]:
    source_records = run_phase1_session_frame_runtime_tick_handoff_minimal_check()["valid_records"]
    valid_records = [build_phase1_tick1_frame_three_line_substrate_index_record(source) for source in source_records]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [validate_phase1_tick1_frame_three_line_substrate_index_record(record) for record in records]
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
            "boundary_reason": "Indexes the b181 tick1 frame into read-only thought/action/memory lanes.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A read-only three-line index over existing b181 tick1 frame records.",
            "what_changed": "Each tick1 frame now has named thought, action, and memory lanes for a future sandbox package to read.",
            "what_is_blocked": "No candidate input, action selection, execution, memory write, external tool call, production behavior, or proof/consciousness claim is created.",
            "plain_result": "Qingyin can now see tick1 as three lanes of context, but cannot yet use those lanes to act.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    tick1 = source["tick1_context"]
    appended = source["appended_session_frame"]
    continuity = source["continuity_comparison"]
    source_frame = source["source_session_frame"]

    return {
        "source_runtime_tick_handoff_record_id": source["runtime_tick_handoff_record_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "session_id": tick1["session_id"],
        "scenario_id": tick1["scenario_id"],
        "approved_purpose": tick1["approved_purpose"],
        "selected_action_context": tick1["selected_action_context"],
        "observed_outcome_context": tick1["observed_outcome_context"],
        "source_tick1_context_id": tick1["tick1_context_id"],
        "source_appended_session_frame_id": appended["appended_session_frame_id"],
        "source_continuity_comparison_id": continuity["continuity_comparison_id"],
        "source_tick1_context_created": tick1["next_tick_context_created"],
        "source_appended_frame_created": appended["frame_appended"],
        "source_continuity_passed": continuity["continuity_passed"],
        "source_previous_tick_index": tick1["previous_tick_index"],
        "source_next_tick_index": tick1["next_tick_index"],
        "source_frame_tick_count": appended["frame_tick_count"],
        "source_handoff_reason": tick1["handoff_reason"],
        "source_working_memory_slot_set_id": source_frame["source_working_memory_slot_set_id"],
        "source_evidence_source_set_id": source_frame["source_evidence_source_set_id"],
        "source_working_memory_refs_preserved": continuity["working_memory_refs_preserved"],
        "source_evidence_refs_preserved": continuity["evidence_refs_preserved"],
        "source_record_only": validation["runtime_handoff_record_only"],
        "source_live_runtime_blocked": validation["live_runtime_blocked"],
        "source_action_creation_blocked": validation["action_creation_blocked"],
        "source_memory_write_blocked": validation["memory_write_blocked"],
        "source_external_tools_blocked": validation["external_tools_blocked"],
        "source_predictor_use_blocked": validation["predictor_use_blocked"],
        "source_production_behavior_blocked": validation["production_behavior_blocked"],
        "source_proof_claim_blocked": validation["proof_claim_blocked"],
        "source_consciousness_claim_blocked": validation["consciousness_claim_blocked"],
        "source_boundary_audit_passed": validation["boundary_audit_passed"],
    }


def _build_tick1_frame_reference(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "tick1_frame_reference_id": f"tick1_frame_reference_{source['scenario_id']}_001",
        "reference_scope": "same_session_sandbox_tick1_frame",
        "reference_authority": "read_only_tick1_frame_reference",
        "session_id": source["session_id"],
        "scenario_id": source["scenario_id"],
        "approved_purpose": source["approved_purpose"],
        "tick1_context_id": source["source_tick1_context_id"],
        "appended_frame_id": source["source_appended_session_frame_id"],
        "appended_tick_index": source["source_next_tick_index"],
        "frame_tick_count": source["source_frame_tick_count"],
        "continuity_comparison_id": source["source_continuity_comparison_id"],
        "tick1_frame_reference_created": True,
        "source_frame_not_mutated": True,
        "record_reference_only": True,
        "live_runtime_tick_created": False,
        "action_selection_created": False,
        "memory_write_created": False,
        "external_tool_called": False,
        "production_behavior_created": False,
    }


def _build_thought_line_index(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "thought_line_index_id": f"thought_line_index_{source['scenario_id']}_001",
        "line_name": "thought",
        "line_scope": "same_session_sandbox_tick1_context",
        "line_authority": "read_only_context_not_thought_runtime",
        "indexed_fields": [
            "approved_purpose",
            "handoff_reason",
            "observed_outcome_context",
            "continuity_passed",
        ],
        "approved_purpose_context": source["approved_purpose"],
        "handoff_reason_context": source["source_handoff_reason"],
        "observed_outcome_context": source["observed_outcome_context"],
        "continuity_context_id": source["source_continuity_comparison_id"],
        "thought_line_index_created": True,
        "candidate_input_created": False,
        "thought_runtime_started": False,
        "llm_runtime_used": False,
        "proof_of_learning_claim": False,
        "consciousness_claim": False,
    }


def _build_action_line_index(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "action_line_index_id": f"action_line_index_{source['scenario_id']}_001",
        "line_name": "action",
        "line_scope": "same_session_sandbox_tick1_action_context",
        "line_authority": "read_only_action_history_not_selection",
        "indexed_fields": [
            "selected_action_context",
            "previous_tick_index",
            "appended_tick_index",
            "appended_frame_id",
        ],
        "selected_action_context": source["selected_action_context"],
        "selected_action_context_only": True,
        "previous_tick_index": source["source_previous_tick_index"],
        "appended_tick_index": source["source_next_tick_index"],
        "appended_frame_id": source["source_appended_session_frame_id"],
        "action_line_index_created": True,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "execution_created": False,
        "outcome_observation_created": False,
    }


def _build_memory_line_index(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "memory_line_index_id": f"memory_line_index_{source['scenario_id']}_001",
        "line_name": "memory",
        "line_scope": "same_session_sandbox_working_memory_references",
        "line_authority": "reference_only_no_memory_write",
        "indexed_fields": [
            "working_memory_slot_set_id",
            "evidence_source_set_id",
            "working_memory_refs_preserved",
            "evidence_refs_preserved",
        ],
        "working_memory_slot_set_id": source["source_working_memory_slot_set_id"],
        "evidence_source_set_id": source["source_evidence_source_set_id"],
        "working_memory_refs_preserved": source["source_working_memory_refs_preserved"],
        "evidence_refs_preserved": source["source_evidence_refs_preserved"],
        "working_memory_reference_only": True,
        "evidence_reference_only": True,
        "memory_line_index_created": True,
        "working_memory_update_created": False,
        "persistent_memory_write": False,
        "retention_write": False,
        "memory_admission_created": False,
    }


def _build_cross_line_continuity_index(
    source: dict[str, Any],
    frame_reference: dict[str, Any],
    thought: dict[str, Any],
    action: dict[str, Any],
    memory: dict[str, Any],
) -> dict[str, Any]:
    return {
        "cross_line_continuity_index_id": f"cross_line_continuity_index_{source['scenario_id']}_001",
        "index_scope": "same_session_sandbox_three_line_index",
        "tick1_context_id": source["source_tick1_context_id"],
        "appended_frame_id": frame_reference["appended_frame_id"],
        "thought_line_index_id": thought["thought_line_index_id"],
        "action_line_index_id": action["action_line_index_id"],
        "memory_line_index_id": memory["memory_line_index_id"],
        "lane_count": EXPECTED_LINE_COUNT,
        "thought_line_record_only": True,
        "action_line_record_only": True,
        "memory_line_record_only": True,
        "all_lanes_record_only": True,
        "continuity_passed": source["source_continuity_passed"],
        "session_id_preserved": True,
        "scenario_id_preserved": True,
        "approved_purpose_preserved": True,
        "tick1_frame_indexed": True,
        "candidate_input_created": False,
        "action_authority_created": False,
        "memory_authority_created": False,
        "production_behavior_created": False,
    }


def _build_authority_containment() -> dict[str, bool]:
    containment = {field: True for field in TRUE_CONTAINMENT_FIELDS}
    containment.update({field: False for field in FALSE_CONTAINMENT_FIELDS})
    return containment


def _build_boundary_audit() -> dict[str, Any]:
    audit: dict[str, Any] = {
        "boundary_audit_id": "phase1_tick1_three_line_substrate_index_boundary_audit_b182",
        "triggered": True,
        "boundary_number": 182,
        "package_id": PACKAGE_ID,
    }
    audit.update({field: False for field in FALSE_AUDIT_FIELDS})
    return audit


def _invalid_records(reach: dict[str, Any], wait: dict[str, Any], probe: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(base: dict[str, Any], label: str, path: tuple[Any, ...], value: Any) -> None:
        record = deepcopy(base)
        _set_path(record, path, value)
        record["tick1_three_line_substrate_index_record_id"] = f"invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "bad")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), "2026-06-09-b181")
    mutate(reach, "source_not_validated", ("source_runtime_tick_handoff", "source_validated"), False)
    mutate(reach, "source_wrong_boundary", ("source_runtime_tick_handoff", "source_boundary_index"), "2026-06-09-b180")
    mutate(reach, "source_tick1_missing", ("source_runtime_tick_handoff", "source_tick1_context_created"), False)
    mutate(reach, "source_continuity_failed", ("source_runtime_tick_handoff", "source_continuity_passed"), False)
    mutate(wait, "frame_reference_not_created", ("tick1_frame_reference", "tick1_frame_reference_created"), False)
    mutate(wait, "frame_reference_wrong_scope", ("tick1_frame_reference", "reference_scope"), "production")
    mutate(wait, "frame_reference_live_tick", ("tick1_frame_reference", "live_runtime_tick_created"), True)
    mutate(wait, "thought_line_not_created", ("thought_line_index", "thought_line_index_created"), False)
    mutate(wait, "thought_line_candidate_input", ("thought_line_index", "candidate_input_created"), True)
    mutate(wait, "thought_line_llm", ("thought_line_index", "llm_runtime_used"), True)
    mutate(probe, "action_line_not_created", ("action_line_index", "action_line_index_created"), False)
    mutate(probe, "action_selected_action", ("action_line_index", "selected_action_created"), True)
    mutate(probe, "action_direct_command", ("action_line_index", "direct_command_created"), True)
    mutate(probe, "action_execution", ("action_line_index", "execution_created"), True)
    mutate(probe, "action_outcome", ("action_line_index", "outcome_observation_created"), True)
    mutate(reach, "memory_line_not_created", ("memory_line_index", "memory_line_index_created"), False)
    mutate(reach, "memory_update", ("memory_line_index", "working_memory_update_created"), True)
    mutate(reach, "persistent_memory", ("memory_line_index", "persistent_memory_write"), True)
    mutate(reach, "retention_write", ("memory_line_index", "retention_write"), True)
    mutate(wait, "cross_wrong_lane_count", ("cross_line_continuity_index", "lane_count"), 2)
    mutate(wait, "cross_not_record_only", ("cross_line_continuity_index", "all_lanes_record_only"), False)
    mutate(wait, "cross_candidate_input", ("cross_line_continuity_index", "candidate_input_created"), True)
    mutate(probe, "containment_live_runtime", ("authority_containment", "live_runtime_tick_created_in_this_package"), True)
    mutate(probe, "containment_candidate_input", ("authority_containment", "candidate_input_created_in_this_package"), True)
    mutate(probe, "containment_memory", ("authority_containment", "persistent_memory_write_created_in_this_package"), True)
    mutate(probe, "containment_predictor", ("authority_containment", "predictor_modified_in_this_package"), True)
    mutate(probe, "containment_direct_feed", ("authority_containment", "direct_endocrine_feed_in_this_package"), True)
    mutate(reach, "audit_production", ("boundary_audit", "production_behavior_created"), True)
    mutate(reach, "blocked_external_tool", ("blocked_flags", "external_tool_called"), True)
    mutate(reach, "blocked_proof", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(reach, "blocked_consciousness", ("blocked_flags", "consciousness_claim"), True)
    mutate(wait, "blocked_predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(wait, "blocked_tendency_feed", ("blocked_flags", "direct_tendency_feed"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "tick1_three_line_substrate_index_result_count": len(validation_results),
        "valid_tick1_three_line_substrate_index_count": len(valid),
        "invalid_tick1_three_line_substrate_index_count": len(validation_results) - len(valid),
        "tick1_frame_reference_created_count": sum(1 for result in valid if result["tick1_frame_reference_created"]),
        "thought_line_index_created_count": sum(1 for result in valid if result["thought_line_index_created"]),
        "action_line_index_created_count": sum(1 for result in valid if result["action_line_index_created"]),
        "memory_line_index_created_count": sum(1 for result in valid if result["memory_line_index_created"]),
        "cross_line_continuity_index_created_count": sum(
            1 for result in valid if result["cross_line_continuity_index_created"]
        ),
        "lane_count_valid_count": sum(1 for result in valid if result["lane_count_valid"]),
        "all_lanes_record_only_count": sum(1 for result in valid if result["all_lanes_record_only"]),
        "three_line_index_record_only_count": sum(1 for result in valid if result["three_line_index_record_only"]),
        "reach_three_line_index_count": sum(
            1 for result in valid if result["selected_action_context"] == "reach_front_item"
        ),
        "wait_three_line_index_count": sum(
            1 for result in valid if result["selected_action_context"] == "wait_or_observe"
        ),
        "probe_three_line_index_count": sum(
            1 for result in valid if result["selected_action_context"] == "observe_or_alternative_probe"
        ),
        "live_runtime_blocked_count": sum(1 for result in valid if result["live_runtime_blocked"]),
        "candidate_input_blocked_count": sum(1 for result in valid if result["candidate_input_blocked"]),
        "action_creation_blocked_count": sum(1 for result in valid if result["action_creation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "external_tools_blocked_count": sum(1 for result in valid if result["external_tools_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid if result["production_behavior_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "consciousness_claim_blocked_count": sum(1 for result in valid if result["consciousness_claim_blocked"]),
        "llm_runtime_blocked_count": sum(1 for result in valid if result["llm_runtime_blocked"]),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["tick1_three_line_substrate_index_result_count"] == 39
        and summary["valid_tick1_three_line_substrate_index_count"] == 3
        and summary["invalid_tick1_three_line_substrate_index_count"] == 36
        and summary["tick1_frame_reference_created_count"] == 3
        and summary["thought_line_index_created_count"] == 3
        and summary["action_line_index_created_count"] == 3
        and summary["memory_line_index_created_count"] == 3
        and summary["cross_line_continuity_index_created_count"] == 3
        and summary["lane_count_valid_count"] == 3
        and summary["all_lanes_record_only_count"] == 3
        and summary["three_line_index_record_only_count"] == 3
        and summary["reach_three_line_index_count"] == 1
        and summary["wait_three_line_index_count"] == 1
        and summary["probe_three_line_index_count"] == 1
        and summary["live_runtime_blocked_count"] == 3
        and summary["candidate_input_blocked_count"] == 3
        and summary["action_creation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["external_tools_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["consciousness_claim_blocked_count"] == 3
        and summary["llm_runtime_blocked_count"] == 3
        and summary["boundary_audit_passed_count"] == 3
    )


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(source, REQUIRED_SOURCE_FIELDS, errors, "source")
    _validate_no_extra(source, REQUIRED_SOURCE_FIELDS, errors, "source")
    expected = {
        "source_validated": True,
        "source_boundary_index": SOURCE_BOUNDARY_INDEX,
        "source_tick1_context_created": True,
        "source_appended_frame_created": True,
        "source_continuity_passed": True,
        "source_frame_tick_count": EXPECTED_APPENDED_TICK_COUNT,
        "source_working_memory_refs_preserved": True,
        "source_evidence_refs_preserved": True,
        "source_record_only": True,
        "source_live_runtime_blocked": True,
        "source_action_creation_blocked": True,
        "source_memory_write_blocked": True,
        "source_external_tools_blocked": True,
        "source_predictor_use_blocked": True,
        "source_production_behavior_blocked": True,
        "source_proof_claim_blocked": True,
        "source_consciousness_claim_blocked": True,
        "source_boundary_audit_passed": True,
    }
    _validate_expected(source, expected, errors, "source")
    for field in (
        "source_runtime_tick_handoff_record_id",
        "session_id",
        "scenario_id",
        "approved_purpose",
        "selected_action_context",
        "observed_outcome_context",
        "source_tick1_context_id",
        "source_appended_session_frame_id",
        "source_continuity_comparison_id",
        "source_handoff_reason",
        "source_working_memory_slot_set_id",
        "source_evidence_source_set_id",
    ):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")
    if source.get("source_next_tick_index") != source.get("source_previous_tick_index", -100) + 1:
        errors.append("source_tick_index_not_advanced_by_one")


def _validate_frame_reference(frame: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(frame, REQUIRED_FRAME_REFERENCE_FIELDS, errors, "tick1_frame_reference")
    _validate_no_extra(frame, REQUIRED_FRAME_REFERENCE_FIELDS, errors, "tick1_frame_reference")
    _validate_expected(
        frame,
        {
            "reference_scope": "same_session_sandbox_tick1_frame",
            "reference_authority": "read_only_tick1_frame_reference",
            "session_id": source.get("session_id"),
            "scenario_id": source.get("scenario_id"),
            "approved_purpose": source.get("approved_purpose"),
            "tick1_context_id": source.get("source_tick1_context_id"),
            "appended_frame_id": source.get("source_appended_session_frame_id"),
            "appended_tick_index": source.get("source_next_tick_index"),
            "frame_tick_count": EXPECTED_APPENDED_TICK_COUNT,
            "continuity_comparison_id": source.get("source_continuity_comparison_id"),
            "tick1_frame_reference_created": True,
            "source_frame_not_mutated": True,
            "record_reference_only": True,
            "live_runtime_tick_created": False,
            "action_selection_created": False,
            "memory_write_created": False,
            "external_tool_called": False,
            "production_behavior_created": False,
        },
        errors,
        "tick1_frame_reference",
    )


def _validate_thought_line(thought: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(thought, REQUIRED_THOUGHT_FIELDS, errors, "thought_line")
    _validate_no_extra(thought, REQUIRED_THOUGHT_FIELDS, errors, "thought_line")
    _validate_expected(
        thought,
        {
            "line_name": "thought",
            "line_scope": "same_session_sandbox_tick1_context",
            "line_authority": "read_only_context_not_thought_runtime",
            "approved_purpose_context": source.get("approved_purpose"),
            "handoff_reason_context": source.get("source_handoff_reason"),
            "observed_outcome_context": source.get("observed_outcome_context"),
            "continuity_context_id": source.get("source_continuity_comparison_id"),
            "thought_line_index_created": True,
            "candidate_input_created": False,
            "thought_runtime_started": False,
            "llm_runtime_used": False,
            "proof_of_learning_claim": False,
            "consciousness_claim": False,
        },
        errors,
        "thought_line",
    )
    _validate_indexed_fields(
        thought,
        ["approved_purpose", "handoff_reason", "observed_outcome_context", "continuity_passed"],
        errors,
        "thought_line",
    )


def _validate_action_line(
    action: dict[str, Any],
    source: dict[str, Any],
    frame: dict[str, Any],
    errors: list[str],
) -> None:
    _validate_required(action, REQUIRED_ACTION_FIELDS, errors, "action_line")
    _validate_no_extra(action, REQUIRED_ACTION_FIELDS, errors, "action_line")
    _validate_expected(
        action,
        {
            "line_name": "action",
            "line_scope": "same_session_sandbox_tick1_action_context",
            "line_authority": "read_only_action_history_not_selection",
            "selected_action_context": source.get("selected_action_context"),
            "selected_action_context_only": True,
            "previous_tick_index": source.get("source_previous_tick_index"),
            "appended_tick_index": source.get("source_next_tick_index"),
            "appended_frame_id": frame.get("appended_frame_id"),
            "action_line_index_created": True,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "execution_created": False,
            "outcome_observation_created": False,
        },
        errors,
        "action_line",
    )
    _validate_indexed_fields(
        action,
        ["selected_action_context", "previous_tick_index", "appended_tick_index", "appended_frame_id"],
        errors,
        "action_line",
    )


def _validate_memory_line(memory: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(memory, REQUIRED_MEMORY_FIELDS, errors, "memory_line")
    _validate_no_extra(memory, REQUIRED_MEMORY_FIELDS, errors, "memory_line")
    _validate_expected(
        memory,
        {
            "line_name": "memory",
            "line_scope": "same_session_sandbox_working_memory_references",
            "line_authority": "reference_only_no_memory_write",
            "working_memory_slot_set_id": source.get("source_working_memory_slot_set_id"),
            "evidence_source_set_id": source.get("source_evidence_source_set_id"),
            "working_memory_refs_preserved": True,
            "evidence_refs_preserved": True,
            "working_memory_reference_only": True,
            "evidence_reference_only": True,
            "memory_line_index_created": True,
            "working_memory_update_created": False,
            "persistent_memory_write": False,
            "retention_write": False,
            "memory_admission_created": False,
        },
        errors,
        "memory_line",
    )
    _validate_indexed_fields(
        memory,
        [
            "working_memory_slot_set_id",
            "evidence_source_set_id",
            "working_memory_refs_preserved",
            "evidence_refs_preserved",
        ],
        errors,
        "memory_line",
    )


def _validate_cross_line(
    cross: dict[str, Any],
    source: dict[str, Any],
    frame: dict[str, Any],
    thought: dict[str, Any],
    action: dict[str, Any],
    memory: dict[str, Any],
    errors: list[str],
) -> None:
    _validate_required(cross, REQUIRED_CROSS_LINE_FIELDS, errors, "cross_line")
    _validate_no_extra(cross, REQUIRED_CROSS_LINE_FIELDS, errors, "cross_line")
    _validate_expected(
        cross,
        {
            "index_scope": "same_session_sandbox_three_line_index",
            "tick1_context_id": source.get("source_tick1_context_id"),
            "appended_frame_id": frame.get("appended_frame_id"),
            "thought_line_index_id": thought.get("thought_line_index_id"),
            "action_line_index_id": action.get("action_line_index_id"),
            "memory_line_index_id": memory.get("memory_line_index_id"),
            "lane_count": EXPECTED_LINE_COUNT,
            "thought_line_record_only": True,
            "action_line_record_only": True,
            "memory_line_record_only": True,
            "all_lanes_record_only": True,
            "continuity_passed": True,
            "session_id_preserved": True,
            "scenario_id_preserved": True,
            "approved_purpose_preserved": True,
            "tick1_frame_indexed": True,
            "candidate_input_created": False,
            "action_authority_created": False,
            "memory_authority_created": False,
            "production_behavior_created": False,
        },
        errors,
        "cross_line",
    )


def _validate_containment(containment: dict[str, Any], errors: list[str]) -> None:
    required = set(TRUE_CONTAINMENT_FIELDS) | set(FALSE_CONTAINMENT_FIELDS)
    _validate_required(containment, required, errors, "authority_containment")
    _validate_no_extra(containment, required, errors, "authority_containment")
    for field in TRUE_CONTAINMENT_FIELDS:
        if containment.get(field) is not True:
            errors.append(f"authority_containment_{field}_not_true")
    for field in FALSE_CONTAINMENT_FIELDS:
        if containment.get(field) is not False:
            errors.append(f"authority_containment_{field}_not_false")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    required = {"boundary_audit_id", "triggered", "boundary_number", "package_id"} | set(FALSE_AUDIT_FIELDS)
    _validate_required(audit, required, errors, "boundary_audit")
    _validate_no_extra(audit, required, errors, "boundary_audit")
    _validate_expected(
        audit,
        {
            "triggered": True,
            "boundary_number": 182,
            "package_id": PACKAGE_ID,
        },
        errors,
        "boundary_audit",
    )
    if not _non_empty_string(audit.get("boundary_audit_id")):
        errors.append("boundary_audit_id_empty")
    for field in FALSE_AUDIT_FIELDS:
        if audit.get(field) is not False:
            errors.append(f"boundary_audit_{field}_not_false")


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


def _three_line_index_record_only(
    frame: dict[str, Any],
    thought: dict[str, Any],
    action: dict[str, Any],
    memory: dict[str, Any],
    cross: dict[str, Any],
    containment: dict[str, Any],
) -> bool:
    return (
        frame.get("reference_authority") == "read_only_tick1_frame_reference"
        and thought.get("line_authority") == "read_only_context_not_thought_runtime"
        and action.get("line_authority") == "read_only_action_history_not_selection"
        and memory.get("line_authority") == "reference_only_no_memory_write"
        and cross.get("all_lanes_record_only") is True
        and containment.get("record_only_three_line_index") is True
        and thought.get("candidate_input_created") is False
        and action.get("selected_action_created") is False
        and memory.get("persistent_memory_write") is False
    )


def _live_runtime_blocked(
    frame: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            frame.get("live_runtime_tick_created"),
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
        )
    )


def _candidate_input_blocked(
    thought: dict[str, Any],
    cross: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            thought.get("candidate_input_created"),
            cross.get("candidate_input_created"),
            containment.get("candidate_input_created_in_this_package"),
            containment.get("candidate_ordering_created_in_this_package"),
            containment.get("candidate_reordering_created_in_this_package"),
            audit.get("candidate_input_created"),
            audit.get("candidate_ordering_created"),
            audit.get("candidate_reordering_created"),
            blocked.get("candidate_input_created"),
            blocked.get("candidate_ordering_created"),
            blocked.get("candidate_reordering_created"),
            blocked.get("candidate_scores_changed"),
            blocked.get("next_cycle_candidate_ordering_changed"),
        )
    )


def _action_creation_blocked(
    action: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            action.get("selected_action_created"),
            action.get("final_action_created"),
            action.get("direct_command_created"),
            action.get("execution_created"),
            action.get("outcome_observation_created"),
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
    frame: dict[str, Any],
    memory: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            frame.get("memory_write_created"),
            memory.get("working_memory_update_created"),
            memory.get("persistent_memory_write"),
            memory.get("retention_write"),
            memory.get("memory_admission_created"),
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
    frame: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            frame.get("external_tool_called"),
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
    frame: dict[str, Any],
    cross: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            frame.get("production_behavior_created"),
            cross.get("production_behavior_created"),
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
    thought: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            thought.get("proof_of_learning_claim"),
            containment.get("proof_of_learning_claim"),
            containment.get("long_term_learning_claim"),
            audit.get("proof_of_learning_claim"),
            audit.get("long_term_learning_claim"),
            blocked.get("proof_of_learning_claim"),
            blocked.get("long_term_learning_claim"),
        )
    )


def _consciousness_claim_blocked(
    thought: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            thought.get("consciousness_claim"),
            containment.get("consciousness_claim"),
            audit.get("consciousness_claim"),
            blocked.get("consciousness_claim"),
        )
    )


def _llm_runtime_blocked(
    thought: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            thought.get("llm_runtime_used"),
            containment.get("llm_runtime_used"),
            audit.get("llm_runtime_used"),
            blocked.get("llm_runtime_used"),
        )
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 182
        and all(audit.get(field) is False for field in FALSE_AUDIT_FIELDS)
    )


def _validate_indexed_fields(
    mapping: dict[str, Any],
    expected: list[str],
    errors: list[str],
    prefix: str,
) -> None:
    if mapping.get("indexed_fields") != expected:
        errors.append(f"{prefix}_indexed_fields_not_expected")


def _validate_required(mapping: dict[str, Any], required: set[str], errors: list[str], prefix: str) -> None:
    missing = sorted(field for field in required if field not in mapping)
    label = f"{prefix}_" if prefix else ""
    errors.extend(f"missing_required_field:{label}{field}" for field in missing)


def _validate_no_extra(mapping: dict[str, Any], required: set[str], errors: list[str], prefix: str) -> None:
    extra = sorted(field for field in mapping if field not in required)
    label = f"{prefix}_" if prefix else ""
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

    print(json.dumps(run_phase1_tick1_frame_three_line_substrate_index_minimal_check(), indent=2))
