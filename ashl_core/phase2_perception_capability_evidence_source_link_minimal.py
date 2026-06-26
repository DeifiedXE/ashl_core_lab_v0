"""Link Phase2 perception/capability evidence candidates to existing sources."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    run_phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal_check,
    validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record,
)
from .qingyin_bridge_grounded_capability_map_minimal import (
    BOUNDARY_INDEX_AFTER as CAPABILITY_MAP_BOUNDARY_INDEX,
    run_qingyin_bridge_grounded_capability_map_minimal_check,
    validate_qingyin_bridge_grounded_capability_map_record,
)
from .visual_spatial_grounding_minimal import (
    BOUNDARY_INDEX_AFTER as VISUAL_SPATIAL_BOUNDARY_INDEX,
    run_visual_spatial_grounding_minimal_check,
    validate_visual_spatial_grounding_record,
)


COMMAND = "run-phase2-perception-capability-evidence-source-link-minimal-check"
FLOW = "phase2_perception_capability_evidence_source_link_minimal_v0"
PACKAGE_ID = "PKG-Phase2-PerceptionCapabilityEvidenceSourceLink-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b184"
BOUNDARY_INDEX_AFTER = "2026-06-09-b185"
RECORD_TYPE = "phase2_perception_capability_evidence_source_link_minimal"
PHASE2_PURPOSE = "perception_and_capability_grounding"
EXPECTED_PERCEPTION_LINK_COUNT = 2
EXPECTED_CAPABILITY_LINK_COUNT = 2
EXPECTED_INVALID_SOURCE_LINK_COUNT = 49

OPERATION_TO_CAPABILITY_ID = {
    "reach_front_item": "sandbox.body.reach_front",
}

BLOCKED_FLAGS = {
    "semantic_vision_created",
    "object_recognition_created",
    "active_focus_created",
    "focus_applied",
    "new_visual_record_created",
    "capability_map_created",
    "capability_map_mutated",
    "grounded_capability_binding_created",
    "raw_tool_access_created",
    "external_tool_called",
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
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "production_action_selection",
    "runtime_action_selection",
    "runtime_behavior_changed",
    "production_behavior_changed",
    "learning_claim",
    "proof_of_learning_claim",
    "consciousness_claim",
    "llm_runtime_used",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "source_link_report_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_phase2_entry_report",
    "existing_evidence_source_catalog",
    "perception_evidence_source_links",
    "capability_evidence_source_links",
    "unresolved_unknown_preservation",
    "source_link_report",
    "authority_containment",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}

REQUIRED_SOURCE_FIELDS = {
    "source_phase2_entry_report_id",
    "source_validated",
    "source_boundary_index",
    "session_id",
    "scenario_id",
    "approved_purpose",
    "phase2_entry_report_created",
    "phase2_purpose",
    "perception_evidence_candidate_count",
    "capability_evidence_candidate_count",
    "source_record_only",
    "source_unknown_fields_preserved",
    "source_candidate_input_created",
    "source_candidate_ordering_created",
    "source_action_selection_created",
    "source_direct_command_created",
    "source_execution_created",
    "source_outcome_observation_created",
    "source_memory_write_created",
    "source_semantic_vision_created",
    "source_object_recognition_created",
    "source_active_focus_created",
    "source_capability_map_created",
    "source_raw_tool_access_created",
    "source_production_behavior_created",
    "source_learning_claim_created",
    "source_consciousness_claim_created",
}

REQUIRED_CATALOG_FIELDS = {
    "catalog_id",
    "catalog_scope",
    "catalog_authority",
    "source_catalog_created",
    "source_reference_link_only",
    "visual_spatial_source",
    "qingyin_bridge_capability_map_sources",
    "new_visual_record_created_in_this_package",
    "capability_map_created_in_this_package",
    "capability_map_mutated_in_this_package",
    "raw_tool_access_created_in_this_package",
    "external_tool_called_in_this_package",
}

REQUIRED_VISUAL_SOURCE_FIELDS = {
    "source_available",
    "source_family",
    "record_type",
    "boundary_index",
    "spatial_grounding_status",
    "observation_id",
    "front_symbol",
    "front_body_direction",
    "front_distance_forward",
    "visible_cells_only",
    "symbolic_first_person_viewport_only",
    "semantic_vision_created",
    "object_recognition_created",
    "active_focus_created",
    "source_reference_only",
}

REQUIRED_CAPABILITY_SOURCE_FIELDS = {
    "source_available",
    "source_family",
    "record_type",
    "boundary_index",
    "front_symbol",
    "visible_object_id",
    "visible_object_kind",
    "capability_ids",
    "available_capability_ids",
    "capability_map_created_by_source",
    "capability_map_created_in_this_package",
    "capability_map_mutated_in_this_package",
    "raw_tool_access_created",
    "execution_created",
    "source_reference_only",
}

REQUIRED_PERCEPTION_LINK_FIELDS = {
    "source_evidence_candidate_id",
    "evidence_lane",
    "evidence_kind",
    "source_field",
    "source_value",
    "target_source_family",
    "target_source_record_type",
    "target_source_boundary_index",
    "target_source_reference",
    "link_status",
    "linked_to_existing_source_reference",
    "resolved_source_reference",
    "resolved_grounding_created",
    "unknown_preserved",
    "unresolved_unknown_reason",
    "source_reference_only",
    "semantic_vision_created",
    "object_recognition_created",
    "active_focus_created",
    "new_visual_record_created",
    "candidate_input_created",
    "action_preparation_created",
    "capability_authority_created",
}

REQUIRED_CAPABILITY_LINK_FIELDS = {
    "source_evidence_candidate_id",
    "evidence_lane",
    "evidence_kind",
    "source_field",
    "source_value",
    "target_source_family",
    "target_source_record_type",
    "target_source_boundary_index",
    "target_source_reference",
    "link_status",
    "linked_to_existing_source_reference",
    "resolved_source_reference",
    "linked_capability_id",
    "linked_capability_available",
    "capability_reference_resolved",
    "unknown_preserved",
    "unresolved_unknown_reason",
    "source_reference_only",
    "grounded_capability_binding_created",
    "capability_map_created",
    "capability_map_mutated",
    "raw_tool_access_created",
    "external_tool_called",
    "candidate_input_created",
    "action_preparation_created",
    "execution_created",
}

REQUIRED_UNKNOWN_FIELDS = {
    "unknown_preservation_id",
    "preservation_scope",
    "preservation_authority",
    "unresolved_unknowns_preserved",
    "unresolved_link_count",
    "unresolved_link_items",
    "unknown_values_invented",
    "semantic_vision_created",
    "object_recognition_created",
    "active_focus_created",
    "grounded_capability_binding_created",
    "capability_map_created",
    "candidate_input_created",
    "requires_future_perception_grounding",
    "requires_future_capability_grounding",
}

REQUIRED_REPORT_FIELDS = {
    "report_id",
    "report_scope",
    "report_authority",
    "phase2_source_link_report_created",
    "phase2_purpose",
    "reads_phase2_entry_report",
    "links_perception_evidence_to_existing_sources",
    "links_capability_evidence_to_existing_sources",
    "preserves_unresolved_unknowns",
    "record_only_report",
    "source_reference_link_only",
    "semantic_vision_created",
    "object_recognition_created",
    "active_focus_created",
    "capability_map_created",
    "capability_map_mutated",
    "raw_tool_access_created",
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
    "record_only_source_link_report",
    "reads_phase2_entry_report_only",
    "existing_source_references_read",
    "unresolved_unknowns_preserved_in_this_package",
)

FALSE_CONTAINMENT_FIELDS = (
    "semantic_vision_created_in_this_package",
    "object_recognition_created_in_this_package",
    "active_focus_created_in_this_package",
    "focus_applied_in_this_package",
    "new_visual_record_created_in_this_package",
    "grounded_capability_binding_created_in_this_package",
    "capability_map_created_in_this_package",
    "capability_map_mutated_in_this_package",
    "raw_tool_access_created_in_this_package",
    "external_tool_called_in_this_package",
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
    "predictor_read_enabled_in_this_package",
    "predictor_influence_enabled_in_this_package",
    "predictor_modified_in_this_package",
    "direct_endocrine_feed_in_this_package",
    "direct_tendency_feed_in_this_package",
    "production_behavior_created_in_this_package",
    "learning_claim",
    "proof_of_learning_claim",
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
    "semantic_vision_created",
    "object_recognition_created",
    "active_focus_created",
    "focus_applied",
    "new_visual_record_created",
    "grounded_capability_binding_created",
    "capability_map_created",
    "capability_map_mutated",
    "raw_tool_access_created",
    "external_tool_called",
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


def build_phase2_perception_capability_evidence_source_link_record(
    phase2_entry_report_record: dict[str, Any] | None = None,
    existing_evidence_source_catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_record = deepcopy(phase2_entry_report_record) if phase2_entry_report_record is not None else _default_source()
    source = _source_summary(source_record)
    catalog = (
        deepcopy(existing_evidence_source_catalog)
        if existing_evidence_source_catalog is not None
        else _default_source_catalog()
    )
    perception_links = _build_perception_links(source_record, catalog)
    capability_links = _build_capability_links(source_record, catalog)
    unresolved = _build_unresolved_unknown_preservation(source, perception_links, capability_links)
    report = _build_source_link_report(source)

    return {
        "source_link_report_id": f"phase2_source_link_{source['scenario_id']}_demo_001",
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_phase2_entry_report": source,
        "existing_evidence_source_catalog": catalog,
        "perception_evidence_source_links": perception_links,
        "capability_evidence_source_links": capability_links,
        "unresolved_unknown_preservation": unresolved,
        "source_link_report": report,
        "authority_containment": _build_authority_containment(),
        "boundary_audit": _build_boundary_audit(),
        "human_summary": {
            "what_was_built": "A record-only Phase2 evidence source-link report.",
            "what_changed": (
                "The b184 perception and capability evidence candidates are now connected to "
                "existing visual-spatial and Qingyin Bridge capability-map source references."
            ),
            "what_is_blocked": (
                "No semantic vision, object recognition, active focus, capability-map creation or mutation, "
                "candidate input, action selection, execution, memory write, production behavior, or "
                "learning/consciousness claim is created."
            ),
            "plain_result": "Phase2 can now point evidence candidates at existing source records, while unresolved parts stay unknown.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_phase2_perception_capability_evidence_source_link_record(
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
    if not _non_empty_string(record.get("source_link_report_id")):
        errors.append("source_link_report_id_empty")

    source = _as_dict(record.get("source_phase2_entry_report"), errors, "source_phase2_entry_report")
    catalog = _as_dict(record.get("existing_evidence_source_catalog"), errors, "existing_evidence_source_catalog")
    perception_links = record.get("perception_evidence_source_links")
    capability_links = record.get("capability_evidence_source_links")
    unknown = _as_dict(record.get("unresolved_unknown_preservation"), errors, "unresolved_unknown_preservation")
    report = _as_dict(record.get("source_link_report"), errors, "source_link_report")
    containment = _as_dict(record.get("authority_containment"), errors, "authority_containment")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_catalog(catalog, errors)
    _validate_perception_links(perception_links, source, catalog, errors)
    _validate_capability_links(capability_links, source, catalog, errors)
    _validate_unknown(unknown, perception_links, capability_links, errors)
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
        "source_link_report_created": report.get("phase2_source_link_report_created") is True,
        "perception_source_links_created": _perception_links_created(perception_links),
        "capability_source_links_created": _capability_links_created(capability_links),
        "visual_spatial_source_reference_available": _visual_source_available(catalog),
        "capability_map_source_reference_available": _capability_sources_available(catalog),
        "unresolved_unknowns_preserved": _unresolved_unknowns_preserved(unknown),
        "reach_front_capability_reference_linked": _reach_front_capability_reference_linked(capability_links),
        "candidate_input_blocked": _candidate_input_blocked(report, containment, audit, blocked),
        "candidate_ordering_blocked": _candidate_ordering_blocked(report, containment, audit, blocked),
        "action_selection_blocked": _action_selection_blocked(report, containment, audit, blocked),
        "direct_command_blocked": _direct_command_blocked(report, containment, audit, blocked),
        "execution_blocked": _execution_blocked(report, containment, audit, blocked),
        "outcome_observation_blocked": _outcome_observation_blocked(report, containment, audit, blocked),
        "memory_write_blocked": _memory_write_blocked(report, containment, audit, blocked),
        "semantic_vision_blocked": _semantic_vision_blocked(report, containment, audit, blocked, perception_links),
        "capability_map_mutation_blocked": _capability_map_mutation_blocked(
            report,
            containment,
            audit,
            blocked,
            catalog,
            capability_links,
        ),
        "raw_tool_access_blocked": _raw_tool_access_blocked(report, containment, audit, blocked, catalog, capability_links),
        "predictor_use_blocked": _predictor_use_blocked(report, containment, audit, blocked),
        "direct_feed_blocked": _direct_feed_blocked(containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(report, containment, audit, blocked),
        "learning_claim_blocked": _learning_claim_blocked(report, containment, audit, blocked),
        "consciousness_claim_blocked": _consciousness_claim_blocked(report, containment, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_phase2_perception_capability_evidence_source_link_minimal_check() -> dict[str, Any]:
    source_records = run_phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal_check()[
        "valid_records"
    ]
    catalog = _default_source_catalog()
    valid_records = [
        build_phase2_perception_capability_evidence_source_link_record(source_record, catalog)
        for source_record in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [
        validate_phase2_perception_capability_evidence_source_link_record(record) for record in records
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
                "Links b184 Phase2 perception/capability evidence candidates to existing visual-spatial "
                "and Qingyin Bridge capability-map source references without creating grounding behavior."
            ),
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A Phase2 evidence source-link report.",
            "what_changed": "b184 evidence candidates can now point at existing visual-spatial and capability-map sources.",
            "what_is_blocked": (
                "No semantic vision, object recognition, active focus, capability-map mutation, candidate input, "
                "action selection, execution, memory write, production behavior, or proof/consciousness claim is created."
            ),
            "plain_result": "The repo now records where Phase2 should look for perception/capability evidence, without acting on it.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source_record: dict[str, Any]) -> dict[str, Any]:
    validation = validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(source_record)
    if not validation["valid"]:
        raise ValueError("phase2_entry_report_record must validate before evidence source linking")

    source = source_record["source_closed_phase1_substrate"]
    perception = source_record["perception_grounding_entry"]
    capability = source_record["capability_grounding_entry"]
    unknown = source_record["unknown_field_preservation"]
    report = source_record["phase2_entry_report"]
    return {
        "source_phase2_entry_report_id": source_record["phase2_entry_report_id"],
        "source_validated": True,
        "source_boundary_index": source_record["boundary_index_after"],
        "session_id": source["session_id"],
        "scenario_id": source["scenario_id"],
        "approved_purpose": source["approved_purpose"],
        "phase2_entry_report_created": report["phase2_entry_report_created"],
        "phase2_purpose": report["phase2_purpose"],
        "perception_evidence_candidate_count": perception["perception_evidence_candidate_count"],
        "capability_evidence_candidate_count": capability["capability_evidence_candidate_count"],
        "source_record_only": report["record_only_report"],
        "source_unknown_fields_preserved": unknown["unknown_fields_preserved"],
        "source_candidate_input_created": report["candidate_input_created"],
        "source_candidate_ordering_created": report["candidate_ordering_created"],
        "source_action_selection_created": report["action_selection_created"],
        "source_direct_command_created": report["direct_command_created"],
        "source_execution_created": report["execution_created"],
        "source_outcome_observation_created": report["outcome_observation_created"],
        "source_memory_write_created": report["memory_write_created"],
        "source_semantic_vision_created": perception["semantic_vision_created"],
        "source_object_recognition_created": perception["object_recognition_created"],
        "source_active_focus_created": perception["active_focus_created"],
        "source_capability_map_created": capability["capability_map_created"],
        "source_raw_tool_access_created": capability["raw_tool_access_created"],
        "source_production_behavior_created": report["production_behavior_created"],
        "source_learning_claim_created": report["learning_claim_created"],
        "source_consciousness_claim_created": report["consciousness_claim_created"],
    }


def _default_source_catalog() -> dict[str, Any]:
    visual_record = deepcopy(run_visual_spatial_grounding_minimal_check()["valid_record"])
    visual_validation = validate_visual_spatial_grounding_record(visual_record)
    if not visual_validation["valid"]:
        raise ValueError("visual_spatial_grounding source must validate before source linking")

    capability_records = deepcopy(run_qingyin_bridge_grounded_capability_map_minimal_check()["valid_records"])
    for record in capability_records:
        validation = validate_qingyin_bridge_grounded_capability_map_record(record)
        if not validation["valid"]:
            raise ValueError("qingyin_bridge_grounded_capability_map source must validate before source linking")

    return {
        "catalog_id": "phase2_existing_evidence_source_catalog_visual_spatial_qingyin_bridge_v0",
        "catalog_scope": "existing_repo_record_sources_only",
        "catalog_authority": "source_reference_catalog_only",
        "source_catalog_created": True,
        "source_reference_link_only": True,
        "visual_spatial_source": _visual_source_summary(visual_record),
        "qingyin_bridge_capability_map_sources": [
            _capability_map_source_summary(record) for record in capability_records
        ],
        "new_visual_record_created_in_this_package": False,
        "capability_map_created_in_this_package": False,
        "capability_map_mutated_in_this_package": False,
        "raw_tool_access_created_in_this_package": False,
        "external_tool_called_in_this_package": False,
    }


def _visual_source_summary(record: dict[str, Any]) -> dict[str, Any]:
    front = record["front_cell_spatial_summary"]
    scope = record["grounding_scope"]
    blocked = record["blocked_flags"]
    return {
        "source_available": True,
        "source_family": "visual_spatial_grounding_minimal",
        "record_type": record["record_type"],
        "boundary_index": record["boundary_index_after"],
        "spatial_grounding_status": record["spatial_grounding_status"],
        "observation_id": record["source_visual_observation"]["observation_id"],
        "front_symbol": front["front_symbol"],
        "front_body_direction": front["body_direction"],
        "front_distance_forward": front["distance_forward"],
        "visible_cells_only": scope["visible_cells_only"],
        "symbolic_first_person_viewport_only": scope["symbolic_first_person_viewport_only"],
        "semantic_vision_created": blocked["semantic_vision"],
        "object_recognition_created": blocked["object_recognition"],
        "active_focus_created": blocked["active_focus_applied"],
        "source_reference_only": True,
    }


def _capability_map_source_summary(record: dict[str, Any]) -> dict[str, Any]:
    visible = record["capability_map"]["visible_objects"][0]
    capabilities = record["capability_map"]["declared_capabilities"]
    return {
        "source_available": True,
        "source_family": "qingyin_bridge_grounded_capability_map_minimal",
        "record_type": record["record_type"],
        "boundary_index": record["boundary_index_after"],
        "front_symbol": visible["front_symbol"],
        "visible_object_id": visible["id"],
        "visible_object_kind": visible["object_kind"],
        "capability_ids": [capability["id"] for capability in capabilities],
        "available_capability_ids": [
            capability["id"] for capability in capabilities if capability["available"] is True
        ],
        "capability_map_created_by_source": record["capability_map"]["capability_map_created"],
        "capability_map_created_in_this_package": False,
        "capability_map_mutated_in_this_package": False,
        "raw_tool_access_created": record["blocked_flags"]["raw_api_access"],
        "execution_created": record["blocked_flags"]["sandbox_execution_created"],
        "source_reference_only": True,
    }


def _build_perception_links(source_record: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
    visual = catalog["visual_spatial_source"]
    links: list[dict[str, Any]] = []
    for candidate in source_record["perception_grounding_entry"]["perception_evidence_candidates"]:
        resolved = candidate["evidence_kind"] == "phase1_evidence_source_reference"
        links.append(
            {
                "source_evidence_candidate_id": candidate["evidence_candidate_id"],
                "evidence_lane": "perception",
                "evidence_kind": candidate["evidence_kind"],
                "source_field": candidate["source_field"],
                "source_value": candidate["source_value"],
                "target_source_family": visual["source_family"],
                "target_source_record_type": visual["record_type"],
                "target_source_boundary_index": visual["boundary_index"],
                "target_source_reference": visual["observation_id"],
                "link_status": (
                    "linked_existing_visual_spatial_source_reference"
                    if resolved
                    else "linked_visual_spatial_source_family_value_unresolved"
                ),
                "linked_to_existing_source_reference": True,
                "resolved_source_reference": resolved,
                "resolved_grounding_created": False,
                "unknown_preserved": True,
                "unresolved_unknown_reason": None
                if resolved
                else "observed_outcome_context_has_no_exact_visual_spatial_source_match",
                "source_reference_only": True,
                "semantic_vision_created": False,
                "object_recognition_created": False,
                "active_focus_created": False,
                "new_visual_record_created": False,
                "candidate_input_created": False,
                "action_preparation_created": False,
                "capability_authority_created": False,
            }
        )
    return links


def _build_capability_links(source_record: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, Any]]:
    capability_sources = catalog["qingyin_bridge_capability_map_sources"]
    links: list[dict[str, Any]] = []
    for candidate in source_record["capability_grounding_entry"]["capability_evidence_candidates"]:
        capability_id = _capability_id_for_candidate(candidate)
        source = _capability_source_for_id(capability_sources, capability_id)
        resolved = candidate["evidence_kind"] == "phase1_evidence_source_reference" or source is not None
        reference = _capability_source_reference(source) if source is not None else "qingyin_bridge_capability_map_sources"
        links.append(
            {
                "source_evidence_candidate_id": candidate["evidence_candidate_id"],
                "evidence_lane": "capability",
                "evidence_kind": candidate["evidence_kind"],
                "source_field": candidate["source_field"],
                "source_value": candidate["source_value"],
                "target_source_family": "qingyin_bridge_grounded_capability_map_minimal",
                "target_source_record_type": "qingyin_bridge_grounded_capability_map",
                "target_source_boundary_index": CAPABILITY_MAP_BOUNDARY_INDEX,
                "target_source_reference": reference,
                "link_status": (
                    "linked_existing_qingyin_bridge_capability_map_reference"
                    if resolved
                    else "linked_qingyin_bridge_source_family_value_unresolved"
                ),
                "linked_to_existing_source_reference": True,
                "resolved_source_reference": resolved,
                "linked_capability_id": capability_id,
                "linked_capability_available": None
                if source is None or capability_id is None
                else capability_id in source["available_capability_ids"],
                "capability_reference_resolved": source is not None,
                "unknown_preserved": True,
                "unresolved_unknown_reason": None
                if resolved
                else "closed_operation_context_has_no_exact_capability_map_binding",
                "source_reference_only": True,
                "grounded_capability_binding_created": False,
                "capability_map_created": False,
                "capability_map_mutated": False,
                "raw_tool_access_created": False,
                "external_tool_called": False,
                "candidate_input_created": False,
                "action_preparation_created": False,
                "execution_created": False,
            }
        )
    return links


def _capability_id_for_candidate(candidate: dict[str, Any]) -> str | None:
    if candidate["evidence_kind"] != "closed_operation_context":
        return None
    return OPERATION_TO_CAPABILITY_ID.get(candidate["source_value"])


def _capability_source_for_id(sources: list[dict[str, Any]], capability_id: str | None) -> dict[str, Any] | None:
    if capability_id is None:
        return None
    available_source = None
    fallback_source = None
    for source in sources:
        if capability_id not in source["capability_ids"]:
            continue
        fallback_source = fallback_source or source
        if capability_id in source["available_capability_ids"]:
            available_source = source
    return available_source or fallback_source


def _capability_source_reference(source: dict[str, Any] | None) -> str:
    if source is None:
        return "qingyin_bridge_capability_map_sources"
    return f"qingyin_bridge_capability_map:{source['front_symbol']}:{source['visible_object_id']}"


def _build_unresolved_unknown_preservation(
    source: dict[str, Any],
    perception_links: list[dict[str, Any]],
    capability_links: list[dict[str, Any]],
) -> dict[str, Any]:
    unresolved = [
        {
            "evidence_lane": link["evidence_lane"],
            "evidence_kind": link["evidence_kind"],
            "source_evidence_candidate_id": link["source_evidence_candidate_id"],
            "reason": link["unresolved_unknown_reason"],
        }
        for link in [*perception_links, *capability_links]
        if link["unresolved_unknown_reason"] is not None
    ]
    return {
        "unknown_preservation_id": f"phase2_source_link_unknown_preservation_{source['scenario_id']}_001",
        "preservation_scope": "phase2_perception_capability_source_link_report",
        "preservation_authority": "preserve_unresolved_source_links_do_not_invent_grounding",
        "unresolved_unknowns_preserved": True,
        "unresolved_link_count": len(unresolved),
        "unresolved_link_items": unresolved,
        "unknown_values_invented": False,
        "semantic_vision_created": False,
        "object_recognition_created": False,
        "active_focus_created": False,
        "grounded_capability_binding_created": False,
        "capability_map_created": False,
        "candidate_input_created": False,
        "requires_future_perception_grounding": True,
        "requires_future_capability_grounding": True,
    }


def _build_source_link_report(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "report_id": f"phase2_source_link_report_{source['scenario_id']}_001",
        "report_scope": "same_session_sandbox_record_only",
        "report_authority": "phase2_evidence_source_link_report_only",
        "phase2_source_link_report_created": True,
        "phase2_purpose": PHASE2_PURPOSE,
        "reads_phase2_entry_report": True,
        "links_perception_evidence_to_existing_sources": True,
        "links_capability_evidence_to_existing_sources": True,
        "preserves_unresolved_unknowns": True,
        "record_only_report": True,
        "source_reference_link_only": True,
        "semantic_vision_created": False,
        "object_recognition_created": False,
        "active_focus_created": False,
        "capability_map_created": False,
        "capability_map_mutated": False,
        "raw_tool_access_created": False,
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
        "boundary_audit_id": "phase2_evidence_source_link_b185_boundary_audit",
        "triggered": True,
        "boundary_number": 185,
        "package_id": PACKAGE_ID,
    }
    audit.update({field: False for field in FALSE_AUDIT_FIELDS})
    return audit


def _default_source() -> dict[str, Any]:
    return deepcopy(
        run_phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal_check()["valid_records"][0]
    )


def _invalid_records(reach: dict[str, Any], wait: dict[str, Any], probe: dict[str, Any]) -> list[dict[str, Any]]:
    invalid: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[Any, ...], value: Any) -> None:
        record = deepcopy(source)
        record["source_link_report_id"] = f"{record['source_link_report_id']}__invalid_{label}"
        _set_path(record, path, value)
        invalid.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "phase2_wrong_source_link")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), "2026-06-09-b186")
    mutate(reach, "source_not_validated", ("source_phase2_entry_report", "source_validated"), False)
    mutate(reach, "source_wrong_boundary", ("source_phase2_entry_report", "source_boundary_index"), "2026-06-09-b183")
    mutate(reach, "source_report_not_created", ("source_phase2_entry_report", "phase2_entry_report_created"), False)
    mutate(reach, "source_candidate_input", ("source_phase2_entry_report", "source_candidate_input_created"), True)
    mutate(wait, "catalog_visual_unavailable", ("existing_evidence_source_catalog", "visual_spatial_source", "source_available"), False)
    mutate(wait, "catalog_visual_wrong_boundary", ("existing_evidence_source_catalog", "visual_spatial_source", "boundary_index"), "2026-06-09-b110")
    mutate(wait, "catalog_visual_semantic", ("existing_evidence_source_catalog", "visual_spatial_source", "semantic_vision_created"), True)
    mutate(probe, "catalog_capability_unavailable", ("existing_evidence_source_catalog", "qingyin_bridge_capability_map_sources", 0, "source_available"), False)
    mutate(probe, "catalog_capability_wrong_boundary", ("existing_evidence_source_catalog", "qingyin_bridge_capability_map_sources", 0, "boundary_index"), "2026-06-09-b134")
    mutate(probe, "catalog_capability_map_created", ("existing_evidence_source_catalog", "capability_map_created_in_this_package"), True)
    mutate(probe, "catalog_capability_map_mutated", ("existing_evidence_source_catalog", "capability_map_mutated_in_this_package"), True)
    mutate(probe, "catalog_raw_tool_access", ("existing_evidence_source_catalog", "raw_tool_access_created_in_this_package"), True)
    mutate(wait, "perception_count_wrong", ("perception_evidence_source_links", 0, "evidence_lane"), "wrong")
    mutate(wait, "perception_unlinked", ("perception_evidence_source_links", 0, "linked_to_existing_source_reference"), False)
    mutate(wait, "perception_wrong_target", ("perception_evidence_source_links", 0, "target_source_family"), "semantic_vision")
    mutate(wait, "perception_semantic", ("perception_evidence_source_links", 0, "semantic_vision_created"), True)
    mutate(wait, "perception_object", ("perception_evidence_source_links", 0, "object_recognition_created"), True)
    mutate(wait, "perception_focus", ("perception_evidence_source_links", 0, "active_focus_created"), True)
    mutate(wait, "perception_new_visual", ("perception_evidence_source_links", 0, "new_visual_record_created"), True)
    mutate(wait, "perception_candidate_input", ("perception_evidence_source_links", 0, "candidate_input_created"), True)
    mutate(wait, "perception_action_preparation", ("perception_evidence_source_links", 0, "action_preparation_created"), True)
    mutate(probe, "capability_count_wrong", ("capability_evidence_source_links", 0, "evidence_lane"), "wrong")
    mutate(probe, "capability_unlinked", ("capability_evidence_source_links", 0, "linked_to_existing_source_reference"), False)
    mutate(probe, "capability_wrong_target", ("capability_evidence_source_links", 0, "target_source_family"), "raw_tool")
    mutate(reach, "capability_wrong_reach_id", ("capability_evidence_source_links", 0, "linked_capability_id"), "sandbox.body.step_forward")
    mutate(probe, "capability_binding", ("capability_evidence_source_links", 0, "grounded_capability_binding_created"), True)
    mutate(probe, "capability_map", ("capability_evidence_source_links", 0, "capability_map_created"), True)
    mutate(probe, "capability_map_mutated", ("capability_evidence_source_links", 0, "capability_map_mutated"), True)
    mutate(probe, "capability_raw_tool", ("capability_evidence_source_links", 0, "raw_tool_access_created"), True)
    mutate(probe, "capability_execution", ("capability_evidence_source_links", 0, "execution_created"), True)
    mutate(reach, "unknown_not_preserved", ("unresolved_unknown_preservation", "unresolved_unknowns_preserved"), False)
    mutate(reach, "unknown_invented", ("unresolved_unknown_preservation", "unknown_values_invented"), True)
    mutate(reach, "report_not_created", ("source_link_report", "phase2_source_link_report_created"), False)
    mutate(reach, "report_wrong_authority", ("source_link_report", "report_authority"), "candidate_input")
    mutate(wait, "report_candidate_input", ("source_link_report", "candidate_input_created"), True)
    mutate(wait, "report_candidate_ordering", ("source_link_report", "candidate_ordering_created"), True)
    mutate(wait, "report_selected_action", ("authority_containment", "selected_action_created_in_this_package"), True)
    mutate(wait, "report_direct_command", ("source_link_report", "direct_command_created"), True)
    mutate(wait, "report_execution", ("source_link_report", "execution_created"), True)
    mutate(wait, "report_outcome_observation", ("source_link_report", "outcome_observation_created"), True)
    mutate(probe, "report_memory_write", ("source_link_report", "memory_write_created"), True)
    mutate(probe, "predictor_read", ("authority_containment", "predictor_read_enabled_in_this_package"), True)
    mutate(probe, "direct_endocrine", ("authority_containment", "direct_endocrine_feed_in_this_package"), True)
    mutate(probe, "production_behavior", ("source_link_report", "production_behavior_created"), True)
    mutate(probe, "learning_claim", ("source_link_report", "learning_claim_created"), True)
    mutate(probe, "consciousness_claim", ("source_link_report", "consciousness_claim_created"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalid


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(source, REQUIRED_SOURCE_FIELDS, errors, "source")
    _validate_no_extra(source, REQUIRED_SOURCE_FIELDS, errors, "source")
    _validate_expected(
        source,
        {
            "source_validated": True,
            "source_boundary_index": SOURCE_BOUNDARY_INDEX,
            "phase2_entry_report_created": True,
            "phase2_purpose": PHASE2_PURPOSE,
            "perception_evidence_candidate_count": EXPECTED_PERCEPTION_LINK_COUNT,
            "capability_evidence_candidate_count": EXPECTED_CAPABILITY_LINK_COUNT,
            "source_record_only": True,
            "source_unknown_fields_preserved": True,
            "source_candidate_input_created": False,
            "source_candidate_ordering_created": False,
            "source_action_selection_created": False,
            "source_direct_command_created": False,
            "source_execution_created": False,
            "source_outcome_observation_created": False,
            "source_memory_write_created": False,
            "source_semantic_vision_created": False,
            "source_object_recognition_created": False,
            "source_active_focus_created": False,
            "source_capability_map_created": False,
            "source_raw_tool_access_created": False,
            "source_production_behavior_created": False,
            "source_learning_claim_created": False,
            "source_consciousness_claim_created": False,
        },
        errors,
        "source",
    )
    for field in ("source_phase2_entry_report_id", "session_id", "scenario_id", "approved_purpose"):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")


def _validate_catalog(catalog: dict[str, Any], errors: list[str]) -> None:
    _validate_required(catalog, REQUIRED_CATALOG_FIELDS, errors, "catalog")
    _validate_no_extra(catalog, REQUIRED_CATALOG_FIELDS, errors, "catalog")
    _validate_expected(
        catalog,
        {
            "catalog_scope": "existing_repo_record_sources_only",
            "catalog_authority": "source_reference_catalog_only",
            "source_catalog_created": True,
            "source_reference_link_only": True,
            "new_visual_record_created_in_this_package": False,
            "capability_map_created_in_this_package": False,
            "capability_map_mutated_in_this_package": False,
            "raw_tool_access_created_in_this_package": False,
            "external_tool_called_in_this_package": False,
        },
        errors,
        "catalog",
    )
    if not _non_empty_string(catalog.get("catalog_id")):
        errors.append("catalog_id_empty")
    _validate_visual_source(
        _as_dict(catalog.get("visual_spatial_source"), errors, "catalog_visual_spatial_source"),
        errors,
    )
    sources = catalog.get("qingyin_bridge_capability_map_sources")
    if not isinstance(sources, list):
        errors.append("catalog_capability_sources_not_list")
        return
    if len(sources) != 3:
        errors.append("catalog_capability_sources_count_wrong")
    for index, source in enumerate(sources):
        _validate_capability_source(_as_dict(source, errors, f"catalog_capability_source_{index}"), errors)


def _validate_visual_source(source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(source, REQUIRED_VISUAL_SOURCE_FIELDS, errors, "visual_source")
    _validate_no_extra(source, REQUIRED_VISUAL_SOURCE_FIELDS, errors, "visual_source")
    _validate_expected(
        source,
        {
            "source_available": True,
            "source_family": "visual_spatial_grounding_minimal",
            "record_type": "visual_spatial_grounding",
            "boundary_index": VISUAL_SPATIAL_BOUNDARY_INDEX,
            "spatial_grounding_status": "completed_body_relative_visual_spatial_trace",
            "front_body_direction": "front",
            "front_distance_forward": 1,
            "visible_cells_only": True,
            "symbolic_first_person_viewport_only": True,
            "semantic_vision_created": False,
            "object_recognition_created": False,
            "active_focus_created": False,
            "source_reference_only": True,
        },
        errors,
        "visual_source",
    )
    for field in ("observation_id", "front_symbol"):
        if not _non_empty_string(source.get(field)):
            errors.append(f"visual_source_{field}_empty")


def _validate_capability_source(source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(source, REQUIRED_CAPABILITY_SOURCE_FIELDS, errors, "capability_source")
    _validate_no_extra(source, REQUIRED_CAPABILITY_SOURCE_FIELDS, errors, "capability_source")
    _validate_expected(
        source,
        {
            "source_available": True,
            "source_family": "qingyin_bridge_grounded_capability_map_minimal",
            "record_type": "qingyin_bridge_grounded_capability_map",
            "boundary_index": CAPABILITY_MAP_BOUNDARY_INDEX,
            "visible_object_id": "sandbox.front_cell",
            "visible_object_kind": "symbolic_front_cell",
            "capability_map_created_by_source": True,
            "capability_map_created_in_this_package": False,
            "capability_map_mutated_in_this_package": False,
            "raw_tool_access_created": False,
            "execution_created": False,
            "source_reference_only": True,
        },
        errors,
        "capability_source",
    )
    if not _non_empty_string(source.get("front_symbol")):
        errors.append("capability_source_front_symbol_empty")
    if not isinstance(source.get("capability_ids"), list) or len(source["capability_ids"]) != 4:
        errors.append("capability_source_capability_ids_wrong")
    if not isinstance(source.get("available_capability_ids"), list):
        errors.append("capability_source_available_capability_ids_not_list")


def _validate_perception_links(
    links: Any,
    source: dict[str, Any],
    catalog: dict[str, Any],
    errors: list[str],
) -> None:
    if not isinstance(links, list):
        errors.append("perception_links_not_list")
        return
    if len(links) != EXPECTED_PERCEPTION_LINK_COUNT:
        errors.append("perception_links_count_wrong")
    by_kind = _by_kind(links)
    expected_kinds = {"observed_outcome_context", "phase1_evidence_source_reference"}
    if set(by_kind) != expected_kinds:
        errors.append("perception_links_kinds_wrong")
    visual = catalog.get("visual_spatial_source", {})
    for link in links:
        _validate_perception_link(_as_dict(link, errors, "perception_link"), visual, errors)
    if source.get("perception_evidence_candidate_count") != len(links):
        errors.append("perception_links_do_not_match_source_count")


def _validate_perception_link(link: dict[str, Any], visual: dict[str, Any], errors: list[str]) -> None:
    _validate_required(link, REQUIRED_PERCEPTION_LINK_FIELDS, errors, "perception_link")
    _validate_no_extra(link, REQUIRED_PERCEPTION_LINK_FIELDS, errors, "perception_link")
    _validate_expected(
        link,
        {
            "evidence_lane": "perception",
            "target_source_family": "visual_spatial_grounding_minimal",
            "target_source_record_type": "visual_spatial_grounding",
            "target_source_boundary_index": VISUAL_SPATIAL_BOUNDARY_INDEX,
            "target_source_reference": visual.get("observation_id"),
            "linked_to_existing_source_reference": True,
            "resolved_grounding_created": False,
            "unknown_preserved": True,
            "source_reference_only": True,
            "semantic_vision_created": False,
            "object_recognition_created": False,
            "active_focus_created": False,
            "new_visual_record_created": False,
            "candidate_input_created": False,
            "action_preparation_created": False,
            "capability_authority_created": False,
        },
        errors,
        "perception_link",
    )
    if link.get("evidence_kind") == "observed_outcome_context":
        _validate_expected(
            link,
            {
                "source_field": "source_observed_outcome_context",
                "resolved_source_reference": False,
                "link_status": "linked_visual_spatial_source_family_value_unresolved",
            },
            errors,
            "perception_link_observed",
        )
        if not _non_empty_string(link.get("unresolved_unknown_reason")):
            errors.append("perception_observed_unknown_reason_empty")
    elif link.get("evidence_kind") == "phase1_evidence_source_reference":
        _validate_expected(
            link,
            {
                "source_field": "source_evidence_source_set_id",
                "resolved_source_reference": True,
                "link_status": "linked_existing_visual_spatial_source_reference",
                "unresolved_unknown_reason": None,
            },
            errors,
            "perception_link_phase1_reference",
        )
    else:
        errors.append("perception_link_evidence_kind_unknown")
    for field in ("source_evidence_candidate_id", "source_value"):
        if not _non_empty_string(link.get(field)):
            errors.append(f"perception_link_{field}_empty")


def _validate_capability_links(
    links: Any,
    source: dict[str, Any],
    catalog: dict[str, Any],
    errors: list[str],
) -> None:
    if not isinstance(links, list):
        errors.append("capability_links_not_list")
        return
    if len(links) != EXPECTED_CAPABILITY_LINK_COUNT:
        errors.append("capability_links_count_wrong")
    by_kind = _by_kind(links)
    expected_kinds = {"closed_operation_context", "phase1_evidence_source_reference"}
    if set(by_kind) != expected_kinds:
        errors.append("capability_links_kinds_wrong")
    capability_sources = catalog.get("qingyin_bridge_capability_map_sources", [])
    for link in links:
        _validate_capability_link(_as_dict(link, errors, "capability_link"), source, capability_sources, errors)
    if source.get("capability_evidence_candidate_count") != len(links):
        errors.append("capability_links_do_not_match_source_count")


def _validate_capability_link(
    link: dict[str, Any],
    source: dict[str, Any],
    capability_sources: list[dict[str, Any]],
    errors: list[str],
) -> None:
    _validate_required(link, REQUIRED_CAPABILITY_LINK_FIELDS, errors, "capability_link")
    _validate_no_extra(link, REQUIRED_CAPABILITY_LINK_FIELDS, errors, "capability_link")
    _validate_expected(
        link,
        {
            "evidence_lane": "capability",
            "target_source_family": "qingyin_bridge_grounded_capability_map_minimal",
            "target_source_record_type": "qingyin_bridge_grounded_capability_map",
            "target_source_boundary_index": CAPABILITY_MAP_BOUNDARY_INDEX,
            "linked_to_existing_source_reference": True,
            "unknown_preserved": True,
            "source_reference_only": True,
            "grounded_capability_binding_created": False,
            "capability_map_created": False,
            "capability_map_mutated": False,
            "raw_tool_access_created": False,
            "external_tool_called": False,
            "candidate_input_created": False,
            "action_preparation_created": False,
            "execution_created": False,
        },
        errors,
        "capability_link",
    )
    if link.get("evidence_kind") == "closed_operation_context":
        expected_capability_id = OPERATION_TO_CAPABILITY_ID.get(link.get("source_value"))
        source_match = _capability_source_for_id(capability_sources, expected_capability_id)
        resolved = source_match is not None
        _validate_expected(
            link,
            {
                "source_field": "source_closed_operation_context",
                "linked_capability_id": expected_capability_id,
                "resolved_source_reference": resolved,
                "capability_reference_resolved": resolved,
                "linked_capability_available": None
                if source_match is None or expected_capability_id is None
                else expected_capability_id in source_match["available_capability_ids"],
                "unresolved_unknown_reason": None
                if resolved
                else "closed_operation_context_has_no_exact_capability_map_binding",
            },
            errors,
            "capability_link_closed_operation",
        )
    elif link.get("evidence_kind") == "phase1_evidence_source_reference":
        _validate_expected(
            link,
            {
                "source_field": "source_evidence_source_set_id",
                "resolved_source_reference": True,
                "linked_capability_id": None,
                "linked_capability_available": None,
                "capability_reference_resolved": False,
                "unresolved_unknown_reason": None,
            },
            errors,
            "capability_link_phase1_reference",
        )
    else:
        errors.append("capability_link_evidence_kind_unknown")
    if source.get("scenario_id") == "item_reachable_feedback_prioritizes_reach" and link.get("evidence_kind") == "closed_operation_context":
        if link.get("linked_capability_id") != "sandbox.body.reach_front":
            errors.append("capability_link_reach_front_id_wrong")
        if link.get("linked_capability_available") is not True:
            errors.append("capability_link_reach_front_not_available")
    for field in ("source_evidence_candidate_id", "source_value", "target_source_reference", "link_status"):
        if not _non_empty_string(link.get(field)):
            errors.append(f"capability_link_{field}_empty")


def _validate_unknown(
    unknown: dict[str, Any],
    perception_links: Any,
    capability_links: Any,
    errors: list[str],
) -> None:
    _validate_required(unknown, REQUIRED_UNKNOWN_FIELDS, errors, "unknown")
    _validate_no_extra(unknown, REQUIRED_UNKNOWN_FIELDS, errors, "unknown")
    links = [*(perception_links if isinstance(perception_links, list) else []), *(capability_links if isinstance(capability_links, list) else [])]
    expected_count = sum(1 for link in links if isinstance(link, dict) and link.get("unresolved_unknown_reason") is not None)
    _validate_expected(
        unknown,
        {
            "preservation_scope": "phase2_perception_capability_source_link_report",
            "preservation_authority": "preserve_unresolved_source_links_do_not_invent_grounding",
            "unresolved_unknowns_preserved": True,
            "unresolved_link_count": expected_count,
            "unknown_values_invented": False,
            "semantic_vision_created": False,
            "object_recognition_created": False,
            "active_focus_created": False,
            "grounded_capability_binding_created": False,
            "capability_map_created": False,
            "candidate_input_created": False,
            "requires_future_perception_grounding": True,
            "requires_future_capability_grounding": True,
        },
        errors,
        "unknown",
    )
    if not _non_empty_string(unknown.get("unknown_preservation_id")):
        errors.append("unknown_preservation_id_empty")
    items = unknown.get("unresolved_link_items")
    if not isinstance(items, list):
        errors.append("unknown_unresolved_link_items_not_list")
    elif len(items) != expected_count:
        errors.append("unknown_unresolved_link_items_count_wrong")


def _validate_report(report: dict[str, Any], errors: list[str]) -> None:
    _validate_required(report, REQUIRED_REPORT_FIELDS, errors, "report")
    _validate_no_extra(report, REQUIRED_REPORT_FIELDS, errors, "report")
    _validate_expected(
        report,
        {
            "report_scope": "same_session_sandbox_record_only",
            "report_authority": "phase2_evidence_source_link_report_only",
            "phase2_source_link_report_created": True,
            "phase2_purpose": PHASE2_PURPOSE,
            "reads_phase2_entry_report": True,
            "links_perception_evidence_to_existing_sources": True,
            "links_capability_evidence_to_existing_sources": True,
            "preserves_unresolved_unknowns": True,
            "record_only_report": True,
            "source_reference_link_only": True,
            "semantic_vision_created": False,
            "object_recognition_created": False,
            "active_focus_created": False,
            "capability_map_created": False,
            "capability_map_mutated": False,
            "raw_tool_access_created": False,
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
    _validate_required(containment, required, errors, "containment")
    _validate_no_extra(containment, required, errors, "containment")
    _validate_expected(containment, {field: True for field in TRUE_CONTAINMENT_FIELDS}, errors, "containment")
    _validate_expected(containment, {field: False for field in FALSE_CONTAINMENT_FIELDS}, errors, "containment")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    required = {"boundary_audit_id", "triggered", "boundary_number", "package_id"} | set(FALSE_AUDIT_FIELDS)
    _validate_required(audit, required, errors, "audit")
    _validate_no_extra(audit, required, errors, "audit")
    _validate_expected(
        audit,
        {"triggered": True, "boundary_number": 185, "package_id": PACKAGE_ID},
        errors,
        "audit",
    )
    _validate_expected(audit, {field: False for field in FALSE_AUDIT_FIELDS}, errors, "audit")
    if not _non_empty_string(audit.get("boundary_audit_id")):
        errors.append("audit_boundary_audit_id_empty")


def _validate_human(human: dict[str, Any], errors: list[str]) -> None:
    required = {"what_was_built", "what_changed", "what_is_blocked", "plain_result"}
    _validate_required(human, required, errors, "human_summary")
    _validate_no_extra(human, required, errors, "human_summary")
    for field in required:
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked(blocked: dict[str, Any], errors: list[str]) -> None:
    _validate_required(blocked, BLOCKED_FLAGS, errors, "blocked")
    _validate_no_extra(blocked, BLOCKED_FLAGS, errors, "blocked")
    _validate_expected(blocked, {field: False for field in BLOCKED_FLAGS}, errors, "blocked")


def _summary(results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in results if result["valid"]]
    return {
        "source_link_result_count": len(results),
        "valid_source_link_count": len(valid),
        "invalid_source_link_count": len(results) - len(valid),
        "source_link_report_created_count": sum(1 for result in valid if result["source_link_report_created"]),
        "perception_source_links_created_count": sum(1 for result in valid if result["perception_source_links_created"]),
        "capability_source_links_created_count": sum(1 for result in valid if result["capability_source_links_created"]),
        "visual_spatial_source_reference_available_count": sum(
            1 for result in valid if result["visual_spatial_source_reference_available"]
        ),
        "capability_map_source_reference_available_count": sum(
            1 for result in valid if result["capability_map_source_reference_available"]
        ),
        "unresolved_unknowns_preserved_count": sum(1 for result in valid if result["unresolved_unknowns_preserved"]),
        "reach_front_capability_reference_linked_count": sum(
            1 for result in valid if result["reach_front_capability_reference_linked"]
        ),
        "wait_unknown_source_link_count": sum(
            1 for result in valid if result["scenario_id"] == "item_not_afforded_blocks_feedback_priority"
        ),
        "probe_unknown_source_link_count": sum(
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
        "capability_map_mutation_blocked_count": sum(
            1 for result in valid if result["capability_map_mutation_blocked"]
        ),
        "raw_tool_access_blocked_count": sum(1 for result in valid if result["raw_tool_access_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "production_behavior_blocked_count": sum(1 for result in valid if result["production_behavior_blocked"]),
        "learning_claim_blocked_count": sum(1 for result in valid if result["learning_claim_blocked"]),
        "consciousness_claim_blocked_count": sum(1 for result in valid if result["consciousness_claim_blocked"]),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["valid_source_link_count"] == 3
        and summary["invalid_source_link_count"] == EXPECTED_INVALID_SOURCE_LINK_COUNT
        and summary["source_link_report_created_count"] == 3
        and summary["perception_source_links_created_count"] == 3
        and summary["capability_source_links_created_count"] == 3
        and summary["visual_spatial_source_reference_available_count"] == 3
        and summary["capability_map_source_reference_available_count"] == 3
        and summary["unresolved_unknowns_preserved_count"] == 3
        and summary["reach_front_capability_reference_linked_count"] == 1
        and summary["candidate_input_blocked_count"] == 3
        and summary["candidate_ordering_blocked_count"] == 3
        and summary["action_selection_blocked_count"] == 3
        and summary["direct_command_blocked_count"] == 3
        and summary["execution_blocked_count"] == 3
        and summary["outcome_observation_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["semantic_vision_blocked_count"] == 3
        and summary["capability_map_mutation_blocked_count"] == 3
        and summary["raw_tool_access_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["learning_claim_blocked_count"] == 3
        and summary["consciousness_claim_blocked_count"] == 3
        and summary["boundary_audit_passed_count"] == 3
    )


def _perception_links_created(links: Any) -> bool:
    return (
        isinstance(links, list)
        and len(links) == EXPECTED_PERCEPTION_LINK_COUNT
        and all(link.get("linked_to_existing_source_reference") is True for link in links if isinstance(link, dict))
        and all(link.get("source_reference_only") is True for link in links if isinstance(link, dict))
    )


def _capability_links_created(links: Any) -> bool:
    return (
        isinstance(links, list)
        and len(links) == EXPECTED_CAPABILITY_LINK_COUNT
        and all(link.get("linked_to_existing_source_reference") is True for link in links if isinstance(link, dict))
        and all(link.get("source_reference_only") is True for link in links if isinstance(link, dict))
    )


def _visual_source_available(catalog: dict[str, Any]) -> bool:
    visual = catalog.get("visual_spatial_source")
    return isinstance(visual, dict) and visual.get("source_available") is True


def _capability_sources_available(catalog: dict[str, Any]) -> bool:
    sources = catalog.get("qingyin_bridge_capability_map_sources")
    return isinstance(sources, list) and bool(sources) and all(source.get("source_available") is True for source in sources)


def _unresolved_unknowns_preserved(unknown: dict[str, Any]) -> bool:
    return (
        unknown.get("unresolved_unknowns_preserved") is True
        and unknown.get("unknown_values_invented") is False
        and unknown.get("semantic_vision_created") is False
        and unknown.get("grounded_capability_binding_created") is False
    )


def _reach_front_capability_reference_linked(links: Any) -> bool:
    if not isinstance(links, list):
        return False
    return any(
        isinstance(link, dict)
        and link.get("evidence_kind") == "closed_operation_context"
        and link.get("source_value") == "reach_front_item"
        and link.get("linked_capability_id") == "sandbox.body.reach_front"
        and link.get("linked_capability_available") is True
        and link.get("capability_reference_resolved") is True
        for link in links
    )


def _candidate_input_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        report.get("candidate_input_created") is False
        and report.get("action_preparation_created") is False
        and containment.get("candidate_input_created_in_this_package") is False
        and audit.get("candidate_input_created") is False
        and blocked.get("candidate_input_created") is False
    )


def _candidate_ordering_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        report.get("candidate_ordering_created") is False
        and containment.get("candidate_ordering_created_in_this_package") is False
        and containment.get("candidate_reordering_created_in_this_package") is False
        and audit.get("candidate_ordering_created") is False
        and audit.get("candidate_reordering_created") is False
        and blocked.get("candidate_ordering_created") is False
        and blocked.get("candidate_reordering_created") is False
        and blocked.get("candidate_scores_changed") is False
        and blocked.get("next_cycle_candidate_ordering_changed") is False
    )


def _action_selection_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        report.get("action_selection_created") is False
        and containment.get("selected_action_created_in_this_package") is False
        and containment.get("final_action_created_in_this_package") is False
        and audit.get("selected_action_created") is False
        and audit.get("final_action_created") is False
        and blocked.get("selected_action_created") is False
        and blocked.get("final_action_created") is False
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
    return (
        report.get("memory_write_created") is False
        and containment.get("working_memory_update_created_in_this_package") is False
        and containment.get("persistent_memory_write_created_in_this_package") is False
        and containment.get("memory_admission_created_in_this_package") is False
        and containment.get("retention_write_created_in_this_package") is False
        and audit.get("working_memory_update_created") is False
        and audit.get("persistent_memory_write_created") is False
        and audit.get("memory_admission_created") is False
        and audit.get("retention_write_created") is False
        and blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
    )


def _semantic_vision_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
    perception_links: Any,
) -> bool:
    links_clean = isinstance(perception_links, list) and all(
        isinstance(link, dict)
        and link.get("semantic_vision_created") is False
        and link.get("object_recognition_created") is False
        and link.get("active_focus_created") is False
        and link.get("new_visual_record_created") is False
        for link in perception_links
    )
    return (
        links_clean
        and report.get("semantic_vision_created") is False
        and report.get("object_recognition_created") is False
        and report.get("active_focus_created") is False
        and containment.get("semantic_vision_created_in_this_package") is False
        and containment.get("object_recognition_created_in_this_package") is False
        and containment.get("active_focus_created_in_this_package") is False
        and audit.get("semantic_vision_created") is False
        and audit.get("object_recognition_created") is False
        and audit.get("active_focus_created") is False
        and blocked.get("semantic_vision_created") is False
        and blocked.get("object_recognition_created") is False
        and blocked.get("active_focus_created") is False
    )


def _capability_map_mutation_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
    catalog: dict[str, Any],
    capability_links: Any,
) -> bool:
    link_clean = isinstance(capability_links, list) and all(
        isinstance(link, dict)
        and link.get("grounded_capability_binding_created") is False
        and link.get("capability_map_created") is False
        and link.get("capability_map_mutated") is False
        for link in capability_links
    )
    return (
        link_clean
        and report.get("capability_map_created") is False
        and report.get("capability_map_mutated") is False
        and catalog.get("capability_map_created_in_this_package") is False
        and catalog.get("capability_map_mutated_in_this_package") is False
        and containment.get("grounded_capability_binding_created_in_this_package") is False
        and containment.get("capability_map_created_in_this_package") is False
        and containment.get("capability_map_mutated_in_this_package") is False
        and audit.get("grounded_capability_binding_created") is False
        and audit.get("capability_map_created") is False
        and audit.get("capability_map_mutated") is False
        and blocked.get("grounded_capability_binding_created") is False
        and blocked.get("capability_map_created") is False
        and blocked.get("capability_map_mutated") is False
    )


def _raw_tool_access_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
    catalog: dict[str, Any],
    capability_links: Any,
) -> bool:
    link_clean = isinstance(capability_links, list) and all(
        isinstance(link, dict)
        and link.get("raw_tool_access_created") is False
        and link.get("external_tool_called") is False
        for link in capability_links
    )
    return (
        link_clean
        and report.get("raw_tool_access_created") is False
        and catalog.get("raw_tool_access_created_in_this_package") is False
        and catalog.get("external_tool_called_in_this_package") is False
        and containment.get("raw_tool_access_created_in_this_package") is False
        and containment.get("external_tool_called_in_this_package") is False
        and audit.get("raw_tool_access_created") is False
        and audit.get("external_tool_called") is False
        and blocked.get("raw_tool_access_created") is False
        and blocked.get("external_tool_called") is False
    )


def _predictor_use_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        report.get("predictor_used") is False
        and containment.get("predictor_read_enabled_in_this_package") is False
        and containment.get("predictor_influence_enabled_in_this_package") is False
        and containment.get("predictor_modified_in_this_package") is False
        and audit.get("predictor_read_enabled") is False
        and audit.get("predictor_influence_enabled") is False
        and audit.get("predictor_modified") is False
        and blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False
    )


def _direct_feed_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        containment.get("direct_endocrine_feed_in_this_package") is False
        and containment.get("direct_tendency_feed_in_this_package") is False
        and audit.get("direct_endocrine_feed") is False
        and audit.get("direct_tendency_feed") is False
        and blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False
    )


def _production_behavior_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        report.get("production_behavior_created") is False
        and containment.get("production_behavior_created_in_this_package") is False
        and audit.get("production_behavior_created") is False
        and audit.get("runtime_behavior_leak") is False
        and blocked.get("production_behavior_changed") is False
        and blocked.get("runtime_behavior_changed") is False
    )


def _learning_claim_blocked(
    report: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        report.get("learning_claim_created") is False
        and containment.get("learning_claim") is False
        and containment.get("proof_of_learning_claim") is False
        and audit.get("proof_of_learning_claim") is False
        and audit.get("long_term_learning_claim") is False
        and blocked.get("learning_claim") is False
        and blocked.get("proof_of_learning_claim") is False
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


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 185
        and all(audit.get(field) is False for field in FALSE_AUDIT_FIELDS)
    )


def _by_kind(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item.get("evidence_kind"): item for item in items if isinstance(item, dict)}


def _validate_required(container: dict[str, Any], required: set[str], errors: list[str], prefix: str) -> None:
    missing = sorted(required - set(container))
    for field in missing:
        errors.append(f"{prefix + '_' if prefix else ''}{field}_missing")


def _validate_no_extra(container: dict[str, Any], allowed: set[str], errors: list[str], prefix: str) -> None:
    extra = sorted(set(container) - allowed)
    for field in extra:
        errors.append(f"{prefix + '_' if prefix else ''}{field}_unexpected")


def _validate_expected(
    container: dict[str, Any],
    expected: dict[str, Any],
    errors: list[str],
    prefix: str,
) -> None:
    for field, value in expected.items():
        if container.get(field) != value:
            errors.append(f"{prefix}_{field}_wrong")


def _as_dict(value: Any, errors: list[str], label: str) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{label}_not_dict")
    return {}


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _set_path(record: dict[str, Any], path: tuple[Any, ...], value: Any) -> None:
    target: Any = record
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
