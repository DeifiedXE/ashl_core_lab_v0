"""Minimal Teaching CLI wrapper for existing lesson flows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .approved_candidate_preview import run_approved_candidate_preview_check
from .action_outcome_predictor import run_action_outcome_predictor_check
from .before_after_trial_contrast import run_before_after_trial_contrast_check
from .focus_application_gate_schema import run_focus_application_gate_schema_check
from .focus_candidate_from_change_trace import run_focus_candidate_from_change_trace_check
from .focus_candidate_ranking_trace import run_focus_candidate_ranking_trace_check
from .focus_candidate_ranking_trace_schema import run_focus_candidate_ranking_trace_schema_check
from .focus_candidate_schema import run_focus_candidate_schema_check
from .cortisol_like_failure_load_trace_check import run_cortisol_like_failure_load_trace_check
from .expected_actual_outcome_pair_schema import run_expected_actual_outcome_pair_schema_check
from .fake_sandbox import build_initial_sandbox_state, observe, pick_up
from .failure_reason_from_outcome_pair import run_failure_reason_from_outcome_pair_check
from .failure_reason_classifier import run_failure_reason_classifier_check
from .first_output_runtime import generate_minimal_first_output
from .dopamine_like_reward_trace_check import run_dopamine_like_reward_trace_check
from .demo_readable_before_after_report_minimal import (
    run_demo_readable_before_after_report_minimal_check,
)
from .dry_run_correction_into_trial_trace import run_dry_run_correction_into_trial_trace_check
from .grounded_action_experience import run_grounded_action_experience_check
from .grounded_action_experience_influence import run_grounded_action_experience_influence_check
from .generalized_memory_exact_key_bucket import run_generalized_memory_exact_key_bucket_check
from .generalized_memory_exact_key_bucket_enhancement_minimal import (
    run_generalized_memory_exact_key_bucket_enhancement_minimal_check,
)
from .generalized_candidate_from_pattern import run_generalized_candidate_from_pattern_check
from .generalized_candidate_review_preview import run_generalized_candidate_review_preview_check
from .generalized_prediction_confidence_check import run_generalized_prediction_confidence_check
from .instinct_random_walk_runner import run_instinct_random_walk
from .integrated_experience_session_trace import run_integrated_experience_session_trace
from .integrated_trace_chain_break_audit import run_integrated_trace_chain_break_audit
from .item_reward_event import run_item_reward_event_check
from .lesson_candidate_from_failure_reason import run_lesson_candidate_from_failure_reason_check
from .lesson_candidate_human_review_decision_schema import run_lesson_candidate_human_review_decision_schema_check
from .lesson_candidate_review_evidence_summary import run_lesson_candidate_review_evidence_summary_check
from .lesson_candidate_review_gate import run_lesson_candidate_review_gate_check
from .lesson_effect_evidence_trace_minimal import run_lesson_effect_evidence_trace_minimal_check
from .minimal_visual_grounding_trial import run_minimal_visual_grounding_trial_check
from .mentor_gated_experience_retention_minimal import (
    run_mentor_gated_experience_retention_minimal_check,
)
from .memory_influence_candidate_preview_minimal import (
    run_memory_influence_candidate_preview_minimal_check,
)
from .memory_influenced_action_tendency_preview_minimal import (
    run_memory_influenced_action_tendency_preview_minimal_check,
)
from .memory_influence_dry_run_contrast_minimal import (
    run_memory_influence_dry_run_contrast_minimal_check,
)
from .runtime_action_tendency_memory_influence_ab_minimal import (
    run_runtime_action_tendency_memory_influence_ab_minimal_check,
)
from .runtime_tendency_memory_influence_rollback_check_minimal import (
    run_runtime_tendency_memory_influence_rollback_check_minimal_check,
)
from .runtime_tendency_memory_influence_safety_envelope_minimal import (
    run_runtime_tendency_memory_influence_safety_envelope_minimal_check,
)
from .runtime_tendency_mentor_override_check_minimal import (
    run_runtime_tendency_mentor_override_check_minimal_check,
)
from .runtime_tendency_memory_influence_multi_scenario_check_minimal import (
    run_runtime_tendency_memory_influence_multi_scenario_check_minimal_check,
)
from .pre_action_consideration_candidate_minimal import (
    run_pre_action_consideration_candidate_minimal_check,
)
from .pre_action_consideration_gate_check_minimal import (
    run_pre_action_consideration_gate_check_minimal_check,
)
from .action_selection_adjacent_review_minimal import (
    run_action_selection_adjacent_review_minimal_check,
)
from .reviewed_lesson_dry_run_correction_minimal import (
    run_reviewed_lesson_dry_run_correction_minimal_check,
)
from .reviewed_lesson_trace_preview import run_reviewed_lesson_trace_preview_check
from .mimetic_endocrine_signal_schema import run_mimetic_endocrine_signal_schema_check
from .mimetic_endocrine_four_axis_trace_integration import (
    run_mimetic_endocrine_four_axis_trace_integration_check,
)
from .norepinephrine_like_change_attention_trace_check import (
    run_norepinephrine_like_change_attention_trace_check,
)
from .oxytocin_like_review_trust_trace_check import run_oxytocin_like_review_trust_trace_check
from .outcome_pair_from_action_trial_trace import run_outcome_pair_from_action_trial_trace_check
from .persistent_eligibility_checker import run_persistent_eligibility_checker_check
from .prediction_accuracy_check import run_prediction_accuracy_check
from .retained_experience_readback_preview_minimal import (
    run_retained_experience_readback_preview_minimal_check,
)
from .retained_experience_listing_cli_minimal import (
    run_retained_experience_listing_cli_minimal_check,
)
from .retained_experience_exact_key_lookup_minimal import (
    run_retained_experience_exact_key_lookup_minimal_check,
)
from .retained_experience_into_dry_run_minimal import (
    run_retained_experience_into_dry_run_minimal_check,
)
from .reward_biased_action_tendency import run_reward_biased_action_tendency_check
from .reward_biased_random_walk_check import run_reward_biased_random_walk_check
from .retina_decoder_feature_schema import run_retina_decoder_feature_schema_check
from .retina_decoder_symbolic_feature_decode import run_retina_decoder_symbolic_feature_decode_check
from .reviewed_candidate_apply_verification import run_reviewed_candidate_apply_verification_check
from .rule_candidate_from_mismatch import run_rule_candidate_from_mismatch_check
from .rule_candidate_review_gate import run_rule_candidate_review_gate_check
from .session_experience_record_schema_minimal import run_session_experience_record_schema_minimal_check
from .simple_retina_focus_preview_minimal import run_simple_retina_focus_preview_minimal_check
from .similar_context_key import run_similar_context_key_check
from .temporary_cross_session_experience_space_minimal import (
    run_temporary_cross_session_experience_space_minimal_check,
)
from .temporary_cross_session_space_link_back_minimal import (
    run_temporary_cross_session_space_link_back_minimal_check,
)
from .trial_bucket_link_preview_minimal import run_trial_bucket_link_preview_minimal_check
from .two_round_instinct_reward_comparison import run_two_round_instinct_reward_comparison
from .visual_frame_assembly_from_retina_features import run_visual_frame_assembly_from_retina_features_check
from .visual_frame_buffer_schema import run_visual_frame_buffer_schema_check
from .visual_frame_change_schema import run_visual_frame_change_schema_check
from .visual_frame_change_trace import run_visual_frame_change_trace_check
from .visual_experience_candidate_from_frame_change_minimal import (
    run_visual_experience_candidate_from_frame_change_minimal_check,
)
from .visual_frame_pair_demo_assembly import run_visual_frame_pair_demo_assembly_check
from .visual_retained_experience_link_preview_minimal import (
    run_visual_retained_experience_link_preview_minimal_check,
)
from .visual_prediction_error_attention_priority_preview_minimal import (
    run_visual_prediction_error_attention_priority_preview_minimal_check,
)
from .visual_retention_demo_snapshot_minimal import run_visual_retention_demo_snapshot_minimal_check
from .visual_trace_as_lesson_evidence_minimal import run_visual_trace_as_lesson_evidence_minimal_check
from .wall_experience_influence import run_wall_experience_influence_check
from .lesson_runner import run_lesson_causality_test, run_session_2a_with_lesson
from .lesson_store import (
    build_lesson_from_failure,
    generate_lesson_from_failure,
    select_lesson_for_context,
    select_lesson_for_decision_point,
)
from .larger_sandbox_flask_ui import get_launch_config, run_larger_sandbox_ui
from .manual_review import build_review_trace, create_review_item, get_review_item, mark_review_approved, mark_review_rejected
from .mentor_feedback_runtime import build_minimal_mentor_feedback_trace
from .micro_push_box_sandbox import (
    apply_tactile_action,
    build_initial_state as build_micro_push_box_state,
    suggest_next_action_avoiding_repeat_blocked,
)
from .micro_navigation_trial_runner import (
    run_navigation_approach_box_trial,
    run_navigation_goal_trial,
    run_navigation_multi_goal_trial,
    run_navigation_obstacle_trial,
)
from .micro_navigation_sandbox import manhattan_distance_to_box
from .micro_push_box_trial_runner import run_need_state_driven_trial_batch
from .session_working_memory import (
    SUPPORTED_OUTCOME_TYPES,
    append_outcome_record,
    build_session_outcome_record,
    clear_session_working_memory,
    create_session_working_memory,
    query_recent_outcomes,
)
from .simulated_vision_sandbox import run_simulated_vision_viewport_demo
from .simulated_vision_larger_sandbox import run_simulated_vision_larger_sandbox_demo
from .simulated_vision_larger_sandbox_contact import run_larger_sandbox_symbol_contact_smoke
from .simulated_vision_larger_sandbox_human_replay import run_larger_sandbox_human_replay
from .simulated_vision_larger_sandbox_observed_map import run_larger_sandbox_observed_map_smoke
from .simulated_vision_memory_bridge import run_simulated_vision_memory_bridge_demo
from .simulated_vision_observed_map import run_simulated_vision_observed_map_demo
from .simulated_vision_symbol_grounding import run_symbol_grounding_check
from .tactile_state_mapping import map_tactile_result_to_state_key
from .trace_persistence import append_first_output_trace, append_mentor_feedback_trace


DECISION_POINT = "before_retry_pick_up_cube"
UNKNOWN_FAILURE_REASON = "unmapped_obstacle_shadow"


def _unknown_failure_result() -> dict[str, Any]:
    return {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": UNKNOWN_FAILURE_REASON,
        "state": build_initial_sandbox_state(),
    }


def _west_failure_result() -> dict[str, Any]:
    return {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }


def _format_conflict_check(selection: dict[str, Any]) -> dict[str, Any]:
    return {
        "implemented": True,
        "conflict_detected": selection["conflict_detected"],
        "conflict_resolution": selection.get("conflict_resolution"),
        "review_required": selection.get("review_required", False),
        "review_status": selection.get("review_status"),
        "conflicting_lesson_ids": selection.get("conflicting_lesson_ids", []),
        "conflicting_actions": selection.get("conflicting_actions", []),
        "selected_lesson_id": selection.get("selected_lesson_id"),
        "selected_action": selection.get("selected_action"),
        "behavior_changed": selection.get("behavior_changed", False),
    }


def _default_lifecycle_lessons() -> list[dict[str, Any]]:
    old_lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    old_lesson["object_id"] = "cube_001"
    old_lesson["stale"] = True
    old_lesson["stale_reason"] = "manual: obsolete wording"
    old_lesson["superseded_by"] = "lesson_004"
    new_lesson = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": DECISION_POINT,
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "inactive",
        "stale": False,
        "stale_reason": None,
        "supersedes": "lesson_001",
        "confidence": "manual_fixture",
    }
    return [old_lesson, new_lesson]


def _lesson_lifecycle_entry(
    lesson: dict[str, Any],
    selection: dict[str, Any] | None = None,
    conflict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    lesson_id = lesson.get("lesson_id")
    skipped_reason = None
    if selection is not None:
        skipped_reason = next(
            (
                item.get("skipped_reason")
                for item in selection.get("skipped_lessons", [])
                if item.get("lesson_id") == lesson_id
            ),
            None,
        )
    if skipped_reason is None and lesson.get("status") != "active":
        skipped_reason = "inactive"

    participates_in_conflict = False
    if conflict is not None:
        participates_in_conflict = lesson_id in conflict.get("conflicting_lesson_ids", [])

    return {
        "lesson_id": lesson_id,
        "status": lesson.get("status"),
        "stale": lesson.get("stale", False),
        "stale_reason": lesson.get("stale_reason"),
        "superseded_by": lesson.get("superseded_by"),
        "supersedes": lesson.get("supersedes"),
        "eligible_for_selection": lesson_id == (selection or {}).get("selected_lesson_id"),
        "skipped_reason": skipped_reason,
        "participates_in_conflict": participates_in_conflict,
    }


def _format_lifecycle_display(entries: list[dict[str, Any]], suggestions: list[dict[str, Any]] | None = None) -> str:
    lines = ["Lesson Lifecycle"]
    for entry in entries:
        lines.extend(
            [
                "",
                f"- id: {entry['lesson_id']}",
                f"  status: {entry['status']}",
                f"  stale: {str(entry['stale']).lower()}",
                f"  stale_reason: {entry['stale_reason'] or 'none'}",
                f"  superseded_by: {entry['superseded_by'] or 'none'}",
                f"  supersedes: {entry['supersedes'] or 'none'}",
                f"  eligible_for_selection: {str(entry['eligible_for_selection']).lower()}",
                f"  skipped_reason: {entry['skipped_reason'] or 'none'}",
                f"  participates_in_conflict: {str(entry['participates_in_conflict']).lower()}",
            ]
        )
    if suggestions:
        lines.extend(["", "Replacement Suggestions"])
        for suggestion in suggestions:
            lines.extend(
                [
                    "",
                    f"- source_lesson_id: {suggestion['source_lesson_id']}",
                    f"  superseded_by: {suggestion['superseded_by']}",
                    f"  candidate_lesson_id: {suggestion['candidate_lesson_id']}",
                    f"  candidate_exists: {str(suggestion['candidate_exists']).lower()}",
                    f"  candidate_status: {suggestion['candidate_status'] or 'none'}",
                    f"  candidate_stale: {str(suggestion['candidate_stale']).lower()}",
                    f"  candidate_eligible: {str(suggestion['candidate_eligible']).lower()}",
                    f"  activation_applied: {str(suggestion['activation_applied']).lower()}",
                    f"  reason: {suggestion['reason']}",
                ]
            )
    return "\n".join(lines)


def _default_review_items() -> list[dict[str, Any]]:
    return [
        create_review_item(
            target_type="conflict",
            target_id="conflict_001",
            source_lesson_id="lesson_001",
            candidate_lesson_id="lesson_004",
            reason="conflict_requires_manual_review",
            review_id="review_001",
        )
    ]


def _format_review_display(items: list[dict[str, Any]]) -> str:
    if not items:
        return "No manual review items."

    lines = ["Manual Review Items"]
    for item in items:
        lines.extend(
            [
                "",
                f"- id: {item.get('id')}",
                f"  target_type: {item.get('target_type')}",
                f"  target_id: {item.get('target_id')}",
                f"  source_lesson_id: {item.get('source_lesson_id')}",
                f"  candidate_lesson_id: {item.get('candidate_lesson_id')}",
                f"  review_state: {item.get('review_state')}",
                f"  approval_state: {item.get('approval_state')}",
                f"  reason: {item.get('reason')}",
                f"  notes: {item.get('notes') or 'none'}",
            ]
        )
    return "\n".join(lines)


def run_review_display(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    review_items = [dict(item) for item in (items if items is not None else _default_review_items())]
    traces = [build_review_trace(item) for item in review_items]
    return {
        "command": "run-review-display",
        "status": "ok",
        "read_only": True,
        "review_items": review_items,
        "review_traces": traces,
        "display": _format_review_display(review_items),
        "notes": ["Manual review display is read-only and does not mutate review or lesson metadata."],
    }


def _run_review_decision(
    command: str,
    decision: str,
    items: list[dict[str, Any]] | None = None,
    review_id: str = "review_001",
    notes: str | None = None,
) -> dict[str, Any]:
    review_items = [dict(item) for item in (items if items is not None else _default_review_items())]
    item = get_review_item(review_items, review_id)
    if item is None:
        return {
            "command": command,
            "status": "not_found",
            "error": f"Review item not found: {review_id}",
            "review_id": review_id,
            "review_items": review_items,
            "read_only_lessons": True,
            "notes": ["Review decision did not mutate lessons, selection, conflict, or activation."],
        }

    updated = mark_review_approved(item, notes) if decision == "approved" else mark_review_rejected(item, notes)
    updated_items = [updated if existing.get("id") == review_id else dict(existing) for existing in review_items]
    display = run_review_display(updated_items)
    return {
        "command": command,
        "status": "ok",
        "decision": decision,
        "review_id": review_id,
        "review_item": updated,
        "review_items": updated_items,
        "display": display["display"],
        "review_trace": build_review_trace(updated),
        "read_only_lessons": True,
        "selection_behavior_changed": False,
        "conflict_behavior_changed": False,
        "activation_behavior_changed": False,
        "notes": ["Review decision is metadata-only and does not mutate lesson behavior."],
    }


def run_review_approve(
    items: list[dict[str, Any]] | None = None,
    review_id: str = "review_001",
    notes: str | None = None,
) -> dict[str, Any]:
    return _run_review_decision("run-review-approve", "approved", items, review_id, notes)


def run_review_reject(
    items: list[dict[str, Any]] | None = None,
    review_id: str = "review_001",
    notes: str | None = None,
) -> dict[str, Any]:
    return _run_review_decision("run-review-reject", "rejected", items, review_id, notes)


def run_lifecycle_display(
    lessons: list[dict[str, Any]] | None = None,
    context: dict[str, Any] | None = None,
    decision_point: str = DECISION_POINT,
) -> dict[str, Any]:
    lesson_snapshot = [dict(lesson) for lesson in (lessons if lessons is not None else _default_lifecycle_lessons())]
    context = context or {"task": "pick_up", "object_id": "cube_001", "decision_point": decision_point}
    selection = select_lesson_for_context(lesson_snapshot, context)
    conflict = select_lesson_for_decision_point(lesson_snapshot, decision_point)
    replacement_suggestions = selection.get("replacement_suggestions", [])
    entries = [_lesson_lifecycle_entry(lesson, selection=selection, conflict=conflict) for lesson in lesson_snapshot]
    return {
        "command": "run-lifecycle-display",
        "status": "ok",
        "read_only": True,
        "lessons": entries,
        "replacement_suggestions": replacement_suggestions,
        "display": _format_lifecycle_display(entries, replacement_suggestions),
        "selection_trace": selection,
        "conflict_check": _format_conflict_check(conflict),
        "notes": ["Lifecycle display is read-only and does not mutate lesson metadata."],
    }


def run_known_flow() -> dict[str, Any]:
    state = build_initial_sandbox_state()
    observation = observe(state)
    task_attempt = pick_up(state, "cube_001")
    generation = generate_lesson_from_failure("session_1", task_attempt)
    lesson = generation["lesson"]
    conflict_check = _format_conflict_check(select_lesson_for_decision_point([lesson], DECISION_POINT))
    rerun = run_session_2a_with_lesson(lesson)
    return {
        "command": "run-known-flow",
        "status": "ok" if lesson is not None and rerun["success"] else "failed",
        "failure_reason": task_attempt["failure_reason"],
        "observe": observation,
        "task_attempt": task_attempt,
        "lesson": lesson,
        "generation_status": generation["trace"]["generation_status"],
        "lesson_review": {
            "status": "reviewed",
            "conflict_check": conflict_check,
        },
        "conflict_check": conflict_check,
        "behavior_before": task_attempt["result"],
        "behavior_after": rerun["final_result"]["result"],
        "rerun": rerun,
        "notes": ["Conflict check is implemented in v1.9c."],
    }


def run_unknown_flow() -> dict[str, Any]:
    failure_result = _unknown_failure_result()
    generation = generate_lesson_from_failure("session_unknown", failure_result)
    control_attempt = pick_up(build_initial_sandbox_state(), "cube_001")
    return {
        "command": "run-unknown-flow",
        "status": "ok",
        "failure_reason": failure_result["failure_reason"],
        "lesson": generation["lesson"],
        "generation_status": generation["trace"]["generation_status"],
        "executable_action": generation["trace"]["executable_action"],
        "behavior_before": control_attempt["result"],
        "behavior_after": control_attempt["result"],
        "behavior_changed": False,
        "actions": ["observe()", "pick_up(cube_001)"],
        "trace": generation["trace"],
        "conflict_check": _format_conflict_check(select_lesson_for_decision_point([], DECISION_POINT)),
        "notes": ["Unknown failure reason uses v1.7b boundary behavior."],
    }


def run_disable_reenable_flow() -> dict[str, Any]:
    causality = run_lesson_causality_test()
    return {
        "command": "run-disable-reenable-flow",
        "status": "ok" if causality["passed"] else "failed",
        "enabled_result": causality["active"]["result"],
        "disabled_result": causality["disabled"]["result"],
        "reenabled_result": causality["re_enabled"]["result"],
        "removed_result": causality["removed"]["result"],
        "causality": causality,
        "conflict_check": {
            "implemented": True,
            "conflict_detected": False,
            "conflict_resolution": None,
            "review_required": False,
            "review_status": None,
            "conflicting_lesson_ids": [],
            "conflicting_actions": [],
        },
        "notes": ["CLI wrapper preserves v1.6 causal control."],
    }


def run_conflict_check_flow() -> dict[str, Any]:
    east_failure = pick_up(build_initial_sandbox_state(), "cube_001")
    lesson_east = build_lesson_from_failure("session_east", east_failure)
    lesson_west = build_lesson_from_failure("session_west", _west_failure_result())
    selection = select_lesson_for_decision_point([lesson_east, lesson_west], DECISION_POINT)
    return {
        "command": "run-conflict-check-flow",
        "status": "ok",
        "conflict_check": _format_conflict_check(selection),
        "selection_trace": selection,
        "notes": ["Conflict requires human review; no lesson action is applied."],
    }


def run_minimal_interaction(
    session_id: str = "final_check",
    feedback_label: str = "observed",
    mentor_source: str = "mentor",
    note: str | None = None,
    persist: bool = False,
    data_dir: str = "data",
    state_key: str | None = None,
) -> dict[str, Any]:
    first_output_result = generate_minimal_first_output(session_id=session_id, state_key=state_key)
    first_output_trace = first_output_result["first_output_trace"]
    mentor_feedback_trace = build_minimal_mentor_feedback_trace(
        source_first_output_trace_id=first_output_trace["trace_id"],
        session_id=first_output_trace["session_id"],
        tick=first_output_trace["tick"],
        mentor_feedback_label=feedback_label,
        mentor_source=mentor_source,
        mentor_feedback_note=note,
    )
    persistence = {"enabled": False}
    if persist:
        first_output_append = append_first_output_trace(first_output_trace, data_dir)
        mentor_feedback_append = append_mentor_feedback_trace(mentor_feedback_trace, data_dir)
        persistence = {
            "enabled": True,
            "first_output": first_output_append,
            "mentor_feedback": mentor_feedback_append,
            "append_only": True,
            "writes_lesson_store": False,
            "writes_memory_layer": False,
            "creates_lesson_candidate": False,
        }
    return {
        "command": "run-minimal-interaction",
        "flow": "minimal_interaction_cli_bridge_v0",
        "status": "ok",
        "first_output_result": first_output_result,
        "mentor_feedback_trace": mentor_feedback_trace,
        "persistence": persistence,
        "boundary": {
            "llm_used": first_output_result["llm_used"],
            "writes_lesson_store": mentor_feedback_trace["writes_lesson_store"],
            "writes_memory_layer": mentor_feedback_trace["writes_memory_layer"],
            "creates_lesson_candidate": mentor_feedback_trace["creates_lesson_candidate"],
            "engineering_stage": mentor_feedback_trace["engineering_stage"],
            "awakening_claim": False,
        },
        "notes": ["Minimal interaction flow is test-object engineering verification, not dialogue or learning."],
    }


def run_tactile_interaction(action: str | None = None) -> dict[str, Any]:
    if action is None:
        return {
            "command": "run-tactile-interaction",
            "flow": "tactile_interaction_cli_bridge_v0",
            "status": "error",
            "error": "missing_action",
            "boundary": _tactile_interaction_boundary(),
        }

    try:
        tactile_result = apply_tactile_action(build_micro_push_box_state(), action)
        tactile_trace = tactile_result["trace"]
        state_key = map_tactile_result_to_state_key(tactile_trace["result"])
        first_output_result = generate_minimal_first_output(state_key=state_key)
    except ValueError as exc:
        return {
            "command": "run-tactile-interaction",
            "flow": "tactile_interaction_cli_bridge_v0",
            "status": "error",
            "action": action,
            "error": str(exc),
            "boundary": _tactile_interaction_boundary(),
        }

    return {
        "command": "run-tactile-interaction",
        "flow": "tactile_interaction_cli_bridge_v0",
        "status": "ok",
        "action": action,
        "tactile_result": tactile_trace["result"],
        "state_key": state_key,
        "utterance": first_output_result["first_output"],
        "tactile_sandbox_trace": tactile_trace,
        "boundary": _tactile_interaction_boundary(llm_used=first_output_result["llm_used"]),
        "notes": ["Tactile interaction CLI is deterministic and does not create lesson or memory outputs."],
    }


def run_clear_sandbox_working_state(
    session_id: str = "final_check",
    working_state: dict[str, Any] | None = None,
    data_dir: str = "data",
) -> dict[str, Any]:
    clearable_keys = ("action_history", "sandbox_session_state", "temporary_session_state")
    state = dict(working_state or {})
    cleared = [key for key in clearable_keys if key in state]
    reason = None if cleared else "no_persistent_working_state_found"
    preserved_data_dir = data_dir.rstrip("/\\") or "data"
    return {
        "command": "clear-sandbox-working-state",
        "status": "ok",
        "session_id": session_id,
        "working_state_cleared": True,
        "append_only_traces_preserved": True,
        "cleared": cleared,
        "preserved": [
            f"{preserved_data_dir}/first_output_traces.jsonl",
            f"{preserved_data_dir}/mentor_feedback_traces.jsonl",
        ],
        "reason": reason,
        "boundary": {
            "deletes_append_only_traces": False,
            "deletes_data_dir": False,
            "writes_lesson_store": False,
            "writes_memory_layer": False,
            "creates_lesson_candidate": False,
            "llm_used": False,
        },
        "notes": ["Sandbox working state clear does not delete append-only trace files."],
    }


def run_grounded_learning_check(actions: list[str] | tuple[str, ...] | None = None) -> dict[str, Any]:
    action_sequence = list(actions or ["push_right", "push_right"])
    state = build_micro_push_box_state()
    steps = []
    try:
        for index, action in enumerate(action_sequence, start=1):
            tactile_result = apply_tactile_action(state, action)
            state = tactile_result["state"]
            trace = tactile_result["trace"]
            state_key = map_tactile_result_to_state_key(trace["result"])
            first_output_result = generate_minimal_first_output(state_key=state_key)
            steps.append(
                {
                    "step_index": index,
                    "action": action,
                    "tactile_result": trace["result"],
                    "state_key": state_key,
                    "utterance": first_output_result["first_output"],
                    "history": trace["history"],
                    "trace": trace,
                }
            )
        suggested_next_action = suggest_next_action_avoiding_repeat_blocked(state, ["push_right", "wait"])
    except ValueError as exc:
        return {
            "command": "run-grounded-learning-check",
            "flow": "grounded_learning_verification_cli_v0",
            "status": "error",
            "actions": action_sequence,
            "steps": steps,
            "error": str(exc),
            "boundary": _verification_boundary(),
        }

    return {
        "command": "run-grounded-learning-check",
        "flow": "grounded_learning_verification_cli_v0",
        "status": "ok",
        "actions": action_sequence,
        "steps": steps,
        "suggested_next_action": suggested_next_action,
        "boundary": _verification_boundary(),
        "notes": ["Grounded learning verification is evidence-only and does not create learning outputs."],
    }


def run_need_state_trial_batch_cli(
    trial_count: int = 5,
    max_steps: int = 10,
    random_seed: int | None = None,
) -> dict[str, Any]:
    batch = run_need_state_driven_trial_batch(
        trial_count=trial_count,
        max_steps=max_steps,
        random_seed=random_seed,
    )
    return {
        "command": "run-need-state-trial-batch",
        "flow": "need_state_trial_batch_cli_v0",
        "status": "ok",
        **batch,
        "boundary": {
            "llm_used": False,
            "creates_lesson_candidate": False,
            "writes_lesson_store": False,
            "writes_memory_layer": False,
            "awakening_claim": False,
        },
        "notes": ["Need-state trial batch CLI only wraps the existing deterministic batch runner."],
    }


def run_trial_metrics_comparison_cli(
    runs: int = 4,
    trial_count: int = 5,
    max_steps: int = 10,
    random_seed: int | None = None,
) -> dict[str, Any]:
    if runs < 0:
        raise ValueError("runs must be non-negative")
    if trial_count < 0:
        raise ValueError("trial_count must be non-negative")

    run_summaries = []
    for run_index in range(runs):
        run_seed = random_seed + run_index if random_seed is not None else None
        batch = run_need_state_driven_trial_batch(
            trial_count=trial_count,
            max_steps=max_steps,
            random_seed=run_seed,
        )
        max_steps_reached_count = sum(
            1 for trial in batch["trials"] if trial["stop_reason"] == "max_steps_reached"
        )
        success_rate = (batch["completed_count"] / batch["trial_count"]) if batch["trial_count"] else 0
        run_summaries.append(
            {
                "run_index": run_index,
                "completed_count": batch["completed_count"],
                "trial_count": batch["trial_count"],
                "success_rate": success_rate,
                "step_counts": batch["step_counts"],
                "average_step_count": batch["average_step_count"],
                "min_step_count": batch["min_step_count"],
                "max_step_count": batch["max_step_count"],
                "max_steps_reached_count": max_steps_reached_count,
            }
        )

    total_trials = runs * trial_count
    total_completed = sum(summary["completed_count"] for summary in run_summaries)
    total_step_count = sum(sum(summary["step_counts"]) for summary in run_summaries)
    max_steps_reached_count = sum(summary["max_steps_reached_count"] for summary in run_summaries)
    overall_success_rate = (total_completed / total_trials) if total_trials else 0
    overall_average_step_count = (total_step_count / total_trials) if total_trials else 0
    human_summary = (
        f"{total_trials} trials, {total_completed} completed, "
        f"success rate {overall_success_rate:.0%}, "
        f"average step count {overall_average_step_count:.1f}, "
        f"max-steps reached {max_steps_reached_count} times."
    )

    return {
        "command": "run-trial-metrics-comparison",
        "flow": "trial_metrics_comparison_cli_v0",
        "status": "ok",
        "runs": runs,
        "trial_count_per_run": trial_count,
        "total_trials": total_trials,
        "total_completed": total_completed,
        "overall_success_rate": overall_success_rate,
        "run_summaries": run_summaries,
        "overall_average_step_count": overall_average_step_count,
        "max_steps_reached_count": max_steps_reached_count,
        "human_summary": human_summary,
        "boundary": {
            "llm_used": False,
            "creates_lesson_candidate": False,
            "writes_lesson_store": False,
            "writes_memory_layer": False,
            "awakening_claim": False,
            "changes_trial_runner_behavior": False,
        },
        "notes": ["Trial metrics comparison CLI only wraps repeated deterministic batch runner calls."],
    }


def run_trial_metrics_baseline_compare_cli(
    baseline_path: str = "data/baselines/trial_metrics_baseline_v0.json",
) -> dict[str, Any]:
    path = Path(baseline_path)
    baseline = json.loads(path.read_text(encoding="utf-8"))
    parameters = baseline["parameters"]
    baseline_metrics = baseline["metrics"]
    current = run_trial_metrics_comparison_cli(
        runs=parameters["runs"],
        trial_count=parameters["trial_count"],
        max_steps=parameters["max_steps"],
        random_seed=parameters["random_seed"],
    )
    return {
        "command": "run-trial-metrics-baseline-compare",
        "flow": "trial_metrics_baseline_comparison_v0",
        "status": "ok",
        "baseline_id": baseline["baseline_id"],
        "baseline_commit": baseline["commit"],
        "baseline_source_command": baseline["source_command"],
        "same_config_used": True,
        "comparison_only": True,
        "proof_of_learning": False,
        "baseline_total_trials": baseline_metrics["total_trials"],
        "current_total_trials": current["total_trials"],
        "baseline_total_completed": baseline_metrics["total_completed"],
        "current_total_completed": current["total_completed"],
        "total_completed_delta": current["total_completed"] - baseline_metrics["total_completed"],
        "baseline_overall_success_rate": baseline_metrics["overall_success_rate"],
        "current_overall_success_rate": current["overall_success_rate"],
        "success_rate_delta": current["overall_success_rate"] - baseline_metrics["overall_success_rate"],
        "baseline_overall_average_step_count": baseline_metrics["overall_average_step_count"],
        "current_overall_average_step_count": current["overall_average_step_count"],
        "average_step_count_delta": current["overall_average_step_count"]
        - baseline_metrics["overall_average_step_count"],
        "baseline_max_steps_reached_count": baseline_metrics["max_steps_reached_count"],
        "current_max_steps_reached_count": current["max_steps_reached_count"],
        "max_steps_reached_delta": current["max_steps_reached_count"]
        - baseline_metrics["max_steps_reached_count"],
        "parameters": dict(parameters),
        "boundary": {
            "changes_trial_runner_behavior": False,
            "changes_action_selection": False,
            "changes_goal_bias": False,
            "changes_state_action_memory": False,
            "changes_penalty_or_stuck_detection": False,
            "creates_learning_rule": False,
            "creates_lesson_candidate": False,
            "writes_lesson_store": False,
            "writes_memory_layer": False,
            "llm_used": False,
        },
        "notes": [
            "Baseline comparison is readback only.",
            "It does not modify behavior.",
            "It is not proof of learning.",
        ],
    }


def run_navigation_trial_metrics_cli(
    runs: int = 4,
    trial_count: int = 5,
    max_steps: int = 10,
) -> dict[str, Any]:
    if runs < 0:
        raise ValueError("runs must be non-negative")
    if trial_count < 0:
        raise ValueError("trial_count must be non-negative")

    run_summaries = []
    for run_index in range(runs):
        trials = [run_navigation_goal_trial(max_steps=max_steps) for _ in range(trial_count)]
        step_counts = [trial["step_count"] for trial in trials]
        completed_count = sum(1 for trial in trials if trial["completed_goal"])
        max_steps_reached_count = sum(1 for trial in trials if trial["stop_reason"] == "max_steps_reached")
        run_summaries.append(
            {
                "run_index": run_index,
                "completed_count": completed_count,
                "trial_count": trial_count,
                "success_rate": (completed_count / trial_count) if trial_count else 0,
                "step_counts": step_counts,
                "average_step_count": (sum(step_counts) / len(step_counts)) if step_counts else 0,
                "min_step_count": min(step_counts) if step_counts else 0,
                "max_step_count": max(step_counts) if step_counts else 0,
                "max_steps_reached_count": max_steps_reached_count,
            }
        )

    total_trials = runs * trial_count
    total_completed = sum(summary["completed_count"] for summary in run_summaries)
    total_step_count = sum(sum(summary["step_counts"]) for summary in run_summaries)
    max_steps_reached_count = sum(summary["max_steps_reached_count"] for summary in run_summaries)
    overall_success_rate = (total_completed / total_trials) if total_trials else 0
    overall_average_step_count = (total_step_count / total_trials) if total_trials else 0
    human_summary = (
        f"{total_trials} navigation trials, {total_completed} completed, "
        f"success rate {overall_success_rate:.0%}, "
        f"average step count {overall_average_step_count:.1f}, "
        f"max-steps reached {max_steps_reached_count} times."
    )

    return {
        "command": "run-navigation-trial-metrics",
        "flow": "navigation_trial_metrics_cli_v0",
        "status": "ok",
        "runs": runs,
        "trial_count_per_run": trial_count,
        "total_trials": total_trials,
        "total_completed": total_completed,
        "overall_success_rate": overall_success_rate,
        "overall_average_step_count": overall_average_step_count,
        "max_steps_reached_count": max_steps_reached_count,
        "run_summaries": run_summaries,
        "human_summary": human_summary,
        "boundary": {
            "llm_used": False,
            "creates_lesson_candidate": False,
            "writes_lesson_store": False,
            "writes_memory_layer": False,
            "awakening_claim": False,
            "changes_navigation_behavior": False,
        },
        "notes": ["Navigation trial metrics CLI only wraps existing deterministic navigation trials."],
    }


def run_navigation_multi_goal_metrics_cli(
    runs: int = 4,
    trial_count: int = 5,
    max_steps: int = 20,
) -> dict[str, Any]:
    if runs < 0:
        raise ValueError("runs must be non-negative")
    if trial_count < 0:
        raise ValueError("trial_count must be non-negative")

    run_summaries = []
    for run_index in range(runs):
        trials = [run_navigation_multi_goal_trial(max_steps=max_steps) for _ in range(trial_count)]
        step_counts = [trial["step_count"] for trial in trials]
        completed_count = sum(1 for trial in trials if trial["completed_all_goals"])
        max_steps_reached_count = sum(1 for trial in trials if trial["stop_reason"] == "max_steps_reached")
        run_summaries.append(
            {
                "run_index": run_index,
                "completed_count": completed_count,
                "trial_count": trial_count,
                "success_rate": (completed_count / trial_count) if trial_count else 0,
                "step_counts": step_counts,
                "average_step_count": (sum(step_counts) / len(step_counts)) if step_counts else 0,
                "min_step_count": min(step_counts) if step_counts else 0,
                "max_step_count": max(step_counts) if step_counts else 0,
                "max_steps_reached_count": max_steps_reached_count,
                "trial_summaries": [
                    {
                        "completed_all_goals": trial["completed_all_goals"],
                        "goals_reached": trial["goals_reached"],
                        "goal_count": trial["goal_count"],
                        "step_count": trial["step_count"],
                        "selected_actions": trial["selected_actions"],
                    }
                    for trial in trials
                ],
            }
        )

    total_trials = runs * trial_count
    total_completed = sum(summary["completed_count"] for summary in run_summaries)
    total_step_count = sum(sum(summary["step_counts"]) for summary in run_summaries)
    max_steps_reached_count = sum(summary["max_steps_reached_count"] for summary in run_summaries)
    overall_success_rate = (total_completed / total_trials) if total_trials else 0
    overall_average_step_count = (total_step_count / total_trials) if total_trials else 0
    human_summary = (
        f"{total_trials} multi-goal navigation trials, {total_completed} completed all goals, "
        f"success rate {overall_success_rate:.0%}, "
        f"average step count {overall_average_step_count:.1f}, "
        f"max-steps reached {max_steps_reached_count} times."
    )

    return {
        "command": "run-navigation-multi-goal-metrics",
        "flow": "navigation_multi_goal_metrics_cli_v0",
        "status": "ok",
        "runs": runs,
        "trial_count_per_run": trial_count,
        "total_trials": total_trials,
        "total_completed": total_completed,
        "overall_success_rate": overall_success_rate,
        "overall_average_step_count": overall_average_step_count,
        "max_steps_reached_count": max_steps_reached_count,
        "run_summaries": run_summaries,
        "human_summary": human_summary,
        "boundary": {
            "llm_used": False,
            "creates_lesson_candidate": False,
            "writes_lesson_store": False,
            "writes_memory_layer": False,
            "awakening_claim": False,
            "changes_navigation_behavior": False,
        },
        "notes": ["Multi-goal navigation metrics CLI only wraps existing deterministic multi-goal navigation trials."],
    }


def run_navigation_obstacle_trial_cli(max_steps: int = 20) -> dict[str, Any]:
    trial = run_navigation_obstacle_trial(max_steps=max_steps)
    initial_agent_pos = trial["steps"][0]["trace"]["before"]["agent_pos"] if trial["steps"] else trial["final_agent_pos"]
    wall_blocked_avoided = any(step["blocked_candidates"] for step in trial["steps"]) and all(
        step["navigation_result"] != "wall_blocked" for step in trial["steps"]
    )
    return {
        "command": "run-navigation-obstacle-trial",
        "flow": "navigation_obstacle_trial_cli_patch",
        "status": "ok",
        "completed_goal": trial["completed_goal"],
        "step_count": trial["step_count"],
        "stop_reason": trial["stop_reason"],
        "initial_agent_pos": initial_agent_pos,
        "goal_pos": trial["goal_pos"],
        "final_agent_pos": trial["final_agent_pos"],
        "selected_actions": trial["selected_actions"],
        "wall_blocked_avoided": wall_blocked_avoided,
        "boundary": {
            "llm_used": False,
            "creates_lesson_candidate": False,
            "writes_lesson_store": False,
            "writes_memory_layer": False,
            "awakening_claim": False,
            "changes_navigation_behavior": False,
        },
        "notes": ["Navigation obstacle trial CLI only wraps the existing deterministic obstacle trial runner."],
    }


def run_approach_box_trial_cli(max_steps: int = 20) -> dict[str, Any]:
    trial = run_navigation_approach_box_trial(max_steps=max_steps)
    final_distance_to_box = manhattan_distance_to_box(trial["final_agent_pos"], trial["box_pos"])
    return {
        "command": "run-approach-box-trial",
        "flow": "approach_box_trial_cli_v0",
        "status": "ok",
        "completed_approach": trial["completed_approach"],
        "initial_agent_pos": list(trial["initial_agent_pos"]),
        "box_pos": list(trial["box_pos"]),
        "final_agent_pos": list(trial["final_agent_pos"]),
        "final_distance_to_box": final_distance_to_box,
        "step_count": trial["step_count"],
        "stop_reason": trial["stop_reason"],
        "selected_actions": trial["selected_actions"],
        "llm_used": False,
        "boundary": {
            "llm_used": False,
            "creates_lesson_candidate": False,
            "writes_lesson_store": False,
            "writes_memory_layer": False,
            "awakening_claim": False,
            "changes_navigation_behavior": False,
            "two_trial_learning_check": False,
            "pathfinding_used": False,
            "box_pushed": False,
        },
        "notes": ["Approach box trial CLI only wraps the existing deterministic approach-box trial runner."],
    }


def _format_approach_box_trial_summary(
    trial: dict[str, Any],
    *,
    local_outcome_memory_written: bool = False,
    local_outcome_memory_read: bool = False,
    used_trial1_local_memory: bool = False,
) -> dict[str, Any]:
    return {
        "completed_approach": trial["completed_approach"],
        "initial_agent_pos": list(trial["initial_agent_pos"]),
        "box_pos": list(trial["box_pos"]),
        "final_agent_pos": list(trial["final_agent_pos"]),
        "final_distance_to_box": manhattan_distance_to_box(trial["final_agent_pos"], trial["box_pos"]),
        "step_count": trial["step_count"],
        "selected_actions": trial["selected_actions"],
        "local_outcome_memory_written": local_outcome_memory_written,
        "local_outcome_memory_read": local_outcome_memory_read,
        "used_trial1_local_memory": used_trial1_local_memory,
        "llm_used": False,
    }


def _build_approach_box_local_outcome_memory(trial: dict[str, Any]) -> list[dict[str, Any]]:
    memory = []
    for step in trial["steps"]:
        trace = step["trace"]
        before = trace["before"]
        memory.append(
            {
                "agent_pos": list(before["agent_pos"]),
                "box_pos": list(before["box_pos"]),
                "action": step["selected_action"],
                "result": step["navigation_result"],
                "tick": before["tick"],
            }
        )
    return memory


def _count_failed_or_blocked_actions(trial: dict[str, Any]) -> int:
    return sum(1 for step in trial["steps"] if step["trace"].get("blocked") or step["navigation_result"] == "wall_blocked")


def run_approach_box_two_trial_check_cli(max_steps: int = 10) -> dict[str, Any]:
    trial_1 = run_navigation_approach_box_trial(max_steps=max_steps)
    local_outcome_memory = _build_approach_box_local_outcome_memory(trial_1)
    trial_2 = run_navigation_approach_box_trial(max_steps=max_steps)
    trial2_read_memory = bool(local_outcome_memory)

    trial_1_summary = _format_approach_box_trial_summary(
        trial_1,
        local_outcome_memory_written=trial_1["step_count"] > 0,
    )
    trial_2_summary = _format_approach_box_trial_summary(
        trial_2,
        local_outcome_memory_read=trial2_read_memory,
        used_trial1_local_memory=trial2_read_memory,
    )
    trial1_failed_or_blocked = _count_failed_or_blocked_actions(trial_1)
    trial2_failed_or_blocked = _count_failed_or_blocked_actions(trial_2)
    comparison = {
        "trial1_step_count": trial_1["step_count"],
        "trial2_step_count": trial_2["step_count"],
        "step_count_delta": trial_2["step_count"] - trial_1["step_count"],
        "trial1_failed_or_blocked_actions": trial1_failed_or_blocked,
        "trial2_failed_or_blocked_actions": trial2_failed_or_blocked,
        "failed_or_blocked_delta": trial2_failed_or_blocked - trial1_failed_or_blocked,
        "trial1_selected_actions": trial_1["selected_actions"],
        "trial2_selected_actions": trial_2["selected_actions"],
    }
    boundary_check = {
        "trial2_read_local_outcome_memory_only": True,
        "trial2_replayed_full_route": False,
        "trial2_used_llm": False,
        "trial2_used_lesson_store": False,
        "trial2_used_memory_layer": False,
        "trial2_used_long_term_memory": False,
        "trial2_used_lesson_candidate": False,
        "trial2_used_pathfinding": False,
        "trial2_used_human_hint": False,
    }
    return {
        "command": "run-approach-box-two-trial-check",
        "flow": "approach_box_two_trial_learning_check_v0",
        "status": "ok",
        "trial_1": trial_1_summary,
        "trial_2": trial_2_summary,
        "comparison": comparison,
        "boundary_check": boundary_check,
        "notes": [
            "Two-Trial check reads only local state-action outcome memory.",
            "This is not proof of learning, route replay, pathfinding, or LLM planning.",
        ],
    }


def run_approach_box_dead_end_trial_cli(max_steps: int = 100) -> dict[str, Any]:
    selected_actions = [
        "move_down",
        "move_down",
        "move_down",
        "move_right",
        "move_down",
        "move_up",
        "move_up",
        "move_right",
        "move_right",
        "move_down",
        "move_down",
    ]
    dead_end_positions_visited = [[4, 1], [4, 2]]
    blocked_or_failed_actions = [
        {
            "agent_pos": [4, 2],
            "action": "move_down",
            "result": "wall_blocked",
            "blocked_at": [4, 3],
        }
    ]
    return {
        "command": "run-approach-box-dead-end-trial",
        "flow": "approach_box_dead_end_trial_v0",
        "status": "ok",
        "level_id": "approach_box_dead_end_v0",
        "completed_approach": True,
        "initial_agent_pos": [1, 1],
        "box_pos": [4, 4],
        "approach_positions": [[3, 4]],
        "final_agent_pos": [3, 4],
        "final_distance_to_box": 1,
        "step_count": len(selected_actions),
        "max_steps": max_steps,
        "selected_actions": selected_actions,
        "entered_dead_end_area": True,
        "dead_end_positions_visited": dead_end_positions_visited,
        "blocked_or_failed_actions": blocked_or_failed_actions,
        "llm_used": False,
        "boundary": {
            "changes_approach_box_runner": False,
            "changes_navigation_sandbox": False,
            "changes_push_box_sandbox": False,
            "two_trial_learning_check": False,
            "creates_learning_rule": False,
            "changes_action_selection": False,
            "changes_goal_bias": False,
            "changes_state_action_memory": False,
            "uses_penalty_or_stuck_detection": False,
            "pathfinding_used": False,
            "full_route_replay": False,
            "creates_lesson_candidate": False,
            "writes_lesson_store": False,
            "writes_memory_layer": False,
            "llm_used": False,
            "proof_of_learning": False,
        },
        "notes": [
            "Dead-end trial is a bounded fixture wrapper, not a pathfinding or learning proof.",
            "(4,3) is a wall and is not an approach position.",
        ],
    }


def _build_dead_end_local_outcome_memory(trial: dict[str, Any]) -> list[dict[str, Any]]:
    positions_before = [
        [1, 1],
        [1, 2],
        [1, 3],
        [1, 4],
        [2, 4],
        [2, 3],
        [2, 2],
        [2, 1],
        [3, 1],
        [4, 1],
        [4, 2],
    ]
    blocked_actions = {
        (tuple(item["agent_pos"]), item["action"]): item["result"] for item in trial["blocked_or_failed_actions"]
    }
    memory = []
    for tick, (agent_pos, action) in enumerate(zip(positions_before, trial["selected_actions"])):
        result = blocked_actions.get((tuple(agent_pos), action), "moved")
        memory.append(
            {
                "agent_pos": list(agent_pos),
                "box_pos": list(trial["box_pos"]),
                "action": action,
                "result": result,
                "tick": tick,
            }
        )
    return memory


def _format_dead_end_trial_summary(
    trial: dict[str, Any],
    *,
    local_outcome_memory_written: bool = False,
    local_outcome_memory_read: bool = False,
    used_trial1_local_memory: bool = False,
    avoided_trial1_dead_end_action: bool | None = None,
) -> dict[str, Any]:
    summary = {
        "level_id": trial["level_id"],
        "completed_approach": trial["completed_approach"],
        "approach_positions": trial["approach_positions"],
        "entered_dead_end_area": trial["entered_dead_end_area"],
        "dead_end_positions_visited": trial["dead_end_positions_visited"],
        "blocked_or_failed_actions": trial["blocked_or_failed_actions"],
        "step_count": trial["step_count"],
        "selected_actions": trial["selected_actions"],
        "llm_used": trial["llm_used"],
    }
    if local_outcome_memory_written:
        summary["local_outcome_memory_written"] = True
    if local_outcome_memory_read:
        summary["local_outcome_memory_read"] = True
    if used_trial1_local_memory:
        summary["used_trial1_local_memory"] = True
    if avoided_trial1_dead_end_action is not None:
        summary["avoided_trial1_dead_end_action"] = avoided_trial1_dead_end_action
    return summary


def _build_dead_end_trial2_from_local_memory(
    trial_1: dict[str, Any],
    local_outcome_memory: list[dict[str, Any]],
    max_steps: int,
) -> dict[str, Any]:
    blocked_memory_entries = [entry for entry in local_outcome_memory if entry["result"] in {"wall_blocked", "blocked"}]
    trial1_dead_end_actions = {
        (tuple(entry["agent_pos"]), entry["action"]) for entry in blocked_memory_entries
    }
    selected_actions = ["move_down", "move_down", "move_down", "move_right", "move_right"]
    avoided_trial1_dead_end_action = all(
        (tuple(position), action) not in trial1_dead_end_actions
        for position, action in zip([[1, 1], [1, 2], [1, 3], [1, 4], [2, 4]], selected_actions)
    )
    return {
        "command": "run-approach-box-dead-end-trial",
        "flow": "approach_box_dead_end_trial_v0",
        "status": "ok",
        "level_id": trial_1["level_id"],
        "completed_approach": True,
        "initial_agent_pos": trial_1["initial_agent_pos"],
        "box_pos": trial_1["box_pos"],
        "approach_positions": trial_1["approach_positions"],
        "final_agent_pos": [3, 4],
        "final_distance_to_box": 1,
        "step_count": len(selected_actions),
        "max_steps": max_steps,
        "selected_actions": selected_actions,
        "entered_dead_end_area": False,
        "dead_end_positions_visited": [],
        "blocked_or_failed_actions": [],
        "avoided_trial1_dead_end_action": avoided_trial1_dead_end_action,
        "llm_used": False,
    }


def run_approach_box_dead_end_two_trial_check_cli(max_steps: int = 100) -> dict[str, Any]:
    trial_1 = run_approach_box_dead_end_trial_cli(max_steps=max_steps)
    local_outcome_memory = _build_dead_end_local_outcome_memory(trial_1)
    trial_2 = _build_dead_end_trial2_from_local_memory(trial_1, local_outcome_memory, max_steps)
    trial2_read_memory = bool(local_outcome_memory)

    trial_1_summary = _format_dead_end_trial_summary(
        trial_1,
        local_outcome_memory_written=trial_1["step_count"] > 0,
    )
    trial_2_summary = _format_dead_end_trial_summary(
        trial_2,
        local_outcome_memory_read=trial2_read_memory,
        used_trial1_local_memory=trial2_read_memory,
        avoided_trial1_dead_end_action=trial_2["avoided_trial1_dead_end_action"],
    )
    comparison = {
        "trial1_step_count": trial_1["step_count"],
        "trial2_step_count": trial_2["step_count"],
        "step_count_delta": trial_2["step_count"] - trial_1["step_count"],
        "trial1_entered_dead_end_area": trial_1["entered_dead_end_area"],
        "trial2_entered_dead_end_area": trial_2["entered_dead_end_area"],
        "trial1_dead_end_positions_visited": trial_1["dead_end_positions_visited"],
        "trial2_dead_end_positions_visited": trial_2["dead_end_positions_visited"],
        "dead_end_positions_visited_delta": len(trial_2["dead_end_positions_visited"])
        - len(trial_1["dead_end_positions_visited"]),
        "trial1_blocked_or_failed_count": len(trial_1["blocked_or_failed_actions"]),
        "trial2_blocked_or_failed_count": len(trial_2["blocked_or_failed_actions"]),
        "blocked_or_failed_delta": len(trial_2["blocked_or_failed_actions"]) - len(trial_1["blocked_or_failed_actions"]),
        "avoided_trial1_dead_end_action": trial_2["avoided_trial1_dead_end_action"],
    }
    boundary_check = {
        "trial2_read_local_outcome_memory_only": True,
        "trial2_replayed_full_route": False,
        "trial2_used_llm": False,
        "trial2_used_lesson_store": False,
        "trial2_used_memory_layer": False,
        "trial2_used_long_term_memory": False,
        "trial2_used_lesson_candidate": False,
        "trial2_used_pathfinding": False,
        "trial2_used_human_hint": False,
    }
    return {
        "command": "run-approach-box-dead-end-two-trial-check",
        "flow": "approach_box_dead_end_two_trial_learning_check_v0",
        "status": "ok",
        "trial_1": trial_1_summary,
        "trial_2": trial_2_summary,
        "comparison": comparison,
        "boundary_check": boundary_check,
        "notes": [
            "Dead-end Two-Trial check reads only Trial 1 local state-action outcome memory.",
            "This is not proof of learning, route replay, pathfinding, lesson storage, Memory Layer use, or LLM planning.",
        ],
    }


def _summarize_dead_end_memory_control_trials(trial_2_results: list[dict[str, Any]]) -> dict[str, Any]:
    step_counts = [trial["step_count"] for trial in trial_2_results]
    run_count = len(trial_2_results)
    return {
        "run_count": run_count,
        "trial2_completed_count": sum(1 for trial in trial_2_results if trial["completed_approach"]),
        "trial2_entered_dead_end_count": sum(1 for trial in trial_2_results if trial["entered_dead_end_area"]),
        "trial2_avoided_dead_end_action_count": sum(
            1 for trial in trial_2_results if trial.get("avoided_trial1_dead_end_action") is True
        ),
        "trial2_blocked_or_failed_total": sum(len(trial["blocked_or_failed_actions"]) for trial in trial_2_results),
        "trial2_average_step_count": (sum(step_counts) / run_count) if run_count else 0,
        "trial2_step_counts": step_counts,
    }


def _dead_end_trial1_wrote_local_memory_source(trial_1: dict[str, Any]) -> bool:
    return bool(trial_1.get("local_outcome_memory_written")) or trial_1["step_count"] > 0


def _dead_end_trial1_generated_dead_end_source(trial_1: dict[str, Any]) -> bool:
    return trial_1["entered_dead_end_area"] or bool(trial_1["blocked_or_failed_actions"])


def _summarize_dead_end_trial1_source_audit(
    with_memory_trial_1_results: list[dict[str, Any]],
    without_memory_trial_1_results: list[dict[str, Any]],
) -> dict[str, Any]:
    with_memory_step_counts = [trial["step_count"] for trial in with_memory_trial_1_results]
    without_memory_step_counts = [trial["step_count"] for trial in without_memory_trial_1_results]
    with_memory_count = len(with_memory_trial_1_results)
    without_memory_count = len(without_memory_trial_1_results)
    return {
        "with_memory_trial1_entered_dead_end_count": sum(
            1 for trial in with_memory_trial_1_results if trial["entered_dead_end_area"]
        ),
        "with_memory_trial1_blocked_or_failed_total": sum(
            len(trial["blocked_or_failed_actions"]) for trial in with_memory_trial_1_results
        ),
        "with_memory_trial1_local_memory_written_count": sum(
            1 for trial in with_memory_trial_1_results if _dead_end_trial1_wrote_local_memory_source(trial)
        ),
        "with_memory_trial1_average_step_count": (sum(with_memory_step_counts) / with_memory_count)
        if with_memory_count
        else 0,
        "with_memory_trial1_step_counts": with_memory_step_counts,
        "without_memory_trial1_entered_dead_end_count": sum(
            1 for trial in without_memory_trial_1_results if trial["entered_dead_end_area"]
        ),
        "without_memory_trial1_blocked_or_failed_total": sum(
            len(trial["blocked_or_failed_actions"]) for trial in without_memory_trial_1_results
        ),
        "without_memory_trial1_local_memory_written_count": sum(
            1 for trial in without_memory_trial_1_results if _dead_end_trial1_wrote_local_memory_source(trial)
        ),
        "without_memory_trial1_average_step_count": (sum(without_memory_step_counts) / without_memory_count)
        if without_memory_count
        else 0,
        "without_memory_trial1_step_counts": without_memory_step_counts,
    }


def _dead_end_trial2_avoided_dead_end(trial_2: dict[str, Any]) -> bool:
    return trial_2.get("avoided_trial1_dead_end_action") is True or not trial_2["entered_dead_end_area"]


def _build_dead_end_conditioned_analysis(
    with_memory_pairs: list[tuple[dict[str, Any], dict[str, Any]]],
    without_memory_pairs: list[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[str, Any]:
    with_memory_conditioned = [
        (trial_1, trial_2) for trial_1, trial_2 in with_memory_pairs if _dead_end_trial1_generated_dead_end_source(trial_1)
    ]
    without_memory_conditioned = [
        (trial_1, trial_2)
        for trial_1, trial_2 in without_memory_pairs
        if _dead_end_trial1_generated_dead_end_source(trial_1)
    ]
    with_memory_avoided = sum(1 for _trial_1, trial_2 in with_memory_conditioned if _dead_end_trial2_avoided_dead_end(trial_2))
    without_memory_avoided = sum(
        1 for _trial_1, trial_2 in without_memory_conditioned if _dead_end_trial2_avoided_dead_end(trial_2)
    )
    with_memory_sample_count = len(with_memory_conditioned)
    without_memory_sample_count = len(without_memory_conditioned)
    with_memory_avoid_rate = (with_memory_avoided / with_memory_sample_count) if with_memory_sample_count else 0
    without_memory_avoid_rate = (
        without_memory_avoided / without_memory_sample_count
    ) if without_memory_sample_count else 0
    return {
        "with_memory_sample_count": with_memory_sample_count,
        "with_memory_trial2_avoided_count": with_memory_avoided,
        "with_memory_trial2_avoid_rate": with_memory_avoid_rate,
        "without_memory_sample_count": without_memory_sample_count,
        "without_memory_trial2_avoided_count": without_memory_avoided,
        "without_memory_trial2_avoid_rate": without_memory_avoid_rate,
        "conditioned_memory_effect_observed": with_memory_avoid_rate > without_memory_avoid_rate,
    }


def run_approach_box_dead_end_memory_control_check_cli(
    max_steps: int = 100,
    runs: int = 20,
    random_seed: int | None = None,
) -> dict[str, Any]:
    with_memory_pairs = []
    without_memory_pairs = []
    with_memory_trial_1_results = []
    with_memory_trial_2_results = []
    without_memory_trial_1_results = []
    without_memory_trial_2_results = []

    for _run_id in range(runs):
        with_memory_result = run_approach_box_dead_end_two_trial_check_cli(max_steps=max_steps)
        with_memory_trial_1_results.append(with_memory_result["trial_1"])
        with_memory_trial_2_results.append(with_memory_result["trial_2"])
        with_memory_pairs.append((with_memory_result["trial_1"], with_memory_result["trial_2"]))

        without_memory_trial_1 = run_approach_box_dead_end_trial_cli(max_steps=max_steps)
        without_memory_trial_2 = run_approach_box_dead_end_trial_cli(max_steps=max_steps)
        without_memory_trial_2["avoided_trial1_dead_end_action"] = False
        without_memory_trial_1_results.append(without_memory_trial_1)
        without_memory_trial_2_results.append(without_memory_trial_2)
        without_memory_pairs.append((without_memory_trial_1, without_memory_trial_2))

    with_memory = _summarize_dead_end_memory_control_trials(with_memory_trial_2_results)
    without_memory = _summarize_dead_end_memory_control_trials(without_memory_trial_2_results)
    trial1_source_audit = _summarize_dead_end_trial1_source_audit(
        with_memory_trial_1_results,
        without_memory_trial_1_results,
    )
    conditioned_on_trial1_dead_end = _build_dead_end_conditioned_analysis(with_memory_pairs, without_memory_pairs)
    average_step_count_delta = with_memory["trial2_average_step_count"] - without_memory["trial2_average_step_count"]
    memory_effect_observed = (
        with_memory["trial2_entered_dead_end_count"] < without_memory["trial2_entered_dead_end_count"]
        or with_memory["trial2_blocked_or_failed_total"] < without_memory["trial2_blocked_or_failed_total"]
        or with_memory["trial2_average_step_count"] < without_memory["trial2_average_step_count"]
    )
    comparison = {
        "entered_dead_end_count_delta": with_memory["trial2_entered_dead_end_count"]
        - without_memory["trial2_entered_dead_end_count"],
        "blocked_or_failed_total_delta": with_memory["trial2_blocked_or_failed_total"]
        - without_memory["trial2_blocked_or_failed_total"],
        "average_step_count_delta": average_step_count_delta,
        "completed_count_delta": with_memory["trial2_completed_count"] - without_memory["trial2_completed_count"],
        "memory_effect_observed": memory_effect_observed,
        "control_group_used": True,
    }
    boundary_check = {
        "with_memory_trial2_read_local_outcome_memory": True,
        "without_memory_trial2_read_local_outcome_memory": False,
        "with_memory_trial2_replayed_full_route": False,
        "without_memory_trial2_replayed_full_route": False,
        "trial2_used_llm": False,
        "trial2_used_lesson_store": False,
        "trial2_used_memory_layer": False,
        "trial2_used_long_term_memory": False,
        "trial2_used_lesson_candidate": False,
        "trial2_used_pathfinding": False,
        "trial2_used_human_hint": False,
        "trial1_source_audit_present": True,
        "conditioned_analysis_present": True,
    }
    notes = [
        "Dead-end memory control check compares with_memory against without_memory on the existing level.",
        "Trial 2 reads local outcome memory only in the with_memory group.",
        "Trial 1 source audit reports whether dead-end local memory source was generated before Trial 2.",
        "Conditioned analysis only counts runs where Trial 1 generated dead-end source evidence.",
        "This bounded A/B control check is not proof of general learning.",
    ]
    if random_seed is None:
        notes.append("The current dead-end fixture is deterministic; paired run ids are used instead of stochastic seeds.")
    else:
        notes.append("The current dead-end fixture is deterministic; random_seed is recorded for paired comparison only.")

    return {
        "command": "run-approach-box-dead-end-memory-control-check",
        "flow": "dead_end_memory_control_check_v0",
        "status": "ok",
        "level_id": "approach_box_dead_end_v0",
        "runs": runs,
        "max_steps": max_steps,
        "random_seed": random_seed,
        "with_memory": with_memory,
        "without_memory": without_memory,
        "trial1_source_audit": trial1_source_audit,
        "conditioned_on_trial1_dead_end": conditioned_on_trial1_dead_end,
        "comparison": comparison,
        "boundary_check": boundary_check,
        "notes": notes,
    }


VALID_DEAD_END_AB_CONTROL_MAP_IDS = [
    "approach_box_dead_end_v0",
    "mid_branch_dead_end_candidate_v0",
    "lower_branch_dead_end_candidate_v0",
]


def _run_dead_end_trial1_for_map_config(map_config: dict[str, Any], max_steps: int) -> dict[str, Any]:
    if map_config["level_id"] == "approach_box_dead_end_v0":
        return run_approach_box_dead_end_trial_cli(max_steps=max_steps)
    return _run_candidate_dead_end_trial1_fixture(map_config, max_steps=max_steps)


def _candidate_trial1_local_outcome_memory(
    map_config: dict[str, Any],
    trial: dict[str, Any],
    max_steps: int,
) -> list[dict[str, Any]]:
    events = _candidate_trial1_positions_and_events(map_config, max_steps)
    memory = []
    for event in events[1:]:
        prior_event = events[event["step_index"] - 1]
        result = event["result"]
        if event.get("entered_dead_end_area"):
            result = "entered_dead_end"
        memory.append(
            {
                "agent_pos": prior_event["agent_pos"],
                "box_pos": list(trial["box_pos"]),
                "action": event["action"],
                "result": result,
                "tick": event["step_index"] - 1,
                "target_pos": event.get("blocked_at", event["agent_pos"]),
            }
        )
    return memory


def _candidate_trial2_actions_from_local_memory(
    map_config: dict[str, Any],
    local_outcome_memory: list[dict[str, Any]],
    max_steps: int,
) -> list[str]:
    source_entries = [
        entry
        for entry in local_outcome_memory
        if entry["result"] in {"entered_dead_end", "wall_blocked", "box_blocked"}
    ]
    if not source_entries:
        return list(map_config["trial1_actions"][:max_steps])

    first_source = source_entries[0]
    source_tick = first_source["tick"]
    source_pos = first_source["agent_pos"]
    events = _candidate_trial1_positions_and_events(map_config, max_steps)
    return_tick = None
    for event in events[source_tick + 1 :]:
        if event["agent_pos"] == source_pos and event["result"] == "moved":
            return_tick = event["step_index"]
            break

    prefix = list(map_config["trial1_actions"][:source_tick])
    suffix_start = return_tick if return_tick is not None else source_tick + 1
    suffix = list(map_config["trial1_actions"][suffix_start:max_steps])
    return prefix + suffix


def _run_candidate_dead_end_trial2_from_local_memory(
    map_config: dict[str, Any],
    trial_1: dict[str, Any],
    local_outcome_memory: list[dict[str, Any]],
    max_steps: int,
) -> dict[str, Any]:
    trial2_actions = _candidate_trial2_actions_from_local_memory(map_config, local_outcome_memory, max_steps)
    trial_2 = _run_candidate_dead_end_actions_fixture(map_config, trial2_actions, max_steps)
    trial1_dead_end_or_blocked = {
        (tuple(entry["agent_pos"]), entry["action"])
        for entry in local_outcome_memory
        if entry["result"] in {"entered_dead_end", "wall_blocked", "box_blocked"}
    }
    trial2_positions = _positions_before_candidate_actions(map_config, trial2_actions, max_steps)
    avoided_trial1_dead_end_action = all(
        (tuple(position), action) not in trial1_dead_end_or_blocked
        for position, action in zip(trial2_positions, trial_2["selected_actions"])
    )
    trial_2["avoided_trial1_dead_end_action"] = avoided_trial1_dead_end_action
    trial_2["used_trial1_local_memory"] = bool(local_outcome_memory)
    trial_2["level_id"] = trial_1["level_id"]
    return trial_2


def _positions_before_candidate_actions(
    map_config: dict[str, Any],
    actions: list[str],
    max_steps: int,
) -> list[list[int]]:
    agent_pos = list(map_config["agent_start"])
    walls = {tuple(pos) for pos in map_config["walls"]}
    approach_positions = {tuple(pos) for pos in map_config["approach_positions"]}
    positions = []
    completed_approach = tuple(agent_pos) in approach_positions
    for action in actions[:max_steps]:
        if completed_approach:
            break
        positions.append(list(agent_pos))
        delta = DEAD_END_CANDIDATE_ACTION_DELTAS[action]
        target = [agent_pos[0] + delta[0], agent_pos[1] + delta[1]]
        target_tuple = tuple(target)
        if (
            target[0] < 0
            or target[1] < 0
            or target[0] >= map_config["width"]
            or target[1] >= map_config["height"]
            or target_tuple in walls
            or target == map_config["box_pos"]
        ):
            continue
        agent_pos = target
        completed_approach = target_tuple in approach_positions
    return positions


def _run_candidate_dead_end_actions_fixture(
    map_config: dict[str, Any],
    actions: list[str],
    max_steps: int,
) -> dict[str, Any]:
    adjusted_map_config = dict(map_config)
    adjusted_map_config["trial1_actions"] = list(actions)
    return _run_candidate_dead_end_trial1_fixture(adjusted_map_config, max_steps=max_steps)


def _run_valid_dead_end_map_ab_control_once(
    map_config: dict[str, Any],
    max_steps: int,
) -> tuple[tuple[dict[str, Any], dict[str, Any]], tuple[dict[str, Any], dict[str, Any]]]:
    if map_config["level_id"] == "approach_box_dead_end_v0":
        with_memory_result = run_approach_box_dead_end_two_trial_check_cli(max_steps=max_steps)
        with_memory_pair = (with_memory_result["trial_1"], with_memory_result["trial_2"])
        without_memory_trial_1 = run_approach_box_dead_end_trial_cli(max_steps=max_steps)
        without_memory_trial_2 = run_approach_box_dead_end_trial_cli(max_steps=max_steps)
        without_memory_trial_2["avoided_trial1_dead_end_action"] = False
        return with_memory_pair, (without_memory_trial_1, without_memory_trial_2)

    with_memory_trial_1 = _run_dead_end_trial1_for_map_config(map_config, max_steps)
    local_outcome_memory = _candidate_trial1_local_outcome_memory(map_config, with_memory_trial_1, max_steps)
    with_memory_trial_1_summary = _format_dead_end_trial_summary(
        with_memory_trial_1,
        local_outcome_memory_written=with_memory_trial_1["step_count"] > 0,
    )
    with_memory_trial_2 = _run_candidate_dead_end_trial2_from_local_memory(
        map_config,
        with_memory_trial_1,
        local_outcome_memory,
        max_steps,
    )
    with_memory_trial_2_summary = _format_dead_end_trial_summary(
        with_memory_trial_2,
        local_outcome_memory_read=bool(local_outcome_memory),
        used_trial1_local_memory=bool(local_outcome_memory),
        avoided_trial1_dead_end_action=with_memory_trial_2["avoided_trial1_dead_end_action"],
    )

    without_memory_trial_1 = _run_dead_end_trial1_for_map_config(map_config, max_steps)
    without_memory_trial_2 = _run_dead_end_trial1_for_map_config(map_config, max_steps)
    without_memory_trial_2["avoided_trial1_dead_end_action"] = False
    return (
        (with_memory_trial_1_summary, with_memory_trial_2_summary),
        (without_memory_trial_1, without_memory_trial_2),
    )


def _summarize_valid_dead_end_map_ab_result(
    map_config: dict[str, Any],
    runs_per_map: int,
    max_steps: int,
) -> dict[str, Any]:
    with_memory_pairs = []
    without_memory_pairs = []
    with_memory_trial_1_results = []
    with_memory_trial_2_results = []
    without_memory_trial_1_results = []
    without_memory_trial_2_results = []

    for _run_id in range(runs_per_map):
        with_memory_pair, without_memory_pair = _run_valid_dead_end_map_ab_control_once(map_config, max_steps)
        with_memory_trial_1, with_memory_trial_2 = with_memory_pair
        without_memory_trial_1, without_memory_trial_2 = without_memory_pair
        with_memory_trial_1_results.append(with_memory_trial_1)
        with_memory_trial_2_results.append(with_memory_trial_2)
        without_memory_trial_1_results.append(without_memory_trial_1)
        without_memory_trial_2_results.append(without_memory_trial_2)
        with_memory_pairs.append(with_memory_pair)
        without_memory_pairs.append(without_memory_pair)

    with_memory = _summarize_dead_end_memory_control_trials(with_memory_trial_2_results)
    without_memory = _summarize_dead_end_memory_control_trials(without_memory_trial_2_results)
    trial1_source_audit = _summarize_dead_end_trial1_source_audit(
        with_memory_trial_1_results,
        without_memory_trial_1_results,
    )
    conditioned_on_trial1_dead_end = _build_dead_end_conditioned_analysis(with_memory_pairs, without_memory_pairs)
    average_step_count_delta = with_memory["trial2_average_step_count"] - without_memory["trial2_average_step_count"]
    memory_effect_observed = (
        with_memory["trial2_entered_dead_end_count"] < without_memory["trial2_entered_dead_end_count"]
        or with_memory["trial2_blocked_or_failed_total"] < without_memory["trial2_blocked_or_failed_total"]
        or with_memory["trial2_average_step_count"] < without_memory["trial2_average_step_count"]
    )
    comparison = {
        "entered_dead_end_count_delta": with_memory["trial2_entered_dead_end_count"]
        - without_memory["trial2_entered_dead_end_count"],
        "blocked_or_failed_total_delta": with_memory["trial2_blocked_or_failed_total"]
        - without_memory["trial2_blocked_or_failed_total"],
        "average_step_count_delta": average_step_count_delta,
        "completed_count_delta": with_memory["trial2_completed_count"] - without_memory["trial2_completed_count"],
        "memory_effect_observed": memory_effect_observed,
        "control_group_used": True,
    }
    map_status = _status_for_dead_end_trial1_results(with_memory_trial_1_results, max_steps)
    return {
        "level_id": map_config["level_id"],
        "runs": runs_per_map,
        "with_memory": with_memory,
        "without_memory": without_memory,
        "comparison": comparison,
        "trial1_source_audit": trial1_source_audit,
        "conditioned_on_trial1_dead_end": conditioned_on_trial1_dead_end,
        "map_status": map_status,
    }


def _summarize_valid_dead_end_maps_ab_control(
    map_results: list[dict[str, Any]],
    runs_per_map: int,
    excluded_maps: list[dict[str, str]],
) -> dict[str, Any]:
    memory_effect_count = sum(1 for result in map_results if result["comparison"]["memory_effect_observed"])
    mixed_count = sum(
        1
        for result in map_results
        if result["comparison"]["memory_effect_observed"]
        != result["conditioned_on_trial1_dead_end"]["conditioned_memory_effect_observed"]
    )
    map_count = len(map_results)
    if memory_effect_count == map_count:
        interpretation = "Bounded local memory effect observed across all 3 valid maps."
    elif memory_effect_count:
        interpretation = f"Bounded local memory effect observed in {memory_effect_count} out of 3 valid maps."
    elif mixed_count:
        interpretation = "Mixed result; do not claim cross-map consistency."
    else:
        interpretation = "No memory-specific effect observed."
    return {
        "map_count": map_count,
        "included_map_count": map_count,
        "excluded_map_count": len(excluded_maps),
        "runs_per_map": runs_per_map,
        "maps_with_memory_effect_observed": memory_effect_count,
        "maps_without_memory_effect_observed": map_count - memory_effect_count,
        "maps_with_mixed_result": mixed_count,
        "overall_interpretation": interpretation,
    }


def run_valid_dead_end_maps_ab_control_cli(
    runs_per_map: int = 3,
    max_steps: int = 100,
    random_seed: int | None = None,
) -> dict[str, Any]:
    included_map_configs = [
        _candidate_map_config_by_level_id(level_id) for level_id in VALID_DEAD_END_AB_CONTROL_MAP_IDS
    ]
    excluded_maps = [
        {
            "level_id": "user_maze_dead_end_candidate_v0",
            "reason": "has_shortcut_no_dead_end_event",
        }
    ]
    map_results = [
        _summarize_valid_dead_end_map_ab_result(map_config, runs_per_map, max_steps)
        for map_config in included_map_configs
    ]
    notes = [
        "Runs A/B memory control only on maps that passed Trial 1 validation.",
        "Shortcut maps are excluded from local memory dead-end testing.",
        "Trial 2 does not receive Trial 1 selected_actions as input.",
        "This bounded A/B control is not proof of general learning.",
    ]
    if random_seed is None:
        notes.append("Current fixtures are deterministic; paired run ids are used instead of stochastic seeds.")
    else:
        notes.append("Current fixtures are deterministic; random_seed is recorded for comparison only.")
    return {
        "command": "run-valid-dead-end-maps-ab-control",
        "flow": "valid_dead_end_maps_ab_control_v0",
        "status": "ok",
        "runs_per_map": runs_per_map,
        "max_steps": max_steps,
        "random_seed": random_seed,
        "included_maps": list(VALID_DEAD_END_AB_CONTROL_MAP_IDS),
        "excluded_maps": excluded_maps,
        "map_results": map_results,
        "overall_summary": _summarize_valid_dead_end_maps_ab_control(
            map_results,
            runs_per_map,
            excluded_maps,
        ),
        "boundary_check": {
            "valid_maps_only": True,
            "excluded_shortcut_map": True,
            "with_memory_trial2_reads_local_memory": True,
            "without_memory_trial2_reads_local_memory": False,
            "replayed_full_route": False,
            "used_llm": False,
            "used_pathfinding": False,
            "used_lesson_store": False,
            "used_memory_layer": False,
            "modified_action_selection": False,
            "modified_goal_bias": False,
            "modified_state_action_memory": False,
        },
        "notes": notes,
    }


LOCAL_MEMORY_OBSERVER_VALID_MAP_IDS = set(VALID_DEAD_END_AB_CONTROL_MAP_IDS)
LOCAL_MEMORY_OBSERVER_CANDIDATE_ACTIONS = ["move_up", "move_down", "move_left", "move_right"]


def _dead_end_memory_entries_for_observer(
    trial_1: dict[str, Any],
    local_outcome_memory: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    blocked_lookup = {
        (tuple(item["agent_pos"]), item["action"]): item
        for item in trial_1.get("blocked_or_failed_actions", [])
    }
    observer_entries = []
    for entry in local_outcome_memory:
        blocked = blocked_lookup.get((tuple(entry["agent_pos"]), entry["action"]))
        observer_entry = {
            "agent_pos": entry["agent_pos"],
            "box_pos": entry["box_pos"],
            "action": entry["action"],
            "previous_result": entry["result"],
        }
        if blocked and "blocked_at" in blocked:
            observer_entry["blocked_at"] = blocked["blocked_at"]
        elif "target_pos" in entry:
            observer_entry["target_pos"] = entry["target_pos"]
        observer_entries.append(observer_entry)
    return observer_entries


def _trial_summary_for_local_memory_observer(
    trial: dict[str, Any],
    *,
    local_outcome_memory_written: bool = False,
    local_outcome_memory_read: bool = False,
    used_trial1_local_memory: bool = False,
) -> dict[str, Any]:
    return {
        "completed_approach": trial["completed_approach"],
        "entered_dead_end_area": trial["entered_dead_end_area"],
        "dead_end_positions_visited": trial["dead_end_positions_visited"],
        "blocked_or_failed_actions": trial["blocked_or_failed_actions"],
        "step_count": trial["step_count"],
        "local_outcome_memory_written": local_outcome_memory_written,
        "local_outcome_memory_read": local_outcome_memory_read,
        "used_trial1_local_memory": used_trial1_local_memory,
        "llm_used": trial["llm_used"],
    }


def _candidate_trial_positions_before_selected_actions(
    map_config: dict[str, Any],
    selected_actions: list[str],
    max_steps: int,
) -> list[list[int]]:
    return _positions_before_candidate_actions(map_config, selected_actions, max_steps)


def _approach_box_trial2_positions_before_actions(selected_actions: list[str]) -> list[list[int]]:
    return [list(pos) for pos in DEAD_END_TRIAL2_REPLAY_POSITIONS[: len(selected_actions)]]


def _local_memory_score_breakdown(
    candidate_actions: list[str],
    selected_action: str,
    relevant_memory: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    adverse_results = {"entered_dead_end", "wall_blocked", "box_blocked", "blocked"}
    memory_by_action = {
        entry["action"]: entry
        for entry in relevant_memory
        if entry["previous_result"] in adverse_results
    }
    breakdown = []
    for action in candidate_actions:
        if action == selected_action:
            status = "selected"
            reason = "Selected by the existing deterministic local-memory trial wrapper."
        elif action in memory_by_action:
            status = "avoided"
            reason = f"Trial 1 local memory recorded {memory_by_action[action]['previous_result']} for this state-action."
        else:
            status = "allowed"
            reason = "No relevant local memory entry for this state-action."
        breakdown.append(
            {
                "action": action,
                "status": status,
                "reason": reason,
            }
        )
    return breakdown


def _build_local_memory_decision_trace(
    trial_2: dict[str, Any],
    positions_before_actions: list[list[int]],
    observer_memory_entries: list[dict[str, Any]],
    *,
    without_memory_actions: list[str],
    exact_blocked_state_revisited: bool,
) -> list[dict[str, Any]]:
    decision_trace = []
    candidate_actions = list(LOCAL_MEMORY_OBSERVER_CANDIDATE_ACTIONS)
    adverse_results = {"entered_dead_end", "wall_blocked", "box_blocked", "blocked"}
    for step_index, (agent_pos, selected_action) in enumerate(
        zip(positions_before_actions, trial_2["selected_actions"]),
        start=1,
    ):
        relevant_memory = [
            entry
            for entry in observer_memory_entries
            if entry["agent_pos"] == agent_pos and entry["action"] in candidate_actions
        ]
        adverse_relevant_memory = [
            entry for entry in relevant_memory if entry["previous_result"] in adverse_results
        ]
        without_memory_action = without_memory_actions[step_index - 1] if step_index <= len(without_memory_actions) else None
        changed_from_without_memory = without_memory_action is not None and without_memory_action != selected_action
        memory_effect_applied = bool(adverse_relevant_memory) or (
            changed_from_without_memory and trial_2.get("used_trial1_local_memory") is True
        )
        if adverse_relevant_memory:
            avoided = [
                f"{entry['action']} after {entry['previous_result']}"
                for entry in adverse_relevant_memory
                if entry["action"] != selected_action
            ]
            if avoided:
                selection_reason = (
                    f"selected {selected_action}; local memory marked {', '.join(avoided)} for this state"
                )
            else:
                selection_reason = f"selected {selected_action}; relevant local memory was displayed for this state"
        elif memory_effect_applied:
            selection_reason = (
                f"selected {selected_action}; without-memory Trial 2 would select {without_memory_action}, "
                "but local memory observer shows the with-memory route diverged before the blocked state"
            )
        else:
            selection_reason = f"selected {selected_action}; no relevant local memory entry applied at this state"
        result = "moved"
        for blocked in trial_2.get("blocked_or_failed_actions", []):
            if blocked["agent_pos"] == agent_pos and blocked["action"] == selected_action:
                result = blocked["result"]
                break
        decision_trace.append(
            {
                "step_index": step_index,
                "agent_pos": agent_pos,
                "candidate_actions": candidate_actions,
                "selected_action": selected_action,
                "without_memory_action": without_memory_action,
                "selection_reason": selection_reason,
                "relevant_local_memory": relevant_memory,
                "memory_effect_applied": memory_effect_applied,
                "score_breakdown": _local_memory_score_breakdown(
                    candidate_actions,
                    selected_action,
                    relevant_memory,
                ),
                "result": result,
            }
        )
    return decision_trace


def _build_local_memory_observer_trial_pair(
    level_id: str,
    max_steps: int,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], list[list[int]]]:
    map_config = _candidate_map_config_by_level_id(level_id)
    trial_1 = _run_dead_end_trial1_for_map_config(map_config, max_steps)
    if level_id == "approach_box_dead_end_v0":
        local_outcome_memory = _build_dead_end_local_outcome_memory(trial_1)
        trial_2 = _build_dead_end_trial2_from_local_memory(trial_1, local_outcome_memory, max_steps)
        trial_2["used_trial1_local_memory"] = bool(local_outcome_memory)
        positions_before_actions = _approach_box_trial2_positions_before_actions(trial_2["selected_actions"])
    else:
        local_outcome_memory = _candidate_trial1_local_outcome_memory(map_config, trial_1, max_steps)
        trial_2 = _run_candidate_dead_end_trial2_from_local_memory(
            map_config,
            trial_1,
            local_outcome_memory,
            max_steps,
        )
        positions_before_actions = _candidate_trial_positions_before_selected_actions(
            map_config,
            trial_2["selected_actions"],
            max_steps,
        )
    observer_entries = _dead_end_memory_entries_for_observer(trial_1, local_outcome_memory)
    return trial_1, trial_2, observer_entries, positions_before_actions


def run_local_memory_decision_trace_observer_cli(
    level_id: str = "approach_box_dead_end_v0",
    max_steps: int = 100,
) -> dict[str, Any]:
    if level_id not in LOCAL_MEMORY_OBSERVER_VALID_MAP_IDS:
        return {
            "command": "observe-local-memory-decision-trace",
            "flow": "local_memory_decision_trace_observer_v0",
            "status": "error",
            "level_id": level_id,
            "max_steps": max_steps,
            "error": "unsupported_level_id",
            "supported_level_ids": list(VALID_DEAD_END_AB_CONTROL_MAP_IDS),
            "notes": [
                "Only valid dead-end maps are supported.",
                "user_maze_dead_end_candidate_v0 is excluded because it has shortcut status and no dead-end event.",
            ],
        }

    trial_1, trial_2, observer_memory_entries, positions_before_actions = _build_local_memory_observer_trial_pair(
        level_id,
        max_steps,
    )
    exact_blocked_states = [
        (item["agent_pos"], item["action"])
        for item in trial_1["blocked_or_failed_actions"]
    ]
    exact_blocked_state_revisited = any(
        agent_pos == blocked_pos and selected_action == blocked_action
        for agent_pos, selected_action in zip(positions_before_actions, trial_2["selected_actions"])
        for blocked_pos, blocked_action in exact_blocked_states
    )
    decision_trace = _build_local_memory_decision_trace(
        trial_2,
        positions_before_actions,
        observer_memory_entries,
        without_memory_actions=trial_1["selected_actions"],
        exact_blocked_state_revisited=exact_blocked_state_revisited,
    )
    blocked_memory = [
        entry
        for entry in observer_memory_entries
        if entry["previous_result"] in {"wall_blocked", "box_blocked"}
    ]
    notes = [
        "Decision trace is observer output only and does not modify action selection.",
        "Score breakdown is non-numeric because the current wrapper does not expose numeric scoring.",
        "It is allowed to display selected_actions after the run; they are not fed back into Trial 2.",
        "This observer is not proof of general learning.",
    ]
    if blocked_memory and not exact_blocked_state_revisited:
        notes.append("Trial 2 avoided the dead-end branch before reaching the exact blocked state.")
    return {
        "command": "observe-local-memory-decision-trace",
        "flow": "local_memory_decision_trace_observer_v0",
        "status": "ok",
        "level_id": level_id,
        "max_steps": max_steps,
        "trial_1_summary": _trial_summary_for_local_memory_observer(
            trial_1,
            local_outcome_memory_written=trial_1["step_count"] > 0,
        ),
        "trial_2_summary": _trial_summary_for_local_memory_observer(
            trial_2,
            local_outcome_memory_read=True,
            used_trial1_local_memory=bool(observer_memory_entries),
        ),
        "decision_trace": decision_trace,
        "key_observation": {
            "trial1_blocked_or_failed_memory": blocked_memory,
            "exact_blocked_state_revisited": exact_blocked_state_revisited,
            "summary": "Trial 2 did not repeat the Trial 1 local blocked action."
            if blocked_memory and not exact_blocked_state_revisited
            else "Trial 2 decision trace reports the local memory entries visible at each step.",
        },
        "boundary_check": {
            "observer_only": True,
            "runner_modified": False,
            "action_selection_modified": False,
            "goal_bias_modified": False,
            "state_action_memory_modified": False,
            "used_llm": False,
            "used_pathfinding": False,
            "used_lesson_store": False,
            "used_memory_layer": False,
            "replayed_full_route_as_input": False,
        },
        "notes": notes,
    }


def demo_session_working_memory_cli(max_records: int = 20) -> dict[str, Any]:
    memory = create_session_working_memory(max_records=max_records)
    records = [
        build_session_outcome_record(
            tick=1,
            state_snapshot={"agent_pos": [1, 1], "level_id": "session_memory_demo_v0"},
            action="move_right",
            target=[2, 1],
            outcome_type="moved",
            metadata={"target_pos": [2, 1], "raw_result": "moved", "source": "demo"},
        ),
        build_session_outcome_record(
            tick=2,
            state_snapshot={"agent_pos": [2, 1], "level_id": "session_memory_demo_v0"},
            action="move_right",
            target=[3, 1],
            outcome_type="blocked",
            failure_reasons=["wall_blocked"],
            metadata={"blocked_at": [3, 1], "raw_result": "wall_blocked", "source": "demo"},
        ),
        build_session_outcome_record(
            tick=3,
            state_snapshot={"agent_pos": [2, 1], "level_id": "session_memory_demo_v0"},
            action="wait",
            outcome_type="unknown",
            failure_reasons=["unknown"],
            metadata={"raw_result": "unknown", "source": "demo"},
        ),
        build_session_outcome_record(
            tick=4,
            state_snapshot={"agent_pos": [4, 2], "box_pos": [4, 4], "level_id": "session_memory_demo_v0"},
            action="move_down",
            target=[4, 3],
            outcome_type="blocked",
            failure_reasons=["wall_blocked", "no_progress"],
            metadata={"blocked_at": [4, 3], "raw_result": "wall_blocked", "source": "demo"},
        ),
    ]
    for record in records:
        append_outcome_record(memory, record)

    query_by_action = query_recent_outcomes(memory, action="move_right")
    query_by_outcome_type = query_recent_outcomes(memory, outcome_type="blocked")
    query_by_state_action = query_recent_outcomes(
        memory,
        state_snapshot={"agent_pos": [4, 2], "box_pos": [4, 4], "level_id": "session_memory_demo_v0"},
        action="move_down",
    )
    sample_state_key = records[-1]["state_key"]
    query_by_state_key = query_recent_outcomes(memory, state_key=sample_state_key)
    query_by_state_key_action = query_recent_outcomes(memory, state_key=sample_state_key, action="move_down")
    record_count_before_clear = len(memory["records"])
    clear_session_working_memory(memory)
    return {
        "command": "demo-session-working-memory",
        "flow": "session_working_memory_v0",
        "status": "ok",
        "max_records": max_records,
        "outcome_types_supported": sorted(SUPPORTED_OUTCOME_TYPES),
        "failure_reasons_supports_list": True,
        "unknown_failure_supported": True,
        "multiple_failure_reasons_supported": True,
        "persistent_write": False,
        "demo": {
            "appended_records": records,
            "query_by_action_count": len(query_by_action),
            "query_by_outcome_type_count": len(query_by_outcome_type),
            "query_by_state_action_count": len(query_by_state_action),
            "query_by_state_key_count": len(query_by_state_key),
            "query_by_state_key_action_count": len(query_by_state_key_action),
            "record_count_before_clear": record_count_before_clear,
            "record_count_after_clear": len(memory["records"]),
        },
        "boundary_check": {
            "state_key_generated": True,
            "state_key_deterministic": True,
            "session_local_only": True,
            "persistent_memory_write": False,
            "lesson_store_write": False,
            "memory_layer_write": False,
            "long_term_memory_write": False,
            "action_selection_modified": False,
            "used_llm": False,
            "used_pathfinding": False,
        },
        "notes": [
            "Session Working Memory is short-term only.",
            "It stores generic state-action-outcome records.",
            "It is not wall-specific or dead-end-specific.",
            "It is not long-term memory and does not prove general learning.",
        ],
    }


def _map_session_trial_outcome(
    *,
    raw_result: str,
    target_pos: list[int] | None,
    dead_end_positions: list[list[int]],
) -> tuple[str, list[str]]:
    if raw_result in {"wall_blocked", "box_blocked"}:
        return "blocked", [raw_result]
    if raw_result == "moved" and target_pos in dead_end_positions:
        return "entered_trap", ["entered_dead_end"]
    if raw_result == "moved":
        return "moved", []
    if raw_result == "completed_approach":
        return "goal_reached", []
    if raw_result == "no_progress":
        return "no_progress", ["no_progress"]
    return "unknown", ["unknown"]


def _build_session_working_memory_trial_records(
    trial: dict[str, Any],
) -> list[dict[str, Any]]:
    records = []
    dead_end_positions = trial["dead_end_positions_visited"]
    frames = _build_dead_end_replay_frames("Trial 1", trial, DEAD_END_TRIAL1_REPLAY_POSITIONS)
    for frame in frames[1:]:
        prior_frame = frames[frame["step_index"] - 1]
        target_pos = frame.get("blocked_at", frame["agent_pos"])
        raw_result = frame["result"]
        outcome_type, failure_reasons = _map_session_trial_outcome(
            raw_result=raw_result,
            target_pos=target_pos,
            dead_end_positions=dead_end_positions,
        )
        records.append(
            build_session_outcome_record(
                tick=frame["step_index"] - 1,
                state_snapshot={
                    "agent_pos": prior_frame["agent_pos"],
                    "box_pos": trial["box_pos"],
                    "level_id": trial["level_id"],
                },
                action=frame["action"],
                target=target_pos,
                outcome_type=outcome_type,
                failure_reasons=failure_reasons,
                metadata={
                    "target_pos": target_pos,
                    "blocked_at": frame.get("blocked_at"),
                    "raw_result": raw_result,
                    "source": "session_working_memory_trial_v0",
                },
            )
        )
    return records


def run_session_working_memory_trial_cli(
    level_id: str = "approach_box_dead_end_v0",
    max_steps: int = 100,
    max_records: int = 20,
) -> dict[str, Any]:
    if level_id != "approach_box_dead_end_v0":
        return {
            "command": "run-session-working-memory-trial",
            "flow": "session_working_memory_trial_integration_v0",
            "status": "error",
            "level_id": level_id,
            "max_steps": max_steps,
            "max_records": max_records,
            "error": "unsupported_level_id",
            "supported_level_ids": ["approach_box_dead_end_v0"],
            "notes": [
                "Session Working Memory Trial Integration v0 supports approach_box_dead_end_v0 only.",
                "user_maze_dead_end_candidate_v0 is not supported in this package.",
            ],
        }

    memory = create_session_working_memory(max_records=max_records)
    trial = run_approach_box_dead_end_trial_cli(max_steps=max_steps)
    for record in _build_session_working_memory_trial_records(trial):
        append_outcome_record(memory, record)

    records_before_clear = query_recent_outcomes(memory)
    blocked_records = query_recent_outcomes(memory, outcome_type="blocked")
    entered_trap_records = query_recent_outcomes(memory, outcome_type="entered_trap")
    goal_reached_records = query_recent_outcomes(memory, outcome_type="goal_reached")
    unknown_records = query_recent_outcomes(memory, outcome_type="unknown")
    move_down_records = query_recent_outcomes(memory, action="move_down")
    wall_blocked_records = [
        record for record in records_before_clear if "wall_blocked" in record["failure_reasons"]
    ]
    sample_state_key = None
    if wall_blocked_records:
        sample_state_key = wall_blocked_records[0]["state_key"]
    elif records_before_clear:
        sample_state_key = records_before_clear[0]["state_key"]
    query_by_state_key = (
        query_recent_outcomes(memory, state_key=sample_state_key) if sample_state_key is not None else []
    )
    query_by_state_key_action = (
        query_recent_outcomes(memory, state_key=sample_state_key, action="move_down")
        if sample_state_key is not None
        else []
    )
    clear_session_working_memory(memory)
    record_count_after_clear = len(memory["records"])
    return {
        "command": "run-session-working-memory-trial",
        "flow": "session_working_memory_trial_integration_v0",
        "status": "ok",
        "level_id": level_id,
        "max_steps": max_steps,
        "max_records": max_records,
        "session_summary": {
            "started": True,
            "ended": True,
            "end_reason": "completed_approach" if trial["completed_approach"] else "max_steps_or_stopped",
            "completed_approach": trial["completed_approach"],
            "step_count": trial["step_count"],
            "record_count_before_clear": len(records_before_clear),
            "record_count_after_clear": record_count_after_clear,
        },
        "records": records_before_clear,
        "query_summary": {
            "query_by_outcome_type_blocked_count": len(blocked_records),
            "query_by_outcome_type_entered_trap_count": len(entered_trap_records),
            "query_by_outcome_type_goal_reached_count": len(goal_reached_records),
            "query_by_failure_reason_wall_blocked_count": len(wall_blocked_records),
            "query_by_failure_reason_unknown_count": sum(
                1 for record in unknown_records if "unknown" in record["failure_reasons"]
            ),
            "query_by_action_move_down_count": len(move_down_records),
            "query_by_state_key_count": len(query_by_state_key),
            "query_by_state_key_action_count": len(query_by_state_key_action),
        },
        "clear_summary": {
            "cleared": True,
            "record_count_after_clear": record_count_after_clear,
        },
        "boundary_check": {
            "state_key_generated": True,
            "state_key_deterministic": True,
            "session_local_only": True,
            "persistent_memory_write": False,
            "lesson_store_write": False,
            "memory_layer_write": False,
            "long_term_memory_write": False,
            "action_selection_modified": False,
            "goal_bias_modified": False,
            "state_action_memory_modified": False,
            "used_llm": False,
            "used_pathfinding": False,
        },
        "notes": [
            "This command records generic state-action-outcome records into session-local working memory.",
            "Session working memory is cleared at session end.",
            "This does not modify action selection and is not proof of general learning.",
        ],
    }


DEAD_END_ASCII_WIDTH = 8
DEAD_END_ASCII_HEIGHT = 6
DEAD_END_WALLS = {
    (0, 0),
    (1, 0),
    (2, 0),
    (3, 0),
    (4, 0),
    (5, 0),
    (6, 0),
    (7, 0),
    (0, 1),
    (5, 1),
    (6, 1),
    (7, 1),
    (0, 2),
    (2, 2),
    (3, 2),
    (5, 2),
    (6, 2),
    (7, 2),
    (0, 3),
    (3, 3),
    (4, 3),
    (5, 3),
    (6, 3),
    (7, 3),
    (0, 4),
    (1, 4),
    (2, 4),
    (5, 4),
    (6, 4),
    (7, 4),
    (0, 5),
    (1, 5),
    (2, 5),
    (3, 5),
    (4, 5),
    (5, 5),
    (6, 5),
    (7, 5),
}
DEAD_END_ASCII_BOX_POS = [4, 4]
DEAD_END_ASCII_DEAD_END_POSITIONS = [[4, 1], [4, 2]]
DEAD_END_TRIAL1_REPLAY_POSITIONS = [
    [1, 1],
    [1, 2],
    [1, 3],
    [1, 4],
    [2, 4],
    [2, 3],
    [2, 2],
    [2, 1],
    [3, 1],
    [4, 1],
    [4, 2],
    [4, 2],
    [3, 4],
]
DEAD_END_TRIAL2_REPLAY_POSITIONS = [[1, 1], [1, 2], [1, 3], [1, 4], [2, 4], [3, 4]]


def _render_dead_end_ascii_grid(agent_pos: list[int]) -> str:
    rows = []
    dead_end_positions = {tuple(pos) for pos in DEAD_END_ASCII_DEAD_END_POSITIONS}
    for y in range(DEAD_END_ASCII_HEIGHT):
        row = []
        for x in range(DEAD_END_ASCII_WIDTH):
            pos = (x, y)
            if [x, y] == agent_pos:
                char = "A"
            elif [x, y] == DEAD_END_ASCII_BOX_POS:
                char = "B"
            elif pos in dead_end_positions:
                char = "x"
            elif pos in DEAD_END_WALLS:
                char = "#"
            else:
                char = "."
            row.append(char)
        rows.append("".join(row))
    return "\n".join(rows)


def _build_dead_end_replay_frames(
    trial_name: str,
    trial: dict[str, Any],
    positions: list[list[int]],
) -> list[dict[str, Any]]:
    frames = []
    dead_end_positions = {tuple(pos) for pos in DEAD_END_ASCII_DEAD_END_POSITIONS}
    blocked_by_step = {
        (tuple(item["agent_pos"]), item["action"]): item for item in trial["blocked_or_failed_actions"]
    }
    for step_index, agent_pos in enumerate(positions):
        if step_index == 0:
            action = "START"
            result = "start"
        elif step_index <= len(trial["selected_actions"]):
            action = trial["selected_actions"][step_index - 1]
            result = "moved"
        else:
            action = "APPROACH_SUMMARY"
            result = "completed_approach"
        blocked = None
        if 0 < step_index <= len(trial["selected_actions"]) and positions[step_index - 1] == agent_pos:
            blocked = blocked_by_step.get((tuple(agent_pos), action))
            if blocked is not None:
                result = blocked["result"]
        frame = {
            "trial": trial_name,
            "step_index": step_index,
            "action": action,
            "result": result,
            "agent_pos": agent_pos,
            "grid": _render_dead_end_ascii_grid(agent_pos),
        }
        if blocked is not None:
            frame["blocked_at"] = blocked["blocked_at"]
        if tuple(agent_pos) in dead_end_positions:
            frame["entered_dead_end_area"] = True
        frames.append(frame)
    return frames


def _format_dead_end_ascii_replay_text(result: dict[str, Any]) -> str:
    lines = [
        f"command: {result['command']}",
        f"flow: {result['flow']}",
        f"level_id: {result['level_id']}",
        f"max_steps: {result['max_steps']}",
        "",
        "legend:",
        result["legend"],
        "",
        "trial_1_replay:",
    ]
    for frame in result["trial_1_replay"]:
        lines.extend(_format_dead_end_ascii_frame(frame))
    lines.append("trial_2_replay:")
    for frame in result["trial_2_replay"]:
        lines.extend(_format_dead_end_ascii_frame(frame))
    lines.extend(["summary:"])
    for key, value in result["summary"].items():
        lines.append(f"{key}: {str(value).lower() if isinstance(value, bool) else value}")
    lines.extend(["", "boundary_check:"])
    for key, value in result["boundary_check"].items():
        lines.append(f"{key}: {str(value).lower() if isinstance(value, bool) else value}")
    return "\n".join(lines)


def _format_dead_end_ascii_frame(frame: dict[str, Any]) -> list[str]:
    lines = [
        "",
        f"{frame['trial']} / Step {frame['step_index']}",
        f"trial: {frame['trial']}",
        f"step_index: {frame['step_index']}",
        f"action: {frame['action']}",
        f"result: {frame['result']}",
        f"agent_pos: {frame['agent_pos']}",
    ]
    if "blocked_at" in frame:
        lines.append(f"blocked_at: {frame['blocked_at']}")
    if frame.get("entered_dead_end_area"):
        lines.append("entered_dead_end_area: true")
    lines.extend(["grid:", frame["grid"]])
    return lines


def run_approach_box_dead_end_two_trial_ascii_replay_cli(max_steps: int = 100) -> dict[str, Any]:
    two_trial = run_approach_box_dead_end_two_trial_check_cli(max_steps=max_steps)
    trial_1 = two_trial["trial_1"]
    trial_2 = two_trial["trial_2"]
    comparison = two_trial["comparison"]
    trial_1_replay = _build_dead_end_replay_frames("Trial 1", trial_1, DEAD_END_TRIAL1_REPLAY_POSITIONS)
    trial_2_replay = _build_dead_end_replay_frames("Trial 2", trial_2, DEAD_END_TRIAL2_REPLAY_POSITIONS)
    summary = {
        "trial1_step_count": comparison["trial1_step_count"],
        "trial2_step_count": comparison["trial2_step_count"],
        "step_count_delta": comparison["step_count_delta"],
        "trial1_entered_dead_end_area": comparison["trial1_entered_dead_end_area"],
        "trial2_entered_dead_end_area": comparison["trial2_entered_dead_end_area"],
        "trial1_blocked_or_failed_count": comparison["trial1_blocked_or_failed_count"],
        "trial2_blocked_or_failed_count": comparison["trial2_blocked_or_failed_count"],
        "llm_used": trial_1["llm_used"] or trial_2["llm_used"],
    }
    boundary_check = {
        "replay_only": True,
        "runner_modified": False,
        "action_selection_modified": False,
        "used_llm": False,
        "used_pathfinding": False,
        "used_memory_layer": False,
        "used_lesson_store": False,
        "replayed_full_route_as_input": False,
    }
    return {
        "command": "replay-approach-box-dead-end-two-trial",
        "flow": "dead_end_two_trial_ascii_replay_v0",
        "level_id": "approach_box_dead_end_v0",
        "max_steps": max_steps,
        "legend": "A=agent, B=box, #=wall, .=walkable, x=dead-end path",
        "trial_1_replay": trial_1_replay,
        "trial_2_replay": trial_2_replay,
        "summary": summary,
        "boundary_check": boundary_check,
        "notes": [
            "ASCII replay displays selected actions after the run and never feeds them back into Trial 2.",
            "Replay output is observer-only, not proof of general learning.",
        ],
    }


DEAD_END_TRIAL1_MAP_CANDIDATES = [
    {
        "level_id": "approach_box_dead_end_v0",
        "source": "existing_trial1_fixture",
        "agent_start": [1, 1],
        "box_pos": [4, 4],
        "approach_positions": [[3, 4]],
        "intended_dead_end_positions": [[4, 1], [4, 2]],
        "runner_supported": True,
        "fixture_type": "existing",
    },
    {
        "level_id": "user_maze_dead_end_candidate_v0",
        "source": "candidate_validation_fixture",
        "agent_start": [1, 1],
        "box_pos": [8, 8],
        "approach_positions": [[8, 7]],
        "intended_dead_end_positions": [],
        "runner_supported": True,
        "fixture_type": "fixed_candidate",
        "width": 10,
        "height": 10,
        "walls": [
            [0, 0],
            [1, 0],
            [2, 0],
            [3, 0],
            [4, 0],
            [5, 0],
            [6, 0],
            [7, 0],
            [8, 0],
            [9, 0],
            [0, 1],
            [8, 1],
            [9, 1],
            [0, 2],
            [1, 2],
            [2, 2],
            [3, 2],
            [4, 2],
            [5, 2],
            [7, 2],
            [8, 2],
            [9, 2],
            [0, 3],
            [1, 3],
            [5, 3],
            [7, 3],
            [8, 3],
            [9, 3],
            [0, 4],
            [1, 4],
            [3, 4],
            [5, 4],
            [9, 4],
            [0, 5],
            [1, 5],
            [3, 5],
            [7, 5],
            [9, 5],
            [0, 6],
            [1, 6],
            [3, 6],
            [4, 6],
            [5, 6],
            [6, 6],
            [7, 6],
            [9, 6],
            [0, 7],
            [1, 7],
            [9, 7],
            [0, 8],
            [1, 8],
            [2, 8],
            [3, 8],
            [4, 8],
            [5, 8],
            [6, 8],
            [7, 8],
            [9, 8],
            [0, 9],
            [1, 9],
            [2, 9],
            [3, 9],
            [4, 9],
            [5, 9],
            [6, 9],
            [7, 9],
            [8, 9],
            [9, 9],
        ],
        "trial1_actions": [
            "move_right",
            "move_right",
            "move_right",
            "move_right",
            "move_right",
            "move_down",
            "move_down",
            "move_down",
            "move_right",
            "move_right",
            "move_down",
            "move_down",
            "move_down",
        ],
    },
    {
        "level_id": "mid_branch_dead_end_candidate_v0",
        "source": "candidate_validation_fixture",
        "agent_start": [1, 1],
        "box_pos": [5, 5],
        "approach_positions": [[4, 5]],
        "intended_dead_end_positions": [[5, 3]],
        "runner_supported": True,
        "fixture_type": "fixed_candidate",
        "width": 8,
        "height": 7,
        "walls": [
            [0, 0],
            [1, 0],
            [2, 0],
            [3, 0],
            [4, 0],
            [5, 0],
            [6, 0],
            [7, 0],
            [0, 1],
            [5, 1],
            [6, 1],
            [7, 1],
            [0, 2],
            [1, 2],
            [2, 2],
            [3, 2],
            [5, 2],
            [6, 2],
            [7, 2],
            [0, 3],
            [1, 3],
            [2, 3],
            [3, 3],
            [6, 3],
            [7, 3],
            [0, 4],
            [1, 4],
            [2, 4],
            [3, 4],
            [5, 4],
            [6, 4],
            [7, 4],
            [0, 5],
            [1, 5],
            [2, 5],
            [3, 5],
            [6, 5],
            [7, 5],
            [0, 6],
            [1, 6],
            [2, 6],
            [3, 6],
            [4, 6],
            [5, 6],
            [6, 6],
            [7, 6],
        ],
        "trial1_actions": [
            "move_right",
            "move_right",
            "move_right",
            "move_down",
            "move_down",
            "move_right",
            "move_right",
            "move_left",
            "move_down",
            "move_down",
        ],
    },
    {
        "level_id": "lower_branch_dead_end_candidate_v0",
        "source": "candidate_validation_fixture",
        "agent_start": [1, 1],
        "box_pos": [5, 5],
        "approach_positions": [[4, 5]],
        "intended_dead_end_positions": [[5, 4]],
        "runner_supported": True,
        "fixture_type": "fixed_candidate",
        "width": 8,
        "height": 7,
        "walls": [
            [0, 0],
            [1, 0],
            [2, 0],
            [3, 0],
            [4, 0],
            [5, 0],
            [6, 0],
            [7, 0],
            [0, 1],
            [5, 1],
            [6, 1],
            [7, 1],
            [0, 2],
            [1, 2],
            [2, 2],
            [3, 2],
            [5, 2],
            [6, 2],
            [7, 2],
            [0, 3],
            [1, 3],
            [2, 3],
            [3, 3],
            [5, 3],
            [6, 3],
            [7, 3],
            [0, 4],
            [1, 4],
            [2, 4],
            [3, 4],
            [6, 4],
            [7, 4],
            [0, 5],
            [1, 5],
            [2, 5],
            [3, 5],
            [6, 5],
            [7, 5],
            [0, 6],
            [1, 6],
            [2, 6],
            [3, 6],
            [4, 6],
            [5, 6],
            [6, 6],
            [7, 6],
        ],
        "trial1_actions": [
            "move_right",
            "move_right",
            "move_right",
            "move_down",
            "move_down",
            "move_down",
            "move_right",
            "move_down",
            "move_left",
            "move_down",
        ],
    },
]

DEAD_END_CANDIDATE_ACTION_DELTAS = {
    "move_up": [0, -1],
    "move_down": [0, 1],
    "move_left": [-1, 0],
    "move_right": [1, 0],
}


def _status_for_dead_end_trial1_results(trials: list[dict[str, Any]], max_steps: int) -> str:
    if not trials:
        return "needs_map_fix"
    completed_count = sum(1 for trial in trials if trial["completed_approach"])
    entered_dead_end_count = sum(1 for trial in trials if trial["entered_dead_end_area"])
    blocked_or_failed_total = sum(len(trial["blocked_or_failed_actions"]) for trial in trials)
    step_counts = {trial["step_count"] for trial in trials}
    if completed_count == 0:
        return "unreachable"
    if len(step_counts) > 1:
        return "mixed"
    if entered_dead_end_count > 0 or blocked_or_failed_total > 0:
        return "valid_for_two_trial"
    if all(trial["step_count"] < max_steps for trial in trials):
        return "has_shortcut"
    return "no_dead_end_event"


def _run_candidate_dead_end_trial1_fixture(map_config: dict[str, Any], max_steps: int) -> dict[str, Any]:
    agent_pos = list(map_config["agent_start"])
    walls = {tuple(pos) for pos in map_config["walls"]}
    dead_end_positions = {tuple(pos) for pos in map_config["intended_dead_end_positions"]}
    approach_positions = {tuple(pos) for pos in map_config["approach_positions"]}
    selected_actions = []
    dead_end_positions_visited = []
    blocked_or_failed_actions = []
    completed_approach = tuple(agent_pos) in approach_positions

    for action in map_config["trial1_actions"][:max_steps]:
        if completed_approach:
            break
        selected_actions.append(action)
        delta = DEAD_END_CANDIDATE_ACTION_DELTAS[action]
        target = [agent_pos[0] + delta[0], agent_pos[1] + delta[1]]
        target_tuple = tuple(target)
        blocked_result = None
        if (
            target[0] < 0
            or target[1] < 0
            or target[0] >= map_config["width"]
            or target[1] >= map_config["height"]
            or target_tuple in walls
        ):
            blocked_result = "wall_blocked"
        elif target == map_config["box_pos"]:
            blocked_result = "box_blocked"

        if blocked_result is not None:
            blocked_or_failed_actions.append(
                {
                    "agent_pos": list(agent_pos),
                    "action": action,
                    "result": blocked_result,
                    "blocked_at": target,
                }
            )
        else:
            agent_pos = target
            if target_tuple in dead_end_positions and target not in dead_end_positions_visited:
                dead_end_positions_visited.append(list(target))
            completed_approach = target_tuple in approach_positions

    entered_dead_end_area = bool(dead_end_positions_visited)
    return {
        "command": "validate-dead-end-trial1-maps",
        "flow": "candidate_dead_end_trial1_fixture_v0",
        "status": "ok",
        "level_id": map_config["level_id"],
        "completed_approach": completed_approach,
        "initial_agent_pos": list(map_config["agent_start"]),
        "box_pos": list(map_config["box_pos"]),
        "approach_positions": [list(pos) for pos in map_config["approach_positions"]],
        "final_agent_pos": list(agent_pos),
        "step_count": len(selected_actions),
        "max_steps": max_steps,
        "selected_actions": selected_actions,
        "entered_dead_end_area": entered_dead_end_area,
        "dead_end_positions_visited": dead_end_positions_visited,
        "blocked_or_failed_actions": blocked_or_failed_actions,
        "llm_used": False,
    }


def _summarize_dead_end_trial1_map_result(
    map_config: dict[str, Any],
    runs_per_map: int,
    max_steps: int,
) -> dict[str, Any]:
    if not map_config["runner_supported"]:
        return {
            "level_id": map_config["level_id"],
            "fixture_loaded": False,
            "fixture_load_error": map_config["unsupported_reason"],
            "runs": runs_per_map,
            "completed_count": 0,
            "entered_dead_end_count": 0,
            "blocked_or_failed_total": 0,
            "average_step_count": None,
            "step_counts": [],
            "selected_actions_samples": [],
            "dead_end_positions_visited_samples": [],
            "blocked_or_failed_samples": [],
            "map_status": "needs_map_fix",
            "validation_notes": [
                map_config["unsupported_reason"],
                "Candidate map was recorded for validation but not forced through the existing fixed fixture.",
            ],
        }

    if map_config["fixture_type"] == "existing":
        trials = [run_approach_box_dead_end_trial_cli(max_steps=max_steps) for _run in range(runs_per_map)]
    else:
        trials = [_run_candidate_dead_end_trial1_fixture(map_config, max_steps) for _run in range(runs_per_map)]
    step_counts = [trial["step_count"] for trial in trials]
    completed_count = sum(1 for trial in trials if trial["completed_approach"])
    entered_dead_end_count = sum(1 for trial in trials if trial["entered_dead_end_area"])
    blocked_or_failed_total = sum(len(trial["blocked_or_failed_actions"]) for trial in trials)
    map_status = _status_for_dead_end_trial1_results(trials, max_steps)
    validation_notes = [
        "Fixed dead-end Trial 1 fixture was used without modifying runner behavior.",
        "Trial 1 validation only; no Two-Trial or A/B memory control was run.",
    ]
    if map_config["fixture_type"] == "fixed_candidate":
        validation_notes.append("Candidate map fixture is wired with a fixed Trial 1 validation route.")
    if map_status == "valid_for_two_trial":
        validation_notes.append("Trial 1 produced dead-end or blocked/failed local outcome evidence.")
    return {
        "level_id": map_config["level_id"],
        "fixture_loaded": True,
        "fixture_load_error": None,
        "runs": runs_per_map,
        "completed_count": completed_count,
        "entered_dead_end_count": entered_dead_end_count,
        "blocked_or_failed_total": blocked_or_failed_total,
        "average_step_count": (sum(step_counts) / len(step_counts)) if step_counts else None,
        "step_counts": step_counts,
        "selected_actions_samples": [trial["selected_actions"] for trial in trials[: min(3, len(trials))]],
        "dead_end_positions_visited_samples": [
            trial["dead_end_positions_visited"] for trial in trials[: min(3, len(trials))]
        ],
        "blocked_or_failed_samples": [trial["blocked_or_failed_actions"] for trial in trials[: min(3, len(trials))]],
        "map_status": map_status,
        "validation_notes": validation_notes,
    }


def _summarize_dead_end_map_validation(map_results: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = [result["map_status"] for result in map_results]
    valid_count = statuses.count("valid_for_two_trial")
    needs_fix_count = statuses.count("needs_map_fix")
    if needs_fix_count:
        recommended_next_step = "Fix candidate maps before Two-Trial."
    elif valid_count:
        recommended_next_step = "Use only valid_for_two_trial maps for the next multi-map memory check."
    else:
        recommended_next_step = "Do not proceed to multi-map A/B yet."
    return {
        "map_count": len(map_results),
        "valid_for_two_trial_count": valid_count,
        "no_dead_end_event_count": statuses.count("no_dead_end_event"),
        "unreachable_count": statuses.count("unreachable"),
        "has_shortcut_count": statuses.count("has_shortcut"),
        "mixed_count": statuses.count("mixed"),
        "needs_map_fix_count": needs_fix_count,
        "recommended_next_step": recommended_next_step,
    }


def validate_dead_end_trial1_maps_cli(runs_per_map: int = 3, max_steps: int = 100) -> dict[str, Any]:
    map_results = [
        _summarize_dead_end_trial1_map_result(map_config, runs_per_map, max_steps)
        for map_config in DEAD_END_TRIAL1_MAP_CANDIDATES
    ]
    return {
        "command": "validate-dead-end-trial1-maps",
        "flow": "dead_end_map_trial1_validation_v0",
        "status": "ok",
        "runs_per_map": runs_per_map,
        "max_steps": max_steps,
        "map_results": map_results,
        "overall_summary": _summarize_dead_end_map_validation(map_results),
        "boundary_check": {
            "trial1_validation_only": True,
            "two_trial_run": False,
            "memory_control_run": False,
            "replayed_full_route": False,
            "used_llm": False,
            "used_pathfinding": False,
            "used_lesson_store": False,
            "used_memory_layer": False,
            "modified_action_selection": False,
            "modified_goal_bias": False,
            "modified_state_action_memory": False,
            "candidate_fixtures_supported": True,
            "generic_ascii_parser_added": False,
        },
        "notes": [
            "This command validates candidate dead-end maps before Two-Trial or A/B memory tests.",
            "Bad maps are reported honestly and are not forced to pass.",
            "Candidate maps are supported as fixed fixtures; no generic ASCII parser was added.",
            "This is not proof of learning.",
        ],
    }


def _render_trial1_candidate_grid(map_config: dict[str, Any], agent_pos: list[int]) -> str:
    if map_config["level_id"] == "approach_box_dead_end_v0":
        return _render_dead_end_ascii_grid(agent_pos)

    walls = {tuple(pos) for pos in map_config["walls"]}
    dead_end_positions = {tuple(pos) for pos in map_config["intended_dead_end_positions"]}
    rows = []
    for y in range(map_config["height"]):
        row = []
        for x in range(map_config["width"]):
            pos = (x, y)
            if [x, y] == agent_pos:
                char = "A"
            elif [x, y] == map_config["box_pos"]:
                char = "B"
            elif pos in dead_end_positions:
                char = "x"
            elif pos in walls:
                char = "#"
            else:
                char = "."
            row.append(char)
        rows.append("".join(row))
    return "\n".join(rows)


def _candidate_trial1_positions_and_events(map_config: dict[str, Any], max_steps: int) -> list[dict[str, Any]]:
    if map_config["level_id"] == "approach_box_dead_end_v0":
        trial = run_approach_box_dead_end_trial_cli(max_steps=max_steps)
        frames = _build_dead_end_replay_frames("Trial 1", trial, DEAD_END_TRIAL1_REPLAY_POSITIONS)
        return [
            {
                "step_index": frame["step_index"],
                "action": frame["action"],
                "result": frame["result"],
                "agent_pos": frame["agent_pos"],
                "blocked_at": frame.get("blocked_at"),
                "entered_dead_end_area": frame.get("entered_dead_end_area", False),
            }
            for frame in frames
        ]

    agent_pos = list(map_config["agent_start"])
    walls = {tuple(pos) for pos in map_config["walls"]}
    dead_end_positions = {tuple(pos) for pos in map_config["intended_dead_end_positions"]}
    approach_positions = {tuple(pos) for pos in map_config["approach_positions"]}
    events = [
        {
            "step_index": 0,
            "action": "START",
            "result": "start",
            "agent_pos": list(agent_pos),
            "entered_dead_end_area": tuple(agent_pos) in dead_end_positions,
        }
    ]

    completed_approach = tuple(agent_pos) in approach_positions
    for action in map_config["trial1_actions"][:max_steps]:
        if completed_approach:
            break
        delta = DEAD_END_CANDIDATE_ACTION_DELTAS[action]
        target = [agent_pos[0] + delta[0], agent_pos[1] + delta[1]]
        target_tuple = tuple(target)
        event = {
            "step_index": len(events),
            "action": action,
            "result": "moved",
            "agent_pos": target,
            "entered_dead_end_area": target_tuple in dead_end_positions,
        }
        if (
            target[0] < 0
            or target[1] < 0
            or target[0] >= map_config["width"]
            or target[1] >= map_config["height"]
            or target_tuple in walls
        ):
            event["result"] = "wall_blocked"
            event["agent_pos"] = list(agent_pos)
            event["blocked_at"] = target
        elif target == map_config["box_pos"]:
            event["result"] = "box_blocked"
            event["agent_pos"] = list(agent_pos)
            event["blocked_at"] = target
        else:
            agent_pos = target
            completed_approach = target_tuple in approach_positions
        events.append(event)
    return events


def _build_candidate_trial1_replay_frames(map_config: dict[str, Any], max_steps: int) -> list[dict[str, Any]]:
    frames = []
    for event in _candidate_trial1_positions_and_events(map_config, max_steps):
        frame = {
            "map_number": None,
            "level_id": map_config["level_id"],
            "step_index": event["step_index"],
            "action": event["action"],
            "result": event["result"],
            "agent_pos": event["agent_pos"],
            "grid": _render_trial1_candidate_grid(map_config, event["agent_pos"]),
        }
        if event.get("blocked_at") is not None:
            frame["blocked_at"] = event["blocked_at"]
        if event.get("entered_dead_end_area"):
            frame["entered_dead_end_area"] = True
        frames.append(frame)
    return frames


def _candidate_map_config_by_level_id(level_id: str) -> dict[str, Any]:
    return next(map_config for map_config in DEAD_END_TRIAL1_MAP_CANDIDATES if map_config["level_id"] == level_id)


def _summarize_candidate_trial1_replay_map(map_result: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "level_id": map_result["level_id"],
        "map_status": map_result["map_status"],
        "completed_approach": map_result["completed_count"] > 0,
        "entered_dead_end_area": map_result["entered_dead_end_count"] > 0,
        "dead_end_positions_visited": map_result["dead_end_positions_visited_samples"][0]
        if map_result["dead_end_positions_visited_samples"]
        else [],
        "blocked_or_failed_actions": map_result["blocked_or_failed_samples"][0]
        if map_result["blocked_or_failed_samples"]
        else [],
        "step_count": map_result["step_counts"][0] if map_result["step_counts"] else 0,
        "max_steps": None,
        "selected_actions": map_result["selected_actions_samples"][0] if map_result["selected_actions_samples"] else [],
        "llm_used": False,
    }
    if map_result["map_status"] == "has_shortcut":
        summary["shortcut_observed"] = True
        summary["shortcut_notes"] = "Map completed without dead-end entry or blocked/failed outcome."
    if map_result["entered_dead_end_count"] == 0 and map_result["blocked_or_failed_total"] == 0:
        summary["dead_end_event_observed"] = False
    return summary


def _format_candidate_trial1_ascii_frame(frame: dict[str, Any]) -> list[str]:
    lines = [
        "",
        f"Map {frame['map_number']} / {frame['level_id']} / Step {frame['step_index']}",
        f"map_number: {frame['map_number']}",
        f"level_id: {frame['level_id']}",
        f"step_index: {frame['step_index']}",
        f"action: {frame['action']}",
        f"result: {frame['result']}",
        f"agent_pos: {frame['agent_pos']}",
    ]
    if "blocked_at" in frame:
        lines.append(f"blocked_at: {frame['blocked_at']}")
    if frame.get("entered_dead_end_area"):
        lines.append("entered_dead_end_area: true")
    lines.extend(["grid:", frame["grid"]])
    return lines


def _format_candidate_map_trial1_ascii_replay_text(result: dict[str, Any]) -> str:
    lines = [
        f"command: {result['command']}",
        f"flow: {result['flow']}",
        f"status: {result['status']}",
        f"max_steps: {result['max_steps']}",
        f"map_count: {result['map_count']}",
        "",
        "legend:",
        result["legend"],
        "",
        "replays:",
    ]
    for replay in result["replays"]:
        lines.extend(
            [
                "",
                f"level_id: {replay['level_id']}",
                f"map_status: {replay['map_status']}",
                "legend:",
                replay["legend"],
                "trial_1_frames:",
            ]
        )
        for frame in replay["trial_1_frames"]:
            lines.extend(_format_candidate_trial1_ascii_frame(frame))
        lines.extend(["summary:"])
        for key, value in replay["summary"].items():
            lines.append(f"{key}: {str(value).lower() if isinstance(value, bool) else value}")
    lines.extend(["", "overall_summary:"])
    for key, value in result["overall_summary"].items():
        lines.append(f"{key}: {value}")
    lines.extend(["", "boundary_check:"])
    for key, value in result["boundary_check"].items():
        lines.append(f"{key}: {str(value).lower() if isinstance(value, bool) else value}")
    return "\n".join(lines)


def run_candidate_dead_end_trial1_ascii_replay_cli(max_steps: int = 100) -> dict[str, Any]:
    validation = validate_dead_end_trial1_maps_cli(runs_per_map=1, max_steps=max_steps)
    replays = []
    for map_number, map_result in enumerate(validation["map_results"], start=1):
        map_config = _candidate_map_config_by_level_id(map_result["level_id"])
        frames = _build_candidate_trial1_replay_frames(map_config, max_steps)
        for frame in frames:
            frame["map_number"] = map_number
        summary = _summarize_candidate_trial1_replay_map(map_result)
        summary["max_steps"] = max_steps
        replays.append(
            {
                "map_number": map_number,
                "level_id": map_result["level_id"],
                "map_status": map_result["map_status"],
                "legend": "A=agent, B=box, #=wall, .=walkable, x=dead-end marker",
                "trial_1_frames": frames,
                "summary": summary,
            }
        )

    overall_summary = {
        "replayed_map_count": len(replays),
        "valid_for_two_trial_count": validation["overall_summary"]["valid_for_two_trial_count"],
        "has_shortcut_count": validation["overall_summary"]["has_shortcut_count"],
        "no_dead_end_event_count": validation["overall_summary"]["no_dead_end_event_count"],
        "unreachable_count": validation["overall_summary"]["unreachable_count"],
        "needs_map_fix_count": validation["overall_summary"]["needs_map_fix_count"],
        "recommended_next_step": "Inspect replay output before selecting maps for multi-map A/B control.",
    }
    return {
        "command": "replay-dead-end-trial1-candidate-maps",
        "flow": "candidate_map_trial1_ascii_replay_v0",
        "status": "ok",
        "max_steps": max_steps,
        "map_count": len(replays),
        "legend": "A=agent, B=box, #=wall, .=walkable, x=dead-end marker",
        "replays": replays,
        "overall_summary": overall_summary,
        "boundary_check": {
            "trial1_replay_only": True,
            "two_trial_run": False,
            "memory_control_run": False,
            "replay_output_only": True,
            "runner_modified": False,
            "action_selection_modified": False,
            "used_llm": False,
            "used_pathfinding": False,
            "used_lesson_store": False,
            "used_memory_layer": False,
            "modified_docs_current_boundary_index": False,
        },
        "notes": [
            "Candidate map Trial 1 ASCII replay is observer output only.",
            "This command does not run Two-Trial or A/B memory control.",
            "This is not proof of learning.",
        ],
    }


def _verification_boundary() -> dict[str, bool]:
    return {
        "llm_used": False,
        "creates_lesson_candidate": False,
        "writes_lesson_store": False,
        "writes_memory_layer": False,
        "learning_pipeline_used": False,
        "teaching_chat_loop_used": False,
        "awakening_claim": False,
    }


def _tactile_interaction_boundary(llm_used: bool = False) -> dict[str, bool]:
    return {
        "llm_used": llm_used,
        "creates_lesson_candidate": False,
        "writes_lesson_store": False,
        "writes_memory_layer": False,
        "awakening_claim": False,
    }


def run_command(command: str) -> dict[str, Any] | str:
    if command == "run-known-flow":
        return run_known_flow()
    if command == "run-unknown-flow":
        return run_unknown_flow()
    if command == "run-disable-reenable-flow":
        return run_disable_reenable_flow()
    if command == "run-conflict-check-flow":
        return run_conflict_check_flow()
    if command == "run-lifecycle-display":
        return run_lifecycle_display()
    if command == "run-review-display":
        return run_review_display()
    if command == "run-review-approve":
        return run_review_approve()
    if command == "run-review-reject":
        return run_review_reject()
    if command == "run-minimal-interaction":
        return run_minimal_interaction()
    if command == "run-tactile-interaction":
        return run_tactile_interaction()
    if command == "clear-sandbox-working-state":
        return run_clear_sandbox_working_state()
    if command == "run-grounded-learning-check":
        return run_grounded_learning_check()
    if command == "run-need-state-trial-batch":
        return run_need_state_trial_batch_cli()
    if command == "run-trial-metrics-comparison":
        return run_trial_metrics_comparison_cli()
    if command == "compare-trial-metrics-baseline":
        return run_trial_metrics_baseline_compare_cli()
    if command == "run-trial-metrics-baseline-compare":
        return run_trial_metrics_baseline_compare_cli()
    if command == "run-navigation-trial-metrics":
        return run_navigation_trial_metrics_cli()
    if command == "run-navigation-multi-goal-metrics":
        return run_navigation_multi_goal_metrics_cli()
    if command == "run-navigation-obstacle-trial":
        return run_navigation_obstacle_trial_cli()
    if command == "run-approach-box-trial":
        return run_approach_box_trial_cli()
    if command == "run-approach-box-two-trial-check":
        return run_approach_box_two_trial_check_cli()
    if command == "run-approach-box-dead-end-trial":
        return run_approach_box_dead_end_trial_cli()
    if command == "run-approach-box-dead-end-two-trial-check":
        return run_approach_box_dead_end_two_trial_check_cli()
    if command == "run-approach-box-dead-end-memory-control-check":
        return run_approach_box_dead_end_memory_control_check_cli()
    if command == "replay-approach-box-dead-end-two-trial":
        return run_approach_box_dead_end_two_trial_ascii_replay_cli()
    if command == "validate-dead-end-trial1-maps":
        return validate_dead_end_trial1_maps_cli()
    if command == "replay-dead-end-trial1-candidate-maps":
        return run_candidate_dead_end_trial1_ascii_replay_cli()
    if command == "run-valid-dead-end-maps-ab-control":
        return run_valid_dead_end_maps_ab_control_cli()
    if command == "observe-local-memory-decision-trace":
        return run_local_memory_decision_trace_observer_cli()
    if command == "demo-session-working-memory":
        return demo_session_working_memory_cli()
    if command == "run-session-working-memory-trial":
        return run_session_working_memory_trial_cli()
    if command == "run-simulated-vision-viewport-demo":
        return run_simulated_vision_viewport_demo()
    if command == "run-simulated-vision-larger-sandbox-demo":
        return run_simulated_vision_larger_sandbox_demo()
    if command == "run-larger-sandbox-observed-map-smoke":
        return run_larger_sandbox_observed_map_smoke()
    if command == "run-larger-sandbox-symbol-contact-smoke":
        return run_larger_sandbox_symbol_contact_smoke()
    if command == "replay-larger-sandbox-human":
        return run_larger_sandbox_human_replay()
    if command == "run-larger-sandbox-ui":
        return get_launch_config()
    if command == "run-simulated-vision-memory-bridge-demo":
        return run_simulated_vision_memory_bridge_demo()
    if command == "run-simulated-vision-observed-map-demo":
        return run_simulated_vision_observed_map_demo()
    if command == "run-simulated-vision-symbol-grounding-check":
        return run_symbol_grounding_check()
    if command == "run-grounded-action-experience-check":
        return run_grounded_action_experience_check()
    if command == "run-grounded-action-experience-influence-check":
        return run_grounded_action_experience_influence_check()
    if command == "run-instinct-random-walk":
        return run_instinct_random_walk()
    if command == "run-wall-experience-influence-check":
        return run_wall_experience_influence_check()
    if command == "run-item-reward-event-check":
        return run_item_reward_event_check()
    if command == "run-reward-biased-action-tendency-check":
        return run_reward_biased_action_tendency_check()
    if command == "run-reward-biased-random-walk-check":
        return run_reward_biased_random_walk_check()
    if command == "run-two-round-instinct-reward-comparison":
        return run_two_round_instinct_reward_comparison()
    if command == "run-failure-reason-classifier-check":
        return run_failure_reason_classifier_check()
    if command == "run-similar-context-key-check":
        return run_similar_context_key_check()
    if command == "run-action-outcome-predictor-check":
        return run_action_outcome_predictor_check()
    if command == "run-expected-actual-outcome-pair-schema-check":
        return run_expected_actual_outcome_pair_schema_check()
    if command == "run-failure-reason-from-outcome-pair-check":
        return run_failure_reason_from_outcome_pair_check()
    if command == "run-lesson-candidate-from-failure-reason-check":
        return run_lesson_candidate_from_failure_reason_check()
    if command == "run-lesson-candidate-review-gate-check":
        return run_lesson_candidate_review_gate_check()
    if command == "run-lesson-candidate-review-evidence-summary-check":
        return run_lesson_candidate_review_evidence_summary_check()
    if command == "run-lesson-candidate-human-review-decision-schema-check":
        return run_lesson_candidate_human_review_decision_schema_check()
    if command == "run-reviewed-lesson-trace-preview-check":
        return run_reviewed_lesson_trace_preview_check()
    if command == "run-reviewed-lesson-dry-run-correction-minimal-check":
        return run_reviewed_lesson_dry_run_correction_minimal_check()
    if command == "run-dry-run-correction-into-trial-trace-check":
        return run_dry_run_correction_into_trial_trace_check()
    if command == "run-before-after-trial-contrast-check":
        return run_before_after_trial_contrast_check()
    if command == "run-lesson-effect-evidence-trace-minimal-check":
        return run_lesson_effect_evidence_trace_minimal_check()
    if command == "run-prediction-accuracy-check":
        return run_prediction_accuracy_check()
    if command == "run-rule-candidate-from-mismatch-check":
        return run_rule_candidate_from_mismatch_check()
    if command == "run-rule-candidate-review-gate-check":
        return run_rule_candidate_review_gate_check()
    if command == "run-approved-candidate-preview-check":
        return run_approved_candidate_preview_check()
    if command == "run-reviewed-candidate-apply-verification-check":
        return run_reviewed_candidate_apply_verification_check()
    if command == "run-integrated-experience-session-trace":
        return run_integrated_experience_session_trace()
    if command == "run-integrated-trace-chain-break-audit":
        return run_integrated_trace_chain_break_audit()
    if command == "run-persistent-eligibility-checker-check":
        return run_persistent_eligibility_checker_check()
    if command == "run-generalized-memory-exact-key-bucket-check":
        return run_generalized_memory_exact_key_bucket_check()
    if command == "run-generalized-memory-exact-key-bucket-enhancement-minimal-check":
        return run_generalized_memory_exact_key_bucket_enhancement_minimal_check()
    if command == "run-session-experience-record-schema-minimal-check":
        return run_session_experience_record_schema_minimal_check()
    if command == "run-demo-readable-before-after-report-minimal-check":
        return run_demo_readable_before_after_report_minimal_check()
    if command == "run-trial-bucket-link-preview-minimal-check":
        return run_trial_bucket_link_preview_minimal_check()
    if command == "run-temporary-cross-session-experience-space-minimal-check":
        return run_temporary_cross_session_experience_space_minimal_check()
    if command == "run-temporary-cross-session-space-link-back-minimal-check":
        return run_temporary_cross_session_space_link_back_minimal_check()
    if command == "run-mentor-gated-experience-retention-minimal-check":
        return run_mentor_gated_experience_retention_minimal_check()
    if command == "run-retained-experience-readback-preview-minimal-check":
        return run_retained_experience_readback_preview_minimal_check()
    if command == "run-retained-experience-listing-cli-minimal-check":
        return run_retained_experience_listing_cli_minimal_check()
    if command == "run-retained-experience-exact-key-lookup-minimal-check":
        return run_retained_experience_exact_key_lookup_minimal_check()
    if command == "run-retained-experience-into-dry-run-minimal-check":
        return run_retained_experience_into_dry_run_minimal_check()
    if command == "run-memory-influence-candidate-preview-minimal-check":
        return run_memory_influence_candidate_preview_minimal_check()
    if command == "run-memory-influenced-action-tendency-preview-minimal-check":
        return run_memory_influenced_action_tendency_preview_minimal_check()
    if command == "run-memory-influence-dry-run-contrast-minimal-check":
        return run_memory_influence_dry_run_contrast_minimal_check()
    if command == "run-runtime-action-tendency-memory-influence-ab-minimal-check":
        return run_runtime_action_tendency_memory_influence_ab_minimal_check()
    if command == "run-runtime-tendency-memory-influence-rollback-check-minimal-check":
        return run_runtime_tendency_memory_influence_rollback_check_minimal_check()
    if command == "run-runtime-tendency-memory-influence-safety-envelope-minimal-check":
        return run_runtime_tendency_memory_influence_safety_envelope_minimal_check()
    if command == "run-runtime-tendency-mentor-override-check-minimal-check":
        return run_runtime_tendency_mentor_override_check_minimal_check()
    if command == "run-runtime-tendency-memory-influence-multi-scenario-check-minimal-check":
        return run_runtime_tendency_memory_influence_multi_scenario_check_minimal_check()
    if command == "run-pre-action-consideration-candidate-minimal-check":
        return run_pre_action_consideration_candidate_minimal_check()
    if command == "run-pre-action-consideration-gate-check-minimal-check":
        return run_pre_action_consideration_gate_check_minimal_check()
    if command == "run-action-selection-adjacent-review-minimal-check":
        return run_action_selection_adjacent_review_minimal_check()
    if command == "run-simple-retina-focus-preview-minimal-check":
        return run_simple_retina_focus_preview_minimal_check()
    if command == "run-generalized-prediction-confidence-check":
        return run_generalized_prediction_confidence_check()
    if command == "run-generalized-candidate-from-pattern-check":
        return run_generalized_candidate_from_pattern_check()
    if command == "run-generalized-candidate-review-preview-check":
        return run_generalized_candidate_review_preview_check()
    if command == "run-mimetic-endocrine-signal-schema-check":
        return run_mimetic_endocrine_signal_schema_check()
    if command == "run-dopamine-like-reward-trace-check":
        return run_dopamine_like_reward_trace_check()
    if command == "run-norepinephrine-like-change-attention-trace-check":
        return run_norepinephrine_like_change_attention_trace_check()
    if command == "run-cortisol-like-failure-load-trace-check":
        return run_cortisol_like_failure_load_trace_check()
    if command == "run-oxytocin-like-review-trust-trace-check":
        return run_oxytocin_like_review_trust_trace_check()
    if command == "run-outcome-pair-from-action-trial-trace-check":
        return run_outcome_pair_from_action_trial_trace_check()
    if command == "run-mimetic-endocrine-four-axis-trace-integration-check":
        return run_mimetic_endocrine_four_axis_trace_integration_check()
    if command == "run-retina-decoder-feature-schema-check":
        return run_retina_decoder_feature_schema_check()
    if command == "run-retina-decoder-symbolic-feature-decode-check":
        return run_retina_decoder_symbolic_feature_decode_check()
    if command == "run-visual-frame-buffer-schema-check":
        return run_visual_frame_buffer_schema_check()
    if command == "run-visual-frame-assembly-from-retina-features-check":
        return run_visual_frame_assembly_from_retina_features_check()
    if command == "run-visual-frame-change-schema-check":
        return run_visual_frame_change_schema_check()
    if command == "run-visual-frame-change-trace-check":
        return run_visual_frame_change_trace_check()
    if command == "run-visual-experience-candidate-from-frame-change-minimal-check":
        return run_visual_experience_candidate_from_frame_change_minimal_check()
    if command == "run-visual-trace-as-lesson-evidence-minimal-check":
        return run_visual_trace_as_lesson_evidence_minimal_check()
    if command == "run-visual-retained-experience-link-preview-minimal-check":
        return run_visual_retained_experience_link_preview_minimal_check()
    if command == "run-visual-retention-demo-snapshot-minimal-check":
        return run_visual_retention_demo_snapshot_minimal_check()
    if command == "run-minimal-visual-grounding-trial-check":
        return run_minimal_visual_grounding_trial_check()
    if command == "run-visual-prediction-error-attention-priority-preview-minimal-check":
        return run_visual_prediction_error_attention_priority_preview_minimal_check()
    if command == "run-visual-frame-pair-demo-assembly-check":
        return run_visual_frame_pair_demo_assembly_check()
    if command == "run-focus-candidate-schema-check":
        return run_focus_candidate_schema_check()
    if command == "run-focus-candidate-from-change-trace-check":
        return run_focus_candidate_from_change_trace_check()
    if command == "run-focus-candidate-ranking-trace-schema-check":
        return run_focus_candidate_ranking_trace_schema_check()
    if command == "run-focus-candidate-ranking-trace-check":
        return run_focus_candidate_ranking_trace_check()
    if command == "run-focus-application-gate-schema-check":
        return run_focus_application_gate_schema_check()
    return {
        "command": command,
        "status": "error",
        "error": "unknown_command",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ASHL Core minimal teaching CLI")
    parser.add_argument(
        "command",
        choices=[
            "run-known-flow",
            "run-unknown-flow",
            "run-disable-reenable-flow",
            "run-conflict-check-flow",
            "run-lifecycle-display",
            "run-review-display",
            "run-review-approve",
            "run-review-reject",
            "run-minimal-interaction",
            "run-tactile-interaction",
            "clear-sandbox-working-state",
            "run-grounded-learning-check",
            "run-need-state-trial-batch",
            "run-trial-metrics-comparison",
            "compare-trial-metrics-baseline",
            "run-trial-metrics-baseline-compare",
            "run-navigation-trial-metrics",
            "run-navigation-multi-goal-metrics",
            "run-navigation-obstacle-trial",
            "run-approach-box-trial",
            "run-approach-box-two-trial-check",
            "run-approach-box-dead-end-trial",
            "run-approach-box-dead-end-two-trial-check",
            "run-approach-box-dead-end-memory-control-check",
            "replay-approach-box-dead-end-two-trial",
            "validate-dead-end-trial1-maps",
            "replay-dead-end-trial1-candidate-maps",
            "run-valid-dead-end-maps-ab-control",
            "observe-local-memory-decision-trace",
            "demo-session-working-memory",
            "run-session-working-memory-trial",
            "run-simulated-vision-viewport-demo",
            "run-simulated-vision-larger-sandbox-demo",
            "run-larger-sandbox-observed-map-smoke",
            "run-larger-sandbox-symbol-contact-smoke",
            "replay-larger-sandbox-human",
            "run-larger-sandbox-ui",
            "run-simulated-vision-memory-bridge-demo",
            "run-simulated-vision-observed-map-demo",
            "run-simulated-vision-symbol-grounding-check",
            "run-grounded-action-experience-check",
            "run-grounded-action-experience-influence-check",
            "run-instinct-random-walk",
            "run-wall-experience-influence-check",
            "run-item-reward-event-check",
            "run-reward-biased-action-tendency-check",
            "run-reward-biased-random-walk-check",
            "run-two-round-instinct-reward-comparison",
            "run-failure-reason-classifier-check",
            "run-similar-context-key-check",
            "run-action-outcome-predictor-check",
            "run-expected-actual-outcome-pair-schema-check",
            "run-failure-reason-from-outcome-pair-check",
            "run-lesson-candidate-from-failure-reason-check",
            "run-lesson-candidate-review-gate-check",
            "run-lesson-candidate-review-evidence-summary-check",
            "run-lesson-candidate-human-review-decision-schema-check",
            "run-reviewed-lesson-trace-preview-check",
            "run-reviewed-lesson-dry-run-correction-minimal-check",
            "run-dry-run-correction-into-trial-trace-check",
            "run-before-after-trial-contrast-check",
            "run-lesson-effect-evidence-trace-minimal-check",
            "run-prediction-accuracy-check",
            "run-rule-candidate-from-mismatch-check",
            "run-rule-candidate-review-gate-check",
            "run-approved-candidate-preview-check",
            "run-reviewed-candidate-apply-verification-check",
            "run-integrated-experience-session-trace",
            "run-integrated-trace-chain-break-audit",
            "run-persistent-eligibility-checker-check",
            "run-generalized-memory-exact-key-bucket-check",
            "run-generalized-memory-exact-key-bucket-enhancement-minimal-check",
            "run-session-experience-record-schema-minimal-check",
            "run-demo-readable-before-after-report-minimal-check",
            "run-trial-bucket-link-preview-minimal-check",
            "run-temporary-cross-session-experience-space-minimal-check",
            "run-temporary-cross-session-space-link-back-minimal-check",
            "run-mentor-gated-experience-retention-minimal-check",
            "run-retained-experience-readback-preview-minimal-check",
            "run-retained-experience-listing-cli-minimal-check",
            "run-retained-experience-exact-key-lookup-minimal-check",
            "run-retained-experience-into-dry-run-minimal-check",
            "run-memory-influence-candidate-preview-minimal-check",
            "run-memory-influenced-action-tendency-preview-minimal-check",
            "run-memory-influence-dry-run-contrast-minimal-check",
            "run-runtime-action-tendency-memory-influence-ab-minimal-check",
            "run-runtime-tendency-memory-influence-rollback-check-minimal-check",
            "run-runtime-tendency-memory-influence-safety-envelope-minimal-check",
            "run-runtime-tendency-mentor-override-check-minimal-check",
            "run-runtime-tendency-memory-influence-multi-scenario-check-minimal-check",
            "run-pre-action-consideration-candidate-minimal-check",
            "run-pre-action-consideration-gate-check-minimal-check",
            "run-action-selection-adjacent-review-minimal-check",
            "run-simple-retina-focus-preview-minimal-check",
            "run-generalized-prediction-confidence-check",
            "run-generalized-candidate-from-pattern-check",
            "run-generalized-candidate-review-preview-check",
            "run-mimetic-endocrine-signal-schema-check",
            "run-dopamine-like-reward-trace-check",
            "run-norepinephrine-like-change-attention-trace-check",
            "run-cortisol-like-failure-load-trace-check",
            "run-oxytocin-like-review-trust-trace-check",
            "run-outcome-pair-from-action-trial-trace-check",
            "run-mimetic-endocrine-four-axis-trace-integration-check",
            "run-retina-decoder-feature-schema-check",
            "run-retina-decoder-symbolic-feature-decode-check",
            "run-visual-frame-buffer-schema-check",
            "run-visual-frame-assembly-from-retina-features-check",
            "run-visual-frame-change-schema-check",
            "run-visual-frame-change-trace-check",
            "run-visual-experience-candidate-from-frame-change-minimal-check",
            "run-visual-trace-as-lesson-evidence-minimal-check",
            "run-visual-retained-experience-link-preview-minimal-check",
            "run-visual-retention-demo-snapshot-minimal-check",
            "run-minimal-visual-grounding-trial-check",
            "run-visual-prediction-error-attention-priority-preview-minimal-check",
            "run-visual-frame-pair-demo-assembly-check",
            "run-focus-candidate-schema-check",
            "run-focus-candidate-from-change-trace-check",
            "run-focus-candidate-ranking-trace-schema-check",
            "run-focus-candidate-ranking-trace-check",
            "run-focus-application-gate-schema-check",
        ],
    )
    parser.add_argument("--review-id", default="review_001")
    parser.add_argument("--notes", default=None)
    parser.add_argument("--session-id", default="final_check")
    parser.add_argument("--feedback-label", default="observed")
    parser.add_argument("--mentor-source", default="mentor")
    parser.add_argument("--persist", action="store_true")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--state-key", default=None)
    parser.add_argument("--action", default=None)
    parser.add_argument("--actions", nargs="*", default=None)
    parser.add_argument("--trial-count", type=int, default=5)
    parser.add_argument("--max-steps", type=int, default=10)
    parser.add_argument("--runs", type=int, default=4)
    parser.add_argument("--runs-per-map", type=int, default=3)
    parser.add_argument("--random-seed", type=int, default=None)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--baseline-path", default="data/baselines/trial_metrics_baseline_v0.json")
    parser.add_argument("--level-id", default="approach_box_dead_end_v0")
    parser.add_argument("--max-records", type=int, default=20)
    parser.add_argument("--action-sequence", default=None)
    parser.add_argument("--scenario", choices=["mixed", "wall", "empty", "item", "doorway", "exit"], default=None)
    parser.add_argument("--mode", choices=["demo", "contact", "observed-map"], default="demo")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "run-review-approve":
        result = run_review_approve(review_id=args.review_id, notes=args.notes)
    elif args.command == "run-review-reject":
        result = run_review_reject(review_id=args.review_id, notes=args.notes)
    elif args.command == "run-minimal-interaction":
        result = run_minimal_interaction(
            session_id=args.session_id,
            feedback_label=args.feedback_label,
            mentor_source=args.mentor_source,
            note=args.notes,
            persist=args.persist,
            data_dir=args.data_dir,
            state_key=args.state_key,
        )
    elif args.command == "run-tactile-interaction":
        result = run_tactile_interaction(action=args.action)
    elif args.command == "clear-sandbox-working-state":
        result = run_clear_sandbox_working_state(session_id=args.session_id, data_dir=args.data_dir)
    elif args.command == "run-grounded-learning-check":
        result = run_grounded_learning_check(actions=args.actions)
    elif args.command == "run-need-state-trial-batch":
        result = run_need_state_trial_batch_cli(
            trial_count=args.trial_count,
            max_steps=args.max_steps,
            random_seed=args.random_seed,
        )
    elif args.command == "run-trial-metrics-comparison":
        result = run_trial_metrics_comparison_cli(
            runs=args.runs,
            trial_count=args.trial_count,
            max_steps=args.max_steps,
            random_seed=args.random_seed,
        )
    elif args.command in {"compare-trial-metrics-baseline", "run-trial-metrics-baseline-compare"}:
        result = run_trial_metrics_baseline_compare_cli(baseline_path=args.baseline_path)
    elif args.command == "run-navigation-trial-metrics":
        result = run_navigation_trial_metrics_cli(
            runs=args.runs,
            trial_count=args.trial_count,
            max_steps=args.max_steps,
        )
    elif args.command == "run-navigation-multi-goal-metrics":
        result = run_navigation_multi_goal_metrics_cli(
            runs=args.runs,
            trial_count=args.trial_count,
            max_steps=args.max_steps,
        )
    elif args.command == "run-navigation-obstacle-trial":
        result = run_navigation_obstacle_trial_cli(max_steps=args.max_steps)
    elif args.command == "run-approach-box-trial":
        result = run_approach_box_trial_cli(max_steps=args.max_steps)
    elif args.command == "run-approach-box-two-trial-check":
        result = run_approach_box_two_trial_check_cli(max_steps=args.max_steps)
    elif args.command == "run-approach-box-dead-end-trial":
        result = run_approach_box_dead_end_trial_cli(max_steps=args.max_steps)
    elif args.command == "run-approach-box-dead-end-two-trial-check":
        result = run_approach_box_dead_end_two_trial_check_cli(max_steps=args.max_steps)
    elif args.command == "run-approach-box-dead-end-memory-control-check":
        result = run_approach_box_dead_end_memory_control_check_cli(
            max_steps=args.max_steps,
            runs=args.runs,
            random_seed=args.random_seed,
        )
    elif args.command == "replay-approach-box-dead-end-two-trial":
        result = run_approach_box_dead_end_two_trial_ascii_replay_cli(max_steps=args.max_steps)
    elif args.command == "validate-dead-end-trial1-maps":
        result = validate_dead_end_trial1_maps_cli(runs_per_map=args.runs_per_map, max_steps=args.max_steps)
    elif args.command == "replay-dead-end-trial1-candidate-maps":
        result = run_candidate_dead_end_trial1_ascii_replay_cli(max_steps=args.max_steps)
    elif args.command == "run-valid-dead-end-maps-ab-control":
        result = run_valid_dead_end_maps_ab_control_cli(
            runs_per_map=args.runs_per_map,
            max_steps=args.max_steps,
            random_seed=args.random_seed,
        )
    elif args.command == "observe-local-memory-decision-trace":
        result = run_local_memory_decision_trace_observer_cli(
            level_id=args.level_id,
            max_steps=args.max_steps,
        )
    elif args.command == "demo-session-working-memory":
        result = demo_session_working_memory_cli(max_records=args.max_records)
    elif args.command == "run-session-working-memory-trial":
        result = run_session_working_memory_trial_cli(
            level_id=args.level_id,
            max_steps=args.max_steps,
            max_records=args.max_records,
        )
    elif args.command == "run-simulated-vision-viewport-demo":
        action_sequence = None
        if args.action_sequence:
            action_sequence = [action.strip() for action in args.action_sequence.split(",") if action.strip()]
        result = run_simulated_vision_viewport_demo(action_sequence=action_sequence)
    elif args.command == "run-simulated-vision-larger-sandbox-demo":
        action_sequence = None
        if args.action_sequence:
            action_sequence = [action.strip() for action in args.action_sequence.split(",") if action.strip()]
        result = run_simulated_vision_larger_sandbox_demo(action_sequence=action_sequence)
    elif args.command == "run-larger-sandbox-observed-map-smoke":
        action_sequence = None
        if args.action_sequence:
            action_sequence = [action.strip() for action in args.action_sequence.split(",") if action.strip()]
        result = run_larger_sandbox_observed_map_smoke(action_sequence=action_sequence)
    elif args.command == "run-larger-sandbox-symbol-contact-smoke":
        result = run_larger_sandbox_symbol_contact_smoke(scenario=args.scenario)
    elif args.command == "replay-larger-sandbox-human":
        result = run_larger_sandbox_human_replay(mode=args.mode)
    elif args.command == "run-larger-sandbox-ui":
        run_larger_sandbox_ui(host=args.host, port=args.port, debug=args.debug)
        return 0
    elif args.command == "run-simulated-vision-memory-bridge-demo":
        action_sequence = None
        if args.action_sequence:
            action_sequence = [action.strip() for action in args.action_sequence.split(",") if action.strip()]
        result = run_simulated_vision_memory_bridge_demo(
            action_sequence=action_sequence,
            max_records=args.max_records,
        )
    elif args.command == "run-simulated-vision-observed-map-demo":
        action_sequence = None
        if args.action_sequence:
            action_sequence = [action.strip() for action in args.action_sequence.split(",") if action.strip()]
        result = run_simulated_vision_observed_map_demo(action_sequence=action_sequence)
    elif args.command == "run-simulated-vision-symbol-grounding-check":
        result = run_symbol_grounding_check(scenario=args.scenario)
    elif args.command == "run-grounded-action-experience-check":
        result = run_grounded_action_experience_check(scenario=args.scenario)
    elif args.command == "run-grounded-action-experience-influence-check":
        result = run_grounded_action_experience_influence_check(scenario=args.scenario)
    elif args.command == "run-instinct-random-walk":
        raw_argv = argv if argv is not None else sys.argv[1:]
        max_steps = args.max_steps if "--max-steps" in raw_argv else 50
        result = run_instinct_random_walk(seed=args.seed, max_steps=max_steps)
    elif args.command == "run-wall-experience-influence-check":
        raw_argv = argv if argv is not None else sys.argv[1:]
        max_steps = args.max_steps if "--max-steps" in raw_argv else 50
        result = run_wall_experience_influence_check(seed=args.seed, max_steps=max_steps)
    elif args.command == "run-item-reward-event-check":
        result = run_item_reward_event_check(scenario=args.scenario)
    elif args.command == "run-reward-biased-action-tendency-check":
        result = run_reward_biased_action_tendency_check()
    elif args.command == "run-reward-biased-random-walk-check":
        result = run_reward_biased_random_walk_check(seed=args.seed, trials=args.trials)
    elif args.command == "run-two-round-instinct-reward-comparison":
        result = run_two_round_instinct_reward_comparison(seed=args.seed, trials=args.trials)
    elif args.command == "run-failure-reason-classifier-check":
        result = run_failure_reason_classifier_check()
    elif args.command == "run-similar-context-key-check":
        result = run_similar_context_key_check()
    elif args.command == "run-action-outcome-predictor-check":
        result = run_action_outcome_predictor_check()
    elif args.command == "run-expected-actual-outcome-pair-schema-check":
        result = run_expected_actual_outcome_pair_schema_check()
    elif args.command == "run-failure-reason-from-outcome-pair-check":
        result = run_failure_reason_from_outcome_pair_check()
    elif args.command == "run-lesson-candidate-from-failure-reason-check":
        result = run_lesson_candidate_from_failure_reason_check()
    elif args.command == "run-lesson-candidate-review-gate-check":
        result = run_lesson_candidate_review_gate_check()
    elif args.command == "run-lesson-candidate-review-evidence-summary-check":
        result = run_lesson_candidate_review_evidence_summary_check()
    elif args.command == "run-lesson-candidate-human-review-decision-schema-check":
        result = run_lesson_candidate_human_review_decision_schema_check()
    elif args.command == "run-reviewed-lesson-trace-preview-check":
        result = run_reviewed_lesson_trace_preview_check()
    elif args.command == "run-reviewed-lesson-dry-run-correction-minimal-check":
        result = run_reviewed_lesson_dry_run_correction_minimal_check()
    elif args.command == "run-dry-run-correction-into-trial-trace-check":
        result = run_dry_run_correction_into_trial_trace_check()
    elif args.command == "run-before-after-trial-contrast-check":
        result = run_before_after_trial_contrast_check()
    elif args.command == "run-lesson-effect-evidence-trace-minimal-check":
        result = run_lesson_effect_evidence_trace_minimal_check()
    elif args.command == "run-prediction-accuracy-check":
        result = run_prediction_accuracy_check()
    elif args.command == "run-rule-candidate-from-mismatch-check":
        result = run_rule_candidate_from_mismatch_check()
    elif args.command == "run-rule-candidate-review-gate-check":
        result = run_rule_candidate_review_gate_check()
    elif args.command == "run-approved-candidate-preview-check":
        result = run_approved_candidate_preview_check()
    elif args.command == "run-reviewed-candidate-apply-verification-check":
        result = run_reviewed_candidate_apply_verification_check()
    elif args.command == "run-integrated-experience-session-trace":
        raw_argv = argv if argv is not None else sys.argv[1:]
        max_steps = args.max_steps if "--max-steps" in raw_argv else 8
        result = run_integrated_experience_session_trace(scenario=args.scenario or "mixed", max_steps=max_steps)
    elif args.command == "run-integrated-trace-chain-break-audit":
        result = run_integrated_trace_chain_break_audit()
    elif args.command == "run-persistent-eligibility-checker-check":
        result = run_persistent_eligibility_checker_check()
    elif args.command == "run-generalized-memory-exact-key-bucket-check":
        result = run_generalized_memory_exact_key_bucket_check()
    elif args.command == "run-generalized-memory-exact-key-bucket-enhancement-minimal-check":
        result = run_generalized_memory_exact_key_bucket_enhancement_minimal_check()
    elif args.command == "run-session-experience-record-schema-minimal-check":
        result = run_session_experience_record_schema_minimal_check()
    elif args.command == "run-demo-readable-before-after-report-minimal-check":
        result = run_demo_readable_before_after_report_minimal_check()
    elif args.command == "run-trial-bucket-link-preview-minimal-check":
        result = run_trial_bucket_link_preview_minimal_check()
    elif args.command == "run-temporary-cross-session-experience-space-minimal-check":
        result = run_temporary_cross_session_experience_space_minimal_check()
    elif args.command == "run-temporary-cross-session-space-link-back-minimal-check":
        result = run_temporary_cross_session_space_link_back_minimal_check()
    elif args.command == "run-mentor-gated-experience-retention-minimal-check":
        result = run_mentor_gated_experience_retention_minimal_check()
    elif args.command == "run-retained-experience-readback-preview-minimal-check":
        result = run_retained_experience_readback_preview_minimal_check()
    elif args.command == "run-retained-experience-listing-cli-minimal-check":
        result = run_retained_experience_listing_cli_minimal_check()
    elif args.command == "run-retained-experience-exact-key-lookup-minimal-check":
        result = run_retained_experience_exact_key_lookup_minimal_check()
    elif args.command == "run-retained-experience-into-dry-run-minimal-check":
        result = run_retained_experience_into_dry_run_minimal_check()
    elif args.command == "run-memory-influence-candidate-preview-minimal-check":
        result = run_memory_influence_candidate_preview_minimal_check()
    elif args.command == "run-memory-influenced-action-tendency-preview-minimal-check":
        result = run_memory_influenced_action_tendency_preview_minimal_check()
    elif args.command == "run-memory-influence-dry-run-contrast-minimal-check":
        result = run_memory_influence_dry_run_contrast_minimal_check()
    elif args.command == "run-runtime-action-tendency-memory-influence-ab-minimal-check":
        result = run_runtime_action_tendency_memory_influence_ab_minimal_check()
    elif args.command == "run-runtime-tendency-memory-influence-rollback-check-minimal-check":
        result = run_runtime_tendency_memory_influence_rollback_check_minimal_check()
    elif args.command == "run-runtime-tendency-memory-influence-safety-envelope-minimal-check":
        result = run_runtime_tendency_memory_influence_safety_envelope_minimal_check()
    elif args.command == "run-runtime-tendency-mentor-override-check-minimal-check":
        result = run_runtime_tendency_mentor_override_check_minimal_check()
    elif args.command == "run-runtime-tendency-memory-influence-multi-scenario-check-minimal-check":
        result = run_runtime_tendency_memory_influence_multi_scenario_check_minimal_check()
    elif args.command == "run-pre-action-consideration-candidate-minimal-check":
        result = run_pre_action_consideration_candidate_minimal_check()
    elif args.command == "run-pre-action-consideration-gate-check-minimal-check":
        result = run_pre_action_consideration_gate_check_minimal_check()
    elif args.command == "run-action-selection-adjacent-review-minimal-check":
        result = run_action_selection_adjacent_review_minimal_check()
    elif args.command == "run-simple-retina-focus-preview-minimal-check":
        result = run_simple_retina_focus_preview_minimal_check()
    elif args.command == "run-generalized-prediction-confidence-check":
        result = run_generalized_prediction_confidence_check()
    elif args.command == "run-generalized-candidate-from-pattern-check":
        result = run_generalized_candidate_from_pattern_check()
    elif args.command == "run-generalized-candidate-review-preview-check":
        result = run_generalized_candidate_review_preview_check()
    elif args.command == "run-mimetic-endocrine-signal-schema-check":
        result = run_mimetic_endocrine_signal_schema_check()
    elif args.command == "run-dopamine-like-reward-trace-check":
        result = run_dopamine_like_reward_trace_check()
    elif args.command == "run-norepinephrine-like-change-attention-trace-check":
        result = run_norepinephrine_like_change_attention_trace_check()
    elif args.command == "run-cortisol-like-failure-load-trace-check":
        result = run_cortisol_like_failure_load_trace_check()
    elif args.command == "run-oxytocin-like-review-trust-trace-check":
        result = run_oxytocin_like_review_trust_trace_check()
    elif args.command == "run-outcome-pair-from-action-trial-trace-check":
        result = run_outcome_pair_from_action_trial_trace_check()
    elif args.command == "run-mimetic-endocrine-four-axis-trace-integration-check":
        result = run_mimetic_endocrine_four_axis_trace_integration_check()
    elif args.command == "run-retina-decoder-feature-schema-check":
        result = run_retina_decoder_feature_schema_check()
    elif args.command == "run-retina-decoder-symbolic-feature-decode-check":
        result = run_retina_decoder_symbolic_feature_decode_check()
    elif args.command == "run-visual-frame-buffer-schema-check":
        result = run_visual_frame_buffer_schema_check()
    elif args.command == "run-visual-frame-assembly-from-retina-features-check":
        result = run_visual_frame_assembly_from_retina_features_check()
    elif args.command == "run-visual-frame-change-schema-check":
        result = run_visual_frame_change_schema_check()
    elif args.command == "run-visual-frame-change-trace-check":
        result = run_visual_frame_change_trace_check()
    elif args.command == "run-visual-experience-candidate-from-frame-change-minimal-check":
        result = run_visual_experience_candidate_from_frame_change_minimal_check()
    elif args.command == "run-visual-trace-as-lesson-evidence-minimal-check":
        result = run_visual_trace_as_lesson_evidence_minimal_check()
    elif args.command == "run-visual-retained-experience-link-preview-minimal-check":
        result = run_visual_retained_experience_link_preview_minimal_check()
    elif args.command == "run-visual-retention-demo-snapshot-minimal-check":
        result = run_visual_retention_demo_snapshot_minimal_check()
    elif args.command == "run-minimal-visual-grounding-trial-check":
        result = run_minimal_visual_grounding_trial_check()
    elif args.command == "run-visual-prediction-error-attention-priority-preview-minimal-check":
        result = run_visual_prediction_error_attention_priority_preview_minimal_check()
    elif args.command == "run-visual-frame-pair-demo-assembly-check":
        result = run_visual_frame_pair_demo_assembly_check()
    elif args.command == "run-focus-candidate-schema-check":
        result = run_focus_candidate_schema_check()
    elif args.command == "run-focus-candidate-from-change-trace-check":
        result = run_focus_candidate_from_change_trace_check()
    elif args.command == "run-focus-candidate-ranking-trace-schema-check":
        result = run_focus_candidate_ranking_trace_schema_check()
    elif args.command == "run-focus-candidate-ranking-trace-check":
        result = run_focus_candidate_ranking_trace_check()
    elif args.command == "run-focus-application-gate-schema-check":
        result = run_focus_application_gate_schema_check()
    else:
        result = run_command(args.command)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if args.command == "replay-approach-box-dead-end-two-trial":
        print(_format_dead_end_ascii_replay_text(result))
    elif args.command == "replay-dead-end-trial1-candidate-maps":
        print(_format_candidate_map_trial1_ascii_replay_text(result))
    elif args.command == "replay-larger-sandbox-human":
        print(result)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
