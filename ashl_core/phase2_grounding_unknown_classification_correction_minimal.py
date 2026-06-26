"""Correct b185 unresolved operation-source classification for Phase2."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .phase2_perception_capability_evidence_source_link_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    run_phase2_perception_capability_evidence_source_link_minimal_check,
    validate_phase2_perception_capability_evidence_source_link_record,
)


COMMAND = "run-phase2-grounding-unknown-classification-correction-minimal-check"
FLOW = "phase2_grounding_unknown_classification_correction_minimal_v0"
PACKAGE_ID = "PKG-Phase2-GroundingUnknownClassificationCorrection-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b185"
BOUNDARY_INDEX_AFTER = "2026-06-09-b186"
RECORD_TYPE = "phase2_grounding_unknown_classification_correction_minimal"
PHASE2_PURPOSE = "perception_and_capability_grounding"
PHASE4_DEFERRED_TARGET = "phase4_endocrine_tendency_settling"

DEFERRED_SOURCE_VALUES = {
    "wait_or_observe": {
        "scenario_id": "item_not_afforded_blocks_feedback_priority",
        "phase4_deferred_reference": "phase4_endocrine_tendency_settling:wait_or_observe",
        "plain_reason": "wait_or_observe is a settling or patience-style state cue, not a body capability binding.",
    },
    "observe_or_alternative_probe": {
        "scenario_id": "mismatch_feedback_outranks_retry_tendency",
        "phase4_deferred_reference": "phase4_endocrine_tendency_settling:observe_or_alternative_probe",
        "plain_reason": "observe_or_alternative_probe is an uncertainty-settling cue, not a body capability binding.",
    },
}

BLOCKED_FLAGS = {
    "semantic_vision_created",
    "object_recognition_created",
    "active_focus_created",
    "capability_binding_created",
    "capability_map_created",
    "capability_map_mutated",
    "raw_tool_access_created",
    "external_tool_called",
    "endocrine_feed_created",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "tendency_state_changed",
    "state_settling_applied",
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
    "persistent_memory_write",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "production_behavior_changed",
    "runtime_behavior_changed",
    "learning_claim",
    "proof_of_learning_claim",
    "consciousness_claim",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "correction_report_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_b185_records",
    "deferred_source_classification",
    "authority_containment",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}

REQUIRED_SOURCE_FIELDS = {
    "source_link_report_id",
    "source_validated",
    "source_boundary_index",
    "scenario_id",
    "approved_purpose",
    "source_value",
    "previous_evidence_lane",
    "previous_evidence_kind",
    "previous_link_status",
    "previous_unresolved_unknown_reason",
    "previous_linked_capability_id",
    "previous_capability_reference_resolved",
    "source_reference_only",
    "source_candidate_input_created",
    "source_action_selection_created",
    "source_memory_write_created",
    "source_endocrine_feed_created",
    "source_production_behavior_created",
}

REQUIRED_CLASSIFICATION_FIELDS = {
    "deferred_source_classification_created",
    "classification_scope",
    "classification_authority",
    "phase2_purpose",
    "source_values_reclassified",
    "classification_items",
    "wait_or_observe_marked_not_capability",
    "observe_or_alternative_probe_marked_not_capability",
    "phase4_deferred_reference_created",
    "unknown_items_not_forced_into_capability",
    "capability_binding_created",
    "capability_map_created",
    "semantic_vision_created",
    "endocrine_feed_created",
    "direct_tendency_feed_created",
    "candidate_input_created",
    "action_selection_created",
    "memory_write_created",
    "record_only_correction",
}

REQUIRED_ITEM_FIELDS = {
    "source_value",
    "source_scenario_id",
    "previous_classification",
    "corrected_classification",
    "deferred_to_phase",
    "phase4_deferred_reference",
    "plain_reason",
    "is_perception_source",
    "is_capability_binding",
    "is_phase4_state_settling_signal",
    "unknown_for_capability_line_after_correction",
    "forced_into_capability",
    "capability_binding_created",
    "capability_map_created",
    "semantic_vision_created",
    "endocrine_feed_created",
    "direct_tendency_feed_created",
    "candidate_input_created",
    "action_selection_created",
    "memory_write_created",
    "record_only",
}

TRUE_CONTAINMENT_FIELDS = (
    "same_session_only",
    "sandbox_only",
    "record_only_correction",
    "reads_b185_source_link_reports",
    "creates_deferred_classification_reference",
    "unknown_items_not_forced_into_capability",
)

FALSE_CONTAINMENT_FIELDS = (
    "semantic_vision_created_in_this_package",
    "object_recognition_created_in_this_package",
    "active_focus_created_in_this_package",
    "capability_binding_created_in_this_package",
    "capability_map_created_in_this_package",
    "capability_map_mutated_in_this_package",
    "raw_tool_access_created_in_this_package",
    "external_tool_called_in_this_package",
    "endocrine_feed_created_in_this_package",
    "direct_endocrine_feed_in_this_package",
    "direct_tendency_feed_in_this_package",
    "tendency_state_changed_in_this_package",
    "state_settling_applied_in_this_package",
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
    "retention_write_created_in_this_package",
    "predictor_read_enabled_in_this_package",
    "predictor_influence_enabled_in_this_package",
    "predictor_modified_in_this_package",
    "production_behavior_created_in_this_package",
    "learning_claim",
    "proof_of_learning_claim",
    "consciousness_claim",
)

FALSE_AUDIT_FIELDS = (
    "production_behavior_created",
    "runtime_behavior_leak",
    "semantic_vision_created",
    "object_recognition_created",
    "active_focus_created",
    "capability_binding_created",
    "capability_map_created",
    "capability_map_mutated",
    "raw_tool_access_created",
    "external_tool_called",
    "endocrine_feed_created",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "tendency_state_changed",
    "state_settling_applied",
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
    "retention_write_created",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "proof_of_learning_claim",
    "long_term_learning_claim",
    "consciousness_claim",
)


def build_phase2_grounding_unknown_classification_correction_record(
    source_link_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    source_records = deepcopy(source_link_records) if source_link_records is not None else _default_source_records()
    source_summaries = _source_summaries(source_records)
    classification = _build_deferred_source_classification(source_summaries)

    return {
        "correction_report_id": "phase2_grounding_unknown_classification_correction_demo_001",
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_b185_records": source_summaries,
        "deferred_source_classification": classification,
        "authority_containment": _build_authority_containment(),
        "boundary_audit": _build_boundary_audit(),
        "human_summary": {
            "what_was_built": "A record-only correction report for b185 unresolved operation classifications.",
            "what_changed": (
                "wait_or_observe and observe_or_alternative_probe are now marked as not capability bindings "
                "and deferred to the future Phase4 endocrine/tendency/settling line."
            ),
            "what_is_blocked": (
                "No endocrine feed, tendency feed, candidate input, action selection, memory write, "
                "production behavior, or learning/consciousness claim is created."
            ),
            "plain_result": "Phase2 stops treating wait/probe settling cues as capability unknowns.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_phase2_grounding_unknown_classification_correction_record(
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
    if not _non_empty_string(record.get("correction_report_id")):
        errors.append("correction_report_id_empty")

    sources = record.get("source_b185_records")
    classification = _as_dict(record.get("deferred_source_classification"), errors, "deferred_source_classification")
    containment = _as_dict(record.get("authority_containment"), errors, "authority_containment")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_sources(sources, errors)
    _validate_classification(classification, errors)
    _validate_containment(containment, errors)
    _validate_audit(audit, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "deferred_source_classification_created": classification.get("deferred_source_classification_created") is True,
        "wait_or_observe_marked_not_capability": classification.get("wait_or_observe_marked_not_capability") is True,
        "observe_or_alternative_probe_marked_not_capability": (
            classification.get("observe_or_alternative_probe_marked_not_capability") is True
        ),
        "phase4_deferred_reference_created": classification.get("phase4_deferred_reference_created") is True,
        "unknown_items_not_forced_into_capability": (
            classification.get("unknown_items_not_forced_into_capability") is True
            and _items_not_forced_into_capability(classification)
        ),
        "no_endocrine_feed": _no_endocrine_feed(classification, containment, audit, blocked),
        "no_candidate_input": _no_candidate_input(classification, containment, audit, blocked),
        "no_action_selection": _no_action_selection(classification, containment, audit, blocked),
        "no_memory_write": _no_memory_write(classification, containment, audit, blocked),
        "no_production_behavior": _no_production_behavior(containment, audit, blocked),
        "no_learning_or_consciousness_claim": _no_learning_or_consciousness_claim(containment, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_phase2_grounding_unknown_classification_correction_minimal_check() -> dict[str, Any]:
    valid_record = build_phase2_grounding_unknown_classification_correction_record()
    records = [valid_record, *_invalid_records(valid_record)]
    validation_results = [
        validate_phase2_grounding_unknown_classification_correction_record(record) for record in records
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
                "Corrects b185 unresolved wait/probe operation labels from capability unknowns "
                "to Phase4-deferred endocrine/tendency/settling cues without applying any feed."
            ),
        },
        "valid_records": [valid_record],
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A Phase2 grounding unknown classification correction report.",
            "what_changed": "wait_or_observe and observe_or_alternative_probe are not treated as capability bindings.",
            "what_is_blocked": (
                "No endocrine feed, candidate input, action selection, memory write, production behavior, "
                "or learning/consciousness claim is created."
            ),
            "plain_result": "The wait/probe cues are deferred to future Phase4 state settling instead of being forced into capability.",
        },
        "valid_result_count": len(valid_results),
    }


def _default_source_records() -> list[dict[str, Any]]:
    return deepcopy(run_phase2_perception_capability_evidence_source_link_minimal_check()["valid_records"])


def _source_summaries(source_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for record in source_records:
        validation = validate_phase2_perception_capability_evidence_source_link_record(record)
        if not validation["valid"]:
            raise ValueError("b185 source-link records must validate before classification correction")
        source = record["source_phase2_entry_report"]
        for link in record["capability_evidence_source_links"]:
            if link["evidence_kind"] != "closed_operation_context":
                continue
            if link["source_value"] not in DEFERRED_SOURCE_VALUES:
                continue
            summaries.append(
                {
                    "source_link_report_id": record["source_link_report_id"],
                    "source_validated": True,
                    "source_boundary_index": record["boundary_index_after"],
                    "scenario_id": source["scenario_id"],
                    "approved_purpose": source["approved_purpose"],
                    "source_value": link["source_value"],
                    "previous_evidence_lane": link["evidence_lane"],
                    "previous_evidence_kind": link["evidence_kind"],
                    "previous_link_status": link["link_status"],
                    "previous_unresolved_unknown_reason": link["unresolved_unknown_reason"],
                    "previous_linked_capability_id": link["linked_capability_id"],
                    "previous_capability_reference_resolved": link["capability_reference_resolved"],
                    "source_reference_only": link["source_reference_only"],
                    "source_candidate_input_created": link["candidate_input_created"],
                    "source_action_selection_created": link["action_preparation_created"],
                    "source_memory_write_created": record["source_link_report"]["memory_write_created"],
                    "source_endocrine_feed_created": False,
                    "source_production_behavior_created": record["source_link_report"]["production_behavior_created"],
                }
            )
    source_values = {summary["source_value"] for summary in summaries}
    if source_values != set(DEFERRED_SOURCE_VALUES):
        raise ValueError("b185 source-link records must contain wait_or_observe and observe_or_alternative_probe")
    return sorted(summaries, key=lambda summary: summary["source_value"])


def _build_deferred_source_classification(sources: list[dict[str, Any]]) -> dict[str, Any]:
    items = [_classification_item(source) for source in sources]
    return {
        "deferred_source_classification_created": True,
        "classification_scope": "phase2_grounding_unknown_classification_correction",
        "classification_authority": "record_only_reclassification_not_phase4_feed",
        "phase2_purpose": PHASE2_PURPOSE,
        "source_values_reclassified": [item["source_value"] for item in items],
        "classification_items": items,
        "wait_or_observe_marked_not_capability": _item_marked_not_capability(items, "wait_or_observe"),
        "observe_or_alternative_probe_marked_not_capability": _item_marked_not_capability(
            items,
            "observe_or_alternative_probe",
        ),
        "phase4_deferred_reference_created": all(
            _non_empty_string(item["phase4_deferred_reference"]) for item in items
        ),
        "unknown_items_not_forced_into_capability": all(item["forced_into_capability"] is False for item in items),
        "capability_binding_created": False,
        "capability_map_created": False,
        "semantic_vision_created": False,
        "endocrine_feed_created": False,
        "direct_tendency_feed_created": False,
        "candidate_input_created": False,
        "action_selection_created": False,
        "memory_write_created": False,
        "record_only_correction": True,
    }


def _classification_item(source: dict[str, Any]) -> dict[str, Any]:
    spec = DEFERRED_SOURCE_VALUES[source["source_value"]]
    return {
        "source_value": source["source_value"],
        "source_scenario_id": source["scenario_id"],
        "previous_classification": "capability_unknown",
        "corrected_classification": "not_capability_binding",
        "deferred_to_phase": PHASE4_DEFERRED_TARGET,
        "phase4_deferred_reference": spec["phase4_deferred_reference"],
        "plain_reason": spec["plain_reason"],
        "is_perception_source": False,
        "is_capability_binding": False,
        "is_phase4_state_settling_signal": True,
        "unknown_for_capability_line_after_correction": False,
        "forced_into_capability": False,
        "capability_binding_created": False,
        "capability_map_created": False,
        "semantic_vision_created": False,
        "endocrine_feed_created": False,
        "direct_tendency_feed_created": False,
        "candidate_input_created": False,
        "action_selection_created": False,
        "memory_write_created": False,
        "record_only": True,
    }


def _build_authority_containment() -> dict[str, bool]:
    containment = {field: True for field in TRUE_CONTAINMENT_FIELDS}
    containment.update({field: False for field in FALSE_CONTAINMENT_FIELDS})
    return containment


def _build_boundary_audit() -> dict[str, Any]:
    audit = {
        "boundary_audit_id": "phase2_grounding_unknown_classification_correction_b186_boundary_audit",
        "triggered": True,
        "boundary_number": 186,
        "package_id": PACKAGE_ID,
    }
    audit.update({field: False for field in FALSE_AUDIT_FIELDS})
    return audit


def _invalid_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalid: list[dict[str, Any]] = []

    def mutate(label: str, path: tuple[Any, ...], value: Any) -> None:
        record = deepcopy(valid)
        record["correction_report_id"] = f"{record['correction_report_id']}__invalid_{label}"
        _set_path(record, path, value)
        invalid.append(record)

    mutate("bad_record_type", ("record_type",), "phase2_wrong_correction")
    mutate("wrong_boundary_after", ("boundary_index_after",), "2026-06-09-b187")
    mutate("source_not_validated", ("source_b185_records", 0, "source_validated"), False)
    mutate("source_wrong_boundary", ("source_b185_records", 0, "source_boundary_index"), "2026-06-09-b184")
    mutate("source_wrong_lane", ("source_b185_records", 0, "previous_evidence_lane"), "perception")
    mutate("source_capability_resolved", ("source_b185_records", 0, "previous_capability_reference_resolved"), True)
    mutate("classification_not_created", ("deferred_source_classification", "deferred_source_classification_created"), False)
    mutate("missing_wait_flag", ("deferred_source_classification", "wait_or_observe_marked_not_capability"), False)
    mutate(
        "missing_probe_flag",
        ("deferred_source_classification", "observe_or_alternative_probe_marked_not_capability"),
        False,
    )
    mutate("missing_phase4_reference", ("deferred_source_classification", "phase4_deferred_reference_created"), False)
    mutate("forced_into_capability", ("deferred_source_classification", "classification_items", 0, "forced_into_capability"), True)
    mutate("wrong_corrected_classification", ("deferred_source_classification", "classification_items", 0, "corrected_classification"), "capability_unknown")
    mutate("wrong_deferred_phase", ("deferred_source_classification", "classification_items", 0, "deferred_to_phase"), "phase2_capability_grounding")
    mutate("endocrine_feed", ("deferred_source_classification", "classification_items", 0, "endocrine_feed_created"), True)
    mutate("direct_tendency_feed", ("authority_containment", "direct_tendency_feed_in_this_package"), True)
    mutate("candidate_input", ("deferred_source_classification", "candidate_input_created"), True)
    mutate("action_selection", ("authority_containment", "selected_action_created_in_this_package"), True)
    mutate("memory_write", ("deferred_source_classification", "memory_write_created"), True)
    mutate("capability_binding", ("deferred_source_classification", "capability_binding_created"), True)
    mutate("semantic_vision", ("deferred_source_classification", "semantic_vision_created"), True)
    mutate("production_behavior", ("authority_containment", "production_behavior_created_in_this_package"), True)
    mutate("proof_claim", ("authority_containment", "proof_of_learning_claim"), True)
    mutate("empty_summary", ("human_summary", "plain_result"), "")
    return invalid


def _validate_sources(sources: Any, errors: list[str]) -> None:
    if not isinstance(sources, list):
        errors.append("source_b185_records_not_list")
        return
    if len(sources) != 2:
        errors.append("source_b185_records_count_wrong")
    source_values = {source.get("source_value") for source in sources if isinstance(source, dict)}
    if source_values != set(DEFERRED_SOURCE_VALUES):
        errors.append("source_b185_values_wrong")
    for source in sources:
        _validate_source(_as_dict(source, errors, "source_b185_record"), errors)


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    _validate_required(source, REQUIRED_SOURCE_FIELDS, errors, "source")
    _validate_no_extra(source, REQUIRED_SOURCE_FIELDS, errors, "source")
    source_value = source.get("source_value")
    expected_scenario = DEFERRED_SOURCE_VALUES.get(source_value, {}).get("scenario_id")
    _validate_expected(
        source,
        {
            "source_validated": True,
            "source_boundary_index": SOURCE_BOUNDARY_INDEX,
            "scenario_id": expected_scenario,
            "previous_evidence_lane": "capability",
            "previous_evidence_kind": "closed_operation_context",
            "previous_link_status": "linked_qingyin_bridge_source_family_value_unresolved",
            "previous_unresolved_unknown_reason": "closed_operation_context_has_no_exact_capability_map_binding",
            "previous_linked_capability_id": None,
            "previous_capability_reference_resolved": False,
            "source_reference_only": True,
            "source_candidate_input_created": False,
            "source_action_selection_created": False,
            "source_memory_write_created": False,
            "source_endocrine_feed_created": False,
            "source_production_behavior_created": False,
        },
        errors,
        "source",
    )
    for field in ("source_link_report_id", "approved_purpose"):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")


def _validate_classification(classification: dict[str, Any], errors: list[str]) -> None:
    _validate_required(classification, REQUIRED_CLASSIFICATION_FIELDS, errors, "classification")
    _validate_no_extra(classification, REQUIRED_CLASSIFICATION_FIELDS, errors, "classification")
    _validate_expected(
        classification,
        {
            "deferred_source_classification_created": True,
            "classification_scope": "phase2_grounding_unknown_classification_correction",
            "classification_authority": "record_only_reclassification_not_phase4_feed",
            "phase2_purpose": PHASE2_PURPOSE,
            "source_values_reclassified": sorted(DEFERRED_SOURCE_VALUES),
            "wait_or_observe_marked_not_capability": True,
            "observe_or_alternative_probe_marked_not_capability": True,
            "phase4_deferred_reference_created": True,
            "unknown_items_not_forced_into_capability": True,
            "capability_binding_created": False,
            "capability_map_created": False,
            "semantic_vision_created": False,
            "endocrine_feed_created": False,
            "direct_tendency_feed_created": False,
            "candidate_input_created": False,
            "action_selection_created": False,
            "memory_write_created": False,
            "record_only_correction": True,
        },
        errors,
        "classification",
    )
    items = classification.get("classification_items")
    if not isinstance(items, list):
        errors.append("classification_items_not_list")
        return
    if len(items) != 2:
        errors.append("classification_items_count_wrong")
    item_values = {item.get("source_value") for item in items if isinstance(item, dict)}
    if item_values != set(DEFERRED_SOURCE_VALUES):
        errors.append("classification_item_values_wrong")
    for item in items:
        _validate_classification_item(_as_dict(item, errors, "classification_item"), errors)


def _validate_classification_item(item: dict[str, Any], errors: list[str]) -> None:
    _validate_required(item, REQUIRED_ITEM_FIELDS, errors, "classification_item")
    _validate_no_extra(item, REQUIRED_ITEM_FIELDS, errors, "classification_item")
    spec = DEFERRED_SOURCE_VALUES.get(item.get("source_value"), {})
    _validate_expected(
        item,
        {
            "source_scenario_id": spec.get("scenario_id"),
            "previous_classification": "capability_unknown",
            "corrected_classification": "not_capability_binding",
            "deferred_to_phase": PHASE4_DEFERRED_TARGET,
            "phase4_deferred_reference": spec.get("phase4_deferred_reference"),
            "plain_reason": spec.get("plain_reason"),
            "is_perception_source": False,
            "is_capability_binding": False,
            "is_phase4_state_settling_signal": True,
            "unknown_for_capability_line_after_correction": False,
            "forced_into_capability": False,
            "capability_binding_created": False,
            "capability_map_created": False,
            "semantic_vision_created": False,
            "endocrine_feed_created": False,
            "direct_tendency_feed_created": False,
            "candidate_input_created": False,
            "action_selection_created": False,
            "memory_write_created": False,
            "record_only": True,
        },
        errors,
        "classification_item",
    )


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
        {"triggered": True, "boundary_number": 186, "package_id": PACKAGE_ID},
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
        "classification_correction_result_count": len(results),
        "valid_classification_correction_count": len(valid),
        "invalid_classification_correction_count": len(results) - len(valid),
        "deferred_source_classification_created_count": sum(
            1 for result in valid if result["deferred_source_classification_created"]
        ),
        "wait_or_observe_marked_not_capability_count": sum(
            1 for result in valid if result["wait_or_observe_marked_not_capability"]
        ),
        "observe_or_alternative_probe_marked_not_capability_count": sum(
            1 for result in valid if result["observe_or_alternative_probe_marked_not_capability"]
        ),
        "phase4_deferred_reference_created_count": sum(
            1 for result in valid if result["phase4_deferred_reference_created"]
        ),
        "unknown_items_not_forced_into_capability_count": sum(
            1 for result in valid if result["unknown_items_not_forced_into_capability"]
        ),
        "no_endocrine_feed_count": sum(1 for result in valid if result["no_endocrine_feed"]),
        "no_candidate_input_count": sum(1 for result in valid if result["no_candidate_input"]),
        "no_action_selection_count": sum(1 for result in valid if result["no_action_selection"]),
        "no_memory_write_count": sum(1 for result in valid if result["no_memory_write"]),
        "no_production_behavior_count": sum(1 for result in valid if result["no_production_behavior"]),
        "no_learning_or_consciousness_claim_count": sum(
            1 for result in valid if result["no_learning_or_consciousness_claim"]
        ),
        "boundary_audit_passed_count": sum(1 for result in valid if result["boundary_audit_passed"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["valid_classification_correction_count"] == 1
        and summary["invalid_classification_correction_count"] == 23
        and summary["deferred_source_classification_created_count"] == 1
        and summary["wait_or_observe_marked_not_capability_count"] == 1
        and summary["observe_or_alternative_probe_marked_not_capability_count"] == 1
        and summary["phase4_deferred_reference_created_count"] == 1
        and summary["unknown_items_not_forced_into_capability_count"] == 1
        and summary["no_endocrine_feed_count"] == 1
        and summary["no_candidate_input_count"] == 1
        and summary["no_action_selection_count"] == 1
        and summary["no_memory_write_count"] == 1
        and summary["no_production_behavior_count"] == 1
        and summary["no_learning_or_consciousness_claim_count"] == 1
        and summary["boundary_audit_passed_count"] == 1
    )


def _item_marked_not_capability(items: list[dict[str, Any]], source_value: str) -> bool:
    return any(
        item["source_value"] == source_value
        and item["corrected_classification"] == "not_capability_binding"
        and item["is_capability_binding"] is False
        and item["deferred_to_phase"] == PHASE4_DEFERRED_TARGET
        for item in items
    )


def _items_not_forced_into_capability(classification: dict[str, Any]) -> bool:
    items = classification.get("classification_items")
    return isinstance(items, list) and all(
        isinstance(item, dict)
        and item.get("forced_into_capability") is False
        and item.get("is_capability_binding") is False
        and item.get("corrected_classification") == "not_capability_binding"
        for item in items
    )


def _no_endocrine_feed(
    classification: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    items = classification.get("classification_items")
    item_clean = isinstance(items, list) and all(
        isinstance(item, dict)
        and item.get("endocrine_feed_created") is False
        and item.get("direct_tendency_feed_created") is False
        for item in items
    )
    return (
        item_clean
        and classification.get("endocrine_feed_created") is False
        and classification.get("direct_tendency_feed_created") is False
        and containment.get("endocrine_feed_created_in_this_package") is False
        and containment.get("direct_endocrine_feed_in_this_package") is False
        and containment.get("direct_tendency_feed_in_this_package") is False
        and containment.get("tendency_state_changed_in_this_package") is False
        and containment.get("state_settling_applied_in_this_package") is False
        and audit.get("endocrine_feed_created") is False
        and audit.get("direct_endocrine_feed") is False
        and audit.get("direct_tendency_feed") is False
        and audit.get("tendency_state_changed") is False
        and audit.get("state_settling_applied") is False
        and blocked.get("endocrine_feed_created") is False
        and blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False
    )


def _no_candidate_input(
    classification: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        classification.get("candidate_input_created") is False
        and containment.get("candidate_input_created_in_this_package") is False
        and audit.get("candidate_input_created") is False
        and blocked.get("candidate_input_created") is False
    )


def _no_action_selection(
    classification: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        classification.get("action_selection_created") is False
        and containment.get("selected_action_created_in_this_package") is False
        and containment.get("final_action_created_in_this_package") is False
        and containment.get("direct_command_created_in_this_package") is False
        and containment.get("execution_created_in_this_package") is False
        and audit.get("selected_action_created") is False
        and audit.get("final_action_created") is False
        and audit.get("direct_command_created") is False
        and audit.get("execution_created") is False
        and blocked.get("selected_action_created") is False
        and blocked.get("execution_created") is False
    )


def _no_memory_write(
    classification: dict[str, Any],
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        classification.get("memory_write_created") is False
        and containment.get("working_memory_update_created_in_this_package") is False
        and containment.get("persistent_memory_write_created_in_this_package") is False
        and containment.get("retention_write_created_in_this_package") is False
        and audit.get("working_memory_update_created") is False
        and audit.get("persistent_memory_write_created") is False
        and audit.get("retention_write_created") is False
        and blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
    )


def _no_production_behavior(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        containment.get("production_behavior_created_in_this_package") is False
        and audit.get("production_behavior_created") is False
        and audit.get("runtime_behavior_leak") is False
        and blocked.get("production_behavior_changed") is False
        and blocked.get("runtime_behavior_changed") is False
    )


def _no_learning_or_consciousness_claim(
    containment: dict[str, Any],
    audit: dict[str, Any],
    blocked: dict[str, Any],
) -> bool:
    return (
        containment.get("learning_claim") is False
        and containment.get("proof_of_learning_claim") is False
        and containment.get("consciousness_claim") is False
        and audit.get("proof_of_learning_claim") is False
        and audit.get("long_term_learning_claim") is False
        and audit.get("consciousness_claim") is False
        and blocked.get("learning_claim") is False
        and blocked.get("proof_of_learning_claim") is False
        and blocked.get("consciousness_claim") is False
    )


def _boundary_audit_passed(audit: dict[str, Any]) -> bool:
    return (
        audit.get("triggered") is True
        and audit.get("boundary_number") == 186
        and all(audit.get(field) is False for field in FALSE_AUDIT_FIELDS)
    )


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
