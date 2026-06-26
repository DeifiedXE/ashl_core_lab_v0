"""Audit that the Phase1 record-only growth substrate is complete."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .phase1_runtime_session_trace_spine_minimal import (
    BOUNDARY_INDEX_AFTER as TRACE_SPINE_BOUNDARY_INDEX,
    run_phase1_runtime_session_trace_spine_minimal_check,
    validate_phase1_runtime_session_trace_spine_record,
)
from .phase1_session_frame_runtime_tick_handoff_minimal import (
    BOUNDARY_INDEX_AFTER as TICK_HANDOFF_BOUNDARY_INDEX,
    run_phase1_session_frame_runtime_tick_handoff_minimal_check,
    validate_phase1_session_frame_runtime_tick_handoff_record,
)
from .phase1_tick1_frame_three_line_substrate_index_minimal import (
    BOUNDARY_INDEX_AFTER as THREE_LINE_INDEX_BOUNDARY_INDEX,
    run_phase1_tick1_frame_three_line_substrate_index_minimal_check,
    validate_phase1_tick1_frame_three_line_substrate_index_record,
)


COMMAND = "run-phase1-closure-audit-minimal-check"
FLOW = "phase1_closure_audit_minimal_v0"
PACKAGE_ID = "PKG-Phase1-ClosureAudit-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b182"
BOUNDARY_INDEX_AFTER = "2026-06-09-b183"
RECORD_TYPE = "phase1_closure_audit_minimal"

BLOCKED_FLAGS = {
    "duplicate_phase1_substrate_package_created",
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
    "persistent_memory_write",
    "memory_write",
    "long_term_memory_write",
    "retention_write",
    "memory_admission_created",
    "external_tool_called",
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
    "phase1_closure_audit_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_phase1_substrates",
    "phase1_closure_audit",
    "duplicate_package_guard",
    "closure_containment",
    "boundary_audit",
    "human_summary",
    "blocked_flags",
}

REQUIRED_SOURCE_FIELDS = {
    "scenario_id",
    "approved_purpose",
    "session_id",
    "trace_spine_record_id",
    "trace_spine_validated",
    "trace_spine_boundary_index",
    "trace_spine_tick_count",
    "tick_handoff_record_id",
    "tick_handoff_validated",
    "tick_handoff_boundary_index",
    "tick_handoff_context_created",
    "tick_handoff_appended_frame_created",
    "three_line_index_record_id",
    "three_line_index_validated",
    "three_line_index_boundary_index",
    "thought_line_index_created",
    "action_line_index_created",
    "memory_line_index_created",
    "cross_line_continuity_index_created",
    "all_source_scenarios_match",
    "all_source_sessions_match",
    "all_source_purposes_match",
}

REQUIRED_CLOSURE_FIELDS = {
    "closure_audit_created",
    "closure_scope",
    "closure_authority",
    "phase1_session_trace_spine_present",
    "tick_handoff_present",
    "three_line_index_present",
    "no_live_runtime",
    "no_action_selection",
    "no_memory_write",
    "phase1_closure_ready",
    "phase1_status",
    "phase1_duplicate_growth_packages_blocked",
    "phase2_may_start_after_this_audit",
}

REQUIRED_DUPLICATE_GUARD_FIELDS = {
    "duplicate_guard_created",
    "guard_scope",
    "phase1_duplicate_packages_blocked",
    "duplicate_session_trace_spine_package_allowed",
    "duplicate_session_frame_package_allowed",
    "duplicate_tick_handoff_package_allowed",
    "duplicate_three_line_index_package_allowed",
    "duplicate_phase1_closure_audit_package_allowed",
    "future_phase1_package_requires_human_override",
    "next_phase_required",
    "allowed_next_direction",
}

TRUE_CONTAINMENT_FIELDS = (
    "same_session_only",
    "sandbox_only",
    "record_only_closure_audit",
    "uses_existing_phase1_substrate_records_only",
    "phase1_closure_audit_created_in_this_package",
    "phase1_duplicate_growth_packages_blocked_in_this_package",
    "future_phase2_work_requires_separate_package",
)

FALSE_CONTAINMENT_FIELDS = (
    "duplicate_phase1_substrate_package_created_in_this_package",
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


def build_phase1_closure_audit_record(
    session_trace_spine_record: dict[str, Any] | None = None,
    tick_handoff_record: dict[str, Any] | None = None,
    three_line_index_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    trace = (
        deepcopy(session_trace_spine_record)
        if session_trace_spine_record is not None
        else deepcopy(run_phase1_runtime_session_trace_spine_minimal_check()["valid_records"][0])
    )
    handoff = (
        deepcopy(tick_handoff_record)
        if tick_handoff_record is not None
        else deepcopy(run_phase1_session_frame_runtime_tick_handoff_minimal_check()["valid_records"][0])
    )
    index = (
        deepcopy(three_line_index_record)
        if three_line_index_record is not None
        else deepcopy(run_phase1_tick1_frame_three_line_substrate_index_minimal_check()["valid_records"][0])
    )

    source = _source_summary(trace, handoff, index)
    closure = _build_closure_audit()

    return {
        "phase1_closure_audit_record_id": f"phase1_closure_audit_{source['scenario_id']}_demo_001",
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_phase1_substrates": source,
        "phase1_closure_audit": closure,
        "duplicate_package_guard": _build_duplicate_package_guard(),
        "closure_containment": _build_closure_containment(),
        "boundary_audit": _build_boundary_audit(),
        "human_summary": {
            "what_was_built": "A record-only audit that closes Phase1 substrate construction.",
            "what_changed": (
                "Phase1 is marked ready because the session trace spine, tick handoff, and "
                "three-line index are all present and still record-only."
            ),
            "what_is_blocked": (
                "No repeated Phase1 substrate package, live runtime, action selection, memory write, "
                "production behavior, or learning/consciousness claim is created."
            ),
            "plain_result": "Phase1 is closed as a checked scaffold. The next work should move to Phase2, not grow another Phase1 duplicate.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_phase1_closure_audit_record(record: dict[str, Any]) -> dict[str, Any]:
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
    if not _non_empty_string(record.get("phase1_closure_audit_record_id")):
        errors.append("phase1_closure_audit_record_id_empty")

    source = _as_dict(record.get("source_phase1_substrates"), errors, "source_phase1_substrates")
    closure = _as_dict(record.get("phase1_closure_audit"), errors, "phase1_closure_audit")
    guard = _as_dict(record.get("duplicate_package_guard"), errors, "duplicate_package_guard")
    containment = _as_dict(record.get("closure_containment"), errors, "closure_containment")
    audit = _as_dict(record.get("boundary_audit"), errors, "boundary_audit")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_closure(closure, errors)
    _validate_guard(guard, errors)
    _validate_containment(containment, errors)
    _validate_audit(audit, errors)
    _validate_human(human, errors)
    _validate_blocked(blocked, errors)

    phase1_ready = _phase1_closure_ready(source, closure, guard)
    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "session_id": source.get("session_id"),
        "phase1_session_trace_spine_present": closure.get("phase1_session_trace_spine_present") is True,
        "tick_handoff_present": closure.get("tick_handoff_present") is True,
        "three_line_index_present": closure.get("three_line_index_present") is True,
        "no_live_runtime": closure.get("no_live_runtime") is True and _live_runtime_blocked(containment, audit, blocked),
        "no_action_selection": closure.get("no_action_selection") is True
        and _action_selection_blocked(containment, audit, blocked),
        "no_memory_write": closure.get("no_memory_write") is True and _memory_write_blocked(containment, audit, blocked),
        "phase1_closure_ready": phase1_ready,
        "duplicate_phase1_packages_blocked": _duplicate_phase1_packages_blocked(guard, containment, blocked),
        "candidate_input_blocked": _candidate_input_blocked(containment, audit, blocked),
        "external_tools_blocked": _external_tools_blocked(containment, audit, blocked),
        "predictor_use_blocked": _predictor_use_blocked(containment, audit, blocked),
        "direct_feed_blocked": _direct_feed_blocked(containment, audit, blocked),
        "production_behavior_blocked": _production_behavior_blocked(containment, audit, blocked),
        "proof_claim_blocked": _proof_claim_blocked(containment, audit, blocked),
        "consciousness_claim_blocked": _consciousness_claim_blocked(containment, audit, blocked),
        "llm_runtime_blocked": _llm_runtime_blocked(containment, audit, blocked),
        "boundary_audit_passed": _boundary_audit_passed(audit),
    }


def run_phase1_closure_audit_minimal_check() -> dict[str, Any]:
    trace_records = _by_scenario(run_phase1_runtime_session_trace_spine_minimal_check()["valid_records"], _trace_scenario)
    handoff_records = _by_scenario(run_phase1_session_frame_runtime_tick_handoff_minimal_check()["valid_records"], _handoff_scenario)
    index_records = _by_scenario(run_phase1_tick1_frame_three_line_substrate_index_minimal_check()["valid_records"], _index_scenario)
    scenarios = sorted(set(trace_records) & set(handoff_records) & set(index_records))
    valid_records = [
        build_phase1_closure_audit_record(trace_records[scenario], handoff_records[scenario], index_records[scenario])
        for scenario in scenarios
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [validate_phase1_closure_audit_record(record) for record in records]
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
            "boundary_reason": "Closes Phase1 record-only substrate construction and blocks duplicate Phase1 growth packages.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "A Phase1 closure audit.",
            "what_changed": "Phase1 is ready because the trace spine, tick handoff, and three-line index are present.",
            "what_is_blocked": "No duplicate Phase1 package, live runtime, action selection, memory write, production behavior, or proof/consciousness claim is created.",
            "plain_result": "Phase1 is closed. The next real work should start Phase2 instead of repeating Phase1 scaffolding.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(
    trace: dict[str, Any],
    handoff: dict[str, Any],
    index: dict[str, Any],
) -> dict[str, Any]:
    trace_validation = validate_phase1_runtime_session_trace_spine_record(trace)
    handoff_validation = validate_phase1_session_frame_runtime_tick_handoff_record(handoff)
    index_validation = validate_phase1_tick1_frame_three_line_substrate_index_record(index)
    if not trace_validation["valid"]:
        raise ValueError("session_trace_spine_record must validate before Phase1 closure audit")
    if not handoff_validation["valid"]:
        raise ValueError("tick_handoff_record must validate before Phase1 closure audit")
    if not index_validation["valid"]:
        raise ValueError("three_line_index_record must validate before Phase1 closure audit")

    trace_spine = trace["session_trace_spine"]
    handoff_source = handoff["source_session_frame"]
    handoff_tick1 = handoff["tick1_context"]
    index_source = index["source_runtime_tick_handoff"]

    scenario_id = trace_validation["scenario_id"]
    session_id = trace_spine["session_id"]
    approved_purpose = trace_validation["approved_purpose"]
    return {
        "scenario_id": scenario_id,
        "approved_purpose": approved_purpose,
        "session_id": session_id,
        "trace_spine_record_id": trace["runtime_session_trace_spine_record_id"],
        "trace_spine_validated": True,
        "trace_spine_boundary_index": trace["boundary_index_after"],
        "trace_spine_tick_count": trace_spine["tick_count"],
        "tick_handoff_record_id": handoff["runtime_tick_handoff_record_id"],
        "tick_handoff_validated": True,
        "tick_handoff_boundary_index": handoff["boundary_index_after"],
        "tick_handoff_context_created": handoff_tick1["next_tick_context_created"],
        "tick_handoff_appended_frame_created": handoff["appended_session_frame"]["frame_appended"],
        "three_line_index_record_id": index["tick1_three_line_substrate_index_record_id"],
        "three_line_index_validated": True,
        "three_line_index_boundary_index": index["boundary_index_after"],
        "thought_line_index_created": index["thought_line_index"]["thought_line_index_created"],
        "action_line_index_created": index["action_line_index"]["action_line_index_created"],
        "memory_line_index_created": index["memory_line_index"]["memory_line_index_created"],
        "cross_line_continuity_index_created": index["cross_line_continuity_index"]["tick1_frame_indexed"],
        "all_source_scenarios_match": scenario_id == handoff_source["scenario_id"] == index_source["scenario_id"],
        "all_source_sessions_match": session_id == handoff_tick1["session_id"] == index_source["session_id"],
        "all_source_purposes_match": approved_purpose == handoff_tick1["approved_purpose"] == index_source["approved_purpose"],
    }


def _build_closure_audit() -> dict[str, Any]:
    return {
        "closure_audit_created": True,
        "closure_scope": "same_session_sandbox_record_only",
        "closure_authority": "phase1_closure_audit_only",
        "phase1_session_trace_spine_present": True,
        "tick_handoff_present": True,
        "three_line_index_present": True,
        "no_live_runtime": True,
        "no_action_selection": True,
        "no_memory_write": True,
        "phase1_closure_ready": True,
        "phase1_status": "complete_as_record_only_growth_substrate",
        "phase1_duplicate_growth_packages_blocked": True,
        "phase2_may_start_after_this_audit": True,
    }


def _build_duplicate_package_guard() -> dict[str, Any]:
    return {
        "duplicate_guard_created": True,
        "guard_scope": "phase1_growth_substrate_duplicate_prevention",
        "phase1_duplicate_packages_blocked": True,
        "duplicate_session_trace_spine_package_allowed": False,
        "duplicate_session_frame_package_allowed": False,
        "duplicate_tick_handoff_package_allowed": False,
        "duplicate_three_line_index_package_allowed": False,
        "duplicate_phase1_closure_audit_package_allowed": False,
        "future_phase1_package_requires_human_override": True,
        "next_phase_required": "Phase2",
        "allowed_next_direction": "Phase2 perception/capability grounding entry from closed Phase1 substrate",
    }


def _build_closure_containment() -> dict[str, bool]:
    containment = {field: True for field in TRUE_CONTAINMENT_FIELDS}
    containment.update({field: False for field in FALSE_CONTAINMENT_FIELDS})
    return containment


def _build_boundary_audit() -> dict[str, Any]:
    audit: dict[str, Any] = {
        "boundary_audit_id": "phase1_closure_audit_boundary_audit_b183",
        "triggered": True,
        "boundary_number": 183,
        "package_id": PACKAGE_ID,
    }
    audit.update({field: False for field in FALSE_AUDIT_FIELDS})
    return audit


def _invalid_records(reach: dict[str, Any], wait: dict[str, Any], probe: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(base: dict[str, Any], label: str, path: tuple[Any, ...], value: Any) -> None:
        record = deepcopy(base)
        _set_path(record, path, value)
        record["phase1_closure_audit_record_id"] = f"invalid_{label}"
        invalids.append(record)

    mutate(reach, "bad_record_type", ("record_type",), "bad")
    mutate(reach, "wrong_boundary_after", ("boundary_index_after",), "2026-06-09-b182")
    mutate(reach, "trace_spine_missing", ("phase1_closure_audit", "phase1_session_trace_spine_present"), False)
    mutate(reach, "tick_handoff_missing", ("phase1_closure_audit", "tick_handoff_present"), False)
    mutate(reach, "three_line_index_missing", ("phase1_closure_audit", "three_line_index_present"), False)
    mutate(wait, "source_trace_wrong_boundary", ("source_phase1_substrates", "trace_spine_boundary_index"), "2026-06-09-b178")
    mutate(wait, "source_tick_wrong_boundary", ("source_phase1_substrates", "tick_handoff_boundary_index"), "2026-06-09-b180")
    mutate(wait, "source_index_wrong_boundary", ("source_phase1_substrates", "three_line_index_boundary_index"), "2026-06-09-b181")
    mutate(wait, "source_mismatch", ("source_phase1_substrates", "all_source_scenarios_match"), False)
    mutate(wait, "not_ready", ("phase1_closure_audit", "phase1_closure_ready"), False)
    mutate(wait, "live_runtime", ("phase1_closure_audit", "no_live_runtime"), False)
    mutate(wait, "action_selection", ("phase1_closure_audit", "no_action_selection"), False)
    mutate(wait, "memory_write", ("phase1_closure_audit", "no_memory_write"), False)
    mutate(probe, "duplicate_guard_missing", ("duplicate_package_guard", "phase1_duplicate_packages_blocked"), False)
    mutate(probe, "duplicate_spine_allowed", ("duplicate_package_guard", "duplicate_session_trace_spine_package_allowed"), True)
    mutate(probe, "duplicate_tick_allowed", ("duplicate_package_guard", "duplicate_tick_handoff_package_allowed"), True)
    mutate(probe, "duplicate_index_allowed", ("duplicate_package_guard", "duplicate_three_line_index_package_allowed"), True)
    mutate(probe, "wrong_next_phase", ("duplicate_package_guard", "next_phase_required"), "Phase1")
    mutate(reach, "containment_duplicate_created", ("closure_containment", "duplicate_phase1_substrate_package_created_in_this_package"), True)
    mutate(reach, "containment_candidate_input", ("closure_containment", "candidate_input_created_in_this_package"), True)
    mutate(reach, "containment_selected_action", ("closure_containment", "selected_action_created_in_this_package"), True)
    mutate(reach, "containment_memory", ("closure_containment", "persistent_memory_write_created_in_this_package"), True)
    mutate(reach, "containment_predictor", ("closure_containment", "predictor_modified_in_this_package"), True)
    mutate(reach, "containment_production", ("closure_containment", "production_behavior_created_in_this_package"), True)
    mutate(wait, "audit_live_runtime", ("boundary_audit", "live_runtime_session_started"), True)
    mutate(wait, "audit_action", ("boundary_audit", "selected_action_created"), True)
    mutate(wait, "audit_memory", ("boundary_audit", "persistent_memory_write_created"), True)
    mutate(wait, "audit_proof", ("boundary_audit", "proof_of_learning_claim"), True)
    mutate(wait, "blocked_duplicate", ("blocked_flags", "duplicate_phase1_substrate_package_created"), True)
    mutate(wait, "blocked_memory", ("blocked_flags", "memory_write"), True)
    mutate(wait, "blocked_consciousness", ("blocked_flags", "consciousness_claim"), True)
    mutate(probe, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "phase1_closure_audit_result_count": len(validation_results),
        "valid_phase1_closure_audit_count": len(valid),
        "invalid_phase1_closure_audit_count": len(validation_results) - len(valid),
        "phase1_session_trace_spine_present_count": sum(
            1 for result in valid if result["phase1_session_trace_spine_present"]
        ),
        "tick_handoff_present_count": sum(1 for result in valid if result["tick_handoff_present"]),
        "three_line_index_present_count": sum(1 for result in valid if result["three_line_index_present"]),
        "no_live_runtime_count": sum(1 for result in valid if result["no_live_runtime"]),
        "no_action_selection_count": sum(1 for result in valid if result["no_action_selection"]),
        "no_memory_write_count": sum(1 for result in valid if result["no_memory_write"]),
        "phase1_closure_ready_count": sum(1 for result in valid if result["phase1_closure_ready"]),
        "duplicate_phase1_packages_blocked_count": sum(
            1 for result in valid if result["duplicate_phase1_packages_blocked"]
        ),
        "candidate_input_blocked_count": sum(1 for result in valid if result["candidate_input_blocked"]),
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
        summary["phase1_closure_audit_result_count"] == 35
        and summary["valid_phase1_closure_audit_count"] == 3
        and summary["invalid_phase1_closure_audit_count"] == 32
        and summary["phase1_session_trace_spine_present_count"] == 3
        and summary["tick_handoff_present_count"] == 3
        and summary["three_line_index_present_count"] == 3
        and summary["no_live_runtime_count"] == 3
        and summary["no_action_selection_count"] == 3
        and summary["no_memory_write_count"] == 3
        and summary["phase1_closure_ready_count"] == 3
        and summary["duplicate_phase1_packages_blocked_count"] == 3
        and summary["candidate_input_blocked_count"] == 3
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
    _validate_expected(
        source,
        {
            "trace_spine_validated": True,
            "trace_spine_boundary_index": TRACE_SPINE_BOUNDARY_INDEX,
            "trace_spine_tick_count": 8,
            "tick_handoff_validated": True,
            "tick_handoff_boundary_index": TICK_HANDOFF_BOUNDARY_INDEX,
            "tick_handoff_context_created": True,
            "tick_handoff_appended_frame_created": True,
            "three_line_index_validated": True,
            "three_line_index_boundary_index": THREE_LINE_INDEX_BOUNDARY_INDEX,
            "thought_line_index_created": True,
            "action_line_index_created": True,
            "memory_line_index_created": True,
            "cross_line_continuity_index_created": True,
            "all_source_scenarios_match": True,
            "all_source_sessions_match": True,
            "all_source_purposes_match": True,
        },
        errors,
        "source",
    )
    for field in (
        "scenario_id",
        "approved_purpose",
        "session_id",
        "trace_spine_record_id",
        "tick_handoff_record_id",
        "three_line_index_record_id",
    ):
        if not _non_empty_string(source.get(field)):
            errors.append(f"source_{field}_empty")


def _validate_closure(closure: dict[str, Any], errors: list[str]) -> None:
    _validate_required(closure, REQUIRED_CLOSURE_FIELDS, errors, "phase1_closure_audit")
    _validate_no_extra(closure, REQUIRED_CLOSURE_FIELDS, errors, "phase1_closure_audit")
    _validate_expected(
        closure,
        {
            "closure_audit_created": True,
            "closure_scope": "same_session_sandbox_record_only",
            "closure_authority": "phase1_closure_audit_only",
            "phase1_session_trace_spine_present": True,
            "tick_handoff_present": True,
            "three_line_index_present": True,
            "no_live_runtime": True,
            "no_action_selection": True,
            "no_memory_write": True,
            "phase1_closure_ready": True,
            "phase1_status": "complete_as_record_only_growth_substrate",
            "phase1_duplicate_growth_packages_blocked": True,
            "phase2_may_start_after_this_audit": True,
        },
        errors,
        "phase1_closure_audit",
    )


def _validate_guard(guard: dict[str, Any], errors: list[str]) -> None:
    _validate_required(guard, REQUIRED_DUPLICATE_GUARD_FIELDS, errors, "duplicate_package_guard")
    _validate_no_extra(guard, REQUIRED_DUPLICATE_GUARD_FIELDS, errors, "duplicate_package_guard")
    _validate_expected(
        guard,
        {
            "duplicate_guard_created": True,
            "guard_scope": "phase1_growth_substrate_duplicate_prevention",
            "phase1_duplicate_packages_blocked": True,
            "duplicate_session_trace_spine_package_allowed": False,
            "duplicate_session_frame_package_allowed": False,
            "duplicate_tick_handoff_package_allowed": False,
            "duplicate_three_line_index_package_allowed": False,
            "duplicate_phase1_closure_audit_package_allowed": False,
            "future_phase1_package_requires_human_override": True,
            "next_phase_required": "Phase2",
            "allowed_next_direction": "Phase2 perception/capability grounding entry from closed Phase1 substrate",
        },
        errors,
        "duplicate_package_guard",
    )


def _validate_containment(containment: dict[str, Any], errors: list[str]) -> None:
    required = set(TRUE_CONTAINMENT_FIELDS) | set(FALSE_CONTAINMENT_FIELDS)
    _validate_required(containment, required, errors, "closure_containment")
    _validate_no_extra(containment, required, errors, "closure_containment")
    for field in TRUE_CONTAINMENT_FIELDS:
        if containment.get(field) is not True:
            errors.append(f"closure_containment_{field}_not_true")
    for field in FALSE_CONTAINMENT_FIELDS:
        if containment.get(field) is not False:
            errors.append(f"closure_containment_{field}_not_false")


def _validate_audit(audit: dict[str, Any], errors: list[str]) -> None:
    required = {"boundary_audit_id", "triggered", "boundary_number", "package_id"} | set(FALSE_AUDIT_FIELDS)
    _validate_required(audit, required, errors, "boundary_audit")
    _validate_no_extra(audit, required, errors, "boundary_audit")
    _validate_expected(
        audit,
        {"triggered": True, "boundary_number": 183, "package_id": PACKAGE_ID},
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


def _phase1_closure_ready(source: dict[str, Any], closure: dict[str, Any], guard: dict[str, Any]) -> bool:
    return all(
        value is True
        for value in (
            source.get("trace_spine_validated"),
            source.get("tick_handoff_validated"),
            source.get("three_line_index_validated"),
            source.get("all_source_scenarios_match"),
            source.get("all_source_sessions_match"),
            source.get("all_source_purposes_match"),
            closure.get("phase1_session_trace_spine_present"),
            closure.get("tick_handoff_present"),
            closure.get("three_line_index_present"),
            closure.get("no_live_runtime"),
            closure.get("no_action_selection"),
            closure.get("no_memory_write"),
            closure.get("phase1_closure_ready"),
            guard.get("phase1_duplicate_packages_blocked"),
        )
    )


def _duplicate_phase1_packages_blocked(
    guard: dict[str, Any], containment: dict[str, Any], blocked: dict[str, Any]
) -> bool:
    return (
        guard.get("phase1_duplicate_packages_blocked") is True
        and guard.get("duplicate_session_trace_spine_package_allowed") is False
        and guard.get("duplicate_session_frame_package_allowed") is False
        and guard.get("duplicate_tick_handoff_package_allowed") is False
        and guard.get("duplicate_three_line_index_package_allowed") is False
        and guard.get("duplicate_phase1_closure_audit_package_allowed") is False
        and guard.get("next_phase_required") == "Phase2"
        and guard.get("allowed_next_direction")
        == "Phase2 perception/capability grounding entry from closed Phase1 substrate"
        and containment.get("duplicate_phase1_substrate_package_created_in_this_package") is False
        and blocked.get("duplicate_phase1_substrate_package_created") is False
    )


def _live_runtime_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return all(
        value is False
        for value in (
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


def _candidate_input_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return all(
        value is False
        for value in (
            containment.get("candidate_input_created_in_this_package"),
            containment.get("candidate_ordering_created_in_this_package"),
            containment.get("candidate_reordering_created_in_this_package"),
            audit.get("candidate_input_created"),
            audit.get("candidate_ordering_created"),
            audit.get("candidate_reordering_created"),
            blocked.get("candidate_input_created"),
            blocked.get("candidate_ordering_created"),
            blocked.get("candidate_reordering_created"),
        )
    )


def _action_selection_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return all(
        value is False
        for value in (
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


def _memory_write_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return all(
        value is False
        for value in (
            containment.get("working_memory_update_created_in_this_package"),
            containment.get("persistent_memory_write_created_in_this_package"),
            containment.get("memory_admission_created_in_this_package"),
            containment.get("retention_write_created_in_this_package"),
            audit.get("working_memory_update_created"),
            audit.get("persistent_memory_write_created"),
            audit.get("memory_admission_created"),
            audit.get("retention_write_created"),
            blocked.get("working_memory_update_created"),
            blocked.get("persistent_memory_write"),
            blocked.get("memory_write"),
            blocked.get("long_term_memory_write"),
            blocked.get("retention_write"),
            blocked.get("memory_admission_created"),
        )
    )


def _external_tools_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        containment.get("external_tool_called_in_this_package") is False
        and audit.get("external_tool_called") is False
        and blocked.get("external_tool_called") is False
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


def _production_behavior_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return all(
        value is False
        for value in (
            containment.get("production_behavior_created_in_this_package"),
            audit.get("production_behavior_created"),
            audit.get("runtime_behavior_leak"),
            blocked.get("production_action_selection"),
            blocked.get("runtime_action_selection"),
            blocked.get("runtime_behavior_changed"),
            blocked.get("production_behavior_changed"),
        )
    )


def _proof_claim_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return all(
        value is False
        for value in (
            containment.get("proof_of_learning_claim"),
            containment.get("long_term_learning_claim"),
            audit.get("proof_of_learning_claim"),
            audit.get("long_term_learning_claim"),
            blocked.get("proof_of_learning_claim"),
            blocked.get("long_term_learning_claim"),
        )
    )


def _consciousness_claim_blocked(containment: dict[str, Any], audit: dict[str, Any], blocked: dict[str, Any]) -> bool:
    return (
        containment.get("consciousness_claim") is False
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
        and audit.get("boundary_number") == 183
        and all(audit.get(field) is False for field in FALSE_AUDIT_FIELDS)
    )


def _by_scenario(records: list[dict[str, Any]], getter) -> dict[str, dict[str, Any]]:
    return {getter(record): record for record in records}


def _trace_scenario(record: dict[str, Any]) -> str:
    return record["source_phase0_closure_audit"]["scenario_id"]


def _handoff_scenario(record: dict[str, Any]) -> str:
    return record["source_session_frame"]["scenario_id"]


def _index_scenario(record: dict[str, Any]) -> str:
    return record["source_runtime_tick_handoff"]["scenario_id"]


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

    print(json.dumps(run_phase1_closure_audit_minimal_check(), indent=2))
