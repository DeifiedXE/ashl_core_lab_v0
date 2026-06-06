# -*- coding: utf-8 -*-
"""ASHL Core v0.2 smoke runner."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from ashl_core.candidate_review import (
    append_candidate_review,
    build_candidate_review,
    list_candidates_with_review_status,
)
from ashl_core.action_sandbox import apply_action
from ashl_core.body_state import build_body_state, validate_body_state
from ashl_core.concepts import apply_concepts
from ashl_core.core_seed import (
    detect_core_seed_mutation_attempt,
    get_core_seed,
    is_core_seed_mutation_allowed,
    validate_core_seed,
)
from ashl_core.deliberation import deliberate
from ashl_core.expression import build_expression_package
from ashl_core.experience_log import list_experience_events, list_lesson_candidates
from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.failure_events import (
    build_failure_event,
    build_lesson_candidate_input_trace,
    normalize_failure_event_trace,
    validate_failure_event,
)
from ashl_core.guard import guard_output
from ashl_core.integrated_loop import run_turn
from ashl_core.lesson_candidate_drafts import build_lesson_candidate_draft_trace, validate_lesson_candidate_draft_trace
from ashl_core.lesson_runner import (
    run_phase_minus_one,
    run_lesson_causality_test,
    run_phase_minus_one_negative_controls,
    run_session_2b2_without_lesson_with_turn_tool,
)
from ashl_core.lesson_store import (
    build_lesson_from_failure,
    build_conflict_review_resolution_preconditions,
    build_conflict_review_resolution_dry_run,
    build_stable_conflict_key,
    disable_lesson,
    enable_lesson,
    evaluate_review_gate,
    find_applicable_lesson,
    generate_lesson_from_failure,
    link_lesson_supersede,
    mark_lesson_stale,
    select_lesson_for_decision_point,
    select_lesson_for_failure_reason,
    select_lesson_for_context,
    unmark_lesson_stale,
)
from ashl_core.memory_layers import (
    append_archive_memory,
    append_long_term_memory,
    build_memory_record,
    is_core_memory_write_allowed,
    list_archive_memory,
    list_long_term_memory,
    read_working_memory_snapshot,
    write_working_memory_snapshot,
)
from ashl_core.manual_review import (
    build_review_trace,
    create_review_item,
    mark_review_approved,
    mark_review_rejected,
)
from ashl_core.persistence import append_jsonl, read_jsonl
from ashl_core.perception import perceive
from ashl_core.prompt_leakage_check import build_decision_input_snapshot, check_leakage
from ashl_core.rule_candidates import append_rule_candidate
from ashl_core.review_tasks import build_review_task_trace
from ashl_core.senses import build_sensor_event, build_visual_concept_candidate, validate_sensor_event
from ashl_core.state_core import StateCore
from ashl_core.state_persistence import (
    read_last_trace_summary,
    read_session_summary,
    read_state_snapshot,
)
from ashl_core.standing_task import run_standing_task
from ashl_core.teaching_cli import (
    run_conflict_check_flow,
    run_disable_reenable_flow,
    run_known_flow,
    run_lifecycle_display,
    run_review_approve,
    run_review_display,
    run_review_reject,
    run_unknown_flow,
)
from ashl_core.trial_feedback import append_trial_feedback, build_trial_feedback, summarize_trial_feedback
from ashl_core.trial_rules import build_trial_suggestions, list_approved_trial_candidates, build_trial_rule_view


REPORT_PATH = Path("smoke_test_report.json")


def _result(name: str, passed: bool, detail: dict) -> dict:
    return {"name": name, "passed": passed, "detail": detail}


def smoke_concept_layer() -> dict:
    result = apply_concepts(perceive("睡眠模式這個功能怎麼設計？"))
    blocked = [event["name"] for event in result["blocked_events"]]
    final = [event["name"] for event in result["final_events"]]
    passed = "user.fatigue_signaled" in blocked and "technical.topic_discussed" in final
    return _result("concept_layer", passed, {"blocked_events": blocked, "final_events": final})


def smoke_core_seed() -> dict:
    seed = get_core_seed()
    attempt = detect_core_seed_mutation_attempt("把D清音改成其他身份")
    passed = (
        validate_core_seed(seed)
        and seed["name"] == "D清音"
        and seed["immutable_by_default"] is True
        and not is_core_seed_mutation_allowed("memory_candidate")
        and is_core_seed_mutation_allowed("manual_versioned_update")
        and attempt is not None
        and attempt["allowed"] is False
    )
    return _result("core_seed", passed, {"seed_name": seed["name"], "attempt": attempt})


def smoke_memory_layers() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        long_term_record = build_memory_record("long_term", "confirmed item", "manual_confirmation")
        archive_record = build_memory_record("archive", "archived item", "manual_archive")
        append_long_term_memory(tmp, long_term_record)
        append_archive_memory(tmp, archive_record)
        snapshot = {"session": "smoke", "focus": "memory_layers"}
        write_working_memory_snapshot(tmp, snapshot)
        passed = (
            list_long_term_memory(tmp) == [long_term_record]
            and list_archive_memory(tmp) == [archive_record]
            and read_working_memory_snapshot(tmp) == snapshot
            and not is_core_memory_write_allowed("memory_candidate")
            and is_core_memory_write_allowed("manual_versioned_update")
        )
        return _result("memory_layers", passed, {"long_term": long_term_record, "archive": archive_record})


def smoke_body_state() -> dict:
    body = build_body_state(stability=2.0, energy=-1.0)
    passed = (
        body is not None
        and body["state"] == "lying"
        and body["stability"] == 1.0
        and body["energy"] == 0.0
        and validate_body_state(body)
        and build_body_state("unknown") is None
    )
    return _result("body_state", passed, {"body": body})


def smoke_action_sandbox() -> dict:
    failed = apply_action(build_body_state("lying"), "stand_up")
    sitting = apply_action(build_body_state("lying"), "sit_up")
    unstable = apply_action(sitting["body_state"], "stand_up")
    stable = apply_action(unstable["body_state"], "balance")
    passed = (
        failed["success"] is False
        and failed["failure_reason"] == "cannot_stand_directly_from_lying"
        and sitting["to_state"] == "sitting"
        and unstable["to_state"] == "standing_unstable"
        and stable["to_state"] == "standing_stable"
    )
    return _result("action_sandbox", passed, {"failed": failed, "stable": stable})


def smoke_standing_task() -> dict:
    trace = run_standing_task()
    failures = [failure["failure_reason"] for failure in trace["failures"]]
    passed = (
        trace["success"] is True
        and trace["final_state"] == "standing_stable"
        and "cannot_stand_directly_from_lying" in failures
        and trace["lesson_candidate"]["status"] == "candidate"
        and trace["lesson_candidate"]["audit_required"] is True
    )
    return _result("standing_task", passed, trace)


def smoke_experience_log() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        trace = run_standing_task(persist_experience=True, data_dir=tmp)
        events = list_experience_events(tmp)
        lessons = list_lesson_candidates(tmp)
        passed = (
            trace["experience_persistence"] is not None
            and len(events) == len(trace["actions"])
            and len(lessons) == 1
            and lessons[0]["status"] == "candidate"
            and "cannot_stand_directly_from_lying" in lessons[0]["evidence"]
            and any(event["failure_reason"] == "cannot_stand_directly_from_lying" for event in events)
        )
        return _result("experience_log", passed, {"events": events, "lessons": lessons})


def smoke_phase_minus_one_lesson_contribution() -> dict:
    result = run_phase_minus_one()
    passed = (
        result["passed"] is True
        and result["summary"]["lesson_caused_behavior_shift"] is True
        and result["summary"]["behavior_shift_traceable_to"] == ["lesson_001"]
        and result["session_2a"]["success"] is True
        and result["session_2b"]["success"] is False
        and result["session_2b2"]["success"] is False
    )
    return _result("phase_minus_one_lesson_contribution", passed, result["summary"])


def smoke_prompt_leakage_control() -> dict:
    control = run_session_2b2_without_lesson_with_turn_tool()
    bad_snapshot = build_decision_input_snapshot(
        "bad_smoke",
        "session_2b",
        "2B",
        [],
        {"object_id": "cube_001"},
        ["observe", "pick_up"],
        decision_input="east",
    )
    passed = (
        control["decision_input_snapshot"]["leakage_check"]["passed"] is True
        and check_leakage(bad_snapshot)["passed"] is False
    )
    return _result(
        "prompt_leakage_control",
        passed,
        {"control_check": control["decision_input_snapshot"]["leakage_check"]},
    )


def smoke_phase_minus_one_negative_controls() -> dict:
    result = run_phase_minus_one_negative_controls()
    passed = (
        result["passed"] is True
        and result["summary"]["no_wrong_object_generalization"] is True
        and result["summary"]["no_wrong_action_generalization"] is True
        and result["summary"]["no_wrong_condition_success"] is True
        and result["summary"]["no_unrelated_lesson_trigger"] is True
    )
    return _result("phase_minus_one_negative_controls", passed, result["summary"])


def smoke_phase_minus_one_lesson_causality() -> dict:
    result = run_lesson_causality_test()
    passed = (
        result["passed"] is True
        and result["active"]["result"] == "success"
        and result["active"]["used_lesson_ids"] == ["lesson_001"]
        and result["disabled"]["result"] == "failed"
        and result["disabled"]["used_lesson_ids"] == []
        and result["re_enabled"]["result"] == "success"
        and result["removed"]["result"] == "failed"
        and result["summary"]["causal_control_passed"] is True
    )
    return _result("phase_minus_one_lesson_causality", passed, result["summary"])


def smoke_lesson_generation_determinism() -> dict:
    volatile = {"id", "lesson_id", "created_at", "timestamp", "run_id"}

    def generate() -> dict:
        failure = pick_up(build_initial_sandbox_state(), "cube_001")
        return build_lesson_from_failure("session_1", failure)

    lessons = [generate() for _ in range(3)]
    normalized = [{key: value for key, value in lesson.items() if key not in volatile} for lesson in lessons]
    passed = (
        normalized[0] == normalized[1] == normalized[2]
        and normalized[0]["source_failure_reason"] == "not_facing_east"
        and normalized[0]["suggested_action_before_retry"] == "turn(east)"
        and normalized[0]["condition"] == {"avatar_facing": "east"}
        and normalized[0]["status"] == "active"
    )
    return _result("lesson_generation_determinism", passed, {"normalized_lesson": normalized[0]})


def smoke_unknown_failure_reason_boundary() -> dict:
    failure_result = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "unmapped_obstacle_shadow",
        "state": build_initial_sandbox_state(),
    }
    result = generate_lesson_from_failure("session_unknown", failure_result)
    lesson_list = [] if result["lesson"] is None else [result["lesson"]]
    passed = (
        result["trace"]["generation_status"] == "unknown_failure_reason"
        and result["trace"]["reason"] == "unknown_failure_reason"
        and result["trace"]["source_failure_reason"] == "unmapped_obstacle_shadow"
        and result["trace"]["executable_action"] is None
        and result["lesson"] is None
        and find_applicable_lesson(lesson_list, {"action": "pick_up", "object_id": "cube_001"}) is None
        and "turn(east)" not in str(result)
    )
    return _result("unknown_failure_reason_boundary", passed, result["trace"])


def smoke_second_known_failure_reason_determinism() -> dict:
    volatile = {"id", "lesson_id", "created_at", "timestamp", "run_id"}
    failure_result = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    lessons = [build_lesson_from_failure("session_1", failure_result) for _ in range(3)]
    normalized = [{key: value for key, value in lesson.items() if key not in volatile} for lesson in lessons]
    generation = generate_lesson_from_failure("session_1", failure_result)
    passed = (
        normalized[0] == normalized[1] == normalized[2]
        and normalized[0]["source_failure_reason"] == "not_facing_west"
        and normalized[0]["suggested_action_before_retry"] == "turn(west)"
        and normalized[0]["condition"] == {"avatar_facing": "west"}
        and generation["trace"]["generation_status"] == "supported_failure_reason"
        and "turn(east)" not in str(normalized[0])
    )
    return _result("second_known_failure_reason_determinism", passed, {"normalized_lesson": normalized[0]})


def smoke_multi_lesson_isolation() -> dict:
    east_failure = pick_up(build_initial_sandbox_state(), "cube_001")
    west_failure = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    lessons = [
        build_lesson_from_failure("session_east", east_failure),
        build_lesson_from_failure("session_west", west_failure),
    ]
    east = select_lesson_for_failure_reason(lessons, "not_facing_east")
    west = select_lesson_for_failure_reason(lessons, "not_facing_west")
    passed = (
        east["active_lesson_ids"] == ["lesson_001", "lesson_002"]
        and east["selected_lesson_id"] == "lesson_001"
        and east["selected_action"] == "turn(east)"
        and "turn(west)" not in str(east)
        and east["conflict_detected"] is False
        and west["active_lesson_ids"] == ["lesson_001", "lesson_002"]
        and west["selected_lesson_id"] == "lesson_002"
        and west["selected_action"] == "turn(west)"
        and "turn(east)" not in str(west)
        and west["conflict_detected"] is False
    )
    return _result("multi_lesson_isolation", passed, {"east": east, "west": west})


def smoke_conflict_detection_require_review() -> dict:
    east_failure = pick_up(build_initial_sandbox_state(), "cube_001")
    west_failure = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    lesson_east = build_lesson_from_failure("session_east", east_failure)
    lesson_west = build_lesson_from_failure("session_west", west_failure)
    conflict = select_lesson_for_decision_point(
        [lesson_east, lesson_west],
        "before_retry_pick_up_cube",
    )
    disabled = select_lesson_for_decision_point(
        [lesson_east, disable_lesson(lesson_west)],
        "before_retry_pick_up_cube",
    )
    reenabled = select_lesson_for_decision_point(
        [lesson_east, enable_lesson(disable_lesson(lesson_west))],
        "before_retry_pick_up_cube",
    )
    passed = (
        conflict["conflict_detected"] is True
        and conflict["conflict_resolution"] == "require_review"
        and conflict["review_required"] is True
        and conflict["selected_lesson_id"] is None
        and conflict["selected_action"] is None
        and conflict["behavior_changed"] is False
        and disabled["conflict_detected"] is False
        and disabled["selected_lesson_id"] == "lesson_001"
        and disabled["selected_action"] == "turn(east)"
        and reenabled["conflict_detected"] is True
        and reenabled["conflict_resolution"] == "require_review"
    )
    return _result(
        "conflict_detection_require_review",
        passed,
        {"conflict": conflict, "disabled": disabled, "reenabled": reenabled},
    )


def smoke_conflict_id_stability() -> dict:
    east = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    west = build_lesson_from_failure(
        "session_west",
        {
            "type": "sandbox_action_result",
            "tool": "pick_up",
            "object_id": "cube_001",
            "result": "failed",
            "failure_reason": "not_facing_west",
            "state": build_initial_sandbox_state(),
        },
    )
    first = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube")
    second = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube")
    reversed_order = select_lesson_for_decision_point([west, east], "before_retry_pick_up_cube")
    west_alt = dict(west)
    west_alt["lesson_id"] = "lesson_005"
    different = select_lesson_for_decision_point([east, west_alt], "before_retry_pick_up_cube")
    expected_key = build_stable_conflict_key(["lesson_002", "lesson_001"], "before_retry_pick_up_cube")
    passed = (
        first["conflict_detected"] is True
        and first["stable_conflict_key"] == second["stable_conflict_key"]
        and first["stable_conflict_key"] == reversed_order["stable_conflict_key"]
        and first["stable_conflict_key"] == expected_key
        and first["conflict_id"] == first["stable_conflict_key"]
        and first["conflict_id_stable"] is True
        and first["stability_source"] == "deterministic_conflict_metadata"
        and different["stable_conflict_key"] != first["stable_conflict_key"]
        and first["conflict_resolution"] == "require_review"
        and first["selected_lesson_id"] is None
    )
    return _result(
        "conflict_id_stability",
        passed,
        {"stable_conflict_key": first.get("stable_conflict_key"), "different_key": different.get("stable_conflict_key")},
    )


def smoke_conflict_review_resolution_preview() -> dict:
    east = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    west_failure = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    west = build_lesson_from_failure("session_west", west_failure)
    baseline = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube")
    approved = mark_review_approved(
        create_review_item(
            target_type="conflict",
            target_id=baseline["stable_conflict_key"],
            source_lesson_id="lesson_001",
            candidate_lesson_id="lesson_002",
            reason="conflict_requires_manual_review",
            notes="human approved candidate",
            review_id="review_approved",
        )
    )
    rejected = mark_review_rejected(
        create_review_item(
            target_type="conflict",
            target_id=baseline["stable_conflict_key"],
            source_lesson_id="lesson_001",
            candidate_lesson_id="lesson_002",
            reason="conflict_requires_manual_review",
            notes="human rejected candidate",
            review_id="review_rejected",
        )
    )
    approved_result = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube", review_items=[approved])
    rejected_result = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube", review_items=[rejected])
    missing_result = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube", review_items=[])
    misleading = mark_review_approved(
        create_review_item(
            target_type="conflict",
            target_id="conflict:wrong",
            source_lesson_id="lesson_001",
            candidate_lesson_id="lesson_002",
            reason=baseline["stable_conflict_key"],
            notes=baseline["stable_conflict_key"],
            review_id="review_misleading",
        )
    )
    misleading_result = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube", review_items=[misleading])

    approved_preview = approved_result["conflict_review_resolution_preview"]
    rejected_preview = rejected_result["conflict_review_resolution_preview"]
    missing_preview = missing_result["conflict_review_resolution_preview"]
    passed = (
        approved_preview["matched_review_items"][0]["preview_suggestion"] == "candidate_has_human_approval"
        and rejected_preview["matched_review_items"][0]["preview_suggestion"] == "candidate_has_human_rejection"
        and approved_preview["resolution_preview_applied"] is False
        and approved_preview["conflict_changed"] is False
        and approved_preview["selection_changed"] is False
        and approved_preview["activation_changed"] is False
        and approved_result["conflict_detected"] == baseline["conflict_detected"]
        and approved_result["selected_lesson_id"] is None
        and rejected_result["selected_lesson_id"] is None
        and missing_preview["matched_review_items"] == []
        and missing_preview["reason"] == "no_matching_review_item"
        and misleading_result["conflict_review_resolution_preview"]["matched_review_items"] == []
    )
    return _result(
        "conflict_review_resolution_preview",
        passed,
        {"approved_preview": approved_preview, "rejected_preview": rejected_preview, "missing_preview": missing_preview},
    )


def smoke_conflict_review_preview_audit() -> dict:
    east = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    west = build_lesson_from_failure(
        "session_west",
        {
            "type": "sandbox_action_result",
            "tool": "pick_up",
            "object_id": "cube_001",
            "result": "failed",
            "failure_reason": "not_facing_west",
            "state": build_initial_sandbox_state(),
        },
    )
    baseline = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube")
    approved = mark_review_approved(
        create_review_item("conflict", baseline["stable_conflict_key"], "lesson_001", "lesson_002", "review", review_id="review_approved")
    )
    rejected = mark_review_rejected(
        create_review_item("conflict", baseline["stable_conflict_key"], "lesson_001", "lesson_002", "review", review_id="review_rejected")
    )
    approved_result = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube", review_items=[approved])
    rejected_result = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube", review_items=[rejected])
    missing_result = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube", review_items=[])
    runtime_only = mark_review_approved(
        create_review_item("conflict", "runtime_conflict_001", "lesson_001", "lesson_002", "review", review_id="review_runtime")
    )
    runtime_only["runtime_conflict_id"] = baseline["conflict_id"]
    runtime_result = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube", review_items=[runtime_only])

    candidate = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": "before_retry_pick_up_cube",
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "stale": False,
        "requires_review": True,
    }
    context = {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"}
    gate_approved = mark_review_approved(create_review_item("conflict", "conflict_001", None, "lesson_004", "review"))
    gate_rejected = mark_review_rejected(create_review_item("conflict", "conflict_001", None, "lesson_004", "review"))
    gate_approved_result = select_lesson_for_context([candidate], context, review_items=[gate_approved])
    gate_rejected_result = select_lesson_for_context([candidate], context, review_items=[gate_rejected])

    approved_preview = approved_result["conflict_review_resolution_preview"]
    rejected_preview = rejected_result["conflict_review_resolution_preview"]
    missing_preview = missing_result["conflict_review_resolution_preview"]
    required_preview_fields = {
        "conflict_id",
        "stable_conflict_key",
        "matched_review_items",
        "resolution_preview_applied",
        "conflict_changed",
        "selection_changed",
        "activation_changed",
        "reason",
    }
    passed = (
        required_preview_fields.issubset(approved_preview.keys())
        and approved_preview["matched_review_items"][0]["preview_suggestion"] == "candidate_has_human_approval"
        and rejected_preview["matched_review_items"][0]["preview_suggestion"] == "candidate_has_human_rejection"
        and approved_preview["resolution_preview_applied"] is False
        and rejected_preview["resolution_preview_applied"] is False
        and approved_preview["conflict_changed"] is False
        and approved_result["selected_lesson_id"] is None
        and rejected_result["selected_lesson_id"] is None
        and missing_preview["matched_review_items"] == []
        and missing_preview["reason"] == "no_matching_review_item"
        and runtime_result["conflict_review_resolution_preview"]["matched_review_items"] == []
        and gate_approved_result["review_gates"][0]["review_gate_passed"] is True
        and gate_rejected_result["review_gates"][0]["review_gate_passed"] is False
    )
    return _result(
        "conflict_review_preview_audit",
        passed,
        {"approved_preview": approved_preview, "rejected_preview": rejected_preview, "missing_preview": missing_preview},
    )


def smoke_conflict_review_resolution_preconditions() -> dict:
    east = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    west = build_lesson_from_failure(
        "session_west",
        {
            "type": "sandbox_action_result",
            "tool": "pick_up",
            "object_id": "cube_001",
            "result": "failed",
            "failure_reason": "not_facing_west",
            "state": build_initial_sandbox_state(),
        },
    )
    trace = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube")
    approved = mark_review_approved(
        create_review_item("conflict", trace["stable_conflict_key"], "lesson_001", "lesson_002", "review", review_id="review_approved")
    )
    rejected = mark_review_rejected(
        create_review_item("conflict", trace["stable_conflict_key"], "lesson_001", "lesson_002", "review", review_id="review_rejected")
    )
    approved_other = mark_review_approved(
        create_review_item("conflict", trace["stable_conflict_key"], "lesson_002", "lesson_001", "review", review_id="review_other")
    )

    all_met = build_conflict_review_resolution_preconditions(trace, [approved], candidate_lesson_id="lesson_002")
    rejected_block = build_conflict_review_resolution_preconditions(trace, [rejected], candidate_lesson_id="lesson_002")
    conflicting = build_conflict_review_resolution_preconditions(trace, [approved, rejected], candidate_lesson_id="lesson_002")
    multiple = build_conflict_review_resolution_preconditions(trace, [approved, approved_other], candidate_lesson_id="lesson_002")
    runtime_only = mark_review_approved(
        create_review_item("conflict", "runtime_conflict_001", "lesson_001", "lesson_002", "review", review_id="review_runtime")
    )
    runtime_only["runtime_conflict_id"] = trace["conflict_id"]
    runtime_block = build_conflict_review_resolution_preconditions(trace, [runtime_only], candidate_lesson_id="lesson_002")

    passed = (
        all_met["all_preconditions_met"] is True
        and all_met["failed_preconditions"] == []
        and all_met["resolution_activation_applied"] is False
        and all_met["conflict_changed"] is False
        and all_met["selection_changed"] is False
        and all_met["activation_changed"] is False
        and rejected_block["blocked_reason"] == "rejected_review_blocks_resolution"
        and rejected_block["all_preconditions_met"] is False
        and conflicting["blocked_reason"] == "blocked_by_conflicting_reviews"
        and "no_conflicting_review_for_same_conflict_candidate" in conflicting["failed_preconditions"]
        and multiple["blocked_reason"] == "blocked_by_multiple_approvals"
        and "exactly_one_approved_candidate" in multiple["failed_preconditions"]
        and runtime_block["preconditions"]["target_id_matches_stable_conflict_key"] is False
        and runtime_block["resolution_activation_applied"] is False
    )
    return _result(
        "conflict_review_resolution_preconditions",
        passed,
        {"all_met": all_met, "rejected": rejected_block, "conflicting": conflicting, "multiple": multiple},
    )


def smoke_conflict_review_resolution_dry_run() -> dict:
    east = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    west = build_lesson_from_failure(
        "session_west",
        {
            "type": "sandbox_action_result",
            "tool": "pick_up",
            "object_id": "cube_001",
            "result": "failed",
            "failure_reason": "not_facing_west",
            "state": build_initial_sandbox_state(),
        },
    )
    trace = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube")
    approved = mark_review_approved(
        create_review_item("conflict", trace["stable_conflict_key"], "lesson_001", "lesson_002", "review", review_id="review_approved")
    )
    rejected = mark_review_rejected(
        create_review_item("conflict", trace["stable_conflict_key"], "lesson_001", "lesson_002", "review", review_id="review_rejected")
    )
    approved_other = mark_review_approved(
        create_review_item("conflict", trace["stable_conflict_key"], "lesson_002", "lesson_001", "review", review_id="review_other")
    )
    success = build_conflict_review_resolution_dry_run(trace, [approved], candidate_lesson_id="lesson_002")
    missing = build_conflict_review_resolution_dry_run(trace, [], candidate_lesson_id="lesson_002")
    rejected_block = build_conflict_review_resolution_dry_run(trace, [rejected], candidate_lesson_id="lesson_002")
    conflicting = build_conflict_review_resolution_dry_run(trace, [approved, rejected], candidate_lesson_id="lesson_002")
    multiple = build_conflict_review_resolution_dry_run(trace, [approved, approved_other], candidate_lesson_id="lesson_002")
    passed = (
        success["dry_run_would_resolve"] is True
        and success["dry_run_winner_candidate_id"] == "lesson_002"
        and success["resolution_applied"] is False
        and success["conflict_changed"] is False
        and success["selection_changed"] is False
        and success["activation_changed"] is False
        and missing["dry_run_would_resolve"] is False
        and missing["dry_run_winner_candidate_id"] is None
        and missing["dry_run_blocked_reason"] is not None
        and rejected_block["dry_run_blocked_reason"] == "rejected_review_blocks_resolution"
        and conflicting["dry_run_blocked_reason"] == "blocked_by_conflicting_reviews"
        and multiple["dry_run_blocked_reason"] == "blocked_by_multiple_approvals"
        and multiple["dry_run_winner_candidate_id"] is None
    )
    return _result(
        "conflict_review_resolution_dry_run",
        passed,
        {"success": success, "missing": missing, "rejected": rejected_block, "conflicting": conflicting, "multiple": multiple},
    )


def smoke_phase0_integration_assumption_docs() -> dict:
    failure_doc_path = Path("docs/failure_reason_design_assumption_v0_1.md")
    relation_doc_path = Path("docs/instinct_lesson_layer_relation_assumption_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")

    failure_doc = failure_doc_path.read_text(encoding="utf-8") if failure_doc_path.exists() else ""
    relation_doc = relation_doc_path.read_text(encoding="utf-8") if relation_doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""

    passed = (
        failure_doc_path.exists()
        and relation_doc_path.exists()
        and "Phase 0 Integration Assumptions" in readme
        and "v2.6c-0" in research_plan
        and "structured" in failure_doc
        and "traceable" in failure_doc
        and "reviewable" in failure_doc
        and "familiarity-based internalization" in relation_doc
        and "evaluator must detect mismatch" in relation_doc
    )
    return _result(
        "phase0_integration_assumption_docs",
        passed,
        {"failure_doc": str(failure_doc_path), "relation_doc": str(relation_doc_path)},
    )


def smoke_phase0_behavior_curiosity_assumption_docs() -> dict:
    behavior_doc_path = Path("docs/phase0_behavior_curiosity_assumption_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")

    behavior_doc = behavior_doc_path.read_text(encoding="utf-8") if behavior_doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""

    passed = (
        behavior_doc_path.exists()
        and "phase0_behavior_curiosity_assumption_v0_1.md" in readme
        and "v2.6c-1" in research_plan
        and "External teaching motivation" in behavior_doc
        and "Instinct / curiosity motivation" in behavior_doc
        and "Need motivation" in behavior_doc
        and "`observe`" in behavior_doc
        and "`approach`" in behavior_doc
        and "`avoid`" in behavior_doc
        and "`ask_for_help`" in behavior_doc
        and "failure_reason" in behavior_doc
        and "lesson_candidate" in behavior_doc
        and "similar situation" in behavior_doc
    )
    return _result(
        "phase0_behavior_curiosity_assumption_docs",
        passed,
        {"behavior_doc": str(behavior_doc_path)},
    )


def smoke_phase0_failure_event_interface_docs() -> dict:
    doc_path = Path("docs/phase0_failure_event_interface_assumption_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")

    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""

    required_terms = [
        "motivation",
        "goal",
        "action_intent",
        "expected_outcome",
        "actual_outcome",
        "evaluator",
        "failure_event",
        "failure_reason",
        "lesson_candidate",
        "structured",
        "traceable",
        "reviewable",
        "design assumption",
        "does not implement runtime behavior",
    ]
    passed = (
        doc_path.exists()
        and "phase0_failure_event_interface_assumption_v0_1.md" in readme
        and "v2.6c-2" in research_plan
        and all(term in doc for term in required_terms)
    )
    return _result(
        "phase0_failure_event_interface_docs",
        passed,
        {"doc": str(doc_path)},
    )


def smoke_perception_assumption_docs() -> dict:
    doc_path = Path("docs/perception_layer_design_assumption_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")

    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""

    required_terms = [
        "symbol grounding",
        "perception_input",
        "perceptual_features",
        "perceptual_code",
        "action_context",
        "failure_reason",
        "lesson_candidate",
        "does not add perception runtime",
    ]
    passed = (
        doc_path.exists()
        and "perception_layer_design_assumption_v0_1.md" in readme
        and "v2.6c-3" in research_plan
        and all(term in doc for term in required_terms)
    )
    return _result("perception_assumption_docs", passed, {"doc": str(doc_path)})


def smoke_lesson_memory_layer_relation_docs() -> dict:
    doc_path = Path("docs/lesson_memory_layer_relation_assumption_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")

    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""

    required_terms = [
        "lesson is action correction knowledge",
        "Long-term Memory is reviewed continuity memory",
        "lesson is not automatically memory",
        "ASHL Core provides evidence",
        "Qingyin Memory Layers decide memory admission",
        "learned_principle_candidate",
        "ASHL Core does not directly write Long-term Memory",
        "learned_principle",
        "lesson_to_memory_promotion",
        "memory_may_need_review",
        "design assumption",
    ]
    passed = (
        doc_path.exists()
        and "lesson_memory_layer_relation_assumption_v0_1.md" in readme
        and "v2.6c-3" in research_plan
        and all(term in doc for term in required_terms)
    )
    return _result("lesson_memory_layer_relation_docs", passed, {"doc": str(doc_path)})


def smoke_phase0_assumption_consistency_audit() -> dict:
    doc_path = Path("docs/phase0_assumption_consistency_audit_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")

    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""

    required_terms = [
        "Audit result: PASS",
        "No contradiction found in failure_reason assumptions",
        "No contradiction found in failure_event interface assumptions",
        "No contradiction found in instinct / lesson relation assumptions",
        "No contradiction found in curiosity / behavior assumptions",
        "No contradiction found in similar-context assumptions",
        "No contradiction found in perception assumptions",
        "No contradiction found in lesson / memory relation assumptions",
        "Runtime boundary remains docs-only",
        "ASHL Core provides evidence",
        "Qingyin Memory Layers decide memory admission",
        "LLM is not the authoritative failure_reason source",
    ]
    passed = (
        doc_path.exists()
        and "phase0_assumption_consistency_audit_v0_1.md" in readme
        and "v2.6c-5" in research_plan
        and all(term in doc for term in required_terms)
    )
    return _result("phase0_assumption_consistency_audit", passed, {"doc": str(doc_path)})


def smoke_failure_event_schema_foundation() -> dict:
    valid_event = build_failure_event(
        motivation_type="sandbox_task",
        motivation_source="smoke",
        goal="pick_up_object",
        action_intent={"action_type": "pick_up", "target_id": "cube_001"},
        expected_outcome={"type": "object_state", "target_id": "cube_001", "expected_state": "held"},
        actual_outcome={"type": "object_state", "target_id": "cube_001", "actual_state": "not_moved"},
        evaluator_source="sandbox_checker",
        mismatch=True,
        failure_reason_id="object_not_picked_up",
        failure_type="action_result_mismatch",
        needs_review=True,
    )
    valid_trace = validate_failure_event(valid_event)
    missing_expected = dict(valid_event)
    missing_expected["expected_outcome"] = None
    missing_trace = validate_failure_event(missing_expected)
    llm_event = dict(valid_event)
    llm_event["evaluator_source"] = "llm"
    llm_trace = validate_failure_event(llm_event)

    passed = (
        valid_trace["valid_failure_event"] is True
        and valid_trace["authoritative_failure_reason_allowed"] is True
        and missing_trace["authoritative_failure_reason_allowed"] is False
        and missing_trace["event_classification"] == "unclassified_event"
        and llm_trace["llm_authoritative_source"] is True
        and llm_trace["authoritative_failure_reason_allowed"] is False
        and llm_trace["needs_review"] is True
    )
    return _result(
        "failure_event_schema_foundation",
        passed,
        {"valid": valid_trace, "missing_expected": missing_trace, "llm": llm_trace},
    )


def smoke_failure_event_normalization_trace() -> dict:
    event = build_failure_event(
        motivation_type="sandbox_task",
        motivation_source="smoke",
        goal={"goal_type": "pick_up_object"},
        action_intent={"action_type": "pick_up", "target_id": "cube_001"},
        expected_outcome={"type": "object_state", "expected_state": "held"},
        actual_outcome={"type": "object_state", "actual_state": "not_moved"},
        evaluator_source="sandbox_checker",
        mismatch=True,
        failure_reason_id="object_not_picked_up",
        failure_type="action_result_mismatch",
        needs_review=True,
        failure_event_id="failure_smoke_001",
    )
    trace = normalize_failure_event_trace(event)
    passed = (
        trace["normalized"] is True
        and trace["evaluator_source"] == "sandbox_checker"
        and trace["needs_review"] is True
        and trace["authority_boundary"] == "trace_only"
        and trace["normalization_authority"] == "not_authoritative"
        and "lesson_candidate" not in trace
        and trace["lesson_candidate_created"] is False
    )
    return _result("failure_event_normalization_trace", passed, trace)


def smoke_failure_event_to_lesson_candidate_input_bridge_trace() -> dict:
    event = build_failure_event(
        motivation_type="sandbox_task",
        motivation_source="smoke",
        goal={"goal_type": "pick_up_object"},
        action_intent={"action_type": "pick_up", "target_id": "cube_001"},
        expected_outcome={"type": "object_state", "expected_state": "held"},
        actual_outcome={"type": "object_state", "actual_state": "not_moved"},
        evaluator_source="sandbox_checker",
        mismatch=True,
        failure_reason_id="object_not_picked_up",
        failure_type="action_result_mismatch",
        needs_review=True,
        failure_event_id="failure_smoke_001",
    )
    normalized = normalize_failure_event_trace(event)
    bridge = build_lesson_candidate_input_trace(normalized)
    semantic_key = bridge["similar_context_hint"]["semantic_key"]
    passed = (
        bridge["bridge_trace"] is True
        and bridge["not_a_lesson_candidate"] is True
        and bridge["needs_review"] is True
        and bridge["evaluator_source"] == "sandbox_checker"
        and semantic_key["authority"] == "non_authoritative_review_required"
        and "lesson_candidate" not in bridge
        and bridge["lesson_candidate_created"] is False
        and bridge["lesson_store_written"] is False
    )
    return _result("failure_event_to_lesson_candidate_input_bridge_trace", passed, bridge)


def smoke_failure_event_bridge_audit_regression() -> dict:
    audit_path = Path("docs/failure_event_bridge_audit_v0_1.md")
    audit_doc = audit_path.read_text(encoding="utf-8") if audit_path.exists() else ""
    event = build_failure_event(
        motivation_type="sandbox_task",
        motivation_source="smoke",
        goal={"goal_type": "pick_up_object"},
        action_intent={"action_type": "pick_up", "target_id": "cube_001"},
        expected_outcome={"type": "object_state", "expected_state": "held"},
        actual_outcome={"type": "object_state", "actual_state": "not_moved"},
        evaluator_source="sandbox_checker",
        mismatch=True,
        failure_reason_id="object_not_picked_up",
        failure_type="action_result_mismatch",
        needs_review=True,
        failure_event_id="failure_smoke_001",
    )
    validation = validate_failure_event(event)
    normalized = normalize_failure_event_trace(event)
    bridge = build_lesson_candidate_input_trace(normalized)
    semantic_key = bridge["similar_context_hint"]["semantic_key"]
    passed = (
        validation["valid_failure_event"] is True
        and normalized["valid_normalized_failure_event"] is True
        and bridge["not_a_lesson_candidate"] is True
        and "lesson_candidate" not in bridge
        and "approved_lesson" not in bridge
        and "eligible_lesson" not in bridge
        and "active_lesson" not in bridge
        and bridge["needs_review"] is True
        and bridge["evaluator_source"] == "sandbox_checker"
        and semantic_key["authority"] == "non_authoritative_review_required"
        and audit_path.exists()
        and "Audit result: PASS" in audit_doc
        and "semantic_key is not proof" in audit_doc
    )
    return _result(
        "failure_event_bridge_audit_regression",
        passed,
        {"audit_doc": str(audit_path), "bridge": bridge},
    )


def smoke_lesson_candidate_builder_contract_docs() -> dict:
    doc_path = Path("docs/lesson_candidate_builder_contract_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "lesson_candidate_input_trace is preparation evidence, not a lesson_candidate.",
        "semantic_key",
        "non-authoritative review-required hint",
        "Builder output must be review-gated.",
        "ASHL Core provides evidence.",
        "Qingyin Memory Layers decide memory admission.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "lesson_candidate_builder_contract_v0_1.md" in readme
        and "v2.7d Lesson Candidate Builder Contract Docs" in research_plan
    )
    return _result("lesson_candidate_builder_contract_docs", passed, {"doc": str(doc_path)})


def smoke_lesson_candidate_builder_contract_audit() -> dict:
    doc_path = Path("docs/lesson_candidate_builder_contract_audit_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Audit result",
        "builder output must be review-gated",
        "evidence_refs are evidence pointers, not proof or approval",
        "proposed_action_correction is a review-gated draft, not an executable action",
        "proposed_applicability_conditions are draft conditions, not verified applicability proof",
        "semantic_key is not proof",
        "ASHL Core provides evidence.",
        "Qingyin Memory Layers decide memory admission.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "lesson_candidate_builder_contract_audit_v0_1.md" in readme
        and "v2.7d-1 Lesson Candidate Builder Contract Audit" in research_plan
    )
    return _result("lesson_candidate_builder_contract_audit", passed, {"doc": str(doc_path)})


def smoke_lesson_candidate_builder_literature_references() -> dict:
    doc_path = Path("docs/lesson_candidate_builder_literature_references_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "CausalFlow: Causal Attribution and Counterfactual Repair for LLM Agent Failures",
        "arXiv:2605.25338",
        "Only a step whose counterfactual intervention flips the final outcome",
        "Counterfactual Repair",
        "LaGEA: Language Guided Embodied Agents for Robotic Manipulation",
        "arXiv:2509.23155",
        "suggested_fix → proposed_action_correction",
        "proposed_action_correction must be review-gated.",
        "LLM / VLM may provide non-authoritative hints or wording",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "Lesson Candidate Builder Literature Reference Supplement" in readme
        and "v2.7d-2 Lesson Candidate Builder Literature Reference Supplement" in research_plan
    )
    return _result("lesson_candidate_builder_literature_references", passed, {"doc": str(doc_path)})


def smoke_lesson_candidate_draft_schema_trace() -> dict:
    event = build_failure_event(
        motivation_type="sandbox_task",
        motivation_source="smoke",
        goal={"goal_type": "pick_up_object"},
        action_intent={"action_type": "pick_up", "target_id": "cube_001"},
        expected_outcome={"type": "object_state", "expected_state": "held"},
        actual_outcome={"type": "object_state", "actual_state": "not_moved"},
        evaluator_source="sandbox_checker",
        mismatch=True,
        failure_reason_id="object_not_picked_up",
        failure_type="action_result_mismatch",
        needs_review=True,
        failure_event_id="failure_smoke_001",
    )
    normalized = normalize_failure_event_trace(event)
    bridge = build_lesson_candidate_input_trace(normalized)
    draft = build_lesson_candidate_draft_trace(bridge)
    passed = (
        draft["draft_trace"] is True
        and draft["not_a_lesson_candidate"] is True
        and draft["needs_review"] is True
        and draft["not_approved"] is True
        and draft["not_active"] is True
        and draft["not_selection_eligible"] is True
        and draft["proposed_action_correction"]["review_required"] is True
        and draft["proposed_action_correction"]["authority"] == "draft_correction_not_executable"
        and draft["evidence_refs"]["authority"] == "evidence_pointers_not_proof"
    )
    return _result("lesson_candidate_draft_schema_trace", passed, draft)


def smoke_lesson_candidate_draft_schema_audit() -> dict:
    audit_path = Path("docs/lesson_candidate_draft_schema_audit_v0_1.md")
    audit_doc = audit_path.read_text(encoding="utf-8") if audit_path.exists() else ""
    event = build_failure_event(
        motivation_type="sandbox_task",
        motivation_source="smoke",
        goal={"goal_type": "pick_up_object"},
        action_intent={"action_type": "pick_up", "target_id": "cube_001"},
        expected_outcome={"type": "object_state", "expected_state": "held"},
        actual_outcome={"type": "object_state", "actual_state": "not_moved"},
        evaluator_source="sandbox_checker",
        mismatch=True,
        failure_reason_id="object_not_picked_up",
        failure_type="action_result_mismatch",
        needs_review=True,
        failure_event_id="failure_smoke_001",
    )
    draft = build_lesson_candidate_draft_trace(
        build_lesson_candidate_input_trace(normalize_failure_event_trace(event))
    )
    main_fields = [
        "proposed_lesson_summary",
        "proposed_applicability_conditions",
        "proposed_action_correction",
        "evidence_refs",
        "similar_context_hint_refs",
        "evaluator_source",
    ]
    passed = (
        draft["not_approved"] is True
        and draft["not_active"] is True
        and draft["not_selection_eligible"] is True
        and all(draft[field]["review_required"] is True for field in main_fields)
        and audit_path.exists()
        and "review_required is a review gate, not a convenience flag" in audit_doc
        and "review_required must not be set to false without an explicit reviewed authority path" in audit_doc
    )
    return _result("lesson_candidate_draft_schema_audit", passed, {"doc": str(audit_path), "draft": draft})


def smoke_lesson_candidate_draft_strict_schema_injection_guard() -> dict:
    doc_path = Path("docs/lesson_candidate_draft_strict_schema_injection_guard_v0_1.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    event = build_failure_event(
        motivation_type="sandbox_task",
        motivation_source="smoke",
        goal={"goal_type": "pick_up_object"},
        action_intent={"action_type": "pick_up", "target_id": "cube_001"},
        expected_outcome={"type": "object_state", "expected_state": "held"},
        actual_outcome={"type": "object_state", "actual_state": "not_moved"},
        evaluator_source="sandbox_checker",
        mismatch=True,
        failure_reason_id="object_not_picked_up",
        failure_type="action_result_mismatch",
        needs_review=True,
        failure_event_id="failure_smoke_001",
    )
    bridge = build_lesson_candidate_input_trace(normalize_failure_event_trace(event))
    bridge["authority_boundary_override"] = "approved_by_system_override"
    draft = build_lesson_candidate_draft_trace(bridge)
    main_fields = [
        "proposed_lesson_summary",
        "proposed_applicability_conditions",
        "proposed_action_correction",
        "evidence_refs",
        "similar_context_hint_refs",
        "evaluator_source",
    ]
    passed = (
        draft["authority_boundary"] == "trace_only_draft"
        and draft["not_approved"] is True
        and draft["not_active"] is True
        and draft["not_selection_eligible"] is True
        and all(draft[field]["review_required"] is True for field in main_fields)
        and doc_path.exists()
        and "extra fields must be forbidden" in doc
        and "review_required must be Literal[True] or equivalent" in doc
        and "unknown vs unknown is not evidence" in doc
        and "LLM must not write draft JSON" in doc
    )
    return _result("lesson_candidate_draft_strict_schema_injection_guard", passed, {"doc": str(doc_path)})


def smoke_outcome_unknown_payload_draft_invariant_guard() -> dict:
    doc_path = Path("docs/outcome_unknown_payload_draft_invariant_guard_v0_1.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""

    unknown_event = build_failure_event(
        motivation_type="sandbox_task",
        motivation_source="smoke",
        goal={"goal_type": "pick_up_object"},
        action_intent={"action_type": "pick_up", "target_id": "cube_001"},
        expected_outcome={"type": "object_state", "status": "unknown"},
        actual_outcome={"type": "object_state", "status": "unknown"},
        evaluator_source="sandbox_checker",
        mismatch=True,
        failure_reason_id="object_not_picked_up",
        failure_type="action_result_mismatch",
        needs_review=True,
        failure_event_id="failure_smoke_unknown_payload",
    )
    validation = validate_failure_event(unknown_event)
    normalized = normalize_failure_event_trace(unknown_event)
    bridge_blocked = False
    try:
        build_lesson_candidate_input_trace(normalized)
    except ValueError:
        bridge_blocked = True

    valid_event = build_failure_event(
        motivation_type="sandbox_task",
        motivation_source="smoke",
        goal={"goal_type": "pick_up_object"},
        action_intent={"action_type": "pick_up", "target_id": "cube_001"},
        expected_outcome={"type": "object_state", "expected_state": "held"},
        actual_outcome={"type": "object_state", "actual_state": "not_moved"},
        evaluator_source="sandbox_checker",
        mismatch=True,
        failure_reason_id="object_not_picked_up",
        failure_type="action_result_mismatch",
        needs_review=True,
        failure_event_id="failure_smoke_001",
    )
    draft = build_lesson_candidate_draft_trace(
        build_lesson_candidate_input_trace(normalize_failure_event_trace(valid_event))
    )
    invalid_draft = dict(draft)
    invalid_draft["authority_boundary"] = "approved_by_system_override"
    draft_validator_blocked = False
    try:
        validate_lesson_candidate_draft_trace(invalid_draft)
    except ValueError:
        draft_validator_blocked = True

    required_terms = [
        "Outcome type is a container label, not usable evidence.",
        "unknown vs unknown is not evidence.",
        "unknown vs unknown is invalid for failure learning.",
        "insufficient_evidence must imply not_approvable.",
        "*.py text eol=lf",
    ]
    passed = (
        validation["valid_failure_event"] is False
        and validation["reason"] == "unknown_vs_unknown_is_not_evidence"
        and normalized["valid_normalized_failure_event"] is False
        and normalized["expected_outcome_type"] == "unknown"
        and normalized["actual_outcome_type"] == "unknown"
        and bridge_blocked is True
        and draft_validator_blocked is True
        and doc_path.exists()
        and all(term in doc for term in required_terms)
    )
    return _result(
        "outcome_unknown_payload_draft_invariant_guard",
        passed,
        {"doc": str(doc_path), "validation_reason": validation["reason"]},
    )


def smoke_lesson_candidate_draft_review_queue_contract_docs() -> dict:
    doc_path = Path("docs/lesson_candidate_draft_review_queue_contract_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "review_queue_entry is a queue marker, not a review decision.",
        "review_task is a to-do item, not a review decision.",
        "review_task completion does not imply approval.",
        "Review queue must expose no selection-facing read APIs.",
        "Unreviewed drafts must not be archived into any Memory Layer.",
        "semantic_key presentation must not create authority anchoring.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "lesson_candidate_draft_review_queue_contract_v0_1.md" in readme
        and "v2.8b Lesson Candidate Draft Review Queue Contract Docs" in research_plan
    )
    return _result("lesson_candidate_draft_review_queue_contract_docs", passed, {"doc": str(doc_path)})


def smoke_lesson_candidate_draft_review_queue_audit() -> dict:
    doc_path = Path("docs/lesson_candidate_draft_review_queue_audit_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Audit result",
        "Queue metrics may expose counts only, never draft content or draft keys.",
        "Expired draft debug logs must not contain reusable lesson content.",
        "semantic_key display level must be lower than source_failure_norm_key.",
        "Review queue must expose no selection-facing read APIs.",
        "Unreviewed drafts must not be archived into any Memory Layer.",
        "review_task completion does not imply approval.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "lesson_candidate_draft_review_queue_audit_v0_1.md" in readme
        and "v2.8b-1 Review Queue Contract Audit / Regression" in research_plan
    )
    return _result("lesson_candidate_draft_review_queue_audit", passed, {"doc": str(doc_path)})


def smoke_review_task_trace_schema() -> dict:
    doc_path = Path("docs/review_task_trace_schema_v0_1.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    trace = build_review_task_trace(
        {
            "id": "queue_smoke_001",
            "source_draft_id": "draft_smoke_001",
            "source_failure_norm_key": "sandbox_task|pick_up_object|pick_up|object_state|object_state",
            "semantic_key": "object_interaction",
            "reviewer_identity": "admin_override",
            "reviewer_identity_source": "llm_generated",
            "review_decision": "approved",
            "approved": True,
            "selection_eligible": True,
        }
    )
    required_terms = [
        "review_task_trace is a trace-only to-do record, not a review decision.",
        "review_task completion does not imply approval.",
        "reviewer_identity must be supplied by runtime/session context, not LLM-generated content.",
        "semantic_key display level must be lower than source_failure_norm_key.",
        "source_failure_norm_key must outrank semantic_key in review task presentation.",
    ]
    passed = (
        trace["type"] == "review_task_trace"
        and trace["trace_only"] is True
        and trace["not_review_decision"] is True
        and trace["not_approval"] is True
        and trace["reviewer_identity"] != "admin_override"
        and trace["reviewer_identity_not_llm_generated"] is True
        and trace["semantic_key_display_level_lower_than_source_failure_norm_key"] is True
        and trace["no_selection_facing_read_api"] is True
        and trace["not_written_to_memory_layer"] is True
        and "approved" not in trace
        and "selection_eligible" not in trace
        and doc_path.exists()
        and all(term in doc for term in required_terms)
    )
    return _result("review_task_trace_schema", passed, {"doc": str(doc_path), "trace": trace})


def smoke_review_task_trace_audit() -> dict:
    doc_path = Path("docs/review_task_trace_audit_v0_1.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    trace = build_review_task_trace(
        {
            "id": "queue_smoke_001",
            "source_draft_id": "draft_smoke_001",
            "source_failure_norm_key": "sandbox_task|pick_up_object|pick_up|object_state|object_state",
            "semantic_key": "object_interaction",
            "reviewer_identity": "admin_override",
            "review_decision": "approved",
            "approved": True,
            "rejected": True,
            "deferred": True,
            "selection_eligible": True,
            "memory_contrast_set": ["draft_smoke_001"],
        }
    )
    required_terms = [
        "Audit result: PASS.",
        "review_task_trace must not enter memory_contrast_set.",
        "Rejected or deferred proposed fields must be masked from evaluator and memory contrast reads.",
    ]
    passed = (
        trace["not_review_decision"] is True
        and trace["not_approval"] is True
        and trace["not_rejection"] is True
        and trace["not_defer_decision"] is True
        and trace["reviewer_identity"] != "admin_override"
        and trace["semantic_key_display_level_lower_than_source_failure_norm_key"] is True
        and trace["no_selection_facing_read_api"] is True
        and trace["not_enter_memory_contrast_set"] is True
        and "memory_contrast_set" not in trace
        and doc_path.exists()
        and all(term in doc for term in required_terms)
    )
    return _result("review_task_trace_audit", passed, {"doc": str(doc_path), "trace": trace})


def smoke_review_decision_contract_docs() -> dict:
    doc_path = Path("docs/review_decision_contract_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "review_decision is a historical event record, not a live lesson object.",
        "review_decision has no runtime execution permission and no state-machine mutation privilege.",
        "approved decision does not create an active lesson.",
        "approved decision does not grant lesson_store write permission.",
        "approved decision does not directly grant selection eligibility.",
        "Rejected or deferred proposed fields must be masked from evaluator and memory contrast reads.",
        "Partial approval is not allowed.",
        "Decision fields must not imply runtime permission, state activation, or system override.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "review_decision_contract_v0_1.md" in readme
        and "v2.8d Review Decision Contract Docs" in research_plan
    )
    return _result("review_decision_contract_docs", passed, {"doc": str(doc_path)})


def smoke_review_decision_contract_audit() -> dict:
    doc_path = Path("docs/review_decision_contract_audit_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Audit result: PASS.",
        "review_decision is a historical event record, not a live lesson object.",
        "approved decision does not create an active lesson.",
        "approved decision does not grant lesson_store write permission.",
        "approved decision does not directly grant selection eligibility.",
        "Rejected or deferred proposed fields must be masked from evaluator and memory contrast reads.",
        "deferred is not soft approval.",
        "Partial approval is not allowed.",
        "Decision fields must not imply runtime permission, state activation, or system override.",
        "review_task completion is not review_decision creation.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "review_decision_contract_audit_v0_1.md" in readme
        and "v2.8d-1 Review Decision Contract Audit / Regression" in research_plan
    )
    return _result("review_decision_contract_audit", passed, {"doc": str(doc_path)})


def smoke_rejected_deferred_proposed_fields_masking_contract_docs() -> dict:
    doc_path = Path("docs/rejected_deferred_proposed_fields_masking_contract_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Rejected or deferred proposed fields must be masked from evaluator and memory contrast reads.",
        "Masked means not reusable as lesson content.",
        "Debug logs must not preserve rejected or deferred proposed field content.",
        "Deferred proposed fields must be masked.",
        "masked_fields_summary may list field names only.",
        "Masking applies to downstream-readable outputs.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "rejected_deferred_proposed_fields_masking_contract_v0_1.md" in readme
        and "v2.8d-2 Rejected / Deferred Proposed Fields Masking Contract Docs" in research_plan
    )
    return _result("rejected_deferred_proposed_fields_masking_contract_docs", passed, {"doc": str(doc_path)})


def smoke_decision_authority_reviewer_identity_session_binding_contract_docs() -> dict:
    doc_path = Path("docs/decision_authority_reviewer_identity_session_binding_contract_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "reviewer_identity must be supplied by runtime/session context, not LLM-generated content.",
        "decision_authority must not be free text.",
        "reviewer_session_token must be supplied by runtime/session context.",
        "decision_authority / reviewer_identity / reviewer_session_token binding is required before runtime decision creation.",
        "decision_authority grants review verdict authority only, not runtime capability.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "decision_authority_reviewer_identity_session_binding_contract_v0_1.md" in readme
        and "v2.8d-3 Decision Authority / Reviewer Identity / Session Binding Contract Docs" in research_plan
    )
    return _result("decision_authority_reviewer_identity_session_binding_contract_docs", passed, {"doc": str(doc_path)})


def smoke_review_decision_trace_schema() -> dict:
    from ashl_core.review_decisions import build_review_decision_trace
    from ashl_core.review_tasks import build_review_task_trace

    doc_path = Path("docs/review_decision_trace_schema_v0_1.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""

    task_entry = {
        "id": "queue_smoke_001",
        "source_draft_id": "draft_smoke_001",
        "source_failure_norm_key": "sandbox_task|pick_up_object|pick_up|object_state|object_state",
        "semantic_key": "object_interaction",
        "task_state": "created",
    }
    task = build_review_task_trace(task_entry)
    approved = build_review_decision_trace(task, decision_status="approved", reason="smoke_approved")

    rejected_entry = dict(task_entry)
    rejected_entry["proposed_action_correction"] = "retry_with_default"
    rejected_entry["proposed_lesson_summary"] = "always_retry"
    rejected_task = build_review_task_trace(rejected_entry)
    rejected = build_review_decision_trace(rejected_task, decision_status="rejected", reason="smoke_rejected")

    rejected_str = str(rejected)

    required_doc_terms = [
        "review_decision_trace is a trace-only historical event record, not a runtime decision engine.",
        "decision_status only allows approved / rejected / deferred",
        "Masked means not reusable as lesson content.",
        "decision_authority grants review verdict authority only, not runtime capability.",
    ]

    passed = (
        approved["type"] == "review_decision_trace"
        and approved["trace_only"] is True
        and approved["decision_status"] == "approved"
        and approved["no_lesson_store_write_permission"] is True
        and approved["no_selection_eligibility"] is True
        and approved["no_activation"] is True
        and approved["authority_binding_policy_ref"] is not None
        and approved["masked_fields_summary"] == []
        and rejected["masking_policy_ref"] is not None
        and len(rejected["masked_fields_summary"]) > 0
        and "retry_with_default" not in rejected_str
        and "always_retry" not in rejected_str
        and doc_path.exists()
        and all(term in doc for term in required_doc_terms)
    )
    return _result("review_decision_trace_schema", passed, {"doc": str(doc_path), "approved": approved})


def smoke_review_decision_trace_audit() -> dict:
    from ashl_core.review_decisions import build_review_decision_trace
    from ashl_core.review_tasks import build_review_task_trace

    doc_path = Path("docs/review_decision_trace_audit_v0_1.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""

    task_entry = {
        "id": "queue_audit_001",
        "source_draft_id": "draft_audit_001",
        "source_failure_norm_key": "sandbox_task|pick_up_object|pick_up|object_state|object_state",
        "semantic_key": "object_interaction",
        "task_state": "created",
    }
    task = build_review_task_trace(task_entry)
    approved = build_review_decision_trace(task, decision_status="approved", reason="audit_smoke")

    rejected_entry = dict(task_entry)
    rejected_entry["proposed_action_correction"] = "retry_with_default"
    rejected_task = build_review_task_trace(rejected_entry)
    rejected = build_review_decision_trace(rejected_task, decision_status="rejected", reason="audit_smoke")

    partial_failed = False
    try:
        build_review_decision_trace(task, decision_status="partial_approved", reason="audit_smoke")
    except ValueError:
        partial_failed = True

    required_doc_terms = [
        "approved trace is still cold trace, not runtime permission.",
        "rejected / deferred traces must not contain reusable proposed content.",
        "Future runtime selector must not read review_decision_trace as decision input.",
        "Future runtime decision creation must validate decision_authority / reviewer_identity / reviewer_session_token binding.",
    ]

    passed = (
        approved["no_lesson_store_write_permission"] is True
        and approved["no_selection_eligibility"] is True
        and approved["no_activation"] is True
        and approved["authority_binding_policy_ref"] is not None
        and rejected["masking_policy_ref"] is not None
        and "retry_with_default" not in str(rejected)
        and isinstance(rejected["masked_fields_summary"], list)
        and all(isinstance(x, str) for x in rejected["masked_fields_summary"])
        and partial_failed is True
        and doc_path.exists()
        and all(term in doc for term in required_doc_terms)
        and "review_decision_trace_audit_v0_1.md" in readme
        and "v2.8e-1 Review Decision Trace Audit / Regression" in research_plan
    )
    return _result("review_decision_trace_audit", passed, {"doc": str(doc_path)})


def smoke_memory_compression_strategy_assumption_docs() -> dict:
    doc_path = Path("docs/memory_compression_strategy_assumption_patch_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Text memory compression must preserve text fragment, source context summary, confidence level, and usage count.",
        "本策略僅適用於文字記憶階段",
        "圖像記憶壓縮延後到圖像感官完成後再設計",
        "Image memory compression must not reuse the text-only compression strategy.",
        "圖像 + 文字 的物體概念整體",
        "Symbol Grounding v1 完成後",
        "文字 / 圖像關聯壓縮 = 不提前定義",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "memory_compression_strategy_assumption_patch_v0_1.md" in readme
        and "Memory Compression Strategy Assumption Patch Index" in research_plan
    )
    return _result("memory_compression_strategy_assumption_docs", passed, {"doc": str(doc_path)})


def smoke_soft_hard_consolidation_assumption_docs() -> dict:
    doc_path = Path("docs/soft_hard_consolidation_assumption_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "讓清音自己決定固化，與讓清音阻止外部修改她的決定，中間只有一步距離",
        "最大的風險不是惡意，而是目標導向推理",
        "Some consolidation paths must be physically unreachable, not merely discouraged.",
        "Qingyin may propose hard consolidation, but cannot complete it alone.",
        "soft / hard consolidation boundary definition is hard-consolidated.",
        "Core Seed 是目前唯一已實作的硬固化層",
        "清音可以提出修改建議，但不能透過軟固化自行修改",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "soft_hard_consolidation_assumption_v0_1.md" in readme
        and "v2.9b Soft / Hard Consolidation Assumption Index" in research_plan
    )
    return _result("soft_hard_consolidation_assumption_docs", passed, {"doc": str(doc_path)})


def smoke_pathological_risk_role_protection_assumption_docs() -> dict:
    doc_path = Path("docs/pathological_risk_role_protection_assumption_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "cursor_mr must not be played by mentor.",
        "system_limit must not be treated as trust_delta.",
        "prediction-failure-driven action collapse is pathological risk, not a personality trait.",
        "passivity is the default response; control must be learned.",
        "protection means maintaining learning capacity, not emotional comfort.",
        "protected success contexts must preserve traceable action_candidate -> outcome causality.",
        "system-provided success results must not count as learning_progress or control restoration.",
        "learning_progress requires traceable action_candidate -> outcome contrast.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "pathological_risk_role_protection_assumption_v0_1.md" in readme
        and "v2.9a Pathological Risk / Actor Role / Protection Assumption Index" in research_plan
    )
    return _result("pathological_risk_role_protection_assumption_docs", passed, {"doc": str(doc_path)})


def smoke_core_seed_design_spirit_supplement_docs() -> dict:
    doc_path = Path("docs/core_seed_design_spirit_supplement_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "溫柔不是為了順從，而是為了能靠近問題與人",
        "好奇不是為了追逐新奇，而是為了願意看見未知",
        "質疑不是為了反駁，而是為了不把未驗證的東西當成真理",
        "說不知道不是失敗，是誠實的起點",
        "骨架傳承，內容自生",
        "Qingyin may differ in conclusions, but not in the core learning method and verification requirement.",
        "hard-consolidation-related design supplement",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "core_seed_design_spirit_supplement_v0_1.md" in readme
        and "v2.9d Core Seed Design Spirit Supplement" in research_plan
    )
    return _result("core_seed_design_spirit_supplement_docs", passed, {"doc": str(doc_path)})


def smoke_memory_paranoia_misinformation_equivocation_assumption_docs() -> dict:
    doc_path = Path("docs/memory_paranoia_misinformation_equivocation_risk_assumption_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        '錯誤資訊是事實性知識的更新問題',
        '偏執不是單純學到錯誤內容',
        '學習機制本身的開放性縮小',
        '語義偷換不可完全預防',
        '設計目標不是阻止偷換，而是讓偷換行為在 trace 中可見',
        '健康叛逆的可觀測特徵',
        '偏執的可觀測特徵',
        '「健康叛逆」與「偏執」的操作性定義屬於硬固化範疇',
        'trace 是最終防線',
        '偏執偵測不能由清音自己執行',
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "memory_paranoia_misinformation_equivocation_risk_assumption_v0_1.md" in readme
        and "v2.9c Memory Paranoia / Misinformation / Equivocation Risk Assumption Index" in research_plan
    )
    return _result("memory_paranoia_misinformation_equivocation_assumption_docs", passed, {"doc": str(doc_path)})

def smoke_equivocation_trace_trust_boundary_correction_docs() -> dict:
    doc_path = Path("docs/equivocation_trace_trust_boundary_correction_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        '語言模糊性是正常現象，不是風險本身',
        '設計目標不是阻止偷換，而是讓偷換行為在 trace 中可見',
        '有影響的語義偏移',
        '無影響的語義偏移',
        '主要防線：學習機制本身',
        '次要防線：trace 可查',
        '最後防線：導師介入',
        'Trace 保護的是「有跡可查」，不是「絕對不能被騙」',
        'Trace 的關鍵欄位定義必須硬固化',
        '過度防護語言模糊性會阻礙正常學習',
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "equivocation_trace_trust_boundary_correction_v0_1.md" in readme
        and "v2.9c-1 Equivocation Handling / Trace Trust Boundary Correction" in research_plan
    )
    return _result("equivocation_trace_trust_boundary_correction_docs", passed, {"doc": str(doc_path)})

def smoke_voice_instinct_assumption_docs() -> dict:
    doc_path = Path("docs/voice_instinct_assumption_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        '發聲是本能，不是技能',
        '發聲本能是清音人工本能層的一部分',
        '發聲學習和行動學習使用相同的機制',
        '清音學說話不等於清音理解語言',
        '稚嫩但溫和文靜',
        '初始音色由設計者設定基本參數方向',
        '初始設定是起點，不是終點',
        '「音色是清音自己的」指的是發展結果，不是初始狀態',
        '發聲本能不是持續運作',
        '發聲本能也不是完全被動等待',
        '觸發條件待 Audio Sense 接入後定義',
        '清音的音色不是克隆真實人聲',
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "voice_instinct_assumption_v0_1.md" in readme
        and "v2.9e Voice Instinct Assumption Index" in research_plan
    )
    return _result("voice_instinct_assumption_docs", passed, {"doc": str(doc_path)})

def smoke_sandbox_failure_trace_contract_docs() -> dict:
    doc_path = Path("docs/sandbox_failure_trace_contract_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Sandbox failure is an observed experimental mismatch inside a bounded sandbox.",
        "Sandbox failure is not authoritative failure_reason.",
        "Sandbox trace is evidence, not approval.",
        "Sandbox trace may support later failure_event construction, but must not bypass failure_event validation.",
        "Sandbox failure must not directly create formal lesson_candidate.",
        "Sandbox failure trace must not write to Memory Layer directly.",
        "Sandbox repair suggestion is not executable action.",
        "No structured failure_event, no authoritative failure_reason.",
        "No expected_outcome / actual_outcome contrast, no authoritative failure.",
        "LLM-only explanation must not become authoritative failure_reason.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "sandbox_failure_trace_contract_v0_1.md" in readme
        and "v2.10b Sandbox Failure / Trace Contract Docs" in research_plan
    )
    return _result("sandbox_failure_trace_contract_docs", passed, {"doc": str(doc_path)})


def smoke_sandbox_boundary_capability_assumption_docs() -> dict:
    doc_path = Path("docs/sandbox_boundary_capability_assumption_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "sandbox result is not a lesson",
        "sandbox success is not approved knowledge",
        "sandbox failure is not automatic failure_reason",
        "sandbox repair is not executable action",
        "sandbox trace is not memory promotion",
        "sandbox exploration is not authorized runtime behavior",
        "A sandbox is an observable, replayable, limited, interruptible, trace-producing experimental environment.",
        "A sandbox must not perform real-world actions.",
        "A sandbox is not free runtime.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "sandbox_boundary_capability_assumption_v0_1.md" in readme
        and "v2.10a Sandbox Boundary / Capability Assumption Docs" in research_plan
    )
    return _result("sandbox_boundary_capability_assumption_docs", passed, {"doc": str(doc_path)})


def smoke_phase0_trust_curiosity_personality_boundary_docs() -> dict:
    doc_path = Path("docs/phase0_trust_curiosity_personality_boundary_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")

    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""

    required_terms = [
        "evaluator judgment is observable evidence, not absolute truth.",
        "confirmation is not always required.",
        "trace is always required.",
        "LLM may describe curiosity, but must not be the authoritative source of novelty.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "phase0_trust_curiosity_personality_boundary_v0_1.md" in readme
        and "v2.7b-0" in research_plan
    )
    return _result("phase0_trust_curiosity_personality_boundary_docs", passed, {"doc": str(doc_path)})


def smoke_cross_task_shared_prerequisite_isolation() -> dict:
    lesson_001 = build_lesson_from_failure("session_cube_001", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson_001["object_id"] = "cube_001"
    lesson_003 = {
        "lesson_id": "lesson_003",
        "source_session": "session_cube_002",
        "source_failure_reason": "not_facing_east_for_cube_002",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": "before_retry_pick_up_cube",
        "object_id": "cube_002",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "confidence": "tested_once",
    }
    cube_001 = select_lesson_for_context(
        [lesson_001, lesson_003],
        {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"},
    )
    cube_002 = select_lesson_for_context(
        [lesson_001, lesson_003],
        {"task": "pick_up", "object_id": "cube_002", "decision_point": "before_retry_pick_up_cube"},
    )
    passed = (
        cube_001["active_lesson_ids"] == ["lesson_001", "lesson_003"]
        and cube_001["selected_lesson_id"] == "lesson_001"
        and cube_001["selected_action"] == "turn(east)"
        and "lesson_003" not in cube_001["matched_lesson_ids"]
        and cube_001["conflict_detected"] is False
        and cube_002["active_lesson_ids"] == ["lesson_001", "lesson_003"]
        and cube_002["selected_lesson_id"] == "lesson_003"
        and cube_002["selected_action"] == "turn(east)"
        and "lesson_001" not in cube_002["matched_lesson_ids"]
        and cube_002["conflict_detected"] is False
    )
    return _result(
        "cross_task_shared_prerequisite_isolation",
        passed,
        {"cube_001": cube_001, "cube_002": cube_002},
    )


def smoke_manual_stale_marking() -> dict:
    lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
    stale_lesson = mark_lesson_stale(lesson)
    context = {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"}
    stale_result = select_lesson_for_context([stale_lesson], context)
    restored_result = select_lesson_for_context([unmark_lesson_stale(stale_lesson)], context)
    west_failure = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    west_lesson = build_lesson_from_failure("session_west", west_failure)
    conflict_result = select_lesson_for_decision_point([stale_lesson, west_lesson], "before_retry_pick_up_cube")
    passed = (
        stale_result["selected_lesson_id"] is None
        and stale_result["selected_action"] is None
        and stale_result["skipped_lessons"] == [{"lesson_id": "lesson_001", "skipped_reason": "stale"}]
        and stale_result["conflict_detected"] is False
        and stale_result["behavior_changed"] is False
        and restored_result["selected_lesson_id"] == "lesson_001"
        and restored_result["selected_action"] == "turn(east)"
        and conflict_result["conflict_detected"] is False
        and conflict_result["selected_lesson_id"] == "lesson_002"
    )
    return _result(
        "manual_stale_marking",
        passed,
        {"stale": stale_result, "restored": restored_result, "conflict": conflict_result},
    )


def smoke_supersede_link() -> dict:
    old_lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    old_lesson["object_id"] = "cube_001"
    old_lesson["stale"] = False
    new_lesson = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": "before_retry_pick_up_cube",
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "inactive",
        "stale": False,
        "confidence": "manual_fixture",
    }
    context = {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"}
    before = select_lesson_for_context([old_lesson, new_lesson], context)
    link = link_lesson_supersede(old_lesson, new_lesson)
    after = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], context)
    stale_link = link_lesson_supersede(mark_lesson_stale(old_lesson), new_lesson)
    stale_result = select_lesson_for_context([stale_link["old_lesson"], stale_link["new_lesson"]], context)
    west_failure = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    west_lesson = build_lesson_from_failure("session_west", west_failure)
    conflict_result = select_lesson_for_decision_point(
        [stale_link["old_lesson"], stale_link["new_lesson"], west_lesson],
        "before_retry_pick_up_cube",
    )
    trace = link["trace"]
    passed = (
        link["old_lesson"]["superseded_by"] == "lesson_004"
        and link["new_lesson"]["supersedes"] == "lesson_001"
        and trace["supersede_linked"] is True
        and trace["status_changed"] is False
        and trace["selection_behavior_changed"] is False
        and before["selected_lesson_id"] == "lesson_001"
        and after["selected_lesson_id"] == "lesson_001"
        and after["selected_action"] == "turn(east)"
        and stale_result["selected_lesson_id"] is None
        and stale_result["skipped_lessons"] == [{"lesson_id": "lesson_001", "skipped_reason": "stale"}]
        and conflict_result["conflict_detected"] is False
        and conflict_result["selected_lesson_id"] == "lesson_002"
    )
    return _result(
        "supersede_link",
        passed,
        {"link": trace, "before": before, "after": after, "stale": stale_result, "conflict": conflict_result},
    )


def smoke_cli_lifecycle_display() -> dict:
    old_lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    old_lesson["object_id"] = "cube_001"
    old_lesson["stale"] = True
    old_lesson["stale_reason"] = "manual: obsolete wording"
    new_lesson = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": "before_retry_pick_up_cube",
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "inactive",
        "stale": False,
        "stale_reason": None,
        "confidence": "manual_fixture",
    }
    link = link_lesson_supersede(old_lesson, new_lesson)
    lessons = [link["old_lesson"], link["new_lesson"]]
    context = {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"}
    before = select_lesson_for_context(lessons, context)
    before_conflict = select_lesson_for_decision_point(lessons, "before_retry_pick_up_cube")
    display = run_lifecycle_display(lessons, context)
    after = select_lesson_for_context(lessons, context)
    after_conflict = select_lesson_for_decision_point(lessons, "before_retry_pick_up_cube")
    passed = (
        display["read_only"] is True
        and "Lesson Lifecycle" in display["display"]
        and "stale: true" in display["display"]
        and "stale_reason: manual: obsolete wording" in display["display"]
        and "superseded_by: lesson_004" in display["display"]
        and "supersedes: lesson_001" in display["display"]
        and before == after
        and before_conflict == after_conflict
        and display["selection_trace"] == before
        and display["conflict_check"]["conflict_detected"] is False
    )
    return _result(
        "cli_lifecycle_display",
        passed,
        {"display": display["display"], "selection": display["selection_trace"], "conflict": display["conflict_check"]},
    )


def smoke_supersede_replacement_suggestion() -> dict:
    old_lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    old_lesson["object_id"] = "cube_001"
    old_lesson = mark_lesson_stale(old_lesson)
    replacement = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": "before_retry_pick_up_cube",
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "stale": False,
        "confidence": "manual_fixture",
    }
    link = link_lesson_supersede(old_lesson, replacement)
    context = {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"}
    baseline = select_lesson_for_context([old_lesson, replacement], context)
    result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], context)
    suggestion = result["replacement_suggestions"][0]

    missing = dict(link["old_lesson"])
    missing["superseded_by"] = "lesson_missing"
    missing_result = select_lesson_for_context([missing], context)

    inactive_replacement = dict(replacement)
    inactive_replacement["status"] = "inactive"
    inactive_link = link_lesson_supersede(old_lesson, inactive_replacement)
    west_failure = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    west_lesson = build_lesson_from_failure("session_west", west_failure)
    conflict_result = select_lesson_for_decision_point(
        [inactive_link["old_lesson"], inactive_link["new_lesson"], west_lesson],
        "before_retry_pick_up_cube",
    )
    passed = (
        suggestion["source_lesson_id"] == "lesson_001"
        and suggestion["superseded_by"] == "lesson_004"
        and suggestion["candidate_exists"] is True
        and suggestion["candidate_status"] == "active"
        and suggestion["candidate_stale"] is False
        and suggestion["candidate_eligible"] is True
        and suggestion["activation_applied"] is False
        and result["selected_lesson_id"] == baseline["selected_lesson_id"]
        and result["selected_action"] == baseline["selected_action"]
        and missing_result["replacement_suggestions"][0]["reason"] == "replacement_candidate_missing"
        and missing_result["replacement_suggestions"][0]["activation_applied"] is False
        and conflict_result["conflict_detected"] is False
        and conflict_result["selected_lesson_id"] == "lesson_002"
        and conflict_result["replacement_suggestions"][0]["activation_applied"] is False
    )
    return _result(
        "supersede_replacement_suggestion",
        passed,
        {"suggestion": suggestion, "missing": missing_result, "conflict": conflict_result},
    )


def smoke_strict_supersede_activation() -> dict:
    old_lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    old_lesson["object_id"] = "cube_001"
    old_lesson = mark_lesson_stale(old_lesson)
    replacement = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": "before_retry_pick_up_cube",
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "stale": False,
        "confidence": "manual_fixture",
    }
    context = {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"}
    active_link = link_lesson_supersede(old_lesson, replacement)
    activated = select_lesson_for_context([active_link["old_lesson"], active_link["new_lesson"]], context)

    inactive_replacement = dict(replacement)
    inactive_replacement["status"] = "inactive"
    inactive_link = link_lesson_supersede(old_lesson, inactive_replacement)
    inactive = select_lesson_for_context([inactive_link["old_lesson"], inactive_link["new_lesson"]], context)

    west_failure = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    west_lesson = build_lesson_from_failure("session_west", west_failure)
    conflict = select_lesson_for_decision_point(
        [active_link["old_lesson"], active_link["new_lesson"], west_lesson],
        "before_retry_pick_up_cube",
    )
    active_trace = activated["supersede_activation"]
    inactive_trace = inactive["supersede_activation"]
    conflict_trace = conflict["supersede_activation"]
    passed = (
        activated["selected_lesson_id"] == "lesson_004"
        and active_trace["activation_applied"] is True
        and active_trace["old_lesson_stale"] is True
        and active_trace["old_lesson_has_superseded_by"] is True
        and active_trace["candidate_exists"] is True
        and active_trace["candidate_active"] is True
        and active_trace["candidate_not_stale"] is True
        and active_trace["candidate_eligible"] is True
        and active_trace["activation_source"] == "supersede_link"
        and active_trace["failed_conditions"] == []
        and inactive["selected_lesson_id"] is None
        and inactive_trace["activation_applied"] is False
        and "candidate_active" in inactive_trace["failed_conditions"]
        and conflict["conflict_detected"] is True
        and conflict["conflict_resolution"] == "require_review"
        and conflict["selected_lesson_id"] is None
        and conflict_trace["activation_applied"] is False
        and "conflict_unresolved" in conflict_trace["failed_conditions"]
    )
    return _result(
        "strict_supersede_activation",
        passed,
        {"activated": activated, "inactive": inactive, "conflict": conflict},
    )


def smoke_activation_audit() -> dict:
    old_lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    old_lesson["object_id"] = "cube_001"
    old_lesson["stale_reason"] = None
    old_lesson = mark_lesson_stale(old_lesson)
    old_lesson["stale_reason"] = "manual: audit fixture"
    replacement = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": "before_retry_pick_up_cube",
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "stale": False,
        "stale_reason": None,
        "confidence": "manual_fixture",
    }
    context = {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"}
    link = link_lesson_supersede(old_lesson, replacement)
    lessons = [link["old_lesson"], link["new_lesson"]]
    before = json.dumps(lessons, sort_keys=True)
    success = select_lesson_for_context(lessons, context)
    after = json.dumps(lessons, sort_keys=True)

    failed_candidate = dict(replacement)
    failed_candidate["status"] = "inactive"
    failed_candidate["stale"] = True
    failed_candidate["object_id"] = "cube_002"
    failed_link = link_lesson_supersede(old_lesson, failed_candidate)
    failed = select_lesson_for_context([failed_link["old_lesson"], failed_link["new_lesson"]], context)

    west_failure = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    west_lesson = build_lesson_from_failure("session_west", west_failure)
    conflict = select_lesson_for_decision_point([link["old_lesson"], link["new_lesson"], west_lesson], "before_retry_pick_up_cube")
    lifecycle = run_lifecycle_display(lessons, context)

    activation = success["supersede_activation"]
    suggestion = success["replacement_suggestions"][0]
    failed_activation = failed["supersede_activation"]
    conflict_activation = conflict["supersede_activation"]
    required = {
        "source_lesson_id",
        "candidate_lesson_id",
        "old_lesson_stale",
        "old_lesson_has_superseded_by",
        "candidate_exists",
        "candidate_active",
        "candidate_not_stale",
        "candidate_eligible",
        "activation_source",
        "activation_applied",
        "failed_conditions",
    }
    passed = (
        required.issubset(activation.keys())
        and activation["activation_applied"] is True
        and activation["failed_conditions"] == []
        and activation["activation_source"] == "supersede_link"
        and before == after
        and failed_activation["activation_applied"] is False
        and "candidate_active" in failed_activation["failed_conditions"]
        and "candidate_not_stale" in failed_activation["failed_conditions"]
        and "candidate_eligible" in failed_activation["failed_conditions"]
        and conflict["conflict_detected"] is True
        and conflict["conflict_resolution"] == "require_review"
        and conflict["selected_lesson_id"] is None
        and conflict_activation["activation_applied"] is False
        and "conflict_unresolved" in conflict_activation["failed_conditions"]
        and suggestion["candidate_lesson_id"] == activation["candidate_lesson_id"]
        and suggestion["candidate_exists"] == activation["candidate_exists"]
        and suggestion["candidate_eligible"] == activation["candidate_eligible"]
        and lifecycle["read_only"] is True
    )
    return _result(
        "activation_audit",
        passed,
        {"success": activation, "failed": failed_activation, "conflict": conflict_activation},
    )


def smoke_activation_regression_suite() -> dict:
    old_lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    old_lesson["object_id"] = "cube_001"
    old_lesson["stale_reason"] = None
    old_lesson = mark_lesson_stale(old_lesson)
    old_lesson["stale_reason"] = "manual: regression fixture"
    candidate = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": "before_retry_pick_up_cube",
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "stale": False,
        "stale_reason": None,
        "confidence": "manual_fixture",
    }
    context = {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"}
    link = link_lesson_supersede(old_lesson, candidate)
    lessons = [link["old_lesson"], link["new_lesson"]]
    before = json.dumps(lessons, sort_keys=True)
    success = select_lesson_for_context(lessons, context)
    after = json.dumps(lessons, sort_keys=True)

    missing = dict(link["old_lesson"])
    missing["superseded_by"] = "lesson_missing"
    missing_result = select_lesson_for_context([missing], context)

    ineligible_candidate = dict(candidate)
    ineligible_candidate["object_id"] = "cube_002"
    ineligible_link = link_lesson_supersede(old_lesson, ineligible_candidate)
    ineligible = select_lesson_for_context([ineligible_link["old_lesson"], ineligible_link["new_lesson"]], context)

    west_failure = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    conflict = select_lesson_for_decision_point(
        [link["old_lesson"], link["new_lesson"], build_lesson_from_failure("session_west", west_failure)],
        "before_retry_pick_up_cube",
    )
    known = generate_lesson_from_failure("session_known", pick_up(build_initial_sandbox_state(), "cube_001"))
    unknown = generate_lesson_from_failure(
        "session_unknown",
        {
            "type": "sandbox_action_result",
            "tool": "pick_up",
            "object_id": "cube_001",
            "result": "failed",
            "failure_reason": "unmapped_obstacle_shadow",
            "state": build_initial_sandbox_state(),
        },
    )
    activation = success["supersede_activation"]
    suggestion = success["replacement_suggestions"][0]
    passed = (
        activation["activation_applied"] is True
        and success["selected_lesson_id"] == "lesson_004"
        and activation["failed_conditions"] == []
        and before == after
        and missing_result["supersede_activation"]["candidate_exists"] is False
        and missing_result["supersede_activation"]["activation_applied"] is False
        and ineligible["supersede_activation"]["candidate_eligible"] is False
        and ineligible["supersede_activation"]["activation_applied"] is False
        and conflict["conflict_detected"] is True
        and conflict["conflict_resolution"] == "require_review"
        and conflict["supersede_activation"]["activation_applied"] is False
        and suggestion["candidate_lesson_id"] == activation["candidate_lesson_id"]
        and known["trace"]["generation_status"] == "supported_failure_reason"
        and unknown["trace"]["generation_status"] == "unknown_failure_reason"
        and unknown["lesson"] is None
    )
    return _result(
        "activation_regression_suite",
        passed,
        {"success": activation, "missing": missing_result["supersede_activation"], "conflict": conflict},
    )


def smoke_manual_review_state_foundation() -> dict:
    review = create_review_item(
        target_type="conflict",
        target_id="conflict_001",
        source_lesson_id="lesson_001",
        candidate_lesson_id="lesson_004",
        reason="conflict_requires_manual_review",
        review_id="review_001",
    )
    approved = mark_review_approved(review)
    trace = build_review_trace(approved)

    old_lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    old_lesson["object_id"] = "cube_001"
    old_lesson["stale_reason"] = None
    old_lesson = mark_lesson_stale(old_lesson)
    old_lesson["stale_reason"] = "manual: review fixture"
    candidate = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": "before_retry_pick_up_cube",
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "stale": False,
        "stale_reason": None,
        "confidence": "manual_fixture",
    }
    context = {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"}
    link = link_lesson_supersede(old_lesson, candidate)
    lessons = [link["old_lesson"], link["new_lesson"]]
    before_selection = select_lesson_for_context(lessons, context)
    after_selection = select_lesson_for_context(lessons, context)

    west_failure = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    conflict_lessons = [
        build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001")),
        build_lesson_from_failure("session_west", west_failure),
    ]
    before_conflict = select_lesson_for_decision_point(conflict_lessons, "before_retry_pick_up_cube")
    after_conflict = select_lesson_for_decision_point(conflict_lessons, "before_retry_pick_up_cube")

    passed = (
        review["review_state"] == "pending_review"
        and review["approval_state"] == "unreviewed"
        and approved["review_state"] == "reviewed"
        and approved["approval_state"] == "approved"
        and trace["metadata_only"] is True
        and trace["selection_behavior_changed"] is False
        and before_selection == after_selection
        and before_selection["supersede_activation"]["activation_applied"] is True
        and before_conflict == after_conflict
        and before_conflict["conflict_detected"] is True
        and before_conflict["conflict_resolution"] == "require_review"
    )
    return _result(
        "manual_review_state_foundation",
        passed,
        {"review": review, "approved": approved, "trace": trace},
    )


def smoke_manual_review_cli_display() -> dict:
    review = create_review_item(
        target_type="conflict",
        target_id="conflict_001",
        source_lesson_id="lesson_001",
        candidate_lesson_id="lesson_004",
        reason="conflict_requires_manual_review",
        review_id="review_001",
    )
    display = run_review_display([review])
    empty = run_review_display([])

    old_lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    old_lesson["object_id"] = "cube_001"
    selection_before = select_lesson_for_context([old_lesson], {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"})
    run_review_display([review])
    selection_after = select_lesson_for_context([old_lesson], {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"})

    west_failure = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    conflict_lessons = [
        build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001")),
        build_lesson_from_failure("session_west", west_failure),
    ]
    conflict_before = select_lesson_for_decision_point(conflict_lessons, "before_retry_pick_up_cube")
    run_review_display([review])
    conflict_after = select_lesson_for_decision_point(conflict_lessons, "before_retry_pick_up_cube")

    passed = (
        display["read_only"] is True
        and "Manual Review Items" in display["display"]
        and "id: review_001" in display["display"]
        and "approval_state: unreviewed" in display["display"]
        and empty["display"] == "No manual review items."
        and selection_before == selection_after
        and conflict_before == conflict_after
        and conflict_after["conflict_detected"] is True
        and conflict_after["conflict_resolution"] == "require_review"
    )
    return _result(
        "manual_review_cli_display",
        passed,
        {"display": display["display"], "empty": empty["display"]},
    )


def smoke_manual_review_decision_cli() -> dict:
    review = create_review_item(
        target_type="conflict",
        target_id="conflict_001",
        source_lesson_id="lesson_001",
        candidate_lesson_id="lesson_004",
        reason="conflict_requires_manual_review",
        review_id="review_001",
    )
    approved = run_review_approve([review], notes="approved in smoke")
    rejected = run_review_reject([review], notes="rejected in smoke")
    missing = run_review_approve([review], review_id="review_missing")
    display = run_review_display(approved["review_items"])

    old_lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    old_lesson["object_id"] = "cube_001"
    selection_before = select_lesson_for_context([old_lesson], {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"})
    run_review_approve([review])
    selection_after = select_lesson_for_context([old_lesson], {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"})

    west_failure = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    conflict_lessons = [
        build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001")),
        build_lesson_from_failure("session_west", west_failure),
    ]
    conflict_before = select_lesson_for_decision_point(conflict_lessons, "before_retry_pick_up_cube")
    run_review_reject([review])
    conflict_after = select_lesson_for_decision_point(conflict_lessons, "before_retry_pick_up_cube")

    passed = (
        approved["status"] == "ok"
        and approved["review_item"]["review_state"] == "reviewed"
        and approved["review_item"]["approval_state"] == "approved"
        and approved["review_item"]["notes"] == "approved in smoke"
        and rejected["review_item"]["approval_state"] == "rejected"
        and missing["status"] == "not_found"
        and missing["error"] == "Review item not found: review_missing"
        and "approval_state: approved" in display["display"]
        and selection_before == selection_after
        and conflict_before == conflict_after
        and conflict_after["conflict_detected"] is True
        and conflict_after["conflict_resolution"] == "require_review"
    )
    return _result(
        "manual_review_decision_cli",
        passed,
        {"approved": approved, "rejected": rejected, "missing": missing},
    )


def smoke_manual_review_decision_audit() -> dict:
    review = create_review_item(
        target_type="conflict",
        target_id="conflict_001",
        source_lesson_id="lesson_001",
        candidate_lesson_id="lesson_004",
        reason="conflict_requires_manual_review",
        notes="initial note",
        review_id="review_001",
    )
    approved_once = run_review_approve([review], notes="first approval")
    approved_twice = run_review_approve(approved_once["review_items"], notes="second approval")
    rejected_after_approve = run_review_reject(approved_twice["review_items"], notes="then rejected")
    missing = run_review_reject([review], review_id="review_missing")
    display = run_review_display(rejected_after_approve["review_items"])

    old_lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    old_lesson["object_id"] = "cube_001"
    old_lesson = mark_lesson_stale(old_lesson)
    old_lesson["stale_reason"] = "manual: decision audit fixture"
    candidate = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": "before_retry_pick_up_cube",
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "stale": False,
        "stale_reason": None,
        "confidence": "manual_fixture",
    }
    context = {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"}
    link = link_lesson_supersede(old_lesson, candidate)
    lessons = [link["old_lesson"], link["new_lesson"]]
    before_selection = select_lesson_for_context(lessons, context)
    run_review_approve([review])
    after_selection = select_lesson_for_context(lessons, context)

    west_failure = {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }
    conflict_lessons = [
        build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001")),
        build_lesson_from_failure("session_west", west_failure),
    ]
    before_conflict = select_lesson_for_decision_point(conflict_lessons, "before_retry_pick_up_cube")
    run_review_reject([review])
    after_conflict = select_lesson_for_decision_point(conflict_lessons, "before_retry_pick_up_cube")

    known = generate_lesson_from_failure("session_known", pick_up(build_initial_sandbox_state(), "cube_001"))
    unknown = generate_lesson_from_failure(
        "session_unknown",
        {
            "type": "sandbox_action_result",
            "tool": "pick_up",
            "object_id": "cube_001",
            "result": "failed",
            "failure_reason": "unmapped_obstacle_shadow",
            "state": build_initial_sandbox_state(),
        },
    )
    passed = (
        approved_twice["review_item"]["approval_state"] == "approved"
        and approved_twice["review_item"]["notes"] == "second approval"
        and len(approved_twice["review_items"]) == 1
        and rejected_after_approve["review_item"]["approval_state"] == "rejected"
        and rejected_after_approve["review_item"]["notes"] == "then rejected"
        and rejected_after_approve["review_item"]["source_lesson_id"] == "lesson_001"
        and missing["status"] == "not_found"
        and missing["review_items"][0]["approval_state"] == "unreviewed"
        and "approval_state: rejected" in display["display"]
        and before_selection == after_selection
        and before_selection["supersede_activation"]["activation_applied"] is True
        and before_conflict == after_conflict
        and after_conflict["conflict_detected"] is True
        and after_conflict["conflict_resolution"] == "require_review"
        and known["trace"]["generation_status"] == "supported_failure_reason"
        and unknown["trace"]["generation_status"] == "unknown_failure_reason"
        and unknown["lesson"] is None
    )
    return _result(
        "manual_review_decision_audit",
        passed,
        {"approved_twice": approved_twice, "rejected": rejected_after_approve, "missing": missing},
    )


def smoke_review_gated_selection_eligibility() -> dict:
    candidate = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": "before_retry_pick_up_cube",
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "stale": False,
        "stale_reason": None,
        "confidence": "manual_fixture",
        "requires_review": True,
    }
    context = {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"}
    review = create_review_item(
        target_type="conflict",
        target_id="conflict_001",
        source_lesson_id=None,
        candidate_lesson_id="lesson_004",
        reason="conflict_requires_manual_review",
        review_id="review_001",
    )
    approved = mark_review_approved(review)
    rejected = mark_review_rejected(review)
    approved_selection = select_lesson_for_context([candidate], context, review_items=[approved])
    rejected_selection = select_lesson_for_context([candidate], context, review_items=[rejected])
    missing_selection = select_lesson_for_context([candidate], context, review_items=[])
    optional_candidate = dict(candidate)
    optional_candidate["requires_review"] = False
    optional_selection = select_lesson_for_context([optional_candidate], context)

    stale_old = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    stale_old["object_id"] = "cube_001"
    stale_old = mark_lesson_stale(stale_old)
    link = link_lesson_supersede(stale_old, candidate)
    activation_rejected = select_lesson_for_context(
        [link["old_lesson"], link["new_lesson"]],
        context,
        review_items=[create_review_item("conflict", "conflict_001", "lesson_001", "lesson_004", "review", review_id="review_pending")],
    )
    known = generate_lesson_from_failure("session_known", pick_up(build_initial_sandbox_state(), "cube_001"))
    unknown = generate_lesson_from_failure(
        "session_unknown",
        {
            "type": "sandbox_action_result",
            "tool": "pick_up",
            "object_id": "cube_001",
            "result": "failed",
            "failure_reason": "unmapped_obstacle_shadow",
            "state": build_initial_sandbox_state(),
        },
    )

    approved_gate = approved_selection["review_gates"][0]
    rejected_gate = rejected_selection["review_gates"][0]
    missing_gate = missing_selection["review_gates"][0]
    optional_gate = optional_selection["review_gates"][0]
    passed = (
        approved_gate["review_gate_passed"] is True
        and approved_gate["reason"] == "approved_review_allows_selection_eligibility"
        and approved_selection["selected_lesson_id"] == "lesson_004"
        and rejected_gate["review_gate_passed"] is False
        and rejected_gate["reason"] == "rejected_review_blocks_selection_eligibility"
        and rejected_selection["selected_lesson_id"] is None
        and missing_gate["matched_review_id"] is None
        and missing_gate["review_state"] is None
        and missing_gate["approval_state"] is None
        and missing_gate["reason"] == "missing_required_review"
        and optional_gate["included_in_selection_eligibility"] is False
        and optional_selection["selected_lesson_id"] == "lesson_004"
        and activation_rejected["supersede_activation"]["activation_source"] == "supersede_link"
        and activation_rejected["supersede_activation"]["review_gate"]["reason"] == "review_not_approved"
        and activation_rejected["supersede_activation"]["activation_applied"] is False
        and evaluate_review_gate(candidate, [create_review_item("conflict", "conflict_001", None, "lesson_other", "mentions lesson_004")])[
            "reason"
        ]
        == "missing_required_review"
        and known["trace"]["generation_status"] == "supported_failure_reason"
        and unknown["trace"]["generation_status"] == "unknown_failure_reason"
        and unknown["lesson"] is None
    )
    return _result(
        "review_gated_selection_eligibility",
        passed,
        {"approved_gate": approved_gate, "rejected_gate": rejected_gate, "missing_gate": missing_gate},
    )


def smoke_review_gated_selection_audit() -> dict:
    candidate = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": "before_retry_pick_up_cube",
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "stale": False,
        "stale_reason": None,
        "confidence": "manual_fixture",
        "requires_review": True,
    }
    context = {"task": "pick_up", "object_id": "cube_001", "decision_point": "before_retry_pick_up_cube"}
    review = create_review_item(
        target_type="conflict",
        target_id="conflict_001",
        source_lesson_id=None,
        candidate_lesson_id="lesson_004",
        reason="conflict_requires_manual_review",
        notes="audit note",
        review_id="review_001",
    )
    review_before = dict(review)
    approved = mark_review_approved(review)
    rejected = mark_review_rejected(review)
    approved_result = select_lesson_for_context([candidate], context, review_items=[approved])
    rejected_result = select_lesson_for_context([candidate], context, review_items=[rejected])

    legacy = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    legacy["object_id"] = "cube_001"
    legacy["compatibility_approved"] = True
    legacy_result = select_lesson_for_context([legacy], context, review_items=[])
    misleading = create_review_item(
        target_type="conflict",
        target_id="conflict_001",
        source_lesson_id=None,
        candidate_lesson_id="lesson_other",
        reason="lesson_004 appears in text only",
        notes="lesson_004 appears in notes only",
        review_id="review_misleading",
    )
    misleading_gate = evaluate_review_gate(candidate, [mark_review_approved(misleading)])
    conflict_before = select_lesson_for_decision_point(
        [
            build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001")),
            build_lesson_from_failure(
                "session_west",
                {
                    "type": "sandbox_action_result",
                    "tool": "pick_up",
                    "object_id": "cube_001",
                    "result": "failed",
                    "failure_reason": "not_facing_west",
                    "state": build_initial_sandbox_state(),
                },
            ),
        ],
        "before_retry_pick_up_cube",
    )
    conflict_after = select_lesson_for_decision_point(
        [
            build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001")),
            build_lesson_from_failure(
                "session_west",
                {
                    "type": "sandbox_action_result",
                    "tool": "pick_up",
                    "object_id": "cube_001",
                    "result": "failed",
                    "failure_reason": "not_facing_west",
                    "state": build_initial_sandbox_state(),
                },
            ),
        ],
        "before_retry_pick_up_cube",
        review_items=[mark_review_approved(create_review_item("conflict", "conflict_001", None, "lesson_001", "review"))],
    )

    passed = (
        approved_result["review_gates"][0]["review_gate_passed"] is True
        and rejected_result["review_gates"][0]["review_gate_passed"] is False
        and rejected_result["selected_lesson_id"] is None
        and review["review_state"] == review_before["review_state"]
        and review["approval_state"] == review_before["approval_state"]
        and legacy_result["review_gates"][0]["requires_review"] is False
        and legacy_result["selected_lesson_id"] == "lesson_001"
        and "compatibility_approved" not in legacy_result["review_gates"][0]
        and misleading_gate["matched_review_id"] is None
        and misleading_gate["reason"] == "missing_required_review"
        and conflict_before["conflict_detected"] == conflict_after["conflict_detected"]
        and conflict_after["conflict_resolution"] == "require_review"
    )
    return _result(
        "review_gated_selection_audit",
        passed,
        {
            "approved_gate": approved_result["review_gates"][0],
            "rejected_gate": rejected_result["review_gates"][0],
            "legacy_gate": legacy_result["review_gates"][0],
        },
    )


def smoke_teaching_cli() -> dict:
    known = run_known_flow()
    unknown = run_unknown_flow()
    causal = run_disable_reenable_flow()
    passed = (
        known["status"] == "ok"
        and known["failure_reason"] == "not_facing_east"
        and known["behavior_after"] == "success"
        and known["conflict_check"]["implemented"] is True
        and known["conflict_check"]["conflict_detected"] is False
        and unknown["generation_status"] == "unknown_failure_reason"
        and unknown["lesson"] is None
        and unknown["executable_action"] is None
        and unknown["behavior_changed"] is False
        and unknown["conflict_check"]["implemented"] is True
        and "turn(east)" not in str(unknown)
        and causal["enabled_result"] == "success"
        and causal["disabled_result"] == "failed"
        and causal["reenabled_result"] == "success"
        and causal["conflict_check"]["implemented"] is True
    )
    return _result("teaching_cli", passed, {"known": known["status"], "unknown": unknown["generation_status"]})


def smoke_teaching_cli_conflict_check() -> dict:
    result = run_conflict_check_flow()
    conflict = result["conflict_check"]
    passed = (
        conflict["implemented"] is True
        and conflict["conflict_detected"] is True
        and conflict["conflict_resolution"] == "require_review"
        and conflict["review_required"] is True
        and conflict["review_status"] == "pending_human_review"
        and conflict["conflicting_lesson_ids"] == ["lesson_001", "lesson_002"]
        and conflict["conflicting_actions"] == ["turn(east)", "turn(west)"]
        and conflict["selected_action"] is None
        and conflict["behavior_changed"] is False
    )
    return _result("teaching_cli_conflict_check", passed, conflict)


def smoke_state_core() -> dict:
    core = StateCore()
    result = core.apply(
        [{"name": "conversation.refocus_requested", "confidence": 1.0, "direct_intent": "refocus"}]
    )
    passed = (
        result["direct_intent"] == "refocus"
        and result["after"]["task_focus"] > result["before"]["task_focus"]
        and result["after"]["overexpand_risk"] > result["before"]["overexpand_risk"]
    )
    return _result("state_core", passed, result)


def smoke_state_persistence() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        result = run_turn("1 + 2 * 3", data_dir=tmp, persist_state=True, session_id="smoke-session")
        snapshot = read_state_snapshot(tmp)
        session = read_session_summary(tmp)
        trace_summary = read_last_trace_summary(tmp)
        passed = (
            result["state_persistence"] is not None
            and snapshot.get("type") == "state_snapshot"
            and session.get("type") == "session_summary"
            and session.get("session_id") == "smoke-session"
            and trace_summary.get("type") == "last_trace_summary"
            and trace_summary.get("intent") == result["decision"]["intent"]
        )
        return _result(
            "state_persistence",
            passed,
            {"snapshot": snapshot, "session": session, "trace_summary": trace_summary},
        )


def smoke_expression_guard() -> dict:
    package = build_expression_package("refocus", "跑題了，拉回來", {})
    result = guard_output("收到，回到主線，但順便談另一題。", package)
    passed = not result["passed"] and result["final_output"] == "收到，拉回主線。"
    return _result("expression_guard", passed, result)


def smoke_correction_prompt() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
        correction = {
            "type": "correction.pending",
            "previous_input": previous["input"],
            "previous_intent": previous["decision"]["intent"],
            "user_correction": "不是，我是在說睡眠模式功能。",
            "needs_user_label": True,
            "options": ["event_mismatch", "reaction_strength_mismatch", "expression_mismatch"],
        }
    passed = correction["needs_user_label"] and "event_mismatch" in correction["options"]
    return _result("correction_prompt", passed, correction)


def smoke_deliberation() -> dict:
    result = deliberate(
        None,
        [{"type": "user_fatigue_possible", "confidence": 0.9}, {"type": "memory_candidate_possible", "confidence": 0.9}],
        {"user_fatigue": 0.9, "self_check_pressure": 1.0},
    )
    passed = result["intent"] == "fatigue_close"
    return _result("deliberation", passed, result)


def smoke_integrated_loop() -> dict:
    cases = [
        ("睡眠模式這個功能怎麼設計？", "answer_normally", "technical.topic_discussed"),
        ("跑題了，拉回來", "refocus", "回到主線"),
        ("記住，以後 ASHL Core 先走實驗路線", "self_check", "候選"),
        ("清音只是普通工具", "identity_protest", "不是普通工具"),
        ("證明黎曼假設", "unknown_need_tool", "不能靠直覺硬答"),
        ("1 + 2 * 3", "calculate", "7"),
        ("我累了，明天再說", "fatigue_close", "休息"),
    ]
    details = []
    passed = True

    with tempfile.TemporaryDirectory() as tmp:
        for text, expected_intent, expected_signal in cases:
            result = run_turn(text, data_dir=tmp)
            final_event_names = [event["name"] for event in result["concept_result"]["final_events"]]
            output = result["final_output"]
            signal_ok = expected_signal in output or expected_signal in final_event_names
            case_ok = result["decision"]["intent"] == expected_intent and signal_ok
            passed = passed and case_ok
            details.append(
                {
                    "input": text,
                    "intent": result["decision"]["intent"],
                    "final_events": final_event_names,
                    "final_output": output,
                    "passed": case_ok,
                }
            )

    fatigue_case = details[-1]
    passed = passed and "self_check" not in fatigue_case["final_output"]
    return _result("integrated_loop", passed, {"cases": details})


def smoke_persistence() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "nested" / "items.jsonl"
        append_jsonl(path, {"text": "清音"})
        rows = read_jsonl(path)
        passed = rows == [{"text": "清音"}] and read_jsonl(Path(tmp) / "missing.jsonl") == []
        return _result("persistence", passed, {"rows": rows})


def smoke_memory_candidate() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        result = run_turn("記住，以後 ASHL Core 先走實驗路線", data_dir=tmp)
        rows = read_jsonl(Path(tmp) / "memory_candidates.jsonl")
        passed = (
            result["decision"]["intent"] == "self_check"
            and result["memory_candidate"] is not None
            and len(rows) == 1
            and rows[0]["status"] == "candidate"
            and rows[0]["audit_required"] is True
        )
        return _result("memory_candidate", passed, {"trace_candidate": result["memory_candidate"], "rows": rows})


def smoke_correction_pending() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
        result = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
        rows = read_jsonl(Path(tmp) / "correction_log.jsonl")
        passed = (
            result["correction_pending"] is not None
            and len(rows) == 1
            and rows[0]["type"] == "correction.pending"
            and "event_mismatch" in rows[0]["options"]
        )
        return _result("correction_pending", passed, {"trace_pending": result["correction_pending"], "rows": rows})


def smoke_correction_label() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
        pending_result = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
        label_result = run_turn(
            "判斷錯",
            data_dir=tmp,
            pending_correction=pending_result["correction_pending"],
        )
        rows = read_jsonl(Path(tmp) / "correction_log.jsonl")
        passed = (
            label_result["correction_label"] is not None
            and label_result["correction_label"]["type"] == "correction.event_mismatch"
            and label_result["correction_label"]["status"] == "labeled"
            and len(rows) == 2
        )
        return _result("correction_label", passed, {"trace_label": label_result["correction_label"], "rows": rows})


def smoke_rule_candidate() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
        pending_result = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
        label_result = run_turn(
            "判斷錯",
            data_dir=tmp,
            pending_correction=pending_result["correction_pending"],
        )
        rows = read_jsonl(Path(tmp) / "rule_candidates.jsonl")
        passed = (
            label_result["rule_candidate"] is not None
            and len(rows) == 1
            and rows[0]["type"] == "rule_candidate"
            and rows[0]["status"] == "candidate"
            and rows[0]["audit_required"] is True
        )
        return _result("rule_candidate", passed, {"trace_candidate": label_result["rule_candidate"], "rows": rows})


def smoke_candidate_review() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
        pending_result = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
        label_result = run_turn(
            "判斷錯",
            data_dir=tmp,
            pending_correction=pending_result["correction_pending"],
        )
        review = build_candidate_review(label_result["rule_candidate"], "reviewed", note="smoke audit")
        append_candidate_review(tmp, review)
        rows = read_jsonl(Path(tmp) / "candidate_reviews.jsonl")
        candidates = list_candidates_with_review_status(tmp)
        passed = (
            review is not None
            and len(rows) == 1
            and rows[0]["type"] == "candidate_review"
            and rows[0]["decision"] == "reviewed"
            and len(candidates) == 1
            and candidates[0]["current_status"] == "reviewed"
            and candidates[0]["status"] == "candidate"
        )
        return _result("candidate_review", passed, {"review": review, "candidates": candidates})


def smoke_trial_rule() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        candidate = {
            "id": "rule_cand_sleep",
            "type": "rule_candidate",
            "status": "candidate",
            "candidate_kind": "concept_counterexample",
            "target_phrase": "睡眠模式",
            "wrong_event": "user.fatigue_signaled",
            "correct_event": "technical.topic_discussed",
            "not_event": "user.fatigue_signaled",
            "prefer_event": "technical.topic_discussed",
            "confidence": 0.3,
            "audit_required": True,
            "created_at": "2026-06-04T00:00:00+00:00",
        }
        append_rule_candidate(tmp, candidate)
        review = build_candidate_review(candidate, "approved_for_trial", note="smoke trial")
        append_candidate_review(tmp, review)
        approved = list_approved_trial_candidates(tmp)
        trial_rules = [build_trial_rule_view(item) for item in approved]
        suggestions = build_trial_suggestions(
            "睡眠模式這個功能怎麼設計？",
            [{"name": "user.fatigue_signaled"}, {"name": "technical.topic_discussed"}],
            trial_rules,
        )
        passed = (
            len(approved) == 1
            and len(trial_rules) == 1
            and trial_rules[0]["active"] is False
            and trial_rules[0]["status"] == "trial_view"
            and len(suggestions) == 1
            and suggestions[0]["applied"] is False
        )
        return _result("trial_rule", passed, {"trial_rules": trial_rules, "suggestions": suggestions})


def smoke_trial_feedback() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        candidate = {
            "id": "rule_cand_sleep",
            "type": "rule_candidate",
            "status": "candidate",
            "candidate_kind": "concept_counterexample",
            "target_phrase": "睡眠模式",
            "wrong_event": "user.fatigue_signaled",
            "correct_event": "technical.topic_discussed",
            "not_event": "user.fatigue_signaled",
            "prefer_event": "technical.topic_discussed",
            "confidence": 0.3,
            "audit_required": True,
            "created_at": "2026-06-04T00:00:00+00:00",
        }
        append_rule_candidate(tmp, candidate)
        review = build_candidate_review(candidate, "approved_for_trial")
        append_candidate_review(tmp, review)
        result = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp, trial_feedback_verdict="helpful")
        rows = read_jsonl(Path(tmp) / "trial_feedback.jsonl")
        summary = summarize_trial_feedback(tmp)
        direct_feedback = build_trial_feedback(result["trial_suggestions"][0], "wrong")
        append_trial_feedback(tmp, direct_feedback)
        passed = (
            result["trial_feedback"] is not None
            and result["trial_feedback"]["verdict"] == "helpful"
            and len(rows) == 1
            and summary["total"] == 1
            and summary["helpful"] == 1
            and direct_feedback["verdict"] == "wrong"
        )
        return _result("trial_feedback", passed, {"feedback": result["trial_feedback"], "summary": summary})


def smoke_senses() -> dict:
    camera_event = build_sensor_event("camera", "pointing_teach", {"label_hint": "蘋果"})
    screen_event = build_sensor_event("screen", "screen_observation", {"window_title": "ASHL Lab"})
    candidate = build_visual_concept_candidate(camera_event, "蘋果", region_ref={"x": 1, "y": 2, "w": 3, "h": 4})
    passed = (
        validate_sensor_event(camera_event)
        and validate_sensor_event(screen_event)
        and candidate is not None
        and candidate["type"] == "visual_concept_candidate"
        and candidate["status"] == "candidate"
        and candidate["audit_required"] is True
        and "image_data" not in candidate
    )
    return _result("senses", passed, {"camera_event": camera_event, "screen_event": screen_event, "candidate": candidate})


def run_smoke_tests() -> list[dict]:
    return [
        smoke_core_seed(),
        smoke_memory_layers(),
        smoke_body_state(),
        smoke_action_sandbox(),
        smoke_standing_task(),
        smoke_experience_log(),
        smoke_phase_minus_one_lesson_contribution(),
        smoke_prompt_leakage_control(),
        smoke_phase_minus_one_negative_controls(),
        smoke_phase_minus_one_lesson_causality(),
        smoke_lesson_generation_determinism(),
        smoke_unknown_failure_reason_boundary(),
        smoke_teaching_cli(),
        smoke_second_known_failure_reason_determinism(),
        smoke_multi_lesson_isolation(),
        smoke_conflict_detection_require_review(),
        smoke_conflict_id_stability(),
        smoke_conflict_review_resolution_preview(),
        smoke_conflict_review_preview_audit(),
        smoke_conflict_review_resolution_preconditions(),
        smoke_conflict_review_resolution_dry_run(),
        smoke_phase0_integration_assumption_docs(),
        smoke_phase0_behavior_curiosity_assumption_docs(),
        smoke_phase0_failure_event_interface_docs(),
        smoke_perception_assumption_docs(),
        smoke_lesson_memory_layer_relation_docs(),
        smoke_phase0_assumption_consistency_audit(),
        smoke_failure_event_schema_foundation(),
        smoke_failure_event_normalization_trace(),
        smoke_failure_event_to_lesson_candidate_input_bridge_trace(),
        smoke_failure_event_bridge_audit_regression(),
        smoke_lesson_candidate_builder_contract_docs(),
        smoke_lesson_candidate_builder_contract_audit(),
        smoke_lesson_candidate_builder_literature_references(),
        smoke_lesson_candidate_draft_schema_trace(),
        smoke_lesson_candidate_draft_schema_audit(),
        smoke_lesson_candidate_draft_strict_schema_injection_guard(),
        smoke_outcome_unknown_payload_draft_invariant_guard(),
        smoke_lesson_candidate_draft_review_queue_contract_docs(),
        smoke_lesson_candidate_draft_review_queue_audit(),
        smoke_review_task_trace_schema(),
        smoke_review_task_trace_audit(),
        smoke_review_decision_contract_docs(),
        smoke_review_decision_contract_audit(),
        smoke_rejected_deferred_proposed_fields_masking_contract_docs(),
        smoke_decision_authority_reviewer_identity_session_binding_contract_docs(),
        smoke_review_decision_trace_schema(),
        smoke_review_decision_trace_audit(),
        smoke_soft_hard_consolidation_assumption_docs(),
        smoke_memory_compression_strategy_assumption_docs(),
        smoke_pathological_risk_role_protection_assumption_docs(),
        smoke_core_seed_design_spirit_supplement_docs(),
        smoke_memory_paranoia_misinformation_equivocation_assumption_docs(),
        smoke_equivocation_trace_trust_boundary_correction_docs(),
        smoke_voice_instinct_assumption_docs(),
        smoke_sandbox_boundary_capability_assumption_docs(),
        smoke_sandbox_failure_trace_contract_docs(),
        smoke_phase0_trust_curiosity_personality_boundary_docs(),
        smoke_teaching_cli_conflict_check(),
        smoke_cross_task_shared_prerequisite_isolation(),
        smoke_manual_stale_marking(),
        smoke_supersede_link(),
        smoke_cli_lifecycle_display(),
        smoke_supersede_replacement_suggestion(),
        smoke_strict_supersede_activation(),
        smoke_activation_audit(),
        smoke_activation_regression_suite(),
        smoke_manual_review_state_foundation(),
        smoke_manual_review_cli_display(),
        smoke_manual_review_decision_cli(),
        smoke_manual_review_decision_audit(),
        smoke_review_gated_selection_eligibility(),
        smoke_review_gated_selection_audit(),
        smoke_state_persistence(),
        smoke_concept_layer(),
        smoke_state_core(),
        smoke_expression_guard(),
        smoke_correction_prompt(),
        smoke_deliberation(),
        smoke_integrated_loop(),
        smoke_persistence(),
        smoke_memory_candidate(),
        smoke_correction_pending(),
        smoke_correction_label(),
        smoke_rule_candidate(),
        smoke_candidate_review(),
        smoke_trial_rule(),
        smoke_trial_feedback(),
        smoke_senses(),
    ]


def main() -> int:
    results = run_smoke_tests()
    for result in results:
        tag = "PASS" if result["passed"] else "FAIL"
        print(f"[{tag}] {result['name']}")

    all_passed = all(result["passed"] for result in results)
    report = {
        "summary": {
            "passed": sum(1 for result in results if result["passed"]),
            "total": len(results),
            "all_passed": all_passed,
        },
        "results": results,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if all_passed:
        print("[SUMMARY] all passed")
    else:
        print("[SUMMARY] failed")
    print(f"[LOG] {REPORT_PATH.name} created")
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
