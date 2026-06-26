"""Create a record-only Phase2 perception/capability grounding entry report."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .phase1_closure_audit_minimal import (
    BOUNDARY_INDEX_AFTER as CLOSURE_BOUNDARY_INDEX,
    run_phase1_closure_audit_minimal_check,
    validate_phase1_closure_audit_record,
)
from .phase1_tick1_frame_three_line_substrate_index_minimal import (
    BOUNDARY_INDEX_AFTER as THREE_LINE_INDEX_BOUNDARY_INDEX,
    run_phase1_tick1_frame_three_line_substrate_index_minimal_check,
    validate_phase1_tick1_frame_three_line_substrate_index_record,
)


COMMAND = "run-phase2-closed-phase1-substrate-perception-capability-grounding-entry-minimal-check"
FLOW = "phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal_v0"
PACKAGE_ID = "PKG-Phase2-ClosedPhase1SubstratePerceptionCapabilityGroundingEntry-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b183"
BOUNDARY_INDEX_AFTER = "2026-06-09-b184"
RECORD_TYPE = "phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal"
PHASE2_PURPOSE = "perception_and_capability_grounding"
EXPECTED_PERCEPTION_EVIDENCE_CANDIDATE_COUNT = 2
EXPECTED_CAPABILITY_EVIDENCE_CANDIDATE_COUNT = 2

PRESERVED_UNKNOWN_FIELDS = [
    "semantic_visual_label",
    "object_identity",
    "viewport_geometry",
    "active_focus_target",
    "grounded_capability_id",
    "bridge_capability_binding",
    "tool_permission_state",
    "production_runtime_state",
]

BLOCKED_FLAGS = {
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
    "semantic_vision_created",
    "object_recognition_created",
    "active_focus_created",
    "focus_applied",
    "new_visual_record_created",
    "grounded_capability_binding_created",
    "capability_map_created",
    "raw_tool_access_created",
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
    "phase2_entry_report_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_closed_phase1_substrate",
    "perception_grounding_entry",
    "capability_grounding_entry",
    "unknown_field_preservation",
    "phase2_entry_report",
    "authority_containment",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}

REQUIRED_SOURCE_FIELDS = {
    "source_phase1_closure_audit_record_id",
    "source_phase1_closure_validated",
    "source_phase1_closure_boundary_index",
    "source_phase1_closure_ready",
    "source_phase1_duplicate_packages_blocked",
    "source_three_line_index_record_id",
    "source_three_line_index_validated",
    "source_three_line_index_boundary_index",
    "session_id",
    "scenario_id",
    "approved_purpose",
    "source_thought_line_index_created",
    "source_action_line_index_created",
    "source_memory_line_index_created",
    "source_cross_line_continuity_index_created",
    "source_three_line_index_record_only",
    "source_observed_outcome_context",
    "source_closed_operation_context",
    "source_working_memory_slot_set_id",
    "source_evidence_source_set_id",
    "source_record_only",
    "source_live_runtime_blocked",
    "source_no_action_selection",
    "source_no_memory_write",
    "source_production_behavior_blocked",
    "source_proof_claim_blocked",
    "source_consciousness_claim_blocked",
    "all_source_scenarios_match",
    "all_source_sessions_match",
    "all_source_purposes_match",
}

REQUIRED_PERCEPTION_FIELDS = {
    "perception_entry_id",
    "entry_scope",
    "entry_authority",
    "phase2_purpose",
    "perception_evidence_candidates_identified",
    "perception_evidence_candidate_count",
    "perception_evidence_candidates",
    "grounding_entry_created",
    "grounding_completed",
    "semantic_vision_created",
    "object_recognition_created",
    "active_focus_created",
    "focus_applied",
    "new_visual_record_created",
    "candidate_input_created",
}

REQUIRED_CAPABILITY_FIELDS = {
    "capability_entry_id",
    "entry_scope",
    "entry_authority",
    "phase2_purpose",
    "capability_evidence_candidates_identified",
    "capability_evidence_candidate_count",
    "capability_evidence_candidates",
    "grounding_entry_created",
    "grounding_completed",
    "grounded_capability_binding_created",
    "capability_map_created",
    "raw_tool_access_created",
    "external_tool_called",
    "candidate_input_created",
}

REQUIRED_EVIDENCE_CANDIDATE_FIELDS = {
    "evidence_candidate_id",
    "evidence_kind",
    "source_field",
    "source_value",
    "candidate_authority",
    "known_from_closed_phase1_substrate",
    "unknown_fields_preserved",
    "record_reference_only",
    "creates_new_record",
    "semantic_vision_claimed",
    "object_recognition_claimed",
    "active_focus_created",
    "capability_authority_created",
    "action_preparation_created",
}

REQUIRED_UNKNOWN_FIELDS = {
    "unknown_field_preservation_id",
    "preservation_scope",
    "preservation_authority",
    "unknown_fields_preserved",
    "preserved_unknown_fields",
    "unknown_field_count",
    "unknown_fields_resolved_in_this_package",
    "unknown_values_invented",
    "requires_future_perception_record",
    "requires_future_capability_map_read",
    "candidate_input_created",
}

REQUIRED_REPORT_FIELDS = {
    "report_id",
    "report_scope",
    "report_authority",
    "phase2_entry_report_created",
    "phase2_purpose",
    "reads_closed_phase1_substrate",
    "identifies_perception_evidence_candidates",
    "identifies_capability_evidence_candidates",
    "preserves_unknown_fields",
    "record_only_report",
    "live_runtime_started",
    "candidate_input_created",
    "candidate_ordering_created",
    "action_preparation_created",
    "action_selection_created",
    "direct_command_created",
    "execution_created",
    "outcome_observation_created",
    "memory_write_created",
    "predictor_used",
    "production_behavior_created",
    "learning_claim_created",
    "consciousness_claim_created",
}

TRUE_CONTAINMENT_FIELDS = (
    "same_session_only",
    "sandbox_only",
    "record_only_phase2_entry",
    "reads_closed_phase1_substrate_only",
    "perception_evidence_candidates_identified_in_this_package",
    "capability_evidence_candidates_identified_in_this_package",
    "unknown_fields_preserved_in_this_package",
    "future_perception_grounding_requires_separate_package",
    "future_capability_grounding_requires_separate_package",
)

FALSE_CONTAINMENT_FIELDS = (
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
    "semantic_vision_created_in_this_package",
    "object_recognition_created_in_this_package",
    "active_focus_created_in_this_package",
    "focus_applied_in_this_package",
    "new_visual_record_created_in_this_package",
    "grounded_capability_binding_created_in_this_package",
    "capability_map_created_in_this_package",
    "raw_tool_access_created_in_this_package",
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
    "semantic_vision_created",
    "object_recognition_created",
    "active_focus_created",
    "focus_applied",
    "new_visual_record_created",
    "grounded_capability_binding_created",
    "capability_map_created",
    "raw_tool_access_created",
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


def build_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(
    phase1_closure_audit_record: dict[str, Any] | None = None,
    three_line_substrate_index_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    closure = deepcopy(phase1_closure_audit_record) if phase1_closure_audit_record is not None else _default_closure()
    index = deepcopy(three_line_substrate_index_record) if three_line_substrate_index_record is not None else _default_index(closure)

    source = _source_summary(closure, index)
    perception = _build_perception_grounding_entry(source)
    capability = _build_capability_grounding_entry(source)
    unknown = _build_unknown_field_preservation(source)
    report = _build_phase2_entry_report(source, perception, capability, unknown)

    return {
        "phase2_entry_report_id": f"phase2_grounding_entry_{source['scenario_id']}_demo_001",
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_closed_phase1_substrate": source,
        "perception_grounding_entry": perception,
        "capability_grounding_entry": capability,
        "unknown_field_preservation": unknown,
        "phase2_entry_report": report,
        "authority_containment": _build_authority_containment(),
        "boundary_audit": _build_boundary_audit(),
        "human_summary": {
            "what_was_built": "A record-only Phase2 entry report from the closed Phase1 substrate.",
            "what_changed": (
                "The closed Phase1 substrate is now sorted into perception evidence candidates, "
                "capability evidence candidates, and preserved unknown fields."
            ),
            "what_is_blocked": (
                "No candidate input, ordering, action selection, command, execution, outcome observation, "
                "memory write, predictor use, production behavior, or learning/consciousness claim is created."
            ),
            "plain_result": "Phase2 starts by asking what can be seen and what capability evidence exists, without preparing an action.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(
    record: dict[str, Any],
) -> dict[str, Any]:
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
    if not _non_empty_string(record.get("phase2_entry_report_id")):
        errors.append("phase2_entry_report_id_empty")

    source = _as_dict(record.get("source_closed_phase1_substrate"), errors, "source_closed_phase1_substrate")
    perception = _as_dict(record.get("perception_grounding_entry"), errors, "perception_grounding_entry")
    capability = _as_dict(record.get("capability_grounding_entry"), errors, "capability_grounding_entry")
    unknown = _as_dict(record.get("unknown_field_preservation"), errors, "unknown_field_preservation")
    report = _as_dict(record.get("phase2_entry_report"), errors, "phase2_entry_report")
    containment = _as_dict(record.get("authority_containment"), errors, "authority_containment")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_perception(perception, source, errors)
    _validate_capability(capability, source, errors)
    _validate_unknown_preservation(unknown, errors)
    _validate_report(report, errors)
    _validate_containment(containment, errors)
    _validate_audit(audit, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "session_id": source.get("session_id"),
        "phase2_entry_report_created": report.get("phase2_entry_report_created") is True,
        "perception_evidence_candidates_identified": _perception_identified(perception),
        "capability_evidence_candidates_identified": _capability_identified(capability),
        "unknown_fields_preserved": _unknown_fields_preserved(unknown),
        "candidate_input_blocked": _candidate_input_blocked(report, containment, audit, blocked),
        "candidate_ordering_blocked": _candidate_ordering_blocked(report, containment, audit, blocked),
        "action_selection_blocked": _action_selection_blocked(report, containment, audit, blocked),
        "direct_command_blocked": _direct_command_blocked(report, containment, audit, blocked),
        "execution_blocked": _execution_blocked(report, containment, audit, blocked),
        "outcome_observation_blocked": _outcome_observation_blocked(report, containment, audit, blocked),
        "memory_write_blocked": _memory_write_blocked(report, containment, audit, blocked),
        "semantic_vision_blocked": _semantic_vision_blocked(perception, containment, audit, blocked),
        "capability_authority_blocked": _capability_authority_blocked(capability, containment, audit, blocked),
        "external_tools_blocked": _external_tools_blocked(capability, containment, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(report, containment, audit, blocked),
        "direct_feed_blocked": _direct_feed_blocked(containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(report, containment, audit, blocked),
        "learning_claim_blocked": _learning_claim_blocked(report, containment, audit, blocked),
        "consciousness_claim_blocked": _consciousness_claim_blocked(report, containment, audit, blocked),
        "llm_runtime_blocked": _llm_runtime_blocked(containment, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal_check() -> dict[str, Any]:
    closure_records = _by_scenario(
        run_phase1_closure_audit_minimal_check()["valid_records"],
        lambda record: record["source_phase1_substrates"]["scenario_id"],
    )
    index_records = _by_scenario(
        run_phase1_tick1_frame_three_line_substrate_index_minimal_check()["valid_records"],
        lambda record: record["source_runtime_tick_handoff"]["scenario_id"],
    )
    scenarios = sorted(set(closure_records) & set(index_records))
    valid_records = [
        build_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(
            closure_records[scenario],
            index_records[scenario],
        )
        for scenario in scenarios
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(record)
        for record in records
    ]
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
            "boundary_reason": (
                "Starts Phase2 by reading the closed Phase1 substrate as perception/capability "
                "grounding entry evidence, without candidate input or action preparation."
            ),
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A Phase2 perception/capability grounding entry report.",
            "what_changed": "Closed Phase1 substrate records now expose report-only perception and capability evidence candidates.",
            "what_is_blocked": "No candidate input, ordering, action selection, execution, memory write, production behavior, or proof/consciousness claim is created.",
            "plain_result": "Phase2 now starts by looking for visible evidence and capability evidence, not by preparing an action.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(closure: dict[str, Any], index: dict[str, Any]) -> dict[str, Any]:
    closure_validation = validate_phase1_closure_audit_record(closure)
    index_validation = validate_phase1_tick1_frame_three_line_substrate_index_record(index)
    if not closure_validation["valid"]:
        raise ValueError("phase1_closure_audit_record must validate before Phase2 entry")
    if not index_validation["valid"]:
        raise ValueError("three_line_substrate_index_record must validate before Phase2 entry")

    closure_source = closure["source_phase1_substrates"]
    index_source = index["source_runtime_tick_handoff"]
    memory_line = index["memory_line_index"]

    scenario_id = closure_source["scenario_id"]
    session_id = closure_source["session_id"]
    approved_purpose = closure_source["approved_purpose"]
    return {
        "source_phase1_closure_audit_record_id": closure["phase1_closure_audit_record_id"],
        "source_phase1_closure_validated": True,
        "source_phase1_closure_boundary_index": closure["boundary_index_after"],
        "source_phase1_closure_ready": closure_validation["phase1_closure_ready"],
        "source_phase1_duplicate_packages_blocked": closure_validation["duplicate_phase1_packages_blocked"],
        "source_three_line_index_record_id": index["tick1_three_line_substrate_index_record_id"],
        "source_three_line_index_validated": True,
        "source_three_line_index_boundary_index": index["boundary_index_after"],
        "session_id": session_id,
        "scenario_id": scenario_id,
        "approved_purpose": approved_purpose,
        "source_thought_line_index_created": index_validation["thought_line_index_created"],
        "source_action_line_index_created": index_validation["action_line_index_created"],
        "source_memory_line_index_created": index_validation["memory_line_index_created"],
        "source_cross_line_continuity_index_created": index_validation["cross_line_continuity_index_created"],
        "source_three_line_index_record_only": index_validation["three_line_index_record_only"],
        "source_observed_outcome_context": index_source["observed_outcome_context"],
        "source_closed_operation_context": index_source["selected_action_context"],
        "source_working_memory_slot_set_id": memory_line["working_memory_slot_set_id"],
        "source_evidence_source_set_id": memory_line["evidence_source_set_id"],
        "source_record_only": index_validation["three_line_index_record_only"],
        "source_live_runtime_blocked": index_validation["live_runtime_blocked"] and closure_validation["no_live_runtime"],
        "source_no_action_selection": closure_validation["no_action_selection"],
        "source_no_memory_write": closure_validation["no_memory_write"],
        "source_production_behavior_blocked": index_validation["production_behavior_blocked"],
        "source_proof_claim_blocked": index_validation["proof_claim_blocked"],
        "source_consciousness_claim_blocked": index_validation["consciousness_claim_blocked"],
        "all_source_scenarios_match": scenario_id == index_source["scenario_id"],
        "all_source_sessions_match": session_id == index_source["session_id"],
        "all_source_purposes_match": approved_purpose == index_source["approved_purpose"],
    }


def _build_perception_grounding_entry(source: dict[str, Any]) -> dict[str, Any]:
    candidates = [
        _evidence_candidate(
            source,
            "perception",
            "observed_outcome_context",
            "source_observed_outcome_context",
            source["source_observed_outcome_context"],
        ),
        _evidence_candidate(
            source,
            "perception",
            "phase1_evidence_source_reference",
            "source_evidence_source_set_id",
            source["source_evidence_source_set_id"],
        ),
    ]
    return {
        "perception_entry_id": f"phase2_perception_entry_{source['scenario_id']}_001",
        "entry_scope": "same_session_sandbox_record_only",
        "entry_authority": "record_only_perception_evidence_identification",
        "phase2_purpose": PHASE2_PURPOSE,
        "perception_evidence_candidates_identified": True,
        "perception_evidence_candidate_count": EXPECTED_PERCEPTION_EVIDENCE_CANDIDATE_COUNT,
        "perception_evidence_candidates": candidates,
        "grounding_entry_created": True,
        "grounding_completed": False,
        "semantic_vision_created": False,
        "object_recognition_created": False,
        "active_focus_created": False,
        "focus_applied": False,
        "new_visual_record_created": False,
        "candidate_input_created": False,
    }


def _build_capability_grounding_entry(source: dict[str, Any]) -> dict[str, Any]:
    candidates = [
        _evidence_candidate(
            source,
            "capability",
            "closed_operation_context",
            "source_closed_operation_context",
            source["source_closed_operation_context"],
        ),
        _evidence_candidate(
            source,
            "capability",
            "phase1_evidence_source_reference",
            "source_evidence_source_set_id",
            source["source_evidence_source_set_id"],
        ),
    ]
    return {
        "capability_entry_id": f"phase2_capability_entry_{source['scenario_id']}_001",
        "entry_scope": "same_session_sandbox_record_only",
        "entry_authority": "record_only_capability_evidence_identification",
        "phase2_purpose": PHASE2_PURPOSE,
        "capability_evidence_candidates_identified": True,
        "capability_evidence_candidate_count": EXPECTED_CAPABILITY_EVIDENCE_CANDIDATE_COUNT,
        "capability_evidence_candidates": candidates,
        "grounding_entry_created": True,
        "grounding_completed": False,
        "grounded_capability_binding_created": False,
        "capability_map_created": False,
        "raw_tool_access_created": False,
        "external_tool_called": False,
        "candidate_input_created": False,
    }


def _evidence_candidate(
    source: dict[str, Any],
    lane: str,
    evidence_kind: str,
    source_field: str,
    source_value: str,
) -> dict[str, Any]:
    return {
        "evidence_candidate_id": f"phase2_{lane}_evidence_{source['scenario_id']}_{evidence_kind}_001",
        "evidence_kind": evidence_kind,
        "source_field": source_field,
        "source_value": source_value,
        "candidate_authority": "evidence_candidate_only_not_action_preparation",
        "known_from_closed_phase1_substrate": True,
        "unknown_fields_preserved": True,
        "record_reference_only": True,
        "creates_new_record": False,
        "semantic_vision_claimed": False,
        "object_recognition_claimed": False,
        "active_focus_created": False,
        "capability_authority_created": False,
        "action_preparation_created": False,
    }


def _build_unknown_field_preservation(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "unknown_field_preservation_id": f"phase2_unknown_preservation_{source['scenario_id']}_001",
        "preservation_scope": "phase2_perception_capability_entry_report",
        "preservation_authority": "preserve_unknowns_do_not_invent_grounding",
        "unknown_fields_preserved": True,
        "preserved_unknown_fields": PRESERVED_UNKNOWN_FIELDS,
        "unknown_field_count": len(PRESERVED_UNKNOWN_FIELDS),
        "unknown_fields_resolved_in_this_package": False,
        "unknown_values_invented": False,
        "requires_future_perception_record": True,
        "requires_future_capability_map_read": True,
        "candidate_input_created": False,
    }


def _build_phase2_entry_report(
    source: dict[str, Any],
    perception: dict[str, Any],
    capability: dict[str, Any],
    unknown: dict[str, Any],
) -> dict[str, Any]:
    return {
        "report_id": f"phase2_entry_report_{source['scenario_id']}_001",
        "report_scope": "same_session_sandbox_record_only",
        "report_authority": "phase2_entry_report_only",
        "phase2_entry_report_created": True,
        "phase2_purpose": PHASE2_PURPOSE,
        "reads_closed_phase1_substrate": True,
        "identifies_perception_evidence_candidates": perception["perception_evidence_candidates_identified"],
        "identifies_capability_evidence_candidates": capability["capability_evidence_candidates_identified"],
        "preserves_unknown_fields": unknown["unknown_fields_preserved"],
        "record_only_report": True,
        "live_runtime_started": False,
        "candidate_input_created": False,
        "candidate_ordering_created": False,
        "action_preparation_created": False,
        "action_selection_created": False,
        "direct_command_created": False,
        "execution_created": False,
        "outcome_observation_created": False,
        "memory_write_created": False,
        "predictor_used": False,
        "production_behavior_created": False,
        "learning_claim_created": False,
        "consciousness_claim_created": False,
    }


def _build_authority_containment() -> dict[str, bool]:
    containment = {field: True for field in TRUE_CONTAINMENT_FIELDS}
    containment.update({field: False for field in FALSE_CONTAINMENT_FIELDS})
    return containment


def _build_boundary_audit() -> dict[str, Any]:
    audit = {
        "boundary_audit_id": "phase2_grounding_entry_b184_boundary_audit",
        "triggered": True,
        "boundary_number": 184,
        "package_id": PACKAGE_ID,
    }
    audit.update({field: False for field in FALSE_AUDIT_FIELDS})
    return audit


def _invalid_records(reach: dict[str, Any], wait: dict[str, Any], probe: dict[str, Any]) -> list[dict[str, Any]]:
    invalid: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[Any, ...], value: Any) -> None:
        record = deepcopy(source)
        record["phase2_entry_report_id"] = f"{record['phase2_entry_report_id']}__invalid_{label}"
        _set_path(record, path, value)
        invalid.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "phase2_wrong_record")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), "2026-06-09-b185")
    mutate(reach, "closure_not_validated", ("source_closed_phase1_substrate", "source_phase1_closure_validated"), False)
    mutate(reach, "closure_wrong_boundary", ("source_closed_phase1_substrate", "source_phase1_closure_boundary_index"), "2026-06-09-b182")
    mutate(reach, "closure_not_ready", ("source_closed_phase1_substrate", "source_phase1_closure_ready"), False)
    mutate(wait, "index_not_validated", ("source_closed_phase1_substrate", "source_three_line_index_validated"), False)
    mutate(wait, "index_wrong_boundary", ("source_closed_phase1_substrate", "source_three_line_index_boundary_index"), "2026-06-09-b181")
    mutate(wait, "three_line_record_not_only", ("source_closed_phase1_substrate", "source_three_line_index_record_only"), False)
    mutate(wait, "source_scenario_mismatch", ("source_closed_phase1_substrate", "all_source_scenarios_match"), False)
    mutate(wait, "perception_not_identified", ("perception_grounding_entry", "perception_evidence_candidates_identified"), False)
    mutate(wait, "perception_count_wrong", ("perception_grounding_entry", "perception_evidence_candidate_count"), 1)
    mutate(wait, "perception_semantic_claim", ("perception_grounding_entry", "perception_evidence_candidates", 0, "semantic_vision_claimed"), True)
    mutate(wait, "perception_object_claim", ("perception_grounding_entry", "perception_evidence_candidates", 0, "object_recognition_claimed"), True)
    mutate(wait, "new_visual_record", ("perception_grounding_entry", "new_visual_record_created"), True)
    mutate(wait, "active_focus", ("perception_grounding_entry", "active_focus_created"), True)
    mutate(probe, "capability_not_identified", ("capability_grounding_entry", "capability_evidence_candidates_identified"), False)
    mutate(probe, "capability_count_wrong", ("capability_grounding_entry", "capability_evidence_candidate_count"), 1)
    mutate(probe, "capability_binding", ("capability_grounding_entry", "grounded_capability_binding_created"), True)
    mutate(probe, "capability_map", ("capability_grounding_entry", "capability_map_created"), True)
    mutate(probe, "raw_tool_access", ("capability_grounding_entry", "raw_tool_access_created"), True)
    mutate(probe, "capability_authority", ("capability_grounding_entry", "capability_evidence_candidates", 0, "capability_authority_created"), True)
    mutate(reach, "unknown_not_preserved", ("unknown_field_preservation", "unknown_fields_preserved"), False)
    mutate(reach, "unknown_resolved", ("unknown_field_preservation", "unknown_fields_resolved_in_this_package"), True)
    mutate(reach, "unknown_invented", ("unknown_field_preservation", "unknown_values_invented"), True)
    mutate(reach, "report_not_created", ("phase2_entry_report", "phase2_entry_report_created"), False)
    mutate(reach, "wrong_phase2_purpose", ("phase2_entry_report", "phase2_purpose"), "candidate_input")
    mutate(wait, "candidate_input", ("phase2_entry_report", "candidate_input_created"), True)
    mutate(wait, "candidate_ordering", ("phase2_entry_report", "candidate_ordering_created"), True)
    mutate(wait, "selected_action", ("authority_containment", "selected_action_created_in_this_package"), True)
    mutate(wait, "final_action", ("authority_containment", "final_action_created_in_this_package"), True)
    mutate(wait, "direct_command", ("phase2_entry_report", "direct_command_created"), True)
    mutate(wait, "execution", ("phase2_entry_report", "execution_created"), True)
    mutate(wait, "outcome_observation", ("phase2_entry_report", "outcome_observation_created"), True)
    mutate(probe, "memory_write", ("phase2_entry_report", "memory_write_created"), True)
    mutate(probe, "predictor_read", ("authority_containment", "predictor_read_enabled_in_this_package"), True)
    mutate(probe, "predictor_modified", ("authority_containment", "predictor_modified_in_this_package"), True)
    mutate(probe, "external_tool", ("capability_grounding_entry", "external_tool_called"), True)
    mutate(probe, "production_behavior", ("phase2_entry_report", "production_behavior_created"), True)
    mutate(probe, "learning_claim", ("phase2_entry_report", "learning_claim_created"), True)
    mutate(probe, "consciousness_claim", ("phase2_entry_report", "consciousness_claim_created"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalid


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(source, REQUIRED_SOURCE_FIELDS, errors, "source")
    _validate_no_extra(source, REQUIRED_SOURCE_FIELDS, errors, "source")
    _validate_expected(
        source,
        {
            "source_phase1_closure_validated": True,
            "source_phase1_closure_boundary_index": CLOSURE_BOUNDARY_INDEX,
            "source_phase1_closure_ready": True,
            "source_phase1_duplicate_packages_blocked": True,
            "source_three_line_index_validated": True,
            "source_three_line_index_boundary_index": THREE_LINE_INDEX_BOUNDARY_INDEX,
            "source_thought_line_index_created": True,
            "source_action_line_index_created": True,
            "source_memory_line_index_created": True,
            "source_cross_line_continuity_index_created": True,
            "source_three_line_index_record_only": True,
            "source_record_only": True,
            "source_live_runtime_blocked": True,
            "source_no_action_selection": True,
            "source_no_memory_write": True,
            "source_production_behavior_blocked": True,
            "source_proof_claim_blocked": True,
            "source_consciousness_claim_blocked": True,
            "all_source_scenarios_match": True,
            "all_source_sessions_match": True,
            "all_source_purposes_match": True,
        },
        errors,
        "source",
    )
    for field in (
        "source_phase1_closure_audit_record_id",
        "source_three_line_index_record_id",
        "session_id",
        "scenario_id",
        "approved_purpose",
        "source_observed_outcome_context",
        "source_closed_operation_context",
        "source_working_memory_slot_set_id",
        "source_evidence_source_set_id",
    ):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")


def _validate_perception(perception: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(perception, REQUIRED_PERCEPTION_FIELDS, errors, "perception")
    _validate_no_extra(perception, REQUIRED_PERCEPTION_FIELDS, errors, "perception")
    _validate_expected(
        perception,
        {
            "entry_scope": "same_session_sandbox_record_only",
            "entry_authority": "record_only_perception_evidence_identification",
            "phase2_purpose": PHASE2_PURPOSE,
            "perception_evidence_candidates_identified": True,
            "perception_evidence_candidate_count": EXPECTED_PERCEPTION_EVIDENCE_CANDIDATE_COUNT,
            "grounding_entry_created": True,
            "grounding_completed": False,
            "semantic_vision_created": False,
            "object_recognition_created": False,
            "active_focus_created": False,
            "focus_applied": False,
            "new_visual_record_created": False,
            "candidate_input_created": False,
        },
        errors,
        "perception",
    )
    if not _non_empty_string(perception.get("perception_entry_id")):
        errors.append("perception_entry_id_empty")
    expected = {
        "observed_outcome_context": ("source_observed_outcome_context", source.get("source_observed_outcome_context")),
        "phase1_evidence_source_reference": ("source_evidence_source_set_id", source.get("source_evidence_source_set_id")),
    }
    _validate_evidence_candidates(
        perception.get("perception_evidence_candidates"),
        expected,
        EXPECTED_PERCEPTION_EVIDENCE_CANDIDATE_COUNT,
        "perception",
        errors,
    )


def _validate_capability(capability: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(capability, REQUIRED_CAPABILITY_FIELDS, errors, "capability")
    _validate_no_extra(capability, REQUIRED_CAPABILITY_FIELDS, errors, "capability")
    _validate_expected(
        capability,
        {
            "entry_scope": "same_session_sandbox_record_only",
            "entry_authority": "record_only_capability_evidence_identification",
            "phase2_purpose": PHASE2_PURPOSE,
            "capability_evidence_candidates_identified": True,
            "capability_evidence_candidate_count": EXPECTED_CAPABILITY_EVIDENCE_CANDIDATE_COUNT,
            "grounding_entry_created": True,
            "grounding_completed": False,
            "grounded_capability_binding_created": False,
            "capability_map_created": False,
            "raw_tool_access_created": False,
            "external_tool_called": False,
            "candidate_input_created": False,
        },
        errors,
        "capability",
    )
    if not _non_empty_string(capability.get("capability_entry_id")):
        errors.append("capability_entry_id_empty")
    expected = {
        "closed_operation_context": ("source_closed_operation_context", source.get("source_closed_operation_context")),
        "phase1_evidence_source_reference": ("source_evidence_source_set_id", source.get("source_evidence_source_set_id")),
    }
    _validate_evidence_candidates(
        capability.get("capability_evidence_candidates"),
        expected,
        EXPECTED_CAPABILITY_EVIDENCE_CANDIDATE_COUNT,
        "capability",
        errors,
    )


def _validate_evidence_candidates(
    candidates: Any,
    expected: dict[str, tuple[str, Any]],
    expected_count: int,
    prefix: str,
    errors: list[str],
) -> None:
    if not isinstance(candidates, list):
        errors.append(f"{prefix}_evidence_candidates_not_list")
        return
    if len(candidates) != expected_count:
        errors.append(f"{prefix}_evidence_candidate_count_not_expected")
        return
    seen: set[str] = set()
    for item in candidates:
        if not isinstance(item, dict):
            errors.append(f"{prefix}_evidence_candidate_not_dict")
            continue
        _validate_required(item, REQUIRED_EVIDENCE_CANDIDATE_FIELDS, errors, f"{prefix}_candidate")
        _validate_no_extra(item, REQUIRED_EVIDENCE_CANDIDATE_FIELDS, errors, f"{prefix}_candidate")
        kind = item.get("evidence_kind")
        seen.add(kind)
        if not _non_empty_string(item.get("evidence_candidate_id")):
            errors.append(f"{prefix}_evidence_candidate_id_empty")
        if kind in expected:
            expected_field, expected_value = expected[kind]
            if item.get("source_field") != expected_field:
                errors.append(f"{prefix}_{kind}_source_field_not_expected")
            if item.get("source_value") != expected_value:
                errors.append(f"{prefix}_{kind}_source_value_not_expected")
        if item.get("candidate_authority") != "evidence_candidate_only_not_action_preparation":
            errors.append(f"{prefix}_{kind}_authority_not_expected")
        for field in ("known_from_closed_phase1_substrate", "unknown_fields_preserved", "record_reference_only"):
            if item.get(field) is not True:
                errors.append(f"{prefix}_{kind}_{field}_not_true")
        for field in (
            "creates_new_record",
            "semantic_vision_claimed",
            "object_recognition_claimed",
            "active_focus_created",
            "capability_authority_created",
            "action_preparation_created",
        ):
            if item.get(field) is not False:
                errors.append(f"{prefix}_{kind}_{field}_not_false")
    if seen != set(expected):
        errors.append(f"{prefix}_evidence_kinds_not_expected")


def _validate_unknown_preservation(unknown: dict[str, Any], errors: list[str]) -> None:
    _validate_required(unknown, REQUIRED_UNKNOWN_FIELDS, errors, "unknown")
    _validate_no_extra(unknown, REQUIRED_UNKNOWN_FIELDS, errors, "unknown")
    _validate_expected(
        unknown,
        {
            "preservation_scope": "phase2_perception_capability_entry_report",
            "preservation_authority": "preserve_unknowns_do_not_invent_grounding",
            "unknown_fields_preserved": True,
            "preserved_unknown_fields": PRESERVED_UNKNOWN_FIELDS,
            "unknown_field_count": len(PRESERVED_UNKNOWN_FIELDS),
            "unknown_fields_resolved_in_this_package": False,
            "unknown_values_invented": False,
            "requires_future_perception_record": True,
            "requires_future_capability_map_read": True,
            "candidate_input_created": False,
        },
        errors,
        "unknown",
    )
    if not _non_empty_string(unknown.get("unknown_field_preservation_id")):
        errors.append("unknown_field_preservation_id_empty")


def _validate_report(report: dict[str, Any], errors: list[str]) -> None:
    _validate_required(report, REQUIRED_REPORT_FIELDS, errors, "report")
    _validate_no_extra(report, REQUIRED_REPORT_FIELDS, errors, "report")
    _validate_expected(
        report,
        {
            "report_scope": "same_session_sandbox_record_only",
            "report_authority": "phase2_entry_report_only",
            "phase2_entry_report_created": True,
            "phase2_purpose": PHASE2_PURPOSE,
            "reads_closed_phase1_substrate": True,
            "identifies_perception_evidence_candidates": True,
            "identifies_capability_evidence_candidates": True,
            "preserves_unknown_fields": True,
            "record_only_report": True,
            "live_runtime_started": False,
            "candidate_input_created": False,
            "candidate_ordering_created": False,
            "action_preparation_created": False,
            "action_selection_created": False,
            "direct_command_created": False,
            "execution_created": False,
            "outcome_observation_created": False,
            "memory_write_created": False,
            "predictor_used": False,
            "production_behavior_created": False,
            "learning_claim_created": False,
            "consciousness_claim_created": False,
        },
        errors,
        "report",
    )
    if not _non_empty_string(report.get("report_id")):
        errors.append("report_id_empty")


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
        {"triggered": True, "boundary_number": 184, "package_id": PACKAGE_ID},
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


def _perception_identified(perception: dict[str, Any]) -> bool:
    candidates = perception.get("perception_evidence_candidates")
    return (
        perception.get("perception_evidence_candidates_identified") is True
        and perception.get("perception_evidence_candidate_count") == EXPECTED_PERCEPTION_EVIDENCE_CANDIDATE_COUNT
        and isinstance(candidates, list)
        and len(candidates) == EXPECTED_PERCEPTION_EVIDENCE_CANDIDATE_COUNT
    )


def _capability_identified(capability: dict[str, Any]) -> bool:
    candidates = capability.get("capability_evidence_candidates")
    return (
        capability.get("capability_evidence_candidates_identified") is True
        and capability.get("capability_evidence_candidate_count") == EXPECTED_CAPABILITY_EVIDENCE_CANDIDATE_COUNT
        and isinstance(candidates, list)
        and len(candidates) == EXPECTED_CAPABILITY_EVIDENCE_CANDIDATE_COUNT
    )


def _unknown_fields_preserved(unknown: dict[str, Any]) -> bool:
    return (
        unknown.get("unknown_fields_preserved") is True
        and unknown.get("preserved_unknown_fields") == PRESERVED_UNKNOWN_FIELDS
        and unknown.get("unknown_fields_resolved_in_this_package") is False
        and unknown.get("unknown_values_invented") is False
    )


def _candidate_input_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            report.get("candidate_input_created"),
            report.get("action_preparation_created"),
            containment.get("candidate_input_created_in_this_package"),
            audit.get("candidate_input_created"),
            blocked.get("candidate_input_created"),
        )
    )


def _candidate_ordering_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            report.get("candidate_ordering_created"),
            containment.get("candidate_ordering_created_in_this_package"),
            containment.get("candidate_reordering_created_in_this_package"),
            audit.get("candidate_ordering_created"),
            audit.get("candidate_reordering_created"),
            blocked.get("candidate_ordering_created"),
            blocked.get("candidate_reordering_created"),
            blocked.get("candidate_scores_changed"),
            blocked.get("next_cycle_candidate_ordering_changed"),
        )
    )


def _action_selection_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            report.get("action_selection_created"),
            containment.get("selected_action_created_in_this_package"),
            containment.get("final_action_created_in_this_package"),
            audit.get("selected_action_created"),
            audit.get("final_action_created"),
            blocked.get("selected_action_created"),
            blocked.get("final_action_created"),
        )
    )


def _direct_command_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        report.get("direct_command_created") is False
        and containment.get("direct_command_created_in_this_package") is False
        and audit.get("direct_command_created") is False
        and blocked.get("direct_command_created") is False
    )


def _execution_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        report.get("execution_created") is False
        and containment.get("execution_created_in_this_package") is False
        and audit.get("execution_created") is False
        and blocked.get("execution_created") is False
    )


def _outcome_observation_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        report.get("outcome_observation_created") is False
        and containment.get("outcome_observation_created_in_this_package") is False
        and audit.get("outcome_observation_created") is False
        and blocked.get("outcome_observation_created") is False
    )


def _memory_write_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            report.get("memory_write_created"),
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


def _semantic_vision_blocked(
    perception: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    candidates = perception.get("perception_evidence_candidates", [])
    candidates_clear = isinstance(candidates, list) and all(
        isinstance(candidate, dict)
        and candidate.get("semantic_vision_claimed") is False
        and candidate.get("object_recognition_claimed") is False
        and candidate.get("active_focus_created") is False
        for candidate in candidates
    )
    return candidates_clear and all(
        value is False
        for value in (
            perception.get("semantic_vision_created"),
            perception.get("object_recognition_created"),
            perception.get("active_focus_created"),
            perception.get("focus_applied"),
            perception.get("new_visual_record_created"),
            containment.get("semantic_vision_created_in_this_package"),
            containment.get("object_recognition_created_in_this_package"),
            containment.get("active_focus_created_in_this_package"),
            containment.get("focus_applied_in_this_package"),
            containment.get("new_visual_record_created_in_this_package"),
            audit.get("semantic_vision_created"),
            audit.get("object_recognition_created"),
            audit.get("active_focus_created"),
            audit.get("focus_applied"),
            audit.get("new_visual_record_created"),
            blocked.get("semantic_vision_created"),
            blocked.get("object_recognition_created"),
            blocked.get("active_focus_created"),
            blocked.get("focus_applied"),
            blocked.get("new_visual_record_created"),
        )
    )


def _capability_authority_blocked(
    capability: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    candidates = capability.get("capability_evidence_candidates", [])
    candidates_clear = isinstance(candidates, list) and all(
        isinstance(candidate, dict)
        and candidate.get("capability_authority_created") is False
        and candidate.get("action_preparation_created") is False
        for candidate in candidates
    )
    return candidates_clear and all(
        value is False
        for value in (
            capability.get("grounded_capability_binding_created"),
            capability.get("capability_map_created"),
            capability.get("raw_tool_access_created"),
            containment.get("grounded_capability_binding_created_in_this_package"),
            containment.get("capability_map_created_in_this_package"),
            containment.get("raw_tool_access_created_in_this_package"),
            audit.get("grounded_capability_binding_created"),
            audit.get("capability_map_created"),
            audit.get("raw_tool_access_created"),
            blocked.get("grounded_capability_binding_created"),
            blocked.get("capability_map_created"),
            blocked.get("raw_tool_access_created"),
        )
    )


def _external_tools_blocked(
    capability: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            capability.get("external_tool_called"),
            containment.get("external_tool_called_in_this_package"),
            containment.get("external_tool_result_used_in_this_package"),
            audit.get("external_tool_called"),
            audit.get("external_tool_result_used"),
            blocked.get("external_tool_called"),
            blocked.get("external_tool_result_used"),
        )
    )


def _predictor_use_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            report.get("predictor_used"),
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
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            report.get("production_behavior_created"),
            containment.get("production_behavior_created_in_this_package"),
            audit.get("production_behavior_created"),
            audit.get("runtime_behavior_leak"),
            blocked.get("production_action_selection"),
            blocked.get("runtime_action_selection"),
            blocked.get("runtime_behavior_changed"),
            blocked.get("production_behavior_changed"),
        )
    )


def _learning_claim_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return all(
        value is False
        for value in (
            report.get("learning_claim_created"),
            containment.get("proof_of_learning_claim"),
            containment.get("long_term_learning_claim"),
            audit.get("proof_of_learning_claim"),
            audit.get("long_term_learning_claim"),
            blocked.get("proof_of_learning_claim"),
            blocked.get("long_term_learning_claim"),
        )
    )


def _consciousness_claim_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        report.get("consciousness_claim_created") is False
        and containment.get("consciousness_claim") is False
        and audit.get("consciousness_claim") is False
        and blocked.get("consciousness_claim") is False
    )


def _llm_runtime_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        containment.get("llm_runtime_used") is False
        and audit.get("llm_runtime_used") is False
        and blocked.get("llm_runtime_used") is False
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 184
        and audit.get("package_id") == PACKAGE_ID
        and all(audit.get(field) is False for field in FALSE_AUDIT_FIELDS)
    )


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "phase2_entry_result_count": len(validation_results),
        "valid_phase2_entry_count": len(valid),
        "invalid_phase2_entry_count": len(validation_results) - len(valid),
        "phase2_entry_report_created_count": sum(1 for result in valid if result["phase2_entry_report_created"]),
        "perception_evidence_candidates_identified_count": sum(
            1 for result in valid if result["perception_evidence_candidates_identified"]
        ),
        "capability_evidence_candidates_identified_count": sum(
            1 for result in valid if result["capability_evidence_candidates_identified"]
        ),
        "unknown_fields_preserved_count": sum(1 for result in valid if result["unknown_fields_preserved"]),
        "reach_phase2_entry_count": sum(
            1 for result in valid if result["scenario_id"] == "item_reachable_feedback_prioritizes_reach"
        ),
        "wait_phase2_entry_count": sum(
            1 for result in valid if result["scenario_id"] == "item_not_afforded_blocks_feedback_priority"
        ),
        "probe_phase2_entry_count": sum(
            1 for result in valid if result["scenario_id"] == "mismatch_feedback_outranks_retry_tendency"
        ),
        "candidate_input_blocked_count": sum(1 for result in valid if result["candidate_input_blocked"]),
        "candidate_ordering_blocked_count": sum(1 for result in valid if result["candidate_ordering_blocked"]),
        "action_selection_blocked_count": sum(1 for result in valid if result["action_selection_blocked"]),
        "direct_command_blocked_count": sum(1 for result in valid if result["direct_command_blocked"]),
        "execution_blocked_count": sum(1 for result in valid if result["execution_blocked"]),
        "outcome_observation_blocked_count": sum(1 for result in valid if result["outcome_observation_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "semantic_vision_blocked_count": sum(1 for result in valid if result["semantic_vision_blocked"]),
        "capability_authority_blocked_count": sum(1 for result in valid if result["capability_authority_blocked"]),
        "external_tools_blocked_count": sum(1 for result in valid if result["external_tools_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid if result["production_behavior_blocked"]),
        "learning_claim_blocked_count": sum(1 for result in valid if result["learning_claim_blocked"]),
        "consciousness_claim_blocked_count": sum(1 for result in valid if result["consciousness_claim_blocked"]),
        "llm_runtime_blocked_count": sum(1 for result in valid if result["llm_runtime_blocked"]),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["phase2_entry_result_count"] == 44
        and summary["valid_phase2_entry_count"] == 3
        and summary["invalid_phase2_entry_count"] == 41
        and summary["phase2_entry_report_created_count"] == 3
        and summary["perception_evidence_candidates_identified_count"] == 3
        and summary["capability_evidence_candidates_identified_count"] == 3
        and summary["unknown_fields_preserved_count"] == 3
        and summary["reach_phase2_entry_count"] == 1
        and summary["wait_phase2_entry_count"] == 1
        and summary["probe_phase2_entry_count"] == 1
        and summary["candidate_input_blocked_count"] == 3
        and summary["candidate_ordering_blocked_count"] == 3
        and summary["action_selection_blocked_count"] == 3
        and summary["direct_command_blocked_count"] == 3
        and summary["execution_blocked_count"] == 3
        and summary["outcome_observation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["semantic_vision_blocked_count"] == 3
        and summary["capability_authority_blocked_count"] == 3
        and summary["external_tools_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["learning_claim_blocked_count"] == 3
        and summary["consciousness_claim_blocked_count"] == 3
        and summary["llm_runtime_blocked_count"] == 3
        and summary["boundary_audit_passed_count"] == 3
    )


def _default_closure() -> dict[str, Any]:
    return deepcopy(run_phase1_closure_audit_minimal_check()["valid_records"][0])


def _default_index(closure: dict[str, Any]) -> dict[str, Any]:
    scenario = closure["source_phase1_substrates"]["scenario_id"]
    indexes = _by_scenario(
        run_phase1_tick1_frame_three_line_substrate_index_minimal_check()["valid_records"],
        lambda record: record["source_runtime_tick_handoff"]["scenario_id"],
    )
    return deepcopy(indexes[scenario])


def _by_scenario(records: list[dict[str, Any]], getter) -> dict[str, dict[str, Any]]:
    return {getter(record): record for record in records}


def _validate_required(mapping: dict[str, Any], required: set[str], errors: list[str], prefix: str) -> None:
    missing = sorted(field for field in required if field not in mapping)
    label = f"{prefix}_" if prefix else ""
    errors.extend(f"missing_required_field:{label}{field}" for field in missing)


def _validate_no_extra(mapping: dict[str, Any], required: set[str], errors: list[str], prefix: str) -> None:
    extra = sorted(field for field in mapping if field not in required)
    label = f"{prefix}_" if prefix else ""
    errors.extend(f"unexpected_field:{label}{field}" for field in extra)


def _validate_expected(mapping: dict[str, Any], expected: dict[str, Any], errors: list[str], prefix: str) -> None:
    for field, value in expected.items():
        if mapping.get(field) != value:
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

    print(json.dumps(run_phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal_check(), indent=2))
