"""Cross-check completed and unfinished Phase2-Phase10 capabilities."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any


COMMAND = "run-phase2-to-phase10-completed-capability-cross-check-minimal-check"
FLOW = "phase2_to_phase10_completed_capability_cross_check_minimal_v0"
PACKAGE_ID = "PKG-Phase2ToPhase10-CompletedCapabilityCrossCheck-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b186"
BOUNDARY_INDEX_AFTER = "2026-06-09-b187"
RECORD_TYPE = "phase2_to_phase10_completed_capability_cross_check_minimal"

SOURCE_DOCS = {
    "capability_inventory": "docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md",
    "capability_matrix": "docs/phase0_capability_matrix.md",
    "status": "docs/phase0_status.md",
    "line_index": "docs/phase0_line_document_index.md",
    "boundary_index": "docs/current_boundary_index.md",
    "growth_plan": "docs/phase1_to_phase5_growth_substrate_plan.md",
}

SOURCE_DOC_REQUIREMENTS = {
    "capability_inventory": (
        "This file records what the repository can actually run or produce after Boundary Index `2026-06-09-b188`.",
        "b186 corrects wait/probe operation labels",
        "b187 creates a docs-backed Phase2-to-Phase10 completed capability cross-check report",
        "b188 adds a structural refactor map and read-only checker",
        "## Not Present Yet",
    ),
    "capability_matrix": (
        "phase2 closed phase1 substrate perception capability grounding entry minimal",
        "phase2 perception capability evidence source link minimal",
        "phase2 grounding unknown classification correction minimal",
        "phase2 to phase10 completed capability cross-check minimal",
        "structural refactor map minimal",
    ),
    "status": (
        "Current version: `Boundary Index Version: 2026-06-09-b188`",
        "After b188, ASHL Core can validate a nine-line structural refactor map.",
        "Next refactor direction is ASHL Core Refactor Phase R2 Compatibility Alias Plan Minimal v0",
    ),
    "line_index": (
        "# ASHL Core Phase0 Line Document Index",
        "## 2. Action / Body-Motor Line",
        "## 10. Governance / Audit / Planning Line",
    ),
    "boundary_index": (
        "Boundary Index Version: 2026-06-09-b188",
        "ASHL Core Structural Refactor Map Minimal v0",
        "ASHL Core Refactor Phase R2 Compatibility Alias Plan Minimal v0",
        "No proof-of-learning claim.",
    ),
    "growth_plan": (
        "## Phase 2: Perception And Capability Grounding",
        "## Phase 3: Memory Admission And Retention",
        "## Phase 4: Layered Thought And State Settling",
        "## Phase 5: Nine-Line Growth Substrate Integration",
    ),
}

COMPLETED_DO_NOT_REPEAT = (
    {
        "capability_id": "phase0_minimal_thought_action_memory_loop_closure",
        "phase": "phase0_source_spine",
        "classification": "completed_do_not_repeat",
        "completed_boundary": "2026-06-09-b178",
        "source_evidence": "Phase0 minimal two-cycle thought/action/working-memory loop closure audit exists.",
        "reuse_rule": "Reuse as source evidence; do not rebuild the Phase0 mini-loop route.",
        "blocked_duplicate": "another Phase0 closure audit that only restates b178",
    },
    {
        "capability_id": "phase1_session_substrate_closure",
        "phase": "phase1_source_spine",
        "classification": "completed_do_not_repeat",
        "completed_boundary": "2026-06-09-b183",
        "source_evidence": "Phase1 session trace spine, tick handoff, and three-line index are closed.",
        "reuse_rule": "Reuse the closed substrate; do not add duplicate Phase1 readback/index/handoff packages.",
        "blocked_duplicate": "duplicate Phase1 substrate readback or classification package",
    },
    {
        "capability_id": "phase2_grounding_entry_report",
        "phase": "phase2",
        "classification": "completed_do_not_repeat",
        "completed_boundary": "2026-06-09-b184",
        "source_evidence": "Closed Phase1 substrate can produce Phase2 perception/capability entry reports.",
        "reuse_rule": "Read b184 reports as inputs; do not create another Phase2 entry package.",
        "blocked_duplicate": "second Phase2 entry report that re-identifies the same candidates",
    },
    {
        "capability_id": "phase2_evidence_source_link_report",
        "phase": "phase2",
        "classification": "completed_do_not_repeat",
        "completed_boundary": "2026-06-09-b185",
        "source_evidence": "b184 evidence candidates can be linked to existing visual-spatial and capability-map source references.",
        "reuse_rule": "Read b185 source-link reports; do not relink the same candidates as a new capability.",
        "blocked_duplicate": "second b185-style source-link report over the same entry reports",
    },
    {
        "capability_id": "phase2_unknown_classification_correction",
        "phase": "phase2",
        "classification": "completed_do_not_repeat",
        "completed_boundary": "2026-06-09-b186",
        "source_evidence": "wait_or_observe and observe_or_alternative_probe are corrected as not capability bindings.",
        "reuse_rule": "Carry the Phase4 deferred labels forward; do not force wait/probe into capability again.",
        "blocked_duplicate": "another correction package for the same wait/probe capability mistake",
    },
)

PARTIAL_ONLY_EXTEND = (
    {
        "capability_id": "phase2_perception_capability_grounding",
        "phase": "phase2",
        "classification": "partial_only_extend",
        "already_exists": "entry report, source-link report, and unknown-classification correction",
        "only_valid_next_connection": "summarize linked, unresolved, and Phase4-deferred evidence availability",
        "must_not_restart_from": "closed Phase1 substrate entry report",
    },
    {
        "capability_id": "phase3_memory_admission_and_retention",
        "phase": "phase3",
        "classification": "partial_only_extend",
        "already_exists": "bounded memory candidate/admission/write/read and retained-experience helper scopes",
        "only_valid_next_connection": "connect reviewed same-session trace candidates through explicit admission checks",
        "must_not_restart_from": "generic memory design or unreviewed session trace persistence",
    },
    {
        "capability_id": "phase4_layered_thought_and_state_settling",
        "phase": "phase4",
        "classification": "partial_only_extend",
        "already_exists": "thought-layer design, mimetic endocrine trace surfaces, and b186 Phase4-deferred wait/probe cues",
        "only_valid_next_connection": "create record-only settling or thought-layer evidence without feeding tendency/endocrine authority",
        "must_not_restart_from": "LLM-like runtime thought or direct endocrine action control",
    },
    {
        "capability_id": "phase5_nine_line_growth_substrate",
        "phase": "phase5",
        "classification": "partial_only_extend",
        "already_exists": "nine lines are indexed and several line-specific record/checker substrates exist",
        "only_valid_next_connection": "integrate existing line evidence under an audited substrate map",
        "must_not_restart_from": "a new monolithic thinking module",
    },
)

UNFINISHED_ROADMAP_CANDIDATES = (
    {
        "capability_id": "phase2_grounding_source_availability_readback",
        "phase": "phase2",
        "classification": "unfinished_can_enter_roadmap",
        "next_work": "read b186 correction plus b185 source links and summarize linked/unresolved/deferred evidence",
        "why_allowed": "current docs explicitly name this as the next useful Phase2 direction",
    },
    {
        "capability_id": "phase2_grounding_completion_without_action_preparation",
        "phase": "phase2",
        "classification": "unfinished_can_enter_roadmap",
        "next_work": "separate perception availability from capability binding without creating candidate input",
        "why_allowed": "Phase2 purpose is perception/capability grounding, not action preparation",
    },
    {
        "capability_id": "phase3_reviewed_session_trace_memory_candidate",
        "phase": "phase3",
        "classification": "unfinished_can_enter_roadmap",
        "next_work": "turn selected same-session trace evidence into reviewed memory candidates only",
        "why_allowed": "growth plan names Phase3 as memory admission and retention",
    },
    {
        "capability_id": "phase4_record_only_settling_signal",
        "phase": "phase4",
        "classification": "unfinished_can_enter_roadmap",
        "next_work": "read b186 deferred wait/probe cues as record-only settling candidates",
        "why_allowed": "b186 creates Phase4 deferred references while blocking any feed",
    },
    {
        "capability_id": "phase5_nine_line_integration_audit",
        "phase": "phase5",
        "classification": "unfinished_can_enter_roadmap",
        "next_work": "cross-link the nine line records into one audited integration substrate",
        "why_allowed": "growth plan names Phase5 as nine-line substrate integration",
    },
    {
        "capability_id": "phase6_to_phase10_authoritative_plan",
        "phase": "phase6_to_phase10",
        "classification": "unfinished_can_enter_roadmap",
        "next_work": "write an explicit Phase6-Phase10 plan before claiming those phases have runtime targets",
        "why_allowed": "repo search shows current authoritative growth plan only reaches Phase5",
    },
)

DESIGN_ONLY_NOT_RUNTIME = (
    {
        "document": "docs/phase1_to_phase5_growth_substrate_plan.md",
        "classification": "design_only_not_runtime",
        "reason": "planning guide only; it does not grant runtime authority",
    },
    {
        "document": "docs/phase0_line_document_index.md",
        "classification": "design_only_not_runtime",
        "reason": "navigation aid only; line grouping does not create capability",
    },
    {
        "document": "docs/qingyin_thought_system_layering_design_v0.md",
        "classification": "design_only_not_runtime",
        "reason": "thought layering is design; no runtime thought layer is created",
    },
    {
        "document": "docs/qingyin_bridge_dual_eye_capability_perception_design_v0.md",
        "classification": "design_only_not_runtime",
        "reason": "Bridge design is not raw tool access or capability-map mutation",
    },
    {
        "document": "docs/qingyin_audio_cochlea_decoder_design_v0.md",
        "classification": "design_only_not_runtime",
        "reason": "audio/cochlea design does not create hearing, STT, TTS, or voice runtime",
    },
)

BLOCKED_FLAGS = {
    "candidate_input_created",
    "candidate_ordering_created",
    "candidate_reordering_created",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "execution_created",
    "outcome_observation_created",
    "semantic_vision_created",
    "object_recognition_created",
    "active_focus_created",
    "capability_binding_created",
    "capability_map_created",
    "capability_map_mutated",
    "working_memory_update_created",
    "persistent_memory_write",
    "memory_write",
    "retention_write",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "endocrine_feed_created",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "state_settling_applied",
    "runtime_behavior_changed",
    "production_behavior_changed",
    "learning_claim",
    "proof_of_learning_claim",
    "consciousness_claim",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "cross_check_report_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_document_readback",
    "plan_alignment",
    "completed_do_not_repeat",
    "partial_only_extend",
    "unfinished_roadmap_candidates",
    "design_only_not_runtime",
    "duplicate_prevention",
    "authority_containment",
    "human_summary",
    "blocked_flags",
}


def _read_source_texts() -> dict[str, str]:
    return {
        source_id: Path(path).read_text(encoding="utf-8")
        for source_id, path in SOURCE_DOCS.items()
    }


def _source_document_readback(source_texts: dict[str, str]) -> dict[str, Any]:
    documents = []
    for source_id, path in SOURCE_DOCS.items():
        text = source_texts.get(source_id, "")
        required_terms = SOURCE_DOC_REQUIREMENTS[source_id]
        documents.append(
            {
                "source_id": source_id,
                "path": path,
                "read": bool(text),
                "required_terms_found": {
                    term: term in text
                    for term in required_terms
                },
                "supports_current_claim": bool(text) and all(term in text for term in required_terms),
            }
        )
    return {
        "source_documents": documents,
        "required_source_count": len(SOURCE_DOCS),
        "required_sources_read": all(document["read"] for document in documents),
        "all_required_terms_found": all(document["supports_current_claim"] for document in documents),
        "reads_capability_inventory": _source_supports(documents, "capability_inventory"),
        "reads_capability_matrix": _source_supports(documents, "capability_matrix"),
        "reads_status": _source_supports(documents, "status"),
        "reads_line_index": _source_supports(documents, "line_index"),
    }


def _source_supports(documents: list[dict[str, Any]], source_id: str) -> bool:
    return any(
        document.get("source_id") == source_id and document.get("supports_current_claim") is True
        for document in documents
    )


def build_phase2_to_phase10_completed_capability_cross_check_record(
    source_texts: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a record-only cross-check from authoritative docs."""

    texts = _read_source_texts() if source_texts is None else dict(source_texts)
    source_readback = _source_document_readback(texts)
    if not source_readback["required_sources_read"]:
        raise ValueError("required source documents were not all read")
    if not source_readback["all_required_terms_found"]:
        raise ValueError("required source documents do not support the current cross-check")

    return {
        "cross_check_report_id": "phase2_to_phase10_completed_capability_cross_check_demo_001",
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_document_readback": source_readback,
        "plan_alignment": {
            "current_boundary": BOUNDARY_INDEX_BEFORE,
            "current_phase": "phase2_perception_and_capability_grounding",
            "planned_line": "governance_audit_roadmap_deduplication",
            "source_plan_doc": "docs/phase1_to_phase5_growth_substrate_plan.md",
            "source_line_index_doc": "docs/phase0_line_document_index.md",
            "advances_exact_plan_step": "protect Phase2-Phase10 planning by separating completed, partial, unfinished, and design-only capabilities",
            "not_duplicate_reason": "b186 corrected two source classifications; this package prevents future work from repeating completed packages or treating design docs as runtime.",
            "not_premature_reason": "Phase2 has already produced entry, source-link, and correction reports; planning needs a de-dup cross-check before choosing the next branch.",
            "visible_output": "CLI-visible cross-check report with four capability buckets",
            "remaining_forbidden": "runtime authority, action selection, memory write, production behavior, and learning/consciousness claims",
        },
        "completed_do_not_repeat": [deepcopy(item) for item in COMPLETED_DO_NOT_REPEAT],
        "partial_only_extend": [deepcopy(item) for item in PARTIAL_ONLY_EXTEND],
        "unfinished_roadmap_candidates": [deepcopy(item) for item in UNFINISHED_ROADMAP_CANDIDATES],
        "design_only_not_runtime": [deepcopy(item) for item in DESIGN_ONLY_NOT_RUNTIME],
        "duplicate_prevention": {
            "completed_capability_cross_check_created": True,
            "completed_items_must_not_be_reimplemented": True,
            "partial_items_must_extend_existing_spines": True,
            "unfinished_items_can_enter_roadmap": True,
            "design_only_docs_blocked_as_runtime": True,
            "phase1_duplicate_substrate_blocked": True,
            "phase2_entry_duplicate_blocked": True,
            "phase2_source_link_duplicate_blocked": True,
            "phase2_wait_probe_capability_mistake_blocked": True,
            "phase6_to_phase10_runtime_claim_blocked_without_plan": True,
            "roadmap_uncertainty_reduced": True,
        },
        "authority_containment": {
            "record_only_cross_check": True,
            "reads_docs_only": True,
            "new_runtime_authority_created": False,
            "candidate_input_created_in_this_package": False,
            "candidate_ordering_created_in_this_package": False,
            "selected_action_created_in_this_package": False,
            "final_action_created_in_this_package": False,
            "direct_command_created_in_this_package": False,
            "execution_created_in_this_package": False,
            "outcome_observation_created_in_this_package": False,
            "semantic_vision_created_in_this_package": False,
            "capability_binding_created_in_this_package": False,
            "memory_write_created_in_this_package": False,
            "retention_write_created_in_this_package": False,
            "predictor_read_enabled_in_this_package": False,
            "predictor_influence_enabled_in_this_package": False,
            "predictor_modified_in_this_package": False,
            "endocrine_feed_created_in_this_package": False,
            "direct_tendency_feed_in_this_package": False,
            "production_behavior_created_in_this_package": False,
            "learning_claim": False,
            "proof_of_learning_claim": False,
            "consciousness_claim": False,
        },
        "human_summary": {
            "what_was_built": "A docs-backed capability cross-check for Phase2-Phase10 planning.",
            "what_changed": "Completed, partial, unfinished, and design-only capability claims are separated before the next roadmap step.",
            "what_error_it_prevents": "It prevents duplicate Phase1/Phase2 packages, prevents wait/probe from being forced back into capability, and prevents design docs from being treated as runtime.",
            "plain_result": "The next package can choose a real unfinished step instead of rebuilding an already completed one.",
        },
        "blocked_flags": {flag: False for flag in sorted(BLOCKED_FLAGS)},
    }


def validate_phase2_to_phase10_completed_capability_cross_check_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []

    _validate_top_level(record, errors)

    source = record.get("source_document_readback", {})
    plan = record.get("plan_alignment", {})
    completed = record.get("completed_do_not_repeat", [])
    partial = record.get("partial_only_extend", [])
    unfinished = record.get("unfinished_roadmap_candidates", [])
    design_only = record.get("design_only_not_runtime", [])
    duplicate = record.get("duplicate_prevention", {})
    authority = record.get("authority_containment", {})
    summary = record.get("human_summary", {})
    blocked_flags = record.get("blocked_flags", {})

    _validate_source_readback(source, errors)
    _validate_plan_alignment(plan, errors)
    _validate_buckets(completed, partial, unfinished, design_only, errors)
    _validate_duplicate_prevention(duplicate, errors)
    _validate_authority(authority, errors)
    _validate_blocked_flags(blocked_flags, errors)
    if not summary.get("what_error_it_prevents"):
        errors.append("human_summary_what_error_it_prevents_empty")
    if not summary.get("plain_result"):
        errors.append("human_summary_plain_result_empty")

    return {
        "valid": not errors,
        "error_codes": errors,
        "reads_capability_inventory": source.get("reads_capability_inventory") is True,
        "reads_capability_matrix": source.get("reads_capability_matrix") is True,
        "reads_status": source.get("reads_status") is True,
        "reads_line_index": source.get("reads_line_index") is True,
        "completed_do_not_repeat_count": len(completed) if isinstance(completed, list) else 0,
        "partial_only_extend_count": len(partial) if isinstance(partial, list) else 0,
        "unfinished_roadmap_candidate_count": len(unfinished) if isinstance(unfinished, list) else 0,
        "design_only_not_runtime_count": len(design_only) if isinstance(design_only, list) else 0,
        "phase2_completed_items_present": _bucket_has(completed, "phase2_grounding_entry_report")
        and _bucket_has(completed, "phase2_evidence_source_link_report")
        and _bucket_has(completed, "phase2_unknown_classification_correction"),
        "phase3_to_phase5_partial_or_unfinished_present": _bucket_has(partial, "phase3_memory_admission_and_retention")
        and _bucket_has(partial, "phase4_layered_thought_and_state_settling")
        and _bucket_has(partial, "phase5_nine_line_growth_substrate"),
        "phase6_to_phase10_not_authorized_as_runtime": duplicate.get("phase6_to_phase10_runtime_claim_blocked_without_plan") is True
        and _bucket_has(unfinished, "phase6_to_phase10_authoritative_plan"),
        "duplicate_reimplementation_blocked": duplicate.get("completed_items_must_not_be_reimplemented") is True,
        "design_only_runtime_confusion_blocked": duplicate.get("design_only_docs_blocked_as_runtime") is True,
        "roadmap_uncertainty_reduced": duplicate.get("roadmap_uncertainty_reduced") is True,
        "new_runtime_authority_created": authority.get("new_runtime_authority_created") is True,
        "no_candidate_input": authority.get("candidate_input_created_in_this_package") is False,
        "no_action_selection": authority.get("selected_action_created_in_this_package") is False,
        "no_memory_write": authority.get("memory_write_created_in_this_package") is False,
        "no_production_behavior": authority.get("production_behavior_created_in_this_package") is False,
        "no_learning_or_consciousness_claim": authority.get("proof_of_learning_claim") is False
        and authority.get("consciousness_claim") is False,
    }


def _validate_top_level(record: dict[str, Any], errors: list[str]) -> None:
    actual_fields = set(record)
    missing = REQUIRED_TOP_LEVEL_FIELDS - actual_fields
    unexpected = actual_fields - REQUIRED_TOP_LEVEL_FIELDS
    if missing:
        errors.append("top_missing_" + ",".join(sorted(missing)))
    if unexpected:
        errors.append("top_unexpected_" + ",".join(sorted(unexpected)))
    expected_values = {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
    }
    for field, expected in expected_values.items():
        if record.get(field) != expected:
            errors.append(f"top_{field}_wrong")
    if record.get("boundary_change_required") is not True:
        errors.append("top_boundary_change_required_wrong")


def _validate_source_readback(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("required_source_count") != len(SOURCE_DOCS):
        errors.append("source_required_source_count_wrong")
    for field in (
        "required_sources_read",
        "all_required_terms_found",
        "reads_capability_inventory",
        "reads_capability_matrix",
        "reads_status",
        "reads_line_index",
    ):
        if source.get(field) is not True:
            errors.append(f"source_{field}_wrong")
    documents = source.get("source_documents", [])
    if not isinstance(documents, list) or len(documents) != len(SOURCE_DOCS):
        errors.append("source_documents_wrong_count")
        return
    document_ids = {document.get("source_id") for document in documents if isinstance(document, dict)}
    if document_ids != set(SOURCE_DOCS):
        errors.append("source_documents_wrong_ids")
    for document in documents:
        if document.get("read") is not True:
            errors.append(f"source_document_{document.get('source_id')}_not_read")
        if document.get("supports_current_claim") is not True:
            errors.append(f"source_document_{document.get('source_id')}_does_not_support_claim")
        required_terms = document.get("required_terms_found", {})
        if not required_terms or not all(required_terms.values()):
            errors.append(f"source_document_{document.get('source_id')}_missing_terms")


def _validate_plan_alignment(plan: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "current_boundary": BOUNDARY_INDEX_BEFORE,
        "current_phase": "phase2_perception_and_capability_grounding",
        "planned_line": "governance_audit_roadmap_deduplication",
        "source_plan_doc": "docs/phase1_to_phase5_growth_substrate_plan.md",
        "source_line_index_doc": "docs/phase0_line_document_index.md",
    }
    for field, value in expected.items():
        if plan.get(field) != value:
            errors.append(f"plan_{field}_wrong")
    for field in (
        "advances_exact_plan_step",
        "not_duplicate_reason",
        "not_premature_reason",
        "visible_output",
        "remaining_forbidden",
    ):
        if not plan.get(field):
            errors.append(f"plan_{field}_empty")


def _validate_buckets(
    completed: Any,
    partial: Any,
    unfinished: Any,
    design_only: Any,
    errors: list[str],
) -> None:
    expected_lengths = (
        (completed, len(COMPLETED_DO_NOT_REPEAT), "completed"),
        (partial, len(PARTIAL_ONLY_EXTEND), "partial"),
        (unfinished, len(UNFINISHED_ROADMAP_CANDIDATES), "unfinished"),
        (design_only, len(DESIGN_ONLY_NOT_RUNTIME), "design_only"),
    )
    for bucket, expected_length, name in expected_lengths:
        if not isinstance(bucket, list) or len(bucket) != expected_length:
            errors.append(f"{name}_wrong_count")
    for item in completed if isinstance(completed, list) else []:
        if item.get("classification") != "completed_do_not_repeat":
            errors.append("completed_classification_wrong")
        if not item.get("reuse_rule") or not item.get("blocked_duplicate"):
            errors.append("completed_reuse_or_duplicate_reason_empty")
    for item in partial if isinstance(partial, list) else []:
        if item.get("classification") != "partial_only_extend":
            errors.append("partial_classification_wrong")
        if not item.get("only_valid_next_connection") or not item.get("must_not_restart_from"):
            errors.append("partial_connection_rule_empty")
    for item in unfinished if isinstance(unfinished, list) else []:
        if item.get("classification") != "unfinished_can_enter_roadmap":
            errors.append("unfinished_classification_wrong")
        if not item.get("next_work") or not item.get("why_allowed"):
            errors.append("unfinished_roadmap_reason_empty")
    for item in design_only if isinstance(design_only, list) else []:
        if item.get("classification") != "design_only_not_runtime":
            errors.append("design_only_classification_wrong")
        if not item.get("document") or not item.get("reason"):
            errors.append("design_only_document_or_reason_empty")

    for required_completed in (
        "phase2_grounding_entry_report",
        "phase2_evidence_source_link_report",
        "phase2_unknown_classification_correction",
    ):
        if not _bucket_has(completed, required_completed):
            errors.append(f"completed_missing_{required_completed}")
    for required_unfinished in (
        "phase2_grounding_source_availability_readback",
        "phase6_to_phase10_authoritative_plan",
    ):
        if not _bucket_has(unfinished, required_unfinished):
            errors.append(f"unfinished_missing_{required_unfinished}")


def _validate_duplicate_prevention(duplicate: dict[str, Any], errors: list[str]) -> None:
    for field in (
        "completed_capability_cross_check_created",
        "completed_items_must_not_be_reimplemented",
        "partial_items_must_extend_existing_spines",
        "unfinished_items_can_enter_roadmap",
        "design_only_docs_blocked_as_runtime",
        "phase1_duplicate_substrate_blocked",
        "phase2_entry_duplicate_blocked",
        "phase2_source_link_duplicate_blocked",
        "phase2_wait_probe_capability_mistake_blocked",
        "phase6_to_phase10_runtime_claim_blocked_without_plan",
        "roadmap_uncertainty_reduced",
    ):
        if duplicate.get(field) is not True:
            errors.append(f"duplicate_{field}_wrong")


def _validate_authority(authority: dict[str, Any], errors: list[str]) -> None:
    if authority.get("record_only_cross_check") is not True:
        errors.append("authority_record_only_cross_check_wrong")
    if authority.get("reads_docs_only") is not True:
        errors.append("authority_reads_docs_only_wrong")
    if authority.get("new_runtime_authority_created") is not False:
        errors.append("authority_new_runtime_authority_created_wrong")
    for field in (
        "candidate_input_created_in_this_package",
        "candidate_ordering_created_in_this_package",
        "selected_action_created_in_this_package",
        "final_action_created_in_this_package",
        "direct_command_created_in_this_package",
        "execution_created_in_this_package",
        "outcome_observation_created_in_this_package",
        "semantic_vision_created_in_this_package",
        "capability_binding_created_in_this_package",
        "memory_write_created_in_this_package",
        "retention_write_created_in_this_package",
        "predictor_read_enabled_in_this_package",
        "predictor_influence_enabled_in_this_package",
        "predictor_modified_in_this_package",
        "endocrine_feed_created_in_this_package",
        "direct_tendency_feed_in_this_package",
        "production_behavior_created_in_this_package",
        "learning_claim",
        "proof_of_learning_claim",
        "consciousness_claim",
    ):
        if authority.get(field) is not False:
            errors.append(f"authority_{field}_wrong")


def _validate_blocked_flags(blocked_flags: dict[str, Any], errors: list[str]) -> None:
    if set(blocked_flags) != BLOCKED_FLAGS:
        errors.append("blocked_flags_keys_wrong")
    for flag in BLOCKED_FLAGS:
        if blocked_flags.get(flag) is not False:
            errors.append(f"blocked_flag_{flag}_wrong")


def _bucket_has(bucket: Any, capability_id: str) -> bool:
    return isinstance(bucket, list) and any(
        isinstance(item, dict) and item.get("capability_id") == capability_id
        for item in bucket
    )


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[tuple[tuple[Any, ...], Any]] = [
        (("record_type",), "wrong_record_type"),
        (("boundary_index_after",), "2026-06-09-b186"),
        (("source_document_readback", "reads_capability_inventory"), False),
        (("source_document_readback", "source_documents", 1, "supports_current_claim"), False),
        (("source_document_readback", "reads_status"), False),
        (("source_document_readback", "reads_line_index"), False),
        (("completed_do_not_repeat", 2, "classification"), "partial_only_extend"),
        (("completed_do_not_repeat", 3, "reuse_rule"), ""),
        (("partial_only_extend", 0, "classification"), "completed_do_not_repeat"),
        (("partial_only_extend", 1, "only_valid_next_connection"), ""),
        (("unfinished_roadmap_candidates", 0, "classification"), "completed_do_not_repeat"),
        (("unfinished_roadmap_candidates", 5, "why_allowed"), ""),
        (("design_only_not_runtime", 0, "classification"), "runtime_ready"),
        (("design_only_not_runtime", 2, "reason"), ""),
        (("duplicate_prevention", "completed_items_must_not_be_reimplemented"), False),
        (("duplicate_prevention", "design_only_docs_blocked_as_runtime"), False),
        (("duplicate_prevention", "phase6_to_phase10_runtime_claim_blocked_without_plan"), False),
        (("authority_containment", "new_runtime_authority_created"), True),
        (("authority_containment", "candidate_input_created_in_this_package"), True),
        (("authority_containment", "selected_action_created_in_this_package"), True),
        (("authority_containment", "memory_write_created_in_this_package"), True),
        (("authority_containment", "production_behavior_created_in_this_package"), True),
        (("authority_containment", "proof_of_learning_claim"), True),
        (("human_summary", "what_error_it_prevents"), ""),
    ]
    records = []
    for path, value in cases:
        bad = deepcopy(valid_record)
        _set_path(bad, path, value)
        records.append(bad)
    return records


def _set_path(record: dict[str, Any], path: tuple[Any, ...], value: Any) -> None:
    target: Any = record
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, Any]:
    valid_results = [result for result in validation_results if result.get("valid")]
    return {
        "cross_check_result_count": len(validation_results),
        "valid_cross_check_count": len(valid_results),
        "invalid_cross_check_count": len(validation_results) - len(valid_results),
        "reads_capability_inventory_count": sum(1 for result in valid_results if result["reads_capability_inventory"]),
        "reads_capability_matrix_count": sum(1 for result in valid_results if result["reads_capability_matrix"]),
        "reads_status_count": sum(1 for result in valid_results if result["reads_status"]),
        "reads_line_index_count": sum(1 for result in valid_results if result["reads_line_index"]),
        "completed_do_not_repeat_count": valid_results[0]["completed_do_not_repeat_count"] if valid_results else 0,
        "partial_only_extend_count": valid_results[0]["partial_only_extend_count"] if valid_results else 0,
        "unfinished_roadmap_candidate_count": valid_results[0]["unfinished_roadmap_candidate_count"] if valid_results else 0,
        "design_only_not_runtime_count": valid_results[0]["design_only_not_runtime_count"] if valid_results else 0,
        "phase2_completed_items_present_count": sum(1 for result in valid_results if result["phase2_completed_items_present"]),
        "phase3_to_phase5_partial_or_unfinished_present_count": sum(
            1 for result in valid_results if result["phase3_to_phase5_partial_or_unfinished_present"]
        ),
        "phase6_to_phase10_not_authorized_as_runtime_count": sum(
            1 for result in valid_results if result["phase6_to_phase10_not_authorized_as_runtime"]
        ),
        "duplicate_reimplementation_blocked_count": sum(
            1 for result in valid_results if result["duplicate_reimplementation_blocked"]
        ),
        "design_only_runtime_confusion_blocked_count": sum(
            1 for result in valid_results if result["design_only_runtime_confusion_blocked"]
        ),
        "roadmap_uncertainty_reduced_count": sum(1 for result in valid_results if result["roadmap_uncertainty_reduced"]),
        "new_runtime_authority_created_count": sum(1 for result in valid_results if result["new_runtime_authority_created"]),
        "no_candidate_input_count": sum(1 for result in valid_results if result["no_candidate_input"]),
        "no_action_selection_count": sum(1 for result in valid_results if result["no_action_selection"]),
        "no_memory_write_count": sum(1 for result in valid_results if result["no_memory_write"]),
        "no_production_behavior_count": sum(1 for result in valid_results if result["no_production_behavior"]),
        "no_learning_or_consciousness_claim_count": sum(
            1 for result in valid_results if result["no_learning_or_consciousness_claim"]
        ),
    }


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary.get("valid_cross_check_count") == 1
        and summary.get("invalid_cross_check_count") == 24
        and summary.get("reads_capability_inventory_count") == 1
        and summary.get("reads_capability_matrix_count") == 1
        and summary.get("reads_status_count") == 1
        and summary.get("reads_line_index_count") == 1
        and summary.get("completed_do_not_repeat_count") == len(COMPLETED_DO_NOT_REPEAT)
        and summary.get("partial_only_extend_count") == len(PARTIAL_ONLY_EXTEND)
        and summary.get("unfinished_roadmap_candidate_count") == len(UNFINISHED_ROADMAP_CANDIDATES)
        and summary.get("design_only_not_runtime_count") == len(DESIGN_ONLY_NOT_RUNTIME)
        and summary.get("phase2_completed_items_present_count") == 1
        and summary.get("phase3_to_phase5_partial_or_unfinished_present_count") == 1
        and summary.get("phase6_to_phase10_not_authorized_as_runtime_count") == 1
        and summary.get("duplicate_reimplementation_blocked_count") == 1
        and summary.get("design_only_runtime_confusion_blocked_count") == 1
        and summary.get("roadmap_uncertainty_reduced_count") == 1
        and summary.get("new_runtime_authority_created_count") == 0
        and summary.get("no_candidate_input_count") == 1
        and summary.get("no_action_selection_count") == 1
        and summary.get("no_memory_write_count") == 1
        and summary.get("no_production_behavior_count") == 1
        and summary.get("no_learning_or_consciousness_claim_count") == 1
    )


def run_phase2_to_phase10_completed_capability_cross_check_minimal_check() -> dict[str, Any]:
    valid_record = build_phase2_to_phase10_completed_capability_cross_check_record()
    records = [valid_record, *_invalid_records(valid_record)]
    validation_results = [
        validate_phase2_to_phase10_completed_capability_cross_check_record(record)
        for record in records
    ]
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
            "boundary_reason": "Adds a docs-backed de-duplication and roadmap cross-check without creating runtime authority.",
        },
        "valid_records": [valid_record],
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A Phase2-to-Phase10 completed-capability cross-check report.",
            "what_error_it_prevents": "It prevents duplicate completed packages and design-only runtime claims before more roadmap work.",
            "plain_result": "The next package can extend an unfinished line instead of rebuilding what already exists.",
        },
        "valid_result_count": 1,
    }
