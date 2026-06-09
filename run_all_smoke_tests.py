# -*- coding: utf-8 -*-
"""ASHL Core v0.2 smoke runner."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from ashl_core.approved_candidate_preview import run_approved_candidate_preview_check
from ashl_core.action_outcome_predictor import run_action_outcome_predictor_check
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
from ashl_core.failure_reason_classifier import run_failure_reason_classifier_check
from ashl_core.failure_events import (
    build_failure_event,
    build_lesson_candidate_input_trace,
    normalize_failure_event_trace,
    validate_failure_event,
)
from ashl_core.first_output_runtime import UTTERANCE_MAP, generate_minimal_first_output
from ashl_core.guard import guard_output
from ashl_core.grounded_action_experience import run_grounded_action_experience_check
from ashl_core.grounded_action_experience_influence import run_grounded_action_experience_influence_check
from ashl_core.instinct_random_walk_runner import run_instinct_random_walk
from ashl_core.item_reward_event import run_item_reward_event_check
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
from ashl_core.larger_sandbox_flask_ui import create_app as create_larger_sandbox_ui_app
from ashl_core.larger_sandbox_flask_ui import get_launch_config as get_larger_sandbox_ui_launch_config
from ashl_core.larger_sandbox_flask_ui import get_ui_state as get_larger_sandbox_ui_state
from ashl_core.larger_sandbox_flask_ui import reset_ui_state as reset_larger_sandbox_ui_state
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
from ashl_core.micro_navigation_sandbox import (
    ALLOWED_NAVIGATION_ACTIONS,
    apply_navigation_approach_box_action,
    apply_multi_goal_navigation_action,
    apply_navigation_action,
    create_navigation_approach_box_level_state,
    create_navigation_obstacle_level_state,
    build_initial_multi_goal_navigation_state,
    build_initial_navigation_state,
    manhattan_distance_to_box,
    manhattan_distance_to_goal as navigation_distance_to_goal,
    select_navigation_action_toward_goal,
)
from ashl_core.micro_navigation_trial_runner import (
    run_navigation_goal_trial,
    run_navigation_approach_box_trial,
    run_navigation_multi_goal_trial,
    run_navigation_obstacle_trial,
)
from ashl_core.micro_push_box_sandbox import (
    ALLOWED_ACTION_SET,
    apply_tactile_action,
    build_box_on_goal_need_state,
    build_initial_state as build_micro_push_box_state,
    build_state_action_key,
    find_previous_same_state_action_result,
    manhattan_distance_to_goal,
    rank_candidate_actions_with_goal_bias,
    score_action_from_state_action_memory,
    score_action_goal_direction,
    select_action_for_need_state,
    select_intrinsic_action,
    suggest_next_action_with_goal_bias,
    suggest_next_action_by_outcome_weight,
    suggest_next_action_avoiding_repeat_blocked,
    validate_allowed_action,
)
from ashl_core.micro_push_box_trial_runner import (
    _select_action_for_trial,
    detect_stuck_from_recent_steps,
    run_need_state_driven_trial,
    run_need_state_driven_trial_batch,
    score_action_repetition_penalty,
)
from ashl_core.manual_review import (
    build_review_trace,
    create_review_item,
    mark_review_approved,
    mark_review_rejected,
)
from ashl_core.mentor_feedback_runtime import build_minimal_mentor_feedback_trace
from ashl_core.persistence import append_jsonl, read_jsonl
from ashl_core.perception import perceive
from ashl_core.prediction_accuracy_check import run_prediction_accuracy_check
from ashl_core.prompt_leakage_check import build_decision_input_snapshot, check_leakage
from ashl_core.reward_biased_action_tendency import run_reward_biased_action_tendency_check
from ashl_core.reward_biased_random_walk_check import run_reward_biased_random_walk_check
from ashl_core.reviewed_candidate_apply_verification import run_reviewed_candidate_apply_verification_check
from ashl_core.rule_candidate_from_mismatch import run_rule_candidate_from_mismatch_check
from ashl_core.rule_candidate_review_gate import run_rule_candidate_review_gate_check
from ashl_core.rule_candidates import append_rule_candidate
from ashl_core.review_tasks import build_review_task_trace
from ashl_core.senses import build_sensor_event, build_visual_concept_candidate, validate_sensor_event
from ashl_core.session_working_memory import (
    append_outcome_record,
    build_session_outcome_record,
    build_state_snapshot_key,
    create_session_working_memory,
    query_recent_outcomes,
)
from ashl_core.similar_context_key import run_similar_context_key_check
from ashl_core.simulated_vision_sandbox import (
    ALLOWED_VIEWPORT_SYMBOLS,
    FIRST_PERSON_AGENT_VIEWPORT_POSITION,
    FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION,
    FIRST_PERSON_FRONT_SYMBOL_POSITION,
    apply_simulated_vision_action,
    build_initial_simulated_vision_state,
    create_simulated_vision_room,
    render_viewport,
    run_simulated_vision_viewport_demo,
)
from ashl_core.simulated_vision_larger_sandbox import (
    apply_larger_sandbox_action,
    build_initial_larger_sandbox_state,
    build_larger_sandbox_map_summary,
    create_simulated_vision_larger_sandbox,
    render_larger_sandbox_viewport,
    run_simulated_vision_larger_sandbox_demo,
)
from ashl_core.simulated_vision_larger_sandbox_contact import run_larger_sandbox_symbol_contact_smoke
from ashl_core.simulated_vision_larger_sandbox_human_replay import run_larger_sandbox_human_replay
from ashl_core.simulated_vision_larger_sandbox_observed_map import run_larger_sandbox_observed_map_smoke
from ashl_core.simulated_vision_memory_bridge import run_simulated_vision_memory_bridge_demo
from ashl_core.simulated_vision_observed_map import run_simulated_vision_observed_map_demo
from ashl_core.simulated_vision_symbol_grounding import run_symbol_grounding_check
from ashl_core.state_core import StateCore
from ashl_core.state_persistence import (
    read_last_trace_summary,
    read_session_summary,
    read_state_snapshot,
)
from ashl_core.standing_task import run_standing_task
from ashl_core.teaching_cli import (
    run_clear_sandbox_working_state,
    run_conflict_check_flow,
    run_disable_reenable_flow,
    run_grounded_learning_check,
    run_known_flow,
    run_lifecycle_display,
    run_minimal_interaction,
    run_approach_box_trial_cli,
    run_approach_box_two_trial_check_cli,
    run_approach_box_dead_end_trial_cli,
    run_approach_box_dead_end_two_trial_check_cli,
    run_approach_box_dead_end_two_trial_ascii_replay_cli,
    run_approach_box_dead_end_memory_control_check_cli,
    validate_dead_end_trial1_maps_cli,
    run_candidate_dead_end_trial1_ascii_replay_cli,
    run_valid_dead_end_maps_ab_control_cli,
    run_local_memory_decision_trace_observer_cli,
    demo_session_working_memory_cli,
    run_session_working_memory_trial_cli,
    run_navigation_multi_goal_metrics_cli,
    run_navigation_obstacle_trial_cli,
    run_navigation_trial_metrics_cli,
    run_need_state_trial_batch_cli,
    run_review_approve,
    run_review_display,
    run_review_reject,
    run_tactile_interaction,
    run_trial_metrics_comparison_cli,
    run_trial_metrics_baseline_compare_cli,
    run_unknown_flow,
)
from ashl_core.tactile_state_mapping import map_tactile_result_to_state_key
from ashl_core.trace_persistence import append_first_output_trace, append_mentor_feedback_trace
from ashl_core.trial_feedback import append_trial_feedback, build_trial_feedback, summarize_trial_feedback
from ashl_core.trial_rules import build_trial_suggestions, list_approved_trial_candidates, build_trial_rule_view
from ashl_core.two_round_instinct_reward_comparison import run_two_round_instinct_reward_comparison
from ashl_core.wall_experience_influence import run_wall_experience_influence_check


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


def smoke_simulated_vision_viewport() -> dict:
    level = create_simulated_vision_room()
    initial_state = build_initial_simulated_vision_state(level)
    moved = apply_simulated_vision_action(initial_state, level, "move_forward")
    wall_state = {"level_id": level["level_id"], "pos": (3, 1), "facing": "north", "tick": 0}
    blocked = apply_simulated_vision_action(wall_state, level, "move_forward")
    item_state = {"level_id": level["level_id"], "pos": (4, 2), "facing": "north", "tick": 0}
    item_contact = apply_simulated_vision_action(item_state, level, "move_forward")
    edge_state = {"level_id": level["level_id"], "pos": (0, 0), "facing": "north", "tick": 0}
    edge_symbols = {symbol for row in render_viewport(edge_state, level) for symbol in row}
    result = run_simulated_vision_viewport_demo()
    boundary = result.get("boundary_check", {})
    viewport_symbols = {
        symbol
        for step in result.get("action_trace", [])
        for row in step.get("viewport", [])
        for symbol in row
    }
    passed = (
        initial_state["pos"] == (3, 3)
        and initial_state["facing"] == "north"
        and moved["state"]["pos"] == (3, 2)
        and moved["trace"]["result"] == "moved"
        and blocked["state"]["pos"] == (3, 1)
        and blocked["trace"]["result"] == "blocked"
        and blocked["trace"]["failure_reasons"] == ["wall_blocked"]
        and item_contact["trace"]["result"] == "item_contact"
        and "x" in edge_symbols
        and viewport_symbols <= ALLOWED_VIEWPORT_SYMBOLS
        and result.get("command") == "run-simulated-vision-viewport-demo"
        and result.get("flow") == "simulated_vision_facing_viewport_v0"
        and len(result.get("action_trace", [])) == 7
        and boundary.get("simulated_vision_only") is True
        and boundary.get("first_person_viewport") is True
        and boundary.get("agent_viewport_position") == [2, 1]
        and boundary.get("front_symbol_position") == [1, 1]
        and boundary.get("far_front_symbol_position") == [0, 1]
        and boundary.get("centered_top_down_viewport") is False
        and boundary.get("real_image_vision") is False
        and boundary.get("structured_symbols_only") is True
        and boundary.get("full_map_visible_to_agent") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("llm_vision_used") is False
        and boundary.get("llm_planning_used") is False
        and boundary.get("session_memory_write") is False
    )
    return _result(
        "simulated_vision_viewport",
        passed,
        {
            "initial_state": {"pos": initial_state["pos"], "facing": initial_state["facing"]},
            "moved_result": moved["trace"]["result"],
            "blocked_result": blocked["trace"]["result"],
            "item_result": item_contact["trace"]["result"],
            "viewport_symbols": sorted(viewport_symbols),
            "edge_symbols": sorted(edge_symbols),
            "boundary": boundary,
        },
    )


def smoke_simulated_vision_first_person_viewport() -> dict:
    level = create_simulated_vision_room()
    initial_state = build_initial_simulated_vision_state(level)
    initial_viewport = render_viewport(initial_state, level)
    wall_state = {"level_id": level["level_id"], "pos": (3, 1), "facing": "north", "tick": 0}
    wall_viewport = render_viewport(wall_state, level)
    item_state = {"level_id": level["level_id"], "pos": (4, 2), "facing": "north", "tick": 0}
    item_viewport = render_viewport(item_state, level)
    result = run_simulated_vision_viewport_demo(action_sequence=["look"])
    boundary = result.get("boundary_check", {})
    passed = (
        initial_viewport[2][1] == "a"
        and initial_viewport[1][1] == "e"
        and initial_viewport[0][1] == "e"
        and wall_viewport[2][1] == "a"
        and wall_viewport[1][1] == "w"
        and item_viewport[2][1] == "a"
        and item_viewport[1][1] == "i"
        and FIRST_PERSON_AGENT_VIEWPORT_POSITION == [2, 1]
        and FIRST_PERSON_FRONT_SYMBOL_POSITION == [1, 1]
        and FIRST_PERSON_FAR_FRONT_SYMBOL_POSITION == [0, 1]
        and boundary.get("first_person_viewport") is True
        and boundary.get("centered_top_down_viewport") is False
    )
    return _result(
        "simulated_vision_first_person_viewport",
        passed,
        {
            "initial_viewport": initial_viewport,
            "wall_front_symbol": wall_viewport[1][1],
            "item_front_symbol": item_viewport[1][1],
            "boundary": boundary,
        },
    )


def smoke_simulated_vision_larger_sandbox_static_runtime() -> dict:
    level = create_simulated_vision_larger_sandbox()
    initial_state = build_initial_larger_sandbox_state(level)
    summary = build_larger_sandbox_map_summary(level)
    initial_viewport = render_larger_sandbox_viewport(initial_state, level)
    doorway_state = {"level_id": level["level_id"], "pos": (3, 2), "facing": "east", "tick": 0}
    doorway_viewport = render_larger_sandbox_viewport(doorway_state, level)
    doorway_result = apply_larger_sandbox_action(doorway_state, level, "move_forward")
    exit_state = {"level_id": level["level_id"], "pos": (10, 7), "facing": "east", "tick": 0}
    exit_viewport = render_larger_sandbox_viewport(exit_state, level)
    exit_result = apply_larger_sandbox_action(exit_state, level, "move_forward")
    item_state = {"level_id": level["level_id"], "pos": (8, 2), "facing": "north", "tick": 0}
    item_result = apply_larger_sandbox_action(item_state, level, "move_forward")
    wall_state = {"level_id": level["level_id"], "pos": (2, 1), "facing": "north", "tick": 0}
    wall_result = apply_larger_sandbox_action(wall_state, level, "move_forward")
    result = run_simulated_vision_larger_sandbox_demo()
    boundary = result.get("boundary_check", {})
    passed = (
        level["level_id"] == "simulated_vision_larger_sandbox_v0"
        and summary.get("width") == 12
        and summary.get("height") == 9
        and summary.get("agent_start") == [2, 2]
        and summary.get("initial_facing") == "north"
        and summary.get("item_count") == 4
        and summary.get("doorway_count") == 2
        and summary.get("exit_count") == 1
        and summary.get("unsupported_symbols") == []
        and initial_viewport[2][1] == "a"
        and initial_viewport[1][1] != "a"
        and doorway_viewport[1][1] == "d"
        and doorway_result["trace"]["result"] == "moved"
        and doorway_result["trace"]["effect_tags"] == ["passage_crossed"]
        and exit_viewport[1][1] == "g"
        and exit_result["trace"]["result"] == "exit_contact"
        and exit_result["trace"]["effect_tags"] == ["exit_contact"]
        and item_result["trace"]["result"] == "item_contact"
        and item_result["trace"]["effect_tags"] == ["item_contact"]
        and wall_result["trace"]["result"] == "blocked"
        and wall_result["trace"]["failure_reasons"] == ["wall_blocked"]
        and result.get("command") == "run-simulated-vision-larger-sandbox-demo"
        and result.get("flow") == "simulated_vision_larger_sandbox_static_runtime_v0"
        and len(result.get("action_trace", [])) == 7
        and boundary.get("larger_static_sandbox_enabled") is True
        and boundary.get("simulated_vision_only") is True
        and boundary.get("structured_symbols_only") is True
        and boundary.get("real_image_vision") is False
        and boundary.get("llm_vision_used") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("route_planner_added") is False
        and boundary.get("full_map_visible_to_agent") is False
        and boundary.get("first_person_viewport") is True
        and boundary.get("agent_viewport_position") == [2, 1]
        and boundary.get("front_symbol_position") == [1, 1]
        and boundary.get("centered_top_down_viewport") is False
        and boundary.get("doorway_symbol_supported") is True
        and boundary.get("doorway_passable") is True
        and boundary.get("doorway_semantic_boundary_given_to_agent") is False
        and boundary.get("exit_placeholder_supported") is True
        and boundary.get("exit_conditional_spawn_enabled") is False
        and boundary.get("task_completion_enabled") is False
        and boundary.get("item_collection_enabled") is False
        and boundary.get("item_pickup_enabled") is False
        and boundary.get("inventory_enabled") is False
        and boundary.get("curiosity_enabled") is False
        and boundary.get("prediction_error_enabled") is False
        and boundary.get("place_memory_enabled") is False
        and boundary.get("home_sandbox_enabled") is False
        and boundary.get("action_selection_modified") is False
        and boundary.get("existing_navigation_action_selection_modified") is False
        and boundary.get("lesson_store_write") is False
        and boundary.get("memory_layer_write") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("visual_understanding_claimed") is False
        and boundary.get("symbol_grounding_solved_claimed") is False
        and boundary.get("general_learning_claimed") is False
    )
    return _result(
        "simulated_vision_larger_sandbox_static_runtime",
        passed,
        {
            "map_summary": summary,
            "doorway_result": doorway_result["trace"]["result"],
            "exit_result": exit_result["trace"]["result"],
            "item_result": item_result["trace"]["result"],
            "wall_result": wall_result["trace"]["result"],
            "boundary": boundary,
        },
    )


def smoke_larger_sandbox_observed_map_smoke() -> dict:
    result = run_larger_sandbox_observed_map_smoke()
    boundary = result.get("boundary_check", {})
    scenarios = {item.get("scenario"): item for item in result.get("scenario_results", [])}
    summary = result.get("observed_map_summary", {})
    persistence_checks = result.get("persistence_checks", [])
    map_summary = result.get("map_summary", {})
    total_map_cells = map_summary.get("width", 0) * map_summary.get("height", 0)
    passed = (
        result.get("command") == "run-larger-sandbox-observed-map-smoke"
        and result.get("flow") == "larger_sandbox_observed_map_smoke_v0"
        and result.get("level_id") == "simulated_vision_larger_sandbox_v0"
        and map_summary.get("item_count") == 4
        and map_summary.get("doorway_count") == 2
        and map_summary.get("exit_count") == 1
        and scenarios.get("doorway_d", {}).get("passed") is True
        and scenarios.get("item_i", {}).get("passed") is True
        and scenarios.get("exit_g", {}).get("passed") is True
        and "d" in summary.get("remembered_symbols", [])
        and "i" in summary.get("remembered_symbols", [])
        and "g" in summary.get("remembered_symbols", [])
        and summary.get("remembered_d_count", 0) >= 1
        and summary.get("remembered_i_count", 0) >= 1
        and summary.get("remembered_g_count", 0) >= 1
        and summary.get("x_does_not_erase_known_cells") is True
        and summary.get("unseen_cells_not_inferred") is True
        and 0 < summary.get("known_cell_count", 0) < total_map_cells
        and all(check.get("passed") is True for check in persistence_checks)
        and boundary.get("larger_static_sandbox_used") is True
        and boundary.get("observed_local_map_enabled") is True
        and boundary.get("doorway_remembered") is True
        and boundary.get("item_remembered") is True
        and boundary.get("exit_remembered") is True
        and boundary.get("x_does_not_erase_known_cells") is True
        and boundary.get("unseen_cells_not_inferred") is True
        and boundary.get("item_collection_enabled") is False
        and boundary.get("exit_conditional_spawn_enabled") is False
        and boundary.get("task_completion_enabled") is False
        and boundary.get("curiosity_enabled") is False
        and boundary.get("prediction_error_enabled") is False
        and boundary.get("place_memory_enabled") is False
        and boundary.get("home_sandbox_enabled") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("route_planner_added") is False
        and boundary.get("long_term_memory_write") is False
    )
    return _result(
        "larger_sandbox_observed_map_smoke",
        passed,
        {
            "map_summary": map_summary,
            "observed_map_summary": summary,
            "persistence_checks": persistence_checks,
            "boundary": boundary,
        },
    )


def smoke_larger_sandbox_symbol_contact_smoke() -> dict:
    result = run_larger_sandbox_symbol_contact_smoke()
    summary = result.get("summary", {})
    boundary = result.get("boundary_check", {})
    scenarios = {item.get("scenario"): item for item in result.get("scenario_results", [])}
    doorway = scenarios.get("doorway_d", {})
    item = scenarios.get("item_i", {})
    exit_result = scenarios.get("exit_g", {})
    passed = (
        result.get("command") == "run-larger-sandbox-symbol-contact-smoke"
        and result.get("flow") == "larger_sandbox_symbol_contact_smoke_v0"
        and result.get("level_id") == "simulated_vision_larger_sandbox_v0"
        and summary.get("scenario_count") == 3
        and summary.get("passed_count") == 3
        and summary.get("failed_count") == 0
        and summary.get("doorway_contact_passed") is True
        and summary.get("item_contact_passed") is True
        and summary.get("exit_contact_passed") is True
        and summary.get("all_larger_sandbox_symbol_contact_checks_passed") is True
        and doorway.get("front_symbol") == "d"
        and doorway.get("actual_outcome") == "moved"
        and "passage_crossed" in doorway.get("effect_tags", [])
        and doorway.get("position_changed") is True
        and doorway.get("contact_match") is True
        and item.get("front_symbol") == "i"
        and item.get("actual_outcome") == "item_contact"
        and "item_contact" in item.get("effect_tags", [])
        and item.get("contact_match") is True
        and exit_result.get("front_symbol") == "g"
        and exit_result.get("actual_outcome") == "exit_contact"
        and "exit_contact" in exit_result.get("effect_tags", [])
        and exit_result.get("contact_match") is True
        and boundary.get("larger_static_sandbox_used") is True
        and boundary.get("symbol_contact_smoke_enabled") is True
        and boundary.get("doorway_contact_checked") is True
        and boundary.get("doorway_passable") is True
        and boundary.get("doorway_semantic_boundary_given_to_agent") is False
        and boundary.get("item_contact_checked") is True
        and boundary.get("item_collection_enabled") is False
        and boundary.get("item_pickup_enabled") is False
        and boundary.get("inventory_enabled") is False
        and boundary.get("exit_contact_checked") is True
        and boundary.get("exit_conditional_spawn_enabled") is False
        and boundary.get("task_completion_enabled") is False
        and boundary.get("win_condition_enabled") is False
        and boundary.get("curiosity_enabled") is False
        and boundary.get("prediction_error_enabled") is False
        and boundary.get("place_memory_enabled") is False
        and boundary.get("home_sandbox_enabled") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("route_planner_added") is False
        and boundary.get("long_term_memory_write") is False
    )
    return _result(
        "larger_sandbox_symbol_contact_smoke",
        passed,
        {
            "summary": summary,
            "scenario_results": result.get("scenario_results", []),
            "boundary": boundary,
        },
    )


def smoke_larger_sandbox_human_replay() -> dict:
    demo = run_larger_sandbox_human_replay()
    contact = run_larger_sandbox_human_replay(mode="contact")
    demo_markers = [
        "Larger Sandbox Human Replay",
        "Level: simulated_vision_larger_sandbox_v0",
        "Mode: demo",
        "Legend:",
        "w = wall",
        "e = empty",
        "i = item",
        "d = passage marker",
        "g = exit placeholder",
        "x = unseen / out of view",
        "a = Qingyin",
        "Step 1: look",
        "w w w",
        "e e e",
        "e a e",
        "e a d",
        "Position:",
        "Facing:",
        "Visible symbols:",
        "Visible symbols: passage marker, empty, wall\nFront symbol: e",
        "Front symbol:",
        "Boundary:",
        "Readability replay only.",
        "No runtime behavior changed.",
        "No action selection changed.",
        "No pathfinding.",
        "No item collection.",
        "No exit activation.",
        "No visual understanding claim.",
    ]
    contact_markers = [
        "Mode: contact",
        "doorway_d",
        "item_i",
        "exit_g",
        "Front symbol: d",
        "Front symbol: i",
        "Front symbol: g",
        "Result: moved",
        "Result: item_contact",
        "Result: exit_contact",
        "passage_crossed",
        "item_contact",
        "exit_contact",
    ]
    passed = (
        isinstance(demo, str)
        and isinstance(contact, str)
        and all(marker in demo for marker in demo_markers)
        and all(marker in contact for marker in contact_markers)
        and not demo.lstrip().startswith("{")
        and not contact.lstrip().startswith("{")
    )
    return _result(
        "larger_sandbox_human_replay",
        passed,
        {
            "demo_preview": demo.splitlines()[:16],
            "contact_preview": contact.splitlines()[:20],
        },
    )


def smoke_larger_sandbox_flask_ui() -> dict:
    reset_larger_sandbox_ui_state()
    app = create_larger_sandbox_ui_app()
    client = app.test_client()
    index_response = client.get("/")
    index_html = index_response.get_data(as_text=True)
    qingyin_initial_response = client.get("/qingyin_state.json")
    qingyin_initial = qingyin_initial_response.get_json() or {}
    cooldown_update_response = client.post("/cooldown", data={"cooldown_seconds": "1.0"})
    look_response = client.post("/action", data={"action": "look"})
    qingyin_after_look = (client.get("/qingyin_state.json").get_json() or {})
    blocked_response = client.post("/action", data={"action": "turn_right"})
    blocked_state = get_larger_sandbox_ui_state()
    reset_after_blocked_response = client.post("/reset")
    cooldown_disable_response = client.post("/cooldown", data={"cooldown_seconds": "0.0"})
    turn_response = client.post("/action", data={"action": "turn_right"})
    move_response = client.post("/action", data={"action": "move_forward"})
    moved_state = get_larger_sandbox_ui_state()
    qingyin_after_move = (client.get("/qingyin_state.json").get_json() or {})
    reset_response = client.post("/reset")
    reset_state = get_larger_sandbox_ui_state()
    launch_config = get_larger_sandbox_ui_launch_config()
    boundary = launch_config.get("boundary_check", {})
    passed = (
        index_response.status_code == 200
        and "Larger Sandbox" in index_html
        and "Manual View" in index_html
        and "Random Walk Playback" in index_html
        and "No playback trace" in index_html
        and "Position: [2, 2]" in index_html
        and "Facing: north" in index_html
        and "look" in index_html
        and "turn_left" in index_html
        and "turn_right" in index_html
        and "move_forward" in index_html
        and "reset" in index_html
        and "Qingyin Observation" in index_html
        and "manual observation" in index_html
        and "symbolic sandbox body" in index_html
        and "Visible symbols" in index_html
        and "Action cooldown" in index_html
        and "Cooldown: 0.5s" in index_html
        and "Cooldown remaining: 0.00 seconds" in index_html
        and "Can act: yes" in index_html
        and "No autonomy." in index_html
        and "No auto exploration." in index_html
        and "No LLM planning." in index_html
        and "No action selection change." in index_html
        and "No pathfinding." in index_html
        and qingyin_initial_response.status_code == 200
        and qingyin_initial.get("name") == "Qingyin"
        and qingyin_initial.get("mode") == "manual_observation"
        and qingyin_initial.get("body") == "symbolic_sandbox_body"
        and qingyin_initial.get("boundary_check", {}).get("manual_observation_only") is True
        and qingyin_initial.get("boundary_check", {}).get("autonomous_action_loop_enabled") is False
        and qingyin_initial.get("boundary_check", {}).get("pathfinding_used") is False
        and cooldown_update_response.status_code == 302
        and look_response.status_code == 302
        and qingyin_after_look.get("last_action") == "look"
        and qingyin_after_look.get("last_result") == "observed"
        and blocked_response.status_code == 302
        and any("Action blocked by cooldown." in entry for entry in blocked_state.get("action_log", []))
        and reset_after_blocked_response.status_code == 302
        and cooldown_disable_response.status_code == 302
        and turn_response.status_code == 302
        and move_response.status_code == 302
        and moved_state.get("pos") == [3, 2]
        and moved_state.get("facing") == "east"
        and moved_state.get("action_cooldown_seconds") == 0.0
        and any("Step 2: move_forward" in entry for entry in moved_state.get("action_log", []))
        and any("Qingyin moved forward." in entry for entry in moved_state.get("action_log", []))
        and qingyin_after_move.get("name") == "Qingyin"
        and qingyin_after_move.get("last_action") == "move_forward"
        and qingyin_after_move.get("boundary_check", {}).get("decision_loop_enabled") is False
        and reset_response.status_code == 302
        and reset_state.get("pos") == [2, 2]
        and reset_state.get("facing") == "north"
        and reset_state.get("action_log") == []
        and launch_config.get("command") == "run-larger-sandbox-ui"
        and launch_config.get("url") == "http://127.0.0.1:7860"
        and launch_config.get("local_only") is True
        and launch_config.get("action_cooldown_enabled") is True
        and launch_config.get("action_cooldown_configurable") is True
        and launch_config.get("qingyin_observation_bridge_enabled") is True
        and launch_config.get("manual_observation_only") is True
        and boundary.get("ui_prototype") is True
        and boundary.get("qingyin_observation_bridge_enabled") is True
        and boundary.get("manual_observation_only") is True
        and boundary.get("action_cooldown_enabled") is True
        and boundary.get("action_cooldown_configurable") is True
        and boundary.get("autonomous_action_loop_enabled") is False
        and boundary.get("auto_exploration_enabled") is False
        and boundary.get("decision_loop_enabled") is False
        and boundary.get("runtime_behavior_modified") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("route_planner_added") is False
        and boundary.get("item_collection_enabled") is False
        and boundary.get("exit_activation_enabled") is False
        and boundary.get("curiosity_enabled") is False
        and boundary.get("prediction_error_enabled") is False
        and boundary.get("place_memory_enabled") is False
        and boundary.get("home_sandbox_enabled") is False
        and boundary.get("long_term_memory_write") is False
    )
    return _result(
        "larger_sandbox_flask_ui",
        passed,
        {
            "index_status": index_response.status_code,
            "blocked_state": blocked_state,
            "moved_state": moved_state,
            "qingyin_initial": qingyin_initial,
            "qingyin_after_move": qingyin_after_move,
            "reset_state": reset_state,
            "launch_config": launch_config,
        },
    )


def smoke_instinct_wall_ui_observation() -> dict:
    reset_larger_sandbox_ui_state()
    app = create_larger_sandbox_ui_app()
    client = app.test_client()
    index_response = client.get("/")
    index_html = index_response.get_data(as_text=True)
    random_response = client.post("/experiment/random-walk", data={"seed": "1", "max_steps": "10"})
    random_html = client.get("/").get_data(as_text=True)
    random_state = client.get("/experiment_state.json").get_json() or {}
    wall_response = client.post("/experiment/wall-influence", data={"seed": "1", "max_steps": "50"})
    wall_html = client.get("/").get_data(as_text=True)
    wall_state = client.get("/experiment_state.json").get_json() or {}
    qingyin_state = client.get("/qingyin_state.json").get_json() or {}
    clear_response = client.post("/experiment/clear")
    clear_state = client.get("/experiment_state.json").get_json() or {}
    boundary = wall_state.get("boundary_check", {})
    random_walk = random_state.get("random_walk", {}) or {}
    wall_influence = wall_state.get("wall_influence", {}) or {}
    passed = (
        index_response.status_code == 200
        and "Instinct / Experience Observation" in index_html
        and "Run random walk sample" in index_html
        and "Run wall influence check" in index_html
        and "Clear experiment observation" in index_html
        and "No continuous loop." in index_html
        and "No pathfinding." in index_html
        and "No reward bias." in index_html
        and random_response.status_code == 302
        and random_state.get("mode") == "instinct_random_walk"
        and random_walk.get("step_count") == 10
        and "Step count" in random_html
        and "Wall blocked count" in random_html
        and "Item contact count" in random_html
        and "Experience count" in random_html
        and "Reward bias enabled</dt><dd>false" in random_html
        and wall_response.status_code == 302
        and wall_state.get("mode") == "wall_experience_influence"
        and wall_influence.get("control_passed") is True
        and wall_influence.get("influence_passed") is True
        and wall_influence.get("selected_action_without_experience") == "move_forward"
        and wall_influence.get("selected_action_with_wall_experience") == "turn_right"
        and wall_influence.get("experience_used_for_decision") is True
        and "No-experience control" in wall_html
        and "With-prior-experience influence" in wall_html
        and "Selected action without experience" in wall_html
        and "Selected action with wall experience" in wall_html
        and qingyin_state.get("experiment_observation", {}).get("mode") == "wall_experience_influence"
        and boundary.get("instinct_random_walk_ui_observation_enabled") is True
        and boundary.get("wall_experience_influence_ui_observation_enabled") is True
        and boundary.get("bounded_runner_only") is True
        and boundary.get("continuous_autonomous_loop_enabled") is False
        and boundary.get("auto_exploration_enabled") is False
        and boundary.get("decision_loop_enabled") is False
        and boundary.get("item_reward_bias_enabled") is False
        and boundary.get("dopamine_like_signal_enabled") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("route_planner_added") is False
        and boundary.get("long_term_memory_write") is False
        and clear_response.status_code == 302
        and clear_state.get("mode") == "none"
    )
    return _result(
        "instinct_wall_ui_observation",
        passed,
        {
            "random_state": random_state,
            "wall_state": wall_state,
            "qingyin_state": qingyin_state,
            "clear_state": clear_state,
        },
    )


def smoke_larger_sandbox_live_step_playback_ui() -> dict:
    reset_larger_sandbox_ui_state()
    app = create_larger_sandbox_ui_app()
    client = app.test_client()
    initial_response = client.get("/")
    initial_html = initial_response.get_data(as_text=True)
    random_response = client.post("/experiment/random-walk", data={"seed": "1", "max_steps": "4"})
    first_html = client.get("/").get_data(as_text=True)
    first_playback = client.get("/playback_state.json").get_json() or {}
    manual_before = get_larger_sandbox_ui_state()
    next_response = client.post("/playback/next")
    next_playback = client.get("/playback_state.json").get_json() or {}
    previous_response = client.post("/playback/previous")
    previous_playback = client.get("/playback_state.json").get_json() or {}
    client.post("/playback/previous")
    below_playback = client.get("/playback_state.json").get_json() or {}
    client.post("/playback/next")
    client.post("/playback/next")
    client.post("/playback/next")
    client.post("/playback/next")
    above_playback = client.get("/playback_state.json").get_json() or {}
    reset_response = client.post("/playback/reset")
    reset_playback = client.get("/playback_state.json").get_json() or {}
    manual_after = get_larger_sandbox_ui_state()
    boundary = first_playback.get("boundary_check", {})
    first_step = first_playback.get("current_step", {}) or {}
    next_step = next_playback.get("current_step", {}) or {}
    passed = (
        initial_response.status_code == 200
        and "Random Walk Playback" in initial_html
        and "No playback trace" in initial_html
        and "Recorded trace only" in initial_html
        and random_response.status_code == 302
        and "Playback: step 1 / 4" in first_html
        and "Playback View" in first_html
        and "Selected action" in first_html
        and "Result" in first_html
        and "Front symbol" in first_html
        and first_playback.get("playback_mode") == "recorded_random_walk"
        and first_playback.get("playback_index") == 0
        and first_playback.get("playback_length") == 4
        and first_step.get("selected_action") is not None
        and first_step.get("result") is not None
        and next_response.status_code == 302
        and next_playback.get("playback_index") == 1
        and next_step.get("tick") != first_step.get("tick")
        and previous_response.status_code == 302
        and previous_playback.get("playback_index") == 0
        and below_playback.get("playback_index") == 0
        and above_playback.get("playback_index") == 3
        and reset_response.status_code == 302
        and reset_playback.get("playback_index") == 0
        and manual_after.get("pos") == manual_before.get("pos")
        and manual_after.get("facing") == manual_before.get("facing")
        and boundary.get("trace_playback_enabled") is True
        and boundary.get("playback_from_recorded_trace_only") is True
        and boundary.get("server_side_autonomous_loop_enabled") is False
        and boundary.get("auto_exploration_enabled") is False
        and boundary.get("decision_loop_enabled") is False
        and boundary.get("manual_state_modified_by_playback") is False
        and boundary.get("reward_bias_enabled") is False
        and boundary.get("dopamine_like_signal_enabled") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("route_planner_added") is False
        and boundary.get("long_term_memory_write") is False
    )
    return _result(
        "larger_sandbox_live_step_playback_ui",
        passed,
        {
            "first_playback": first_playback,
            "next_playback": next_playback,
            "reset_playback": reset_playback,
            "manual_before": manual_before,
            "manual_after": manual_after,
        },
    )


def smoke_simulated_vision_memory_bridge() -> dict:
    result = run_simulated_vision_memory_bridge_demo()
    blocked_result = run_simulated_vision_memory_bridge_demo(
        action_sequence=["move_forward", "move_forward", "move_forward"],
    )
    boundary = result.get("boundary_check", {})
    query_summary = result.get("query_summary", {})
    records = result.get("memory_records", [])
    blocked_summary = blocked_result.get("query_summary", {})
    passed = (
        result.get("command") == "run-simulated-vision-memory-bridge-demo"
        and result.get("flow") == "simulated_vision_session_memory_bridge_v0"
        and len(result.get("action_trace", [])) == len(records)
        and query_summary.get("record_count_before_clear") == len(result.get("action_trace", []))
        and result.get("clear_summary", {}).get("record_count_after_clear") == 0
        and all(record.get("state_key") for record in records)
        and all("viewport" in record.get("state_snapshot", {}) for record in records)
        and all("visible_symbols" in record.get("state_snapshot", {}) for record in records)
        and query_summary.get("query_by_action_look_count") == 4
        and query_summary.get("query_by_action_move_forward_count") == 1
        and "query_by_visible_symbol_i_count" in query_summary
        and blocked_summary.get("query_by_outcome_type_blocked_count") == 1
        and blocked_summary.get("query_by_failure_reason_wall_blocked_count") == 1
        and boundary.get("simulated_vision_only") is True
        and boundary.get("structured_symbols_only") is True
        and boundary.get("first_person_viewport") is True
        and boundary.get("agent_viewport_position") == [2, 1]
        and boundary.get("front_symbol_position") == [1, 1]
        and boundary.get("centered_top_down_viewport") is False
        and boundary.get("real_image_vision") is False
        and boundary.get("llm_vision_used") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("session_memory_write") is True
        and boundary.get("session_memory_cleared") is True
        and boundary.get("action_selection_modified") is False
    )
    return _result(
        "simulated_vision_memory_bridge",
        passed,
        {
            "action_trace_count": len(result.get("action_trace", [])),
            "memory_record_count": len(records),
            "query_summary": query_summary,
            "blocked_query_summary": blocked_summary,
            "boundary": boundary,
        },
    )


def smoke_simulated_vision_observed_map() -> dict:
    result = run_simulated_vision_observed_map_demo()
    boundary = result.get("boundary_check", {})
    trace = result.get("observed_map_trace", [])
    persistence = result.get("persistence_check", {})
    final_map = trace[-1].get("observed_local_map", {}) if trace else {}
    known_cells = final_map.get("known_cells", [])
    remembered_symbols = sorted({cell.get("symbol") for cell in known_cells})
    passed = (
        result.get("command") == "run-simulated-vision-observed-map-demo"
        and result.get("flow") == "simulated_vision_observed_local_map_v0"
        and len(result.get("action_trace", [])) == len(trace)
        and trace
        and trace[0].get("known_cell_count_before") == 0
        and trace[0].get("known_cell_count_after", 0) > 0
        and final_map.get("known_cell_count", 0) >= trace[0].get("known_cell_count_after", 0)
        and persistence.get("passed") is True
        and persistence.get("current_viewport_symbol_for_same_cell_or_x") == "x"
        and boundary.get("simulated_vision_only") is True
        and boundary.get("structured_symbols_only") is True
        and boundary.get("first_person_viewport") is True
        and boundary.get("agent_viewport_position") == [2, 1]
        and boundary.get("front_symbol_position") == [1, 1]
        and boundary.get("centered_top_down_viewport") is False
        and boundary.get("real_image_vision") is False
        and boundary.get("llm_vision_used") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("observed_local_map_enabled") is True
        and boundary.get("observed_map_session_local") is True
        and boundary.get("x_does_not_erase_known_cells") is True
        and boundary.get("unseen_cells_not_inferred") is True
        and boundary.get("action_selection_modified") is False
        and boundary.get("route_planner_added") is False
        and boundary.get("item_seeking_added") is False
        and boundary.get("session_memory_write") is False
    )
    return _result(
        "simulated_vision_observed_map",
        passed,
        {
            "action_trace_count": len(result.get("action_trace", [])),
            "observed_map_trace_count": len(trace),
            "known_cell_count_initial": trace[0].get("known_cell_count_before") if trace else None,
            "known_cell_count_final": final_map.get("known_cell_count"),
            "remembered_symbols": remembered_symbols,
            "persistence_check": persistence,
            "boundary": boundary,
        },
    )


def smoke_simulated_vision_symbol_grounding() -> dict:
    result = run_symbol_grounding_check()
    summary = result.get("summary", {})
    boundary = result.get("boundary_check", {})
    scenarios = {item.get("scenario"): item for item in result.get("scenario_results", [])}
    wall = scenarios.get("wall", {})
    empty = scenarios.get("empty", {})
    item = scenarios.get("item", {})
    passed = (
        result.get("command") == "run-simulated-vision-symbol-grounding-check"
        and result.get("flow") == "simulated_vision_symbol_grounding_check_v0"
        and summary.get("scenario_count") == 3
        and summary.get("passed_count") == 3
        and summary.get("failed_count") == 0
        and summary.get("all_grounding_checks_passed") is True
        and wall.get("front_symbol") == "w"
        and wall.get("actual_outcome") == "blocked"
        and wall.get("failure_reasons") == ["wall_blocked"]
        and wall.get("position_changed") is False
        and empty.get("front_symbol") == "e"
        and empty.get("actual_outcome") == "moved"
        and empty.get("position_changed") is True
        and item.get("front_symbol") == "i"
        and item.get("actual_outcome") == "item_contact"
        and item.get("item_grounding_match") is True
        and boundary.get("simulated_vision_only") is True
        and boundary.get("structured_symbols_only") is True
        and boundary.get("first_person_viewport") is True
        and boundary.get("agent_viewport_position") == [2, 1]
        and boundary.get("front_symbol_position") == [1, 1]
        and boundary.get("centered_top_down_viewport") is False
        and boundary.get("real_image_vision") is False
        and boundary.get("llm_vision_used") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("symbol_grounding_check_enabled") is True
        and boundary.get("symbol_grounding_solved_claimed") is False
        and boundary.get("visual_understanding_claimed") is False
        and boundary.get("action_selection_modified") is False
        and boundary.get("item_seeking_added") is False
        and boundary.get("inventory_added") is False
    )
    return _result(
        "simulated_vision_symbol_grounding",
        passed,
        {
            "summary": summary,
            "scenario_results": result.get("scenario_results", []),
            "boundary": boundary,
        },
    )


def smoke_grounded_action_experience() -> dict:
    result = run_grounded_action_experience_check()
    summary = result.get("experience_summary", {})
    boundary = result.get("boundary_check", {})
    scenarios = {item.get("scenario"): item for item in result.get("scenario_results", [])}
    records = {item.get("front_symbol"): item for item in result.get("experience_records", [])}
    wall = scenarios.get("wall", {})
    empty = scenarios.get("empty", {})
    item = scenarios.get("item", {})
    passed = (
        result.get("command") == "run-grounded-action-experience-check"
        and result.get("flow") == "grounded_action_experience_v0"
        and summary.get("experience_count") == 3
        and summary.get("wall_experience_recorded") is True
        and summary.get("empty_experience_recorded") is True
        and summary.get("item_experience_recorded") is True
        and summary.get("experience_records_have_front_symbol") is True
        and summary.get("experience_records_have_action") is True
        and summary.get("experience_records_have_outcome") is True
        and summary.get("all_grounded_action_experiences_recorded") is True
        and wall.get("front_symbol") == "w"
        and wall.get("actual_outcome") == "blocked"
        and wall.get("failure_reasons") == ["wall_blocked"]
        and empty.get("front_symbol") == "e"
        and empty.get("actual_outcome") == "moved"
        and item.get("front_symbol") == "i"
        and item.get("actual_outcome") == "item_contact"
        and records.get("w", {}).get("outcome_type") == "blocked"
        and records.get("e", {}).get("outcome_type") == "moved"
        and records.get("i", {}).get("outcome_type") == "item_contact"
        and boundary.get("grounded_action_experience_enabled") is True
        and boundary.get("first_person_viewport") is True
        and boundary.get("agent_viewport_position") == [2, 1]
        and boundary.get("front_symbol_position") == [1, 1]
        and boundary.get("centered_top_down_viewport") is False
        and boundary.get("grounded_action_influence_enabled") is False
        and boundary.get("action_selection_modified") is False
        and boundary.get("experience_used_for_decision") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("llm_vision_used") is False
        and boundary.get("long_term_memory_write") is False
    )
    return _result(
        "grounded_action_experience",
        passed,
        {
            "experience_summary": summary,
            "scenario_results": result.get("scenario_results", []),
            "boundary": boundary,
        },
    )


def smoke_instinct_random_walk_runner() -> dict:
    result = run_instinct_random_walk(seed=1, max_steps=20)
    same = run_instinct_random_walk(seed=1, max_steps=20)
    different = run_instinct_random_walk(seed=2, max_steps=20)
    boundary = result.get("boundary_check", {})
    metrics = result.get("metrics", {})
    experience_summary = result.get("experience_summary", {})
    actions = [step.get("selected_action") for step in result.get("step_trace", [])]
    different_actions = [step.get("selected_action") for step in different.get("step_trace", [])]
    experience_keys = experience_summary.get("experience_keys", [])
    passed = (
        result.get("command") == "run-instinct-random-walk"
        and result.get("flow") == "instinct_random_walk_runner_v0"
        and result.get("status") == "ok"
        and result.get("level_id") == "simulated_vision_larger_sandbox_v0"
        and result.get("seed") == 1
        and result.get("max_steps") == 20
        and result.get("action_weights") == {"look": 1, "turn_left": 1, "turn_right": 1, "move_forward": 2}
        and len(result.get("step_trace", [])) == 20
        and metrics.get("step_count") == 20
        and metrics.get("step_count") <= result.get("max_steps")
        and "wall_blocked_count" in metrics
        and "item_contact_count" in metrics
        and experience_summary.get("experience_count") == 20
        and all(action in {"look", "turn_left", "turn_right", "move_forward"} for action in actions)
        and all(step.get("experience_record", {}).get("experience_key", "").startswith("front_symbol=") for step in result.get("step_trace", []))
        and all("|action=" in key for key in experience_keys)
        and result.get("step_trace") == same.get("step_trace")
        and actions != different_actions
        and boundary.get("instinct_random_walk_enabled") is True
        and boundary.get("round_1_only") is True
        and boundary.get("prior_experience_loaded") is False
        and boundary.get("experience_influence_enabled") is False
        and boundary.get("reward_bias_enabled") is False
        and boundary.get("dopamine_like_signal_enabled") is False
        and boundary.get("two_round_comparison_enabled") is False
        and boundary.get("simulated_vision_only") is True
        and boundary.get("larger_static_sandbox_used") is True
        and boundary.get("structured_symbols_only") is True
        and boundary.get("llm_planning_used") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("route_planner_added") is False
        and boundary.get("full_map_visible_to_agent") is False
        and boundary.get("autonomous_action_loop_enabled") is False
        and boundary.get("item_collection_enabled") is False
        and boundary.get("lesson_store_write") is False
        and boundary.get("memory_layer_write") is False
        and boundary.get("long_term_memory_write") is False
    )
    return _result(
        "instinct_random_walk_runner",
        passed,
        {
            "actions": actions,
            "different_actions": different_actions,
            "metrics": metrics,
            "experience_summary": experience_summary,
            "boundary": boundary,
        },
    )


def smoke_wall_experience_influence() -> dict:
    result = run_wall_experience_influence_check(seed=1, max_steps=20)
    control = result.get("control_result", {})
    influence = result.get("influence_result", {})
    store_summary = result.get("experience_store_summary", {})
    summary = result.get("summary", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("command") == "run-wall-experience-influence-check"
        and result.get("flow") == "wall_experience_influence_v0"
        and result.get("status") == "ok"
        and result.get("level_id") == "simulated_vision_larger_sandbox_v0"
        and control.get("front_symbol") == "w"
        and control.get("candidate_action") == "move_forward"
        and control.get("selected_action") == "move_forward"
        and control.get("experience_used_for_decision") is False
        and control.get("influence_applied") is False
        and control.get("passed") is True
        and influence.get("prior_experience", {}).get("front_symbol") == "w"
        and influence.get("prior_experience", {}).get("action") == "move_forward"
        and influence.get("prior_experience", {}).get("outcome_type") == "blocked"
        and influence.get("prior_experience", {}).get("failure_reasons") == ["wall_blocked"]
        and influence.get("candidate_action") == "move_forward"
        and influence.get("selected_action") != "move_forward"
        and influence.get("selected_action") == "turn_right"
        and influence.get("matching_experience_found") is True
        and influence.get("experience_used_for_decision") is True
        and influence.get("influence_applied") is True
        and influence.get("influence_type") == "suppress"
        and influence.get("passed") is True
        and store_summary.get("experience_count") == 1
        and store_summary.get("experience_keys") == ["front_symbol=w|action=move_forward"]
        and store_summary.get("wall_blocked_experience_available") is True
        and summary.get("control_passed") is True
        and summary.get("influence_passed") is True
        and summary.get("requires_prior_experience_for_influence") is True
        and summary.get("all_wall_experience_influence_checks_passed") is True
        and boundary.get("wall_experience_influence_enabled") is True
        and boundary.get("requires_prior_experience_for_influence") is True
        and boundary.get("no_experience_control_used") is True
        and boundary.get("item_reward_bias_enabled") is False
        and boundary.get("dopamine_like_signal_enabled") is False
        and boundary.get("item_seeking_enabled") is False
        and boundary.get("two_round_item_comparison_enabled") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("route_planner_added") is False
        and boundary.get("full_map_visible_to_agent") is False
        and boundary.get("long_term_memory_write") is False
    )
    return _result(
        "wall_experience_influence",
        passed,
        {
            "control": control,
            "influence": influence,
            "experience_store_summary": store_summary,
            "summary": summary,
            "boundary": boundary,
        },
    )


def smoke_grounded_action_experience_influence() -> dict:
    result = run_grounded_action_experience_influence_check()
    summary = result.get("summary", {})
    store_summary = result.get("experience_store_summary", {})
    boundary = result.get("boundary_check", {})
    scenarios = {item.get("scenario"): item for item in result.get("scenario_results", [])}
    control = result.get("control_results", [{}])[0]
    wall = scenarios.get("wall", {})
    empty = scenarios.get("empty", {})
    item = scenarios.get("item", {})
    passed = (
        result.get("command") == "run-grounded-action-experience-influence-check"
        and result.get("flow") == "grounded_action_experience_influence_v0"
        and summary.get("scenario_count") == 3
        and summary.get("passed_count") == 3
        and summary.get("failed_count") == 0
        and summary.get("wall_experience_influence_passed") is True
        and summary.get("empty_experience_influence_passed") is True
        and summary.get("item_experience_influence_passed") is True
        and summary.get("no_experience_control_passed") is True
        and summary.get("all_grounded_action_experience_influence_checks_passed") is True
        and wall.get("trial1", {}).get("outcome_type") == "blocked"
        and wall.get("matching_experience_found") is True
        and wall.get("experience_used_for_decision") is True
        and wall.get("selected_action") != "move_forward"
        and wall.get("influence_type") == "suppress"
        and empty.get("trial1", {}).get("outcome_type") == "moved"
        and empty.get("selected_action") == "move_forward"
        and empty.get("influence_type") == "allow"
        and item.get("trial1", {}).get("outcome_type") == "item_contact"
        and item.get("selected_action") == "move_forward"
        and item.get("influence_type") == "allow_contact"
        and control.get("selected_action") == "move_forward"
        and control.get("experience_used_for_decision") is False
        and control.get("influence_applied") is False
        and control.get("passed") is True
        and store_summary.get("experience_count") == 3
        and store_summary.get("wall_experience_available") is True
        and store_summary.get("empty_experience_available") is True
        and store_summary.get("item_experience_available") is True
        and boundary.get("grounded_action_experience_influence_enabled") is True
        and boundary.get("first_person_viewport") is True
        and boundary.get("agent_viewport_position") == [2, 1]
        and boundary.get("front_symbol_position") == [1, 1]
        and boundary.get("centered_top_down_viewport") is False
        and boundary.get("requires_prior_experience_for_influence") is True
        and boundary.get("no_experience_control_used") is True
        and boundary.get("action_selection_modified_in_this_runner_only") is True
        and boundary.get("existing_navigation_action_selection_modified") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("llm_vision_used") is False
        and boundary.get("long_term_memory_write") is False
    )
    return _result(
        "grounded_action_experience_influence",
        passed,
        {
            "summary": summary,
            "experience_store_summary": store_summary,
            "control": control,
            "boundary": boundary,
        },
    )


def smoke_item_reward_event() -> dict:
    result = run_item_reward_event_check()
    scenario = result.get("scenario_result", {})
    event = result.get("reward_event", {})
    summary = result.get("reward_summary", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("command") == "run-item-reward-event-check"
        and result.get("flow") == "item_reward_event_v0"
        and result.get("status") == "ok"
        and result.get("level_id") == "simulated_vision_larger_sandbox_v0"
        and scenario.get("scenario") == "item_contact_reward"
        and scenario.get("front_symbol") == "i"
        and scenario.get("action") == "move_forward"
        and scenario.get("actual_outcome") == "item_contact"
        and "item_contact" in scenario.get("effect_tags", [])
        and event.get("source") == "grounded_action_experience"
        and event.get("trigger") == "item_contact"
        and event.get("front_symbol") == "i"
        and event.get("action") == "move_forward"
        and event.get("outcome_type") == "item_contact"
        and event.get("reward_type") == "item_contact_reward"
        and event.get("reward_value") == 1.0
        and event.get("dopamine_like_signal") is True
        and event.get("non_subjective") is True
        and summary.get("reward_event_created") is True
        and summary.get("reward_event_count") == 1
        and summary.get("item_contact_reward_count") == 1
        and summary.get("dopamine_like_signal_count") == 1
        and summary.get("total_reward_value") == 1.0
        and summary.get("non_subjective_reward_events") == 1
        and boundary.get("item_reward_event_enabled") is True
        and boundary.get("dopamine_like_signal_enabled") is True
        and boundary.get("reward_bias_enabled") is False
        and boundary.get("item_seeking_enabled") is False
        and boundary.get("reward_used_for_action_selection") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("route_planner_added") is False
        and boundary.get("item_collection_enabled") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("pleasure_claimed") is False
        and boundary.get("desire_claimed") is False
        and boundary.get("consciousness_claimed") is False
        and boundary.get("subjective_experience_claimed") is False
    )
    return _result(
        "item_reward_event",
        passed,
        {
            "scenario": scenario,
            "reward_event": event,
            "summary": summary,
            "boundary": boundary,
        },
    )


def smoke_reward_biased_action_tendency() -> dict:
    result = run_reward_biased_action_tendency_check()
    control = result.get("control_result", {})
    reward_bias = result.get("reward_bias_result", {})
    store_summary = result.get("reward_store_summary", {})
    summary = result.get("summary", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("command") == "run-reward-biased-action-tendency-check"
        and result.get("flow") == "reward_biased_action_tendency_v0"
        and result.get("status") == "ok"
        and result.get("level_id") == "simulated_vision_larger_sandbox_v0"
        and control.get("scenario") == "no_reward_control"
        and control.get("front_symbol") == "i"
        and control.get("candidate_action") == "move_forward"
        and control.get("matching_reward_event_found") is False
        and control.get("reward_bias_applied") is False
        and control.get("reward_used_for_decision") is False
        and control.get("reward_bias_delta") == 0.0
        and control.get("passed") is True
        and reward_bias.get("scenario") == "with_item_reward"
        and reward_bias.get("trial1_reward_event", {}).get("reward_type") == "item_contact_reward"
        and reward_bias.get("front_symbol") == "i"
        and reward_bias.get("candidate_action") == "move_forward"
        and reward_bias.get("matching_reward_event_found") is True
        and reward_bias.get("reward_bias_applied") is True
        and reward_bias.get("reward_used_for_decision") is True
        and reward_bias.get("selected_action") == "move_forward"
        and reward_bias.get("reward_bias_delta") > 0.0
        and reward_bias.get("final_action_score") > reward_bias.get("base_action_score")
        and reward_bias.get("passed") is True
        and store_summary.get("reward_event_count") == 1
        and store_summary.get("item_contact_reward_available") is True
        and store_summary.get("dopamine_like_signal_count") == 1
        and summary.get("control_passed") is True
        and summary.get("reward_bias_passed") is True
        and summary.get("requires_prior_reward_for_bias") is True
        and summary.get("all_reward_biased_action_tendency_checks_passed") is True
        and boundary.get("reward_biased_action_tendency_enabled") is True
        and boundary.get("requires_prior_reward_for_bias") is True
        and boundary.get("no_reward_control_used") is True
        and boundary.get("item_reward_event_enabled") is True
        and boundary.get("dopamine_like_signal_enabled") is True
        and boundary.get("item_seeking_enabled") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("route_planner_added") is False
        and boundary.get("observed_map_route_use") is False
        and boundary.get("item_collection_enabled") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("pleasure_claimed") is False
        and boundary.get("desire_claimed") is False
        and boundary.get("consciousness_claimed") is False
    )
    return _result(
        "reward_biased_action_tendency",
        passed,
        {
            "control": control,
            "reward_bias": reward_bias,
            "store_summary": store_summary,
            "summary": summary,
            "boundary": boundary,
        },
    )


def smoke_reward_biased_random_walk_check() -> dict:
    result = run_reward_biased_random_walk_check(seed=1, trials=20)
    no_reward = result.get("no_reward_result", {})
    with_reward = result.get("with_reward_result", {})
    comparison = result.get("comparison", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("command") == "run-reward-biased-random-walk-check"
        and result.get("flow") == "reward_biased_random_walk_check_v0"
        and result.get("status") == "ok"
        and result.get("level_id") == "simulated_vision_larger_sandbox_v0"
        and result.get("seed") == 1
        and result.get("trials") == 20
        and no_reward.get("front_symbol") == "i"
        and no_reward.get("reward_store_empty") is True
        and no_reward.get("reward_bias_applied") is False
        and no_reward.get("move_forward_score") == 1.0
        and sum(no_reward.get("selected_action_counts", {}).values()) == 20
        and with_reward.get("front_symbol") == "i"
        and with_reward.get("reward_event_count") == 1
        and with_reward.get("matching_reward_event_found") is True
        and with_reward.get("reward_bias_applied") is True
        and with_reward.get("reward_bias_delta") == 0.5
        and with_reward.get("move_forward_score") > no_reward.get("move_forward_score")
        and with_reward.get("move_forward_selected_count") >= no_reward.get("move_forward_selected_count")
        and comparison.get("move_forward_score_delta") == 0.5
        and comparison.get("move_forward_selected_count_delta") >= 0
        and comparison.get("with_reward_score_higher") is True
        and comparison.get("with_reward_selection_not_lower") is True
        and comparison.get("reward_bias_effect_observed") is True
        and boundary.get("reward_biased_random_walk_check_enabled") is True
        and boundary.get("controlled_front_symbol_item_scenario") is True
        and boundary.get("whole_map_random_walk_improvement_claimed") is False
        and boundary.get("item_reward_event_enabled") is True
        and boundary.get("reward_biased_action_tendency_enabled") is True
        and boundary.get("requires_prior_reward_for_bias") is True
        and boundary.get("no_reward_control_used") is True
        and boundary.get("item_seeking_enabled") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("route_planner_added") is False
        and boundary.get("observed_map_route_use") is False
        and boundary.get("random_walk_base_behavior_modified") is False
        and boundary.get("action_selection_modified_in_this_check_only") is True
        and boundary.get("existing_navigation_action_selection_modified") is False
        and boundary.get("item_collection_enabled") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("pleasure_claimed") is False
        and boundary.get("desire_claimed") is False
        and boundary.get("consciousness_claimed") is False
        and boundary.get("subjective_experience_claimed") is False
    )
    return _result(
        "reward_biased_random_walk_check",
        passed,
        {
            "no_reward": no_reward,
            "with_reward": with_reward,
            "comparison": comparison,
            "boundary": boundary,
        },
    )


def smoke_two_round_instinct_reward_comparison() -> dict:
    result = run_two_round_instinct_reward_comparison(seed=1, trials=20)
    round1 = result.get("round1", {})
    round2 = result.get("round2", {})
    wall_control = round1.get("wall_control", {})
    item_control = round1.get("item_control", {})
    wall_with_experience = round2.get("wall_with_experience", {})
    item_with_reward = round2.get("item_with_reward", {})
    comparison = result.get("comparison", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("command") == "run-two-round-instinct-reward-comparison"
        and result.get("flow") == "two_round_instinct_reward_comparison_v0"
        and result.get("status") == "ok"
        and result.get("level_id") == "simulated_vision_larger_sandbox_v0"
        and result.get("seed") == 1
        and result.get("trials") == 20
        and wall_control.get("front_symbol") == "w"
        and wall_control.get("candidate_action") == "move_forward"
        and wall_control.get("selected_action") == "move_forward"
        and wall_control.get("experience_used_for_decision") is False
        and wall_control.get("influence_applied") is False
        and wall_with_experience.get("carried_wall_experience") is True
        and wall_with_experience.get("front_symbol") == "w"
        and wall_with_experience.get("selected_action") != "move_forward"
        and wall_with_experience.get("experience_used_for_decision") is True
        and wall_with_experience.get("influence_applied") is True
        and wall_with_experience.get("influence_type") == "suppress"
        and item_control.get("front_symbol") == "i"
        and item_control.get("candidate_action") == "move_forward"
        and item_control.get("reward_bias_applied") is False
        and item_control.get("move_forward_score") == 1.0
        and item_with_reward.get("carried_item_reward") is True
        and item_with_reward.get("front_symbol") == "i"
        and item_with_reward.get("reward_bias_applied") is True
        and item_with_reward.get("reward_used_for_decision") is True
        and item_with_reward.get("move_forward_score") > item_control.get("move_forward_score")
        and item_with_reward.get("move_forward_selected_count") >= item_control.get("move_forward_selected_count")
        and comparison.get("wall_round2_improved") is True
        and comparison.get("item_round2_bias_improved") is True
        and comparison.get("move_forward_score_delta_for_i") == 0.5
        and comparison.get("move_forward_selected_count_delta_for_i") >= 0
        and comparison.get("round2_uses_carried_experience") is True
        and comparison.get("round2_uses_carried_reward") is True
        and comparison.get("all_two_round_checks_passed") is True
        and boundary.get("two_round_instinct_reward_comparison_enabled") is True
        and boundary.get("controlled_immediate_tendency_comparison") is True
        and boundary.get("whole_map_item_seeking_claimed") is False
        and boundary.get("whole_map_random_walk_improvement_claimed") is False
        and boundary.get("wall_experience_influence_enabled") is True
        and boundary.get("item_reward_event_enabled") is True
        and boundary.get("reward_biased_action_tendency_enabled") is True
        and boundary.get("reward_biased_random_walk_check_enabled") is True
        and boundary.get("requires_prior_wall_experience_for_wall_influence") is True
        and boundary.get("requires_prior_reward_for_item_bias") is True
        and boundary.get("item_seeking_enabled") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("route_planner_added") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("pleasure_claimed") is False
        and boundary.get("desire_claimed") is False
        and boundary.get("consciousness_claimed") is False
        and boundary.get("subjective_experience_claimed") is False
    )
    return _result(
        "two_round_instinct_reward_comparison",
        passed,
        {
            "round1": round1,
            "round2": round2,
            "comparison": comparison,
            "boundary": boundary,
        },
    )


def smoke_failure_reason_classifier() -> dict:
    result = run_failure_reason_classifier_check()
    classification_results = result.get("classification_results", [])
    summary = result.get("summary", {})
    boundary = result.get("boundary_check", {})
    reasons = {
        item.get("case_name"): item.get("classification", {}).get("primary_reason")
        for item in classification_results
    }
    passed = (
        result.get("command") == "run-failure-reason-classifier-check"
        and result.get("flow") == "failure_reason_classifier_v0"
        and result.get("status") == "ok"
        and reasons.get("wall_blocked") == "front_cell_wall"
        and reasons.get("empty_moved") == "front_cell_empty_walkable"
        and reasons.get("item_contact") == "front_cell_item_contact"
        and reasons.get("passage_crossed") == "front_cell_passage_crossed"
        and reasons.get("exit_contact") == "front_cell_exit_contact"
        and reasons.get("turn_right") == "turn_action_orientation_change"
        and reasons.get("look") == "look_action_observation_only"
        and reasons.get("unknown") == "unknown_outcome_reason"
        and summary.get("case_count") == 8
        and summary.get("passed_count") == 8
        and summary.get("failed_count") == 0
        and summary.get("known_reason_count") == 7
        and summary.get("unknown_reason_count") == 1
        and summary.get("all_failure_reason_classifier_checks_passed") is True
        and boundary.get("failure_reason_classifier_enabled") is True
        and boundary.get("experience_abstraction_layer_started") is True
        and boundary.get("deterministic_rules_only") is True
        and boundary.get("action_selection_modified") is False
        and boundary.get("prediction_enabled") is False
        and boundary.get("similar_context_matching_enabled") is False
        and boundary.get("rule_learning_enabled") is False
        and boundary.get("rule_revision_enabled") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("llm_reasoning_used") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("general_learning_claimed") is False
    )
    return _result(
        "failure_reason_classifier",
        passed,
        {
            "reasons": reasons,
            "summary": summary,
            "boundary": boundary,
        },
    )


def smoke_similar_context_key() -> dict:
    result = run_similar_context_key_check()
    key_results = result.get("key_results", [])
    comparison = result.get("comparison_results", {})
    summary = result.get("summary", {})
    boundary = result.get("boundary_check", {})
    keys = {item.get("case_name"): item.get("similar_context_key") for item in key_results}
    passed = (
        result.get("command") == "run-similar-context-key-check"
        and result.get("flow") == "similar_context_key_v0"
        and result.get("status") == "ok"
        and keys.get("wall_position_a") == keys.get("wall_position_b")
        and keys.get("wall_position_a") == "front_symbol=w|action=move_forward|primary_reason=front_cell_wall"
        and keys.get("wall_position_a") != keys.get("empty_moved")
        and keys.get("item_contact") != keys.get("unknown")
        and keys.get("turn_right")
        == "front_symbol=null|action=turn_right|primary_reason=turn_action_orientation_change"
        and keys.get("look") == "front_symbol=null|action=look|primary_reason=look_action_observation_only"
        and keys.get("unknown") == "front_symbol=null|action=move_forward|primary_reason=unknown_outcome_reason"
        and comparison.get("same_structure_different_position_match") is True
        and comparison.get("different_front_symbol_differs") is True
        and comparison.get("different_reason_differs") is True
        and comparison.get("turn_key_stable") is True
        and comparison.get("look_key_stable") is True
        and comparison.get("unknown_key_stable") is True
        and summary.get("case_count") == 9
        and summary.get("passed_count") == 9
        and summary.get("failed_count") == 0
        and summary.get("position_independent_match_count") == 1
        and summary.get("different_context_diff_count") == 2
        and summary.get("unknown_key_count") == 1
        and summary.get("all_similar_context_key_checks_passed") is True
        and boundary.get("similar_context_key_enabled") is True
        and boundary.get("position_independent_by_default") is True
        and boundary.get("deterministic_rules_only") is True
        and boundary.get("failure_reason_classifier_required") is True
        and boundary.get("prediction_enabled") is False
        and boundary.get("rule_learning_enabled") is False
        and boundary.get("rule_revision_enabled") is False
        and boundary.get("action_selection_modified") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("llm_reasoning_used") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("general_learning_claimed") is False
    )
    return _result(
        "similar_context_key",
        passed,
        {
            "keys": keys,
            "comparison": comparison,
            "summary": summary,
            "boundary": boundary,
        },
    )


def smoke_action_outcome_predictor() -> dict:
    result = run_action_outcome_predictor_check()
    prediction_results = result.get("prediction_results", [])
    predictions = {item.get("case_name"): item.get("prediction", {}) for item in prediction_results}
    summary = result.get("summary", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("command") == "run-action-outcome-predictor-check"
        and result.get("flow") == "action_outcome_predictor_v0"
        and result.get("status") == "ok"
        and predictions.get("wall_prediction", {}).get("predicted_outcome_type") == "blocked"
        and predictions.get("wall_prediction", {}).get("predicted_primary_reason") == "front_cell_wall"
        and predictions.get("wall_position_transfer_prediction", {}).get("predicted_outcome_type") == "blocked"
        and predictions.get("wall_position_transfer_prediction", {}).get("predicted_primary_reason")
        == "front_cell_wall"
        and predictions.get("empty_prediction", {}).get("predicted_outcome_type") == "moved"
        and predictions.get("empty_prediction", {}).get("predicted_primary_reason") == "front_cell_empty_walkable"
        and predictions.get("item_prediction", {}).get("predicted_outcome_type") == "item_contact"
        and predictions.get("item_prediction", {}).get("predicted_primary_reason") == "front_cell_item_contact"
        and predictions.get("passage_prediction", {}).get("predicted_outcome_type") == "moved"
        and predictions.get("passage_prediction", {}).get("predicted_primary_reason")
        == "front_cell_passage_crossed"
        and predictions.get("exit_prediction", {}).get("predicted_outcome_type") == "exit_contact"
        and predictions.get("exit_prediction", {}).get("predicted_primary_reason") == "front_cell_exit_contact"
        and predictions.get("unknown_prediction", {}).get("predicted_outcome_type") == "unknown"
        and predictions.get("unknown_prediction", {}).get("unknown_prediction") is True
        and predictions.get("unknown_prediction", {}).get("confidence") == 0.0
        and summary.get("case_count") == 7
        and summary.get("passed_count") == 7
        and summary.get("failed_count") == 0
        and summary.get("known_prediction_count") == 6
        and summary.get("unknown_prediction_count") == 1
        and summary.get("position_transfer_prediction_passed") is True
        and summary.get("all_action_outcome_predictor_checks_passed") is True
        and boundary.get("action_outcome_predictor_enabled") is True
        and boundary.get("uses_failure_reason_classifier") is True
        and boundary.get("uses_similar_context_key") is True
        and boundary.get("position_independent_prediction") is True
        and boundary.get("action_selection_modified") is False
        and boundary.get("prediction_used_for_action_selection") is False
        and boundary.get("rule_learning_enabled") is False
        and boundary.get("rule_revision_enabled") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("llm_reasoning_used") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("general_learning_claimed") is False
    )
    return _result(
        "action_outcome_predictor",
        passed,
        {
            "predictions": predictions,
            "summary": summary,
            "boundary": boundary,
        },
    )


def smoke_prediction_accuracy_check() -> dict:
    result = run_prediction_accuracy_check()
    checks = {item.get("case_name"): item.get("prediction_check", {}) for item in result.get("check_results", [])}
    summary = result.get("summary", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("command") == "run-prediction-accuracy-check"
        and result.get("flow") == "prediction_accuracy_check_v0"
        and result.get("status") == "ok"
        and checks.get("wall_prediction_match", {}).get("prediction_match") is True
        and checks.get("wall_position_transfer_match", {}).get("prediction_match") is True
        and checks.get("item_prediction_match", {}).get("prediction_match") is True
        and checks.get("outcome_mismatch", {}).get("mismatch_type") == "outcome_mismatch"
        and checks.get("reason_mismatch", {}).get("mismatch_type") == "reason_mismatch"
        and checks.get("unknown_prediction", {}).get("mismatch_type") == "unknown_prediction"
        and summary.get("case_count") == 6
        and summary.get("passed_count") == 6
        and summary.get("failed_count") == 0
        and summary.get("prediction_match_count") == 3
        and summary.get("prediction_mismatch_count") == 3
        and summary.get("unknown_prediction_count") == 1
        and summary.get("outcome_mismatch_count") == 1
        and summary.get("reason_mismatch_count") == 1
        and summary.get("position_transfer_match_passed") is True
        and summary.get("all_prediction_accuracy_checks_passed") is True
        and boundary.get("prediction_accuracy_check_enabled") is True
        and boundary.get("uses_action_outcome_predictor") is True
        and boundary.get("position_independent_prediction_checked") is True
        and boundary.get("prediction_used_for_action_selection") is False
        and boundary.get("action_selection_modified") is False
        and boundary.get("rule_learning_enabled") is False
        and boundary.get("rule_revision_enabled") is False
        and boundary.get("mismatch_recorded_only") is True
        and boundary.get("pathfinding_used") is False
        and boundary.get("llm_reasoning_used") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("general_learning_claimed") is False
    )
    return _result(
        "prediction_accuracy_check",
        passed,
        {
            "checks": checks,
            "summary": summary,
            "boundary": boundary,
        },
    )


def smoke_rule_candidate_from_mismatch() -> dict:
    result = run_rule_candidate_from_mismatch_check()
    candidates = {item.get("case_name"): item.get("candidate", {}) for item in result.get("candidate_results", [])}
    summary = result.get("summary", {})
    boundary = result.get("boundary_check", {})
    created = [
        candidate
        for candidate in candidates.values()
        if candidate.get("candidate_created") is True
    ]
    passed = (
        result.get("command") == "run-rule-candidate-from-mismatch-check"
        and result.get("flow") == "rule_candidate_from_mismatch_v0"
        and result.get("status") == "ok"
        and candidates.get("match_no_candidate", {}).get("candidate_created") is False
        and candidates.get("match_no_candidate", {}).get("candidate_type") == "no_candidate_for_match"
        and candidates.get("outcome_mismatch_candidate", {}).get("candidate_type")
        == "outcome_rule_revision_candidate"
        and candidates.get("reason_mismatch_candidate", {}).get("candidate_type")
        == "reason_rule_revision_candidate"
        and candidates.get("unknown_prediction_candidate", {}).get("candidate_type")
        == "unknown_context_rule_candidate"
        and all(candidate.get("requires_review") is True for candidate in created)
        and all(candidate.get("candidate_status") == "proposed" for candidate in created)
        and summary.get("case_count") == 4
        and summary.get("passed_count") == 4
        and summary.get("failed_count") == 0
        and summary.get("candidate_created_count") == 3
        and summary.get("no_candidate_count") == 1
        and summary.get("outcome_revision_candidate_count") == 1
        and summary.get("reason_revision_candidate_count") == 1
        and summary.get("unknown_context_candidate_count") == 1
        and summary.get("all_rule_candidate_from_mismatch_checks_passed") is True
        and boundary.get("rule_candidate_from_mismatch_enabled") is True
        and boundary.get("candidate_creation_only") is True
        and boundary.get("requires_review") is True
        and boundary.get("rule_learning_enabled") is False
        and boundary.get("rule_revision_enabled") is False
        and boundary.get("rule_application_enabled") is False
        and boundary.get("candidate_auto_approved") is False
        and boundary.get("action_selection_modified") is False
        and boundary.get("lesson_store_write") is False
        and boundary.get("memory_layer_write") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("llm_reasoning_used") is False
        and boundary.get("general_learning_claimed") is False
    )
    return _result(
        "rule_candidate_from_mismatch",
        passed,
        {
            "candidates": candidates,
            "summary": summary,
            "boundary": boundary,
        },
    )


def smoke_rule_candidate_review_gate() -> dict:
    result = run_rule_candidate_review_gate_check()
    reviews = {item.get("case_name"): item for item in result.get("review_results", [])}
    summary = result.get("summary", {})
    boundary = result.get("boundary_check", {})
    self_block = reviews.get("non_human_self_approval_blocked", {})
    self_result = self_block.get("review_result", {})
    passed = (
        result.get("command") == "run-rule-candidate-review-gate-check"
        and result.get("flow") == "rule_candidate_review_gate_v0"
        and result.get("status") == "ok"
        and reviews.get("enter_pending_review", {}).get("candidate_after", {}).get("candidate_status") == "pending_review"
        and reviews.get("approve_candidate", {}).get("candidate_after", {}).get("candidate_status") == "approved"
        and reviews.get("reject_candidate", {}).get("candidate_after", {}).get("candidate_status") == "rejected"
        and reviews.get("defer_candidate", {}).get("candidate_after", {}).get("candidate_status") == "deferred"
        and self_result.get("review_allowed") is False
        and self_result.get("applied") is False
        and self_block.get("candidate_after", {}).get("candidate_status") != "approved"
        and all(item.get("review_result", {}).get("applied") is False for item in reviews.values())
        and summary.get("case_count") == 5
        and summary.get("passed_count") == 5
        and summary.get("failed_count") == 0
        and summary.get("pending_review_count") == 2
        and summary.get("approved_count") == 1
        and summary.get("rejected_count") == 1
        and summary.get("deferred_count") == 1
        and summary.get("self_approval_blocked_count") == 1
        and summary.get("all_rule_candidate_review_gate_checks_passed") is True
        and boundary.get("rule_candidate_review_gate_enabled") is True
        and boundary.get("human_reviewer_required") is True
        and boundary.get("qingyin_self_approval_allowed") is False
        and boundary.get("candidate_review_only") is True
        and boundary.get("candidate_application_enabled") is False
        and boundary.get("rule_learning_enabled") is False
        and boundary.get("rule_revision_enabled") is False
        and boundary.get("rule_application_enabled") is False
        and boundary.get("predictor_rule_modified") is False
        and boundary.get("action_selection_modified") is False
        and boundary.get("lesson_store_write") is False
        and boundary.get("memory_layer_write") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("llm_reasoning_used") is False
        and boundary.get("general_learning_claimed") is False
    )
    return _result(
        "rule_candidate_review_gate",
        passed,
        {
            "reviews": reviews,
            "summary": summary,
            "boundary": boundary,
        },
    )


def smoke_approved_candidate_preview() -> dict:
    result = run_approved_candidate_preview_check()
    previews = {item.get("case_name"): item.get("preview", {}) for item in result.get("preview_results", [])}
    summary = result.get("summary", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("command") == "run-approved-candidate-preview-check"
        and result.get("flow") == "approved_candidate_preview_v0"
        and result.get("status") == "ok"
        and previews.get("approved_outcome_revision_preview", {}).get("preview_created") is True
        and "predicted_outcome_type" in previews.get("approved_outcome_revision_preview", {}).get("changed_fields", [])
        and "predicted_primary_reason" in previews.get("approved_outcome_revision_preview", {}).get("changed_fields", [])
        and previews.get("approved_reason_revision_preview", {}).get("preview_created") is True
        and "predicted_primary_reason" in previews.get("approved_reason_revision_preview", {}).get("changed_fields", [])
        and previews.get("approved_unknown_context_preview", {}).get("preview_type") == "new_prediction_entry_preview"
        and "new_prediction_entry" in previews.get("approved_unknown_context_preview", {}).get("changed_fields", [])
        and previews.get("pending_candidate_preview_blocked", {}).get("preview_created") is False
        and previews.get("pending_candidate_preview_blocked", {}).get("preview_blocked_reason") == "candidate_not_approved"
        and previews.get("rejected_candidate_preview_blocked", {}).get("preview_created") is False
        and previews.get("rejected_candidate_preview_blocked", {}).get("preview_blocked_reason") == "candidate_not_approved"
        and all(preview.get("applied_now") is False for preview in previews.values())
        and all(preview.get("predictor_modified_now") is False for preview in previews.values())
        and summary.get("case_count") == 5
        and summary.get("passed_count") == 5
        and summary.get("failed_count") == 0
        and summary.get("preview_created_count") == 3
        and summary.get("preview_blocked_count") == 2
        and summary.get("approved_preview_count") == 3
        and summary.get("applied_now_count") == 0
        and summary.get("predictor_modified_now_count") == 0
        and summary.get("all_approved_candidate_preview_checks_passed") is True
        and boundary.get("approved_candidate_preview_enabled") is True
        and boundary.get("requires_approved_candidate") is True
        and boundary.get("preview_only") is True
        and boundary.get("application_step_enabled") is False
        and boundary.get("candidate_application_enabled") is False
        and boundary.get("predictor_rule_modified") is False
        and boundary.get("action_selection_modified") is False
        and boundary.get("rule_learning_enabled") is False
        and boundary.get("rule_revision_enabled") is False
        and boundary.get("rule_application_enabled") is False
        and boundary.get("lesson_store_write") is False
        and boundary.get("memory_layer_write") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("llm_reasoning_used") is False
        and boundary.get("general_learning_claimed") is False
    )
    return _result(
        "approved_candidate_preview",
        passed,
        {
            "previews": previews,
            "summary": summary,
            "boundary": boundary,
        },
    )


def smoke_reviewed_candidate_apply_verification() -> dict:
    result = run_reviewed_candidate_apply_verification_check()
    applications = {
        item.get("case_name"): item
        for item in result.get("application_results", [])
    }
    summary = result.get("summary", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("command") == "run-reviewed-candidate-apply-verification-check"
        and result.get("flow") == "reviewed_candidate_apply_verification_v0"
        and result.get("status") == "ok"
        and applications.get("approved_outcome_revision_apply", {}).get("application_result", {}).get("applied_in_memory") is True
        and applications.get("approved_outcome_revision_apply", {}).get("prediction_after_apply", {}).get("predicted_outcome_type") == "blocked"
        and applications.get("approved_outcome_revision_apply", {}).get("prediction_after_apply", {}).get("predicted_primary_reason") == "front_cell_wall"
        and applications.get("approved_reason_revision_apply", {}).get("application_result", {}).get("applied_in_memory") is True
        and applications.get("approved_reason_revision_apply", {}).get("prediction_after_apply", {}).get("predicted_outcome_type") == "moved"
        and applications.get("approved_reason_revision_apply", {}).get("prediction_after_apply", {}).get("predicted_primary_reason") == "front_cell_passage_crossed"
        and applications.get("approved_unknown_context_apply", {}).get("application_result", {}).get("applied_in_memory") is True
        and applications.get("approved_unknown_context_apply", {}).get("application_result", {}).get("rule_table_changed") is True
        and applications.get("pending_candidate_blocked", {}).get("application_result", {}).get("applied_in_memory") is False
        and applications.get("pending_candidate_blocked", {}).get("application_result", {}).get("application_blocked_reason") == "candidate_not_approved"
        and applications.get("rejected_candidate_blocked", {}).get("application_result", {}).get("applied_in_memory") is False
        and applications.get("rejected_candidate_blocked", {}).get("application_result", {}).get("application_blocked_reason") == "candidate_not_approved"
        and applications.get("self_approved_candidate_blocked", {}).get("application_result", {}).get("applied_in_memory") is False
        and applications.get("self_approved_candidate_blocked", {}).get("application_result", {}).get("application_blocked_reason") == "invalid_reviewer"
        and all(item.get("verification", {}).get("verification_passed") is True for item in applications.values())
        and summary.get("case_count") == 6
        and summary.get("passed_count") == 6
        and summary.get("failed_count") == 0
        and summary.get("applied_in_memory_count") == 3
        and summary.get("blocked_application_count") == 3
        and summary.get("persistent_write_count") == 0
        and summary.get("predictor_global_modified_count") == 0
        and summary.get("lesson_store_write_count") == 0
        and summary.get("memory_layer_write_count") == 0
        and summary.get("long_term_memory_write_count") == 0
        and summary.get("all_reviewed_candidate_apply_verification_checks_passed") is True
        and boundary.get("reviewed_candidate_apply_verification_enabled") is True
        and boundary.get("requires_approved_candidate") is True
        and boundary.get("requires_human_review") is True
        and boundary.get("temporary_in_memory_rule_table") is True
        and boundary.get("persistent_rule_application_enabled") is False
        and boundary.get("global_predictor_modified") is False
        and boundary.get("predictor_rule_modified_in_memory_only") is True
        and boundary.get("action_selection_modified") is False
        and boundary.get("lesson_store_write") is False
        and boundary.get("memory_layer_write") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("candidate_auto_approved") is False
        and boundary.get("qingyin_self_approval_allowed") is False
        and boundary.get("llm_reasoning_used") is False
        and boundary.get("general_learning_claimed") is False
    )
    return _result(
        "reviewed_candidate_apply_verification",
        passed,
        {
            "applications": applications,
            "summary": summary,
            "boundary": boundary,
        },
    )


def smoke_micro_navigation_goal_reach() -> dict:
    initial_state = build_initial_navigation_state()
    wall_state = build_initial_navigation_state()
    wall_state["agent_pos"] = (1, 1)
    wall_trace = apply_navigation_action(wall_state, "move_left")["trace"]
    moved_trace = apply_navigation_action(initial_state, "move_down")["trace"]
    goal_trace = apply_navigation_action(moved_trace["after"], "move_right")["trace"]
    selected_action = select_navigation_action_toward_goal(
        build_initial_navigation_state(),
        ["move_up", "move_down", "move_right"],
    )
    trial = run_navigation_goal_trial(max_steps=10)
    passed = (
        initial_state["grid"] == ("#####", "#...#", "#.Q.#", "#..G#", "#####")
        and wall_trace["result"] == "wall_blocked"
        and moved_trace["result"] == "moved"
        and goal_trace["result"] == "goal_reached"
        and navigation_distance_to_goal(initial_state["agent_pos"], initial_state["goal_pos"]) == 2
        and selected_action == "move_down"
        and trial["completed_goal"] is True
        and trial["final_agent_pos"] == trial["goal_pos"]
        and trial["step_count"] <= 10
        and all(action in ALLOWED_NAVIGATION_ACTIONS for action in trial["selected_actions"])
        and "lesson_candidate" not in trial
        and "memory_layer_write" not in trial
    )
    return _result(
        "micro_navigation_goal_reach",
        passed,
        {
            "initial_agent_pos": initial_state["agent_pos"],
            "goal_pos": initial_state["goal_pos"],
            "wall_result": wall_trace["result"],
            "moved_result": moved_trace["result"],
            "goal_result": goal_trace["result"],
            "selected_action": selected_action,
            "completed_goal": trial["completed_goal"],
            "step_count": trial["step_count"],
            "selected_actions": trial["selected_actions"],
            "final_agent_pos": trial["final_agent_pos"],
        },
    )


def smoke_micro_navigation_trial_metrics_cli() -> dict:
    result = run_navigation_trial_metrics_cli(runs=4, trial_count=5, max_steps=10)
    boundary = result.get("boundary", {})
    passed = (
        result.get("flow") == "navigation_trial_metrics_cli_v0"
        and result.get("status") == "ok"
        and result.get("runs") == 4
        and result.get("trial_count_per_run") == 5
        and result.get("total_trials") == 20
        and result.get("total_trials") == result.get("runs") * result.get("trial_count_per_run")
        and result.get("total_completed") == 20
        and "overall_success_rate" in result
        and "overall_average_step_count" in result
        and "max_steps_reached_count" in result
        and len(result.get("run_summaries", [])) == 4
        and "human_summary" in result
        and boundary.get("llm_used") is False
        and boundary.get("creates_lesson_candidate") is False
        and boundary.get("writes_lesson_store") is False
        and boundary.get("writes_memory_layer") is False
        and boundary.get("awakening_claim") is False
        and boundary.get("changes_navigation_behavior") is False
    )
    return _result(
        "micro_navigation_trial_metrics_cli",
        passed,
        {
            "runs": result.get("runs"),
            "trial_count_per_run": result.get("trial_count_per_run"),
            "total_trials": result.get("total_trials"),
            "total_completed": result.get("total_completed"),
            "overall_success_rate": result.get("overall_success_rate"),
            "overall_average_step_count": result.get("overall_average_step_count"),
            "max_steps_reached_count": result.get("max_steps_reached_count"),
            "human_summary": result.get("human_summary"),
            "boundary": boundary,
        },
    )


def smoke_micro_navigation_multi_goal_level() -> dict:
    initial_state = build_initial_multi_goal_navigation_state()
    first_goal_distance = navigation_distance_to_goal(initial_state["agent_pos"], initial_state["goal_pos"])
    first_goal_state = initial_state
    first_goal_trace = None
    for action in ("move_down", "move_down", "move_right", "move_right", "move_right", "move_right"):
        action_result = apply_multi_goal_navigation_action(first_goal_state, action)
        first_goal_state = action_result["state"]
        first_goal_trace = action_result["trace"]
    trial = run_navigation_multi_goal_trial(max_steps=20)
    passed = (
        initial_state["grid"] == ("#######", "#Q....#", "#.###.#", "#....G#", "#######")
        and first_goal_distance > 2
        and first_goal_trace is not None
        and first_goal_trace["goal_reached_this_step"] is True
        and first_goal_trace["next_goal_spawned"] is True
        and first_goal_trace["goals_reached"] == 1
        and first_goal_trace["goal_index"] == 1
        and trial["completed_all_goals"] is True
        and trial["goals_reached"] == 2
        and trial["goal_count"] == 2
        and trial["step_count"] > 2
        and all(action in ALLOWED_NAVIGATION_ACTIONS for action in trial["selected_actions"])
        and "lesson_candidate" not in trial
        and "memory_layer_write" not in trial
    )
    return _result(
        "micro_navigation_multi_goal_level",
        passed,
        {
            "initial_agent_pos": initial_state["agent_pos"],
            "first_goal_pos": initial_state["goal_sequence"][0],
            "second_goal_pos": initial_state["goal_sequence"][1],
            "first_goal_distance": first_goal_distance,
            "first_goal_reached": first_goal_trace["goal_reached_this_step"] if first_goal_trace else False,
            "second_goal_spawned": first_goal_trace["next_goal_spawned"] if first_goal_trace else False,
            "completed_all_goals": trial["completed_all_goals"],
            "goals_reached": trial["goals_reached"],
            "goal_count": trial["goal_count"],
            "step_count": trial["step_count"],
            "selected_actions": trial["selected_actions"],
            "final_agent_pos": trial["final_agent_pos"],
            "final_goal_pos": trial["final_goal_pos"],
        },
    )


def smoke_micro_navigation_multi_goal_metrics_cli() -> dict:
    result = run_navigation_multi_goal_metrics_cli(runs=4, trial_count=5, max_steps=20)
    boundary = result.get("boundary", {})
    first_trial_summary = result.get("run_summaries", [{}])[0].get("trial_summaries", [{}])[0]
    passed = (
        result.get("flow") == "navigation_multi_goal_metrics_cli_v0"
        and result.get("status") == "ok"
        and result.get("runs") == 4
        and result.get("trial_count_per_run") == 5
        and result.get("total_trials") == 20
        and result.get("total_trials") == result.get("runs") * result.get("trial_count_per_run")
        and result.get("total_completed") == 20
        and "overall_success_rate" in result
        and "overall_average_step_count" in result
        and "max_steps_reached_count" in result
        and len(result.get("run_summaries", [])) == 4
        and "human_summary" in result
        and first_trial_summary.get("completed_all_goals") is True
        and first_trial_summary.get("goals_reached") == 2
        and first_trial_summary.get("goal_count") == 2
        and boundary.get("llm_used") is False
        and boundary.get("creates_lesson_candidate") is False
        and boundary.get("writes_lesson_store") is False
        and boundary.get("writes_memory_layer") is False
        and boundary.get("awakening_claim") is False
        and boundary.get("changes_navigation_behavior") is False
    )
    return _result(
        "micro_navigation_multi_goal_metrics_cli",
        passed,
        {
            "runs": result.get("runs"),
            "trial_count_per_run": result.get("trial_count_per_run"),
            "total_trials": result.get("total_trials"),
            "total_completed": result.get("total_completed"),
            "overall_success_rate": result.get("overall_success_rate"),
            "overall_average_step_count": result.get("overall_average_step_count"),
            "max_steps_reached_count": result.get("max_steps_reached_count"),
            "human_summary": result.get("human_summary"),
            "first_trial_summary": first_trial_summary,
            "boundary": boundary,
        },
    )


def smoke_navigation_obstacle_wall_detour_level() -> dict:
    initial_state = create_navigation_obstacle_level_state()
    wall_state = create_navigation_obstacle_level_state()
    wall_state["agent_pos"] = (2, 1)
    wall_state["grid"] = ("#######", "#.....#", "#Q###.#", "#....G#", "#######")
    wall_trace = apply_navigation_action(wall_state, "move_right")["trace"]
    trial = run_navigation_obstacle_trial(max_steps=20)
    wall_blocked_avoided = any(step["blocked_candidates"] for step in trial["steps"]) and all(
        step["navigation_result"] != "wall_blocked" for step in trial["steps"]
    )
    passed = (
        initial_state["grid"] == ("#######", "#Q....#", "#.###.#", "#....G#", "#######")
        and wall_trace["result"] == "wall_blocked"
        and trial["completed_goal"] is True
        and trial["step_count"] > 2
        and trial["final_agent_pos"] == trial["goal_pos"]
        and all(action in ALLOWED_NAVIGATION_ACTIONS for action in trial["selected_actions"])
        and wall_blocked_avoided is True
        and "lesson_candidate" not in trial
        and "memory_layer_write" not in trial
    )
    return _result(
        "navigation_obstacle_wall_detour_level",
        passed,
        {
            "initial_agent_pos": initial_state["agent_pos"],
            "goal_pos": initial_state["goal_pos"],
            "wall_result": wall_trace["result"],
            "completed_goal": trial["completed_goal"],
            "step_count": trial["step_count"],
            "selected_actions": trial["selected_actions"],
            "final_agent_pos": trial["final_agent_pos"],
            "wall_blocked_avoided": wall_blocked_avoided,
        },
    )


def smoke_navigation_obstacle_trial_cli() -> dict:
    result = run_navigation_obstacle_trial_cli(max_steps=20)
    boundary = result.get("boundary", {})
    passed = (
        result.get("command") == "run-navigation-obstacle-trial"
        and result.get("flow") == "navigation_obstacle_trial_cli_patch"
        and result.get("status") == "ok"
        and result.get("completed_goal") is True
        and result.get("step_count", 0) > 2
        and bool(result.get("selected_actions"))
        and all(action in ALLOWED_NAVIGATION_ACTIONS for action in result.get("selected_actions", []))
        and result.get("wall_blocked_avoided") is True
        and boundary.get("llm_used") is False
        and boundary.get("creates_lesson_candidate") is False
        and boundary.get("writes_lesson_store") is False
        and boundary.get("writes_memory_layer") is False
        and boundary.get("awakening_claim") is False
        and boundary.get("changes_navigation_behavior") is False
    )
    return _result(
        "navigation_obstacle_trial_cli",
        passed,
        {
            "completed_goal": result.get("completed_goal"),
            "step_count": result.get("step_count"),
            "selected_actions": result.get("selected_actions"),
            "wall_blocked_avoided": result.get("wall_blocked_avoided"),
            "boundary": boundary,
        },
    )


def smoke_approach_box_level() -> dict:
    initial_state = create_navigation_approach_box_level_state()
    move_trace = apply_navigation_approach_box_action(initial_state, "move_down")["trace"]
    trial = run_navigation_approach_box_trial(max_steps=20)
    final_distance_to_box = manhattan_distance_to_box(trial["final_agent_pos"], trial["box_pos"])
    passed = (
        initial_state["grid"] == ("#######", "#Q....#", "#.###.#", "#...B.#", "#######")
        and initial_state["agent_pos"] == (1, 1)
        and initial_state["box_pos"] == (3, 4)
        and "goal_pos" not in initial_state
        and move_trace["trace_type"] == "navigation_approach_box_trace"
        and trial["completed_approach"] is True
        and final_distance_to_box == 1
        and trial["step_count"] > 0
        and all(action in ALLOWED_NAVIGATION_ACTIONS for action in trial["selected_actions"])
        and "lesson_candidate" not in trial
        and "memory_layer_write" not in trial
        and "two_trial_learning_check" not in trial
    )
    return _result(
        "approach_box_level",
        passed,
        {
            "initial_agent_pos": initial_state["agent_pos"],
            "box_pos": initial_state["box_pos"],
            "completed_approach": trial["completed_approach"],
            "final_distance_to_box": final_distance_to_box,
            "step_count": trial["step_count"],
            "selected_actions": trial["selected_actions"],
        },
    )


def smoke_approach_box_trial_cli() -> dict:
    result = run_approach_box_trial_cli(max_steps=10)
    boundary = result.get("boundary", {})
    passed = (
        result.get("command") == "run-approach-box-trial"
        and result.get("flow") == "approach_box_trial_cli_v0"
        and result.get("status") == "ok"
        and result.get("completed_approach") is True
        and result.get("initial_agent_pos") == [1, 1]
        and result.get("box_pos") == [3, 4]
        and result.get("final_agent_pos") == [3, 3]
        and result.get("final_distance_to_box") == 1
        and result.get("step_count") == 4
        and result.get("selected_actions") == ["move_down", "move_down", "move_right", "move_right"]
        and result.get("llm_used") is False
        and boundary.get("llm_used") is False
        and boundary.get("creates_lesson_candidate") is False
        and boundary.get("writes_lesson_store") is False
        and boundary.get("writes_memory_layer") is False
        and boundary.get("changes_navigation_behavior") is False
        and boundary.get("two_trial_learning_check") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("box_pushed") is False
    )
    return _result(
        "approach_box_trial_cli",
        passed,
        {
            "completed_approach": result.get("completed_approach"),
            "final_distance_to_box": result.get("final_distance_to_box"),
            "step_count": result.get("step_count"),
            "selected_actions": result.get("selected_actions"),
            "llm_used": result.get("llm_used"),
            "boundary": boundary,
        },
    )


def smoke_approach_box_two_trial_learning_check() -> dict:
    result = run_approach_box_two_trial_check_cli(max_steps=10)
    trial_1 = result.get("trial_1", {})
    trial_2 = result.get("trial_2", {})
    comparison = result.get("comparison", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("flow") == "approach_box_two_trial_learning_check_v0"
        and trial_1.get("completed_approach") is True
        and trial_2.get("completed_approach") is True
        and trial_1.get("final_distance_to_box") == 1
        and trial_2.get("final_distance_to_box") == 1
        and trial_1.get("local_outcome_memory_written") is True
        and trial_2.get("local_outcome_memory_read") is True
        and trial_2.get("used_trial1_local_memory") is True
        and trial_1.get("llm_used") is False
        and trial_2.get("llm_used") is False
        and comparison.get("trial1_step_count") == 4
        and comparison.get("trial2_step_count") == 4
        and comparison.get("step_count_delta") == 0
        and comparison.get("trial1_failed_or_blocked_actions") == 0
        and comparison.get("trial2_failed_or_blocked_actions") == 0
        and comparison.get("failed_or_blocked_delta") == 0
        and boundary.get("trial2_read_local_outcome_memory_only") is True
        and boundary.get("trial2_replayed_full_route") is False
        and boundary.get("trial2_used_llm") is False
        and boundary.get("trial2_used_lesson_store") is False
        and boundary.get("trial2_used_memory_layer") is False
        and boundary.get("trial2_used_long_term_memory") is False
        and boundary.get("trial2_used_lesson_candidate") is False
        and boundary.get("trial2_used_pathfinding") is False
        and boundary.get("trial2_used_human_hint") is False
        and "steps" not in result
        and "trace" not in result
        and "route" not in result
    )
    return _result(
        "approach_box_two_trial_learning_check",
        passed,
        {
            "trial1_step_count": comparison.get("trial1_step_count"),
            "trial2_step_count": comparison.get("trial2_step_count"),
            "step_count_delta": comparison.get("step_count_delta"),
            "failed_or_blocked_delta": comparison.get("failed_or_blocked_delta"),
            "boundary_check": boundary,
        },
    )


def smoke_approach_box_dead_end_trial() -> dict:
    result = run_approach_box_dead_end_trial_cli(max_steps=100)
    boundary = result.get("boundary", {})
    passed = (
        result.get("flow") == "approach_box_dead_end_trial_v0"
        and result.get("level_id") == "approach_box_dead_end_v0"
        and result.get("completed_approach") is True
        and result.get("initial_agent_pos") == [1, 1]
        and result.get("box_pos") == [4, 4]
        and result.get("approach_positions") == [[3, 4]]
        and [4, 3] not in result.get("approach_positions", [])
        and result.get("final_agent_pos") == [3, 4]
        and result.get("final_distance_to_box") == 1
        and result.get("max_steps") == 100
        and result.get("step_count", 0) > 0
        and result.get("selected_actions")
        and result.get("entered_dead_end_area") is True
        and result.get("dead_end_positions_visited") == [[4, 1], [4, 2]]
        and [4, 3] not in result.get("dead_end_positions_visited", [])
        and result.get("blocked_or_failed_actions")
        and result.get("blocked_or_failed_actions")[0].get("blocked_at") == [4, 3]
        and result.get("llm_used") is False
        and boundary.get("changes_approach_box_runner") is False
        and boundary.get("changes_navigation_sandbox") is False
        and boundary.get("changes_push_box_sandbox") is False
        and boundary.get("two_trial_learning_check") is False
        and boundary.get("changes_action_selection") is False
        and boundary.get("changes_goal_bias") is False
        and boundary.get("changes_state_action_memory") is False
        and boundary.get("uses_penalty_or_stuck_detection") is False
        and boundary.get("pathfinding_used") is False
        and boundary.get("full_route_replay") is False
        and boundary.get("creates_lesson_candidate") is False
        and boundary.get("writes_lesson_store") is False
        and boundary.get("writes_memory_layer") is False
        and boundary.get("proof_of_learning") is False
    )
    return _result(
        "approach_box_dead_end_trial",
        passed,
        {
            "level_id": result.get("level_id"),
            "completed_approach": result.get("completed_approach"),
            "approach_positions": result.get("approach_positions"),
            "entered_dead_end_area": result.get("entered_dead_end_area"),
            "dead_end_positions_visited": result.get("dead_end_positions_visited"),
            "blocked_or_failed_actions": result.get("blocked_or_failed_actions"),
            "step_count": result.get("step_count"),
            "llm_used": result.get("llm_used"),
        },
    )


def smoke_approach_box_dead_end_two_trial_learning_check() -> dict:
    result = run_approach_box_dead_end_two_trial_check_cli(max_steps=100)
    trial_1 = result.get("trial_1", {})
    trial_2 = result.get("trial_2", {})
    comparison = result.get("comparison", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("flow") == "approach_box_dead_end_two_trial_learning_check_v0"
        and trial_1.get("level_id") == "approach_box_dead_end_v0"
        and trial_2.get("level_id") == "approach_box_dead_end_v0"
        and trial_1.get("completed_approach") is True
        and trial_2.get("completed_approach") is True
        and trial_1.get("entered_dead_end_area") is True
        and trial_2.get("entered_dead_end_area") is False
        and trial_1.get("dead_end_positions_visited") == [[4, 1], [4, 2]]
        and trial_2.get("dead_end_positions_visited") == []
        and trial_1.get("blocked_or_failed_actions")
        and trial_2.get("blocked_or_failed_actions") == []
        and trial_1.get("local_outcome_memory_written") is True
        and trial_2.get("local_outcome_memory_read") is True
        and trial_2.get("used_trial1_local_memory") is True
        and trial_2.get("avoided_trial1_dead_end_action") is True
        and trial_1.get("llm_used") is False
        and trial_2.get("llm_used") is False
        and comparison.get("trial1_step_count") == 11
        and comparison.get("trial2_step_count") == 5
        and comparison.get("step_count_delta") == -6
        and comparison.get("dead_end_positions_visited_delta") == -2
        and comparison.get("blocked_or_failed_delta") == -1
        and comparison.get("avoided_trial1_dead_end_action") is True
        and boundary.get("trial2_read_local_outcome_memory_only") is True
        and boundary.get("trial2_replayed_full_route") is False
        and boundary.get("trial2_used_llm") is False
        and boundary.get("trial2_used_lesson_store") is False
        and boundary.get("trial2_used_memory_layer") is False
        and boundary.get("trial2_used_long_term_memory") is False
        and boundary.get("trial2_used_lesson_candidate") is False
        and boundary.get("trial2_used_pathfinding") is False
        and boundary.get("trial2_used_human_hint") is False
        and "steps" not in result
        and "trace" not in result
        and "route" not in result
    )
    return _result(
        "approach_box_dead_end_two_trial_learning_check",
        passed,
        {
            "trial1_step_count": comparison.get("trial1_step_count"),
            "trial2_step_count": comparison.get("trial2_step_count"),
            "step_count_delta": comparison.get("step_count_delta"),
            "dead_end_positions_visited_delta": comparison.get("dead_end_positions_visited_delta"),
            "blocked_or_failed_delta": comparison.get("blocked_or_failed_delta"),
            "avoided_trial1_dead_end_action": comparison.get("avoided_trial1_dead_end_action"),
            "boundary_check": boundary,
        },
    )


def smoke_approach_box_dead_end_memory_control_check() -> dict:
    result = run_approach_box_dead_end_memory_control_check_cli(max_steps=100, runs=3)
    with_memory = result.get("with_memory", {})
    without_memory = result.get("without_memory", {})
    comparison = result.get("comparison", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("flow") == "dead_end_memory_control_check_v0"
        and result.get("level_id") == "approach_box_dead_end_v0"
        and result.get("runs") == 3
        and result.get("max_steps") == 100
        and with_memory.get("run_count") == 3
        and without_memory.get("run_count") == 3
        and len(with_memory.get("trial2_step_counts", [])) == 3
        and len(without_memory.get("trial2_step_counts", [])) == 3
        and "entered_dead_end_count_delta" in comparison
        and "blocked_or_failed_total_delta" in comparison
        and "average_step_count_delta" in comparison
        and "completed_count_delta" in comparison
        and isinstance(comparison.get("memory_effect_observed"), bool)
        and comparison.get("control_group_used") is True
        and boundary.get("with_memory_trial2_read_local_outcome_memory") is True
        and boundary.get("without_memory_trial2_read_local_outcome_memory") is False
        and boundary.get("with_memory_trial2_replayed_full_route") is False
        and boundary.get("without_memory_trial2_replayed_full_route") is False
        and boundary.get("trial2_used_llm") is False
        and boundary.get("trial2_used_lesson_store") is False
        and boundary.get("trial2_used_memory_layer") is False
        and boundary.get("trial2_used_long_term_memory") is False
        and boundary.get("trial2_used_lesson_candidate") is False
        and boundary.get("trial2_used_pathfinding") is False
        and boundary.get("trial2_used_human_hint") is False
        and "steps" not in result
        and "trace" not in result
        and "route" not in result
    )
    return _result(
        "approach_box_dead_end_memory_control_check",
        passed,
        {
            "with_memory": with_memory,
            "without_memory": without_memory,
            "comparison": comparison,
            "boundary_check": boundary,
        },
    )


def smoke_dead_end_memory_control_trial1_source_audit() -> dict:
    result = run_approach_box_dead_end_memory_control_check_cli(max_steps=100, runs=3)
    audit = result.get("trial1_source_audit", {})
    conditioned = result.get("conditioned_on_trial1_dead_end", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("flow") == "dead_end_memory_control_check_v0"
        and "with_memory_trial1_entered_dead_end_count" in audit
        and "with_memory_trial1_blocked_or_failed_total" in audit
        and "with_memory_trial1_local_memory_written_count" in audit
        and "with_memory_trial1_average_step_count" in audit
        and len(audit.get("with_memory_trial1_step_counts", [])) == 3
        and "without_memory_trial1_entered_dead_end_count" in audit
        and "without_memory_trial1_blocked_or_failed_total" in audit
        and "without_memory_trial1_local_memory_written_count" in audit
        and "without_memory_trial1_average_step_count" in audit
        and len(audit.get("without_memory_trial1_step_counts", [])) == 3
        and "with_memory_sample_count" in conditioned
        and "with_memory_trial2_avoided_count" in conditioned
        and "with_memory_trial2_avoid_rate" in conditioned
        and "without_memory_sample_count" in conditioned
        and "without_memory_trial2_avoided_count" in conditioned
        and "without_memory_trial2_avoid_rate" in conditioned
        and isinstance(conditioned.get("conditioned_memory_effect_observed"), bool)
        and boundary.get("trial1_source_audit_present") is True
        and boundary.get("conditioned_analysis_present") is True
        and boundary.get("with_memory_trial2_read_local_outcome_memory") is True
        and boundary.get("without_memory_trial2_read_local_outcome_memory") is False
        and boundary.get("trial2_used_llm") is False
        and boundary.get("trial2_used_pathfinding") is False
    )
    return _result(
        "dead_end_memory_control_trial1_source_audit",
        passed,
        {
            "trial1_source_audit": audit,
            "conditioned_on_trial1_dead_end": conditioned,
            "boundary_check": boundary,
        },
    )


def smoke_dead_end_two_trial_ascii_replay() -> dict:
    result = run_approach_box_dead_end_two_trial_ascii_replay_cli(max_steps=100)
    trial_1 = result.get("trial_1_replay", [])
    trial_2 = result.get("trial_2_replay", [])
    summary = result.get("summary", {})
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("flow") == "dead_end_two_trial_ascii_replay_v0"
        and result.get("command") == "replay-approach-box-dead-end-two-trial"
        and result.get("level_id") == "approach_box_dead_end_v0"
        and "A=agent" in result.get("legend", "")
        and trial_1
        and trial_2
        and trial_1[0].get("step_index") == 0
        and trial_2[0].get("step_index") == 0
        and "########" in trial_1[0].get("grid", "")
        and any(frame.get("entered_dead_end_area") is True for frame in trial_1)
        and any(frame.get("blocked_at") == [4, 3] for frame in trial_1)
        and not any(frame.get("entered_dead_end_area") is True for frame in trial_2)
        and summary.get("trial1_step_count") == 11
        and summary.get("trial2_step_count") == 5
        and summary.get("step_count_delta") == -6
        and summary.get("llm_used") is False
        and boundary.get("replay_only") is True
        and boundary.get("runner_modified") is False
        and boundary.get("action_selection_modified") is False
        and boundary.get("used_llm") is False
        and boundary.get("used_pathfinding") is False
        and boundary.get("used_memory_layer") is False
        and boundary.get("used_lesson_store") is False
        and boundary.get("replayed_full_route_as_input") is False
    )
    return _result(
        "dead_end_two_trial_ascii_replay",
        passed,
        {
            "summary": summary,
            "boundary_check": boundary,
            "first_trial1_frame": trial_1[0] if trial_1 else {},
            "first_trial2_frame": trial_2[0] if trial_2 else {},
        },
    )


def smoke_dead_end_map_trial1_validation() -> dict:
    result = validate_dead_end_trial1_maps_cli(runs_per_map=3, max_steps=100)
    map_results = result.get("map_results", [])
    summary = result.get("overall_summary", {})
    boundary = result.get("boundary_check", {})
    statuses = {item.get("level_id"): item.get("map_status") for item in map_results}
    fixture_loaded = {item.get("level_id"): item.get("fixture_loaded") for item in map_results}
    passed = (
        result.get("flow") == "dead_end_map_trial1_validation_v0"
        and result.get("command") == "validate-dead-end-trial1-maps"
        and result.get("runs_per_map") == 3
        and result.get("max_steps") == 100
        and len(map_results) == 4
        and summary.get("map_count") == 4
        and "recommended_next_step" in summary
        and statuses.get("approach_box_dead_end_v0") == "valid_for_two_trial"
        and "user_maze_dead_end_candidate_v0" in statuses
        and "mid_branch_dead_end_candidate_v0" in statuses
        and "lower_branch_dead_end_candidate_v0" in statuses
        and fixture_loaded.get("user_maze_dead_end_candidate_v0") is True
        and fixture_loaded.get("mid_branch_dead_end_candidate_v0") is True
        and fixture_loaded.get("lower_branch_dead_end_candidate_v0") is True
        and all("level_id" in item for item in map_results)
        and all("fixture_loaded" in item for item in map_results)
        and all("fixture_load_error" in item for item in map_results)
        and all("completed_count" in item for item in map_results)
        and all("entered_dead_end_count" in item for item in map_results)
        and all("blocked_or_failed_total" in item for item in map_results)
        and all("average_step_count" in item for item in map_results)
        and boundary.get("trial1_validation_only") is True
        and boundary.get("two_trial_run") is False
        and boundary.get("memory_control_run") is False
        and boundary.get("replayed_full_route") is False
        and boundary.get("used_llm") is False
        and boundary.get("used_pathfinding") is False
        and boundary.get("used_lesson_store") is False
        and boundary.get("used_memory_layer") is False
        and boundary.get("modified_action_selection") is False
        and boundary.get("modified_goal_bias") is False
        and boundary.get("modified_state_action_memory") is False
        and boundary.get("candidate_fixtures_supported") is True
        and boundary.get("generic_ascii_parser_added") is False
    )
    return _result(
        "dead_end_map_trial1_validation",
        passed,
        {
            "overall_summary": summary,
            "map_statuses": statuses,
            "fixture_loaded": fixture_loaded,
            "boundary_check": boundary,
        },
    )


def smoke_candidate_map_trial1_ascii_replay() -> dict:
    result = run_candidate_dead_end_trial1_ascii_replay_cli(max_steps=100)
    replays = result.get("replays", [])
    level_ids = {replay.get("level_id") for replay in replays}
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("flow") == "candidate_map_trial1_ascii_replay_v0"
        and result.get("command") == "replay-dead-end-trial1-candidate-maps"
        and result.get("map_count") == 4
        and level_ids
        == {
            "approach_box_dead_end_v0",
            "user_maze_dead_end_candidate_v0",
            "mid_branch_dead_end_candidate_v0",
            "lower_branch_dead_end_candidate_v0",
        }
        and all(replay.get("trial_1_frames") for replay in replays)
        and all(replay["trial_1_frames"][0].get("step_index") == 0 for replay in replays)
        and all("grid" in replay["trial_1_frames"][0] for replay in replays)
        and result.get("overall_summary", {}).get("replayed_map_count") == 4
        and boundary.get("trial1_replay_only") is True
        and boundary.get("two_trial_run") is False
        and boundary.get("memory_control_run") is False
        and boundary.get("replay_output_only") is True
        and boundary.get("runner_modified") is False
        and boundary.get("action_selection_modified") is False
        and boundary.get("used_llm") is False
        and boundary.get("used_pathfinding") is False
        and boundary.get("used_lesson_store") is False
        and boundary.get("used_memory_layer") is False
    )
    return _result(
        "candidate_map_trial1_ascii_replay",
        passed,
        {
            "level_ids": sorted(level_ids),
            "overall_summary": result.get("overall_summary", {}),
            "boundary_check": boundary,
        },
    )


def smoke_valid_dead_end_maps_ab_control() -> dict:
    result = run_valid_dead_end_maps_ab_control_cli(runs_per_map=3, max_steps=100)
    included_maps = result.get("included_maps", [])
    excluded_maps = result.get("excluded_maps", [])
    map_results = result.get("map_results", [])
    boundary = result.get("boundary_check", {})
    passed = (
        result.get("flow") == "valid_dead_end_maps_ab_control_v0"
        and result.get("command") == "run-valid-dead-end-maps-ab-control"
        and result.get("runs_per_map") == 3
        and result.get("max_steps") == 100
        and included_maps
        == [
            "approach_box_dead_end_v0",
            "mid_branch_dead_end_candidate_v0",
            "lower_branch_dead_end_candidate_v0",
        ]
        and "user_maze_dead_end_candidate_v0" not in included_maps
        and {
            "level_id": "user_maze_dead_end_candidate_v0",
            "reason": "has_shortcut_no_dead_end_event",
        }
        in excluded_maps
        and len(map_results) == 3
        and all("with_memory" in item for item in map_results)
        and all("without_memory" in item for item in map_results)
        and all("comparison" in item for item in map_results)
        and all("trial1_source_audit" in item for item in map_results)
        and all("conditioned_on_trial1_dead_end" in item for item in map_results)
        and "overall_summary" in result
        and boundary.get("valid_maps_only") is True
        and boundary.get("excluded_shortcut_map") is True
        and boundary.get("with_memory_trial2_reads_local_memory") is True
        and boundary.get("without_memory_trial2_reads_local_memory") is False
        and boundary.get("replayed_full_route") is False
        and boundary.get("used_llm") is False
        and boundary.get("used_pathfinding") is False
        and boundary.get("used_lesson_store") is False
        and boundary.get("used_memory_layer") is False
    )
    return _result(
        "valid_dead_end_maps_ab_control",
        passed,
        {
            "included_maps": included_maps,
            "excluded_maps": excluded_maps,
            "overall_summary": result.get("overall_summary", {}),
            "boundary_check": boundary,
        },
    )


def smoke_local_memory_decision_trace_observer() -> dict:
    result = run_local_memory_decision_trace_observer_cli(
        level_id="approach_box_dead_end_v0",
        max_steps=100,
    )
    trace = result.get("decision_trace", [])
    boundary = result.get("boundary_check", {})
    first_trace = trace[0] if trace else {}
    passed = (
        result.get("flow") == "local_memory_decision_trace_observer_v0"
        and result.get("command") == "observe-local-memory-decision-trace"
        and result.get("level_id") == "approach_box_dead_end_v0"
        and result.get("max_steps") == 100
        and "trial_1_summary" in result
        and "trial_2_summary" in result
        and bool(trace)
        and "step_index" in first_trace
        and "agent_pos" in first_trace
        and "candidate_actions" in first_trace
        and "selected_action" in first_trace
        and "selection_reason" in first_trace
        and "relevant_local_memory" in first_trace
        and "memory_effect_applied" in first_trace
        and "score_breakdown" in first_trace
        and boundary.get("observer_only") is True
        and boundary.get("runner_modified") is False
        and boundary.get("action_selection_modified") is False
        and boundary.get("goal_bias_modified") is False
        and boundary.get("state_action_memory_modified") is False
        and boundary.get("used_llm") is False
        and boundary.get("used_pathfinding") is False
        and boundary.get("used_lesson_store") is False
        and boundary.get("used_memory_layer") is False
        and boundary.get("replayed_full_route_as_input") is False
    )
    return _result(
        "local_memory_decision_trace_observer",
        passed,
        {
            "level_id": result.get("level_id"),
            "trial1_step_count": result.get("trial_1_summary", {}).get("step_count"),
            "trial2_step_count": result.get("trial_2_summary", {}).get("step_count"),
            "decision_trace_count": len(trace),
            "key_observation": result.get("key_observation", {}),
            "boundary_check": boundary,
        },
    )


def smoke_session_working_memory_demo() -> dict:
    result = demo_session_working_memory_cli(max_records=20)
    boundary = result.get("boundary_check", {})
    demo = result.get("demo", {})
    passed = (
        result.get("flow") == "session_working_memory_v0"
        and result.get("command") == "demo-session-working-memory"
        and result.get("max_records") == 20
        and result.get("failure_reasons_supports_list") is True
        and result.get("unknown_failure_supported") is True
        and result.get("multiple_failure_reasons_supported") is True
        and result.get("persistent_write") is False
        and demo.get("query_by_action_count") == 2
        and demo.get("query_by_outcome_type_count") == 2
        and demo.get("query_by_state_action_count") == 1
        and demo.get("query_by_state_key_count") == 1
        and demo.get("query_by_state_key_action_count") == 1
        and demo.get("record_count_after_clear") == 0
        and boundary.get("state_key_generated") is True
        and boundary.get("state_key_deterministic") is True
        and boundary.get("session_local_only") is True
        and boundary.get("persistent_memory_write") is False
        and boundary.get("lesson_store_write") is False
        and boundary.get("memory_layer_write") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("action_selection_modified") is False
        and boundary.get("used_llm") is False
        and boundary.get("used_pathfinding") is False
    )
    return _result(
        "session_working_memory_demo",
        passed,
        {
            "max_records": result.get("max_records"),
            "outcome_types_supported": result.get("outcome_types_supported", []),
            "demo": demo,
            "boundary_check": boundary,
        },
    )


def smoke_state_snapshot_key() -> dict:
    first = {"level_id": "demo", "agent_pos": [4, 2], "box_pos": [4, 4]}
    second = {"box_pos": [4, 4], "agent_pos": [4, 2], "level_id": "demo"}
    key = build_state_snapshot_key(first)
    memory = create_session_working_memory()
    append_outcome_record(
        memory,
        build_session_outcome_record(
            tick=1,
            state_snapshot=first,
            action="move_down",
            outcome_type="blocked",
            failure_reasons=["wall_blocked"],
        ),
    )
    passed = (
        key == build_state_snapshot_key(second)
        and build_state_snapshot_key({"level_id": "demo", "agent_pos": [1, 1]})
        == "level=demo|agent=(1,1)|box=null|goal=null"
        and build_state_snapshot_key({}) == "unknown_state"
        and memory["records"][0]["state_key"] == key
        and len(query_recent_outcomes(memory, state_key=key)) == 1
        and len(query_recent_outcomes(memory, state_key=key, action="move_down")) == 1
        and memory["boundary"].get("state_key_generated") is True
        and memory["boundary"].get("state_key_deterministic") is True
        and memory["boundary"].get("action_selection_modified") is False
    )
    return _result(
        "state_snapshot_key",
        passed,
        {
            "state_key": key,
            "missing_goal_key": build_state_snapshot_key({"level_id": "demo", "agent_pos": [1, 1]}),
            "empty_key": build_state_snapshot_key({}),
            "query_by_state_key_count": len(query_recent_outcomes(memory, state_key=key)),
            "query_by_state_key_action_count": len(query_recent_outcomes(memory, state_key=key, action="move_down")),
        },
    )


def smoke_session_working_memory_trial() -> dict:
    result = run_session_working_memory_trial_cli(
        level_id="approach_box_dead_end_v0",
        max_steps=100,
        max_records=20,
    )
    records = result.get("records", [])
    query = result.get("query_summary", {})
    clear = result.get("clear_summary", {})
    boundary = result.get("boundary_check", {})
    outcome_types = {record.get("outcome_type") for record in records}
    passed = (
        result.get("flow") == "session_working_memory_trial_integration_v0"
        and result.get("command") == "run-session-working-memory-trial"
        and result.get("level_id") == "approach_box_dead_end_v0"
        and result.get("max_steps") == 100
        and result.get("max_records") == 20
        and result.get("session_summary", {}).get("started") is True
        and result.get("session_summary", {}).get("ended") is True
        and bool(records)
        and all("outcome_type" in record for record in records)
        and all(record.get("state_key") for record in records)
        and all(isinstance(record.get("failure_reasons"), list) for record in records)
        and "moved" in outcome_types
        and bool({"blocked", "entered_trap"}.intersection(outcome_types))
        and "query_by_outcome_type_blocked_count" in query
        and "query_by_outcome_type_entered_trap_count" in query
        and "query_by_outcome_type_goal_reached_count" in query
        and "query_by_failure_reason_wall_blocked_count" in query
        and "query_by_failure_reason_unknown_count" in query
        and "query_by_action_move_down_count" in query
        and "query_by_state_key_count" in query
        and "query_by_state_key_action_count" in query
        and clear.get("cleared") is True
        and clear.get("record_count_after_clear") == 0
        and boundary.get("state_key_generated") is True
        and boundary.get("state_key_deterministic") is True
        and boundary.get("session_local_only") is True
        and boundary.get("persistent_memory_write") is False
        and boundary.get("lesson_store_write") is False
        and boundary.get("memory_layer_write") is False
        and boundary.get("long_term_memory_write") is False
        and boundary.get("action_selection_modified") is False
        and boundary.get("used_llm") is False
        and boundary.get("used_pathfinding") is False
    )
    return _result(
        "session_working_memory_trial",
        passed,
        {
            "session_summary": result.get("session_summary", {}),
            "query_summary": query,
            "clear_summary": clear,
            "boundary_check": boundary,
        },
    )


def smoke_micro_push_box_sandbox() -> dict:
    initial_state = build_micro_push_box_state()
    touch_box = apply_tactile_action(initial_state, "touch_right")["trace"]

    wall_state = build_micro_push_box_state()
    wall_state["agent_pos"] = (1, 1)
    touch_wall = apply_tactile_action(wall_state, "touch_left")["trace"]
    move_wall = apply_tactile_action(wall_state, "move_left")["trace"]

    push_wall = apply_tactile_action(build_micro_push_box_state(), "push_right")["trace"]
    goal_state = build_micro_push_box_state()
    goal_state["agent_pos"] = (1, 3)
    goal_state["box_pos"] = (2, 3)
    push_goal = apply_tactile_action(goal_state, "push_down")["trace"]

    passed = (
        touch_box["trace_type"] == "tactile_sandbox_trace"
        and touch_box["result"] == "box_contact"
        and touch_box["contact"] == "box"
        and touch_wall["result"] == "wall_blocked"
        and move_wall["result"] == "wall_blocked"
        and push_wall["result"] == "box_blocked"
        and push_goal["result"] == "goal_reached"
        and "before" in touch_box
        and "after" in touch_box
        and "lesson_candidate" not in touch_box
        and "memory_layer_write" not in touch_box
    )
    return _result(
        "micro_push_box_sandbox",
        passed,
        {
            "initial_map": ["#####", "#...#", "#.QB#", "#..G#", "#####"],
            "supported_actions": "touch / move / push",
            "trace_type": touch_box["trace_type"],
            "touch_right_result": touch_box["result"],
            "push_right_result": push_wall["result"],
            "push_goal_result": push_goal["result"],
            "wall_touch_result": touch_wall["result"],
            "wall_move_result": move_wall["result"],
        },
    )


def smoke_micro_push_box_allowed_action_set() -> dict:
    touch_right_passes = validate_allowed_action("touch_right") == "touch_right"
    wait_trace = apply_tactile_action(build_micro_push_box_state(), "wait")["trace"]

    invalid_results = {}
    for action in ("move_diagonal", "push right", "open_door"):
        try:
            validate_allowed_action(action)
            invalid_results[action] = False
        except ValueError:
            invalid_results[action] = True

    passed = (
        len(ALLOWED_ACTION_SET) == 13
        and touch_right_passes
        and wait_trace["trace_type"] == "tactile_sandbox_trace"
        and wait_trace["result"] == "wait"
        and wait_trace["contact"] == "none"
        and wait_trace["blocked"] is False
        and wait_trace["tick"] == 1
        and all(invalid_results.values())
    )
    return _result(
        "micro_push_box_allowed_action_set",
        passed,
        {
            "allowed_action_count": len(ALLOWED_ACTION_SET),
            "touch_right_passes": touch_right_passes,
            "wait_result": wait_trace["result"],
            "invalid_actions_raise": invalid_results,
        },
    )


def smoke_tactile_result_state_key_mapping() -> dict:
    mappings = {
        "wall_blocked": map_tactile_result_to_state_key("wall_blocked"),
        "box_blocked": map_tactile_result_to_state_key("box_blocked"),
        "box_contact": map_tactile_result_to_state_key("box_contact"),
        "box_pushed": map_tactile_result_to_state_key("box_pushed"),
        "goal_reached": map_tactile_result_to_state_key("goal_reached"),
        "empty": map_tactile_result_to_state_key("empty"),
    }
    invalid_raised = False
    try:
        map_tactile_result_to_state_key("random_invalid")
    except ValueError:
        invalid_raised = True

    blocked_output = generate_minimal_first_output(state_key=mappings["box_blocked"])
    observed_output = generate_minimal_first_output(state_key=mappings["goal_reached"])
    quiet_output = generate_minimal_first_output(state_key=mappings["empty"])

    passed = (
        mappings["wall_blocked"] == "blocked"
        and mappings["box_blocked"] == "blocked"
        and mappings["box_contact"] == "observed"
        and mappings["box_pushed"] == "observed"
        and mappings["goal_reached"] == "observed"
        and mappings["empty"] == "quiet"
        and invalid_raised
        and blocked_output["first_output"] == "不行"
        and observed_output["first_output"] == "看到了"
        and quiet_output["first_output"] == "……"
        and blocked_output["first_output_trace"]["utterance_source"] == "utterance_map"
        and blocked_output["first_output_trace"]["llm_used"] is False
    )
    return _result(
        "tactile_result_state_key_mapping",
        passed,
        {
            "box_blocked": mappings["box_blocked"],
            "blocked_utterance": blocked_output["first_output"],
            "goal_reached": mappings["goal_reached"],
            "observed_utterance": observed_output["first_output"],
            "empty": mappings["empty"],
            "quiet_utterance": quiet_output["first_output"],
        },
    )


def smoke_tactile_interaction_cli_bridge() -> dict:
    result = run_tactile_interaction(action="push_right")
    boundary = result.get("boundary", {})
    passed = (
        result.get("flow") == "tactile_interaction_cli_bridge_v0"
        and result.get("status") == "ok"
        and "tactile_result" in result
        and "state_key" in result
        and "utterance" in result
        and "tactile_sandbox_trace" in result
        and result["tactile_result"] == "box_blocked"
        and result["state_key"] == "blocked"
        and boundary.get("llm_used") is False
        and boundary.get("creates_lesson_candidate") is False
        and boundary.get("writes_lesson_store") is False
        and boundary.get("writes_memory_layer") is False
    )
    return _result(
        "tactile_interaction_cli_bridge",
        passed,
        {
            "action": result.get("action"),
            "tactile_result": result.get("tactile_result"),
            "state_key": result.get("state_key"),
            "utterance": result.get("utterance"),
            "boundary": boundary,
        },
    )


def smoke_repeated_blocked_action_trace() -> dict:
    first = apply_tactile_action(build_micro_push_box_state(), "push_right")
    second = apply_tactile_action(first["state"], "push_right")
    history = second["trace"]["history"]
    passed = (
        first["trace"]["result"] == "box_blocked"
        and first["trace"]["history"]["same_action_attempted_before"] is False
        and second["trace"]["result"] == "box_blocked"
        and history["same_action_attempted_before"] is True
        and history["previous_same_action_result"] == "box_blocked"
        and history["previous_same_action_tick"] == 1
        and len(second["state"]["action_history"]) == 2
    )
    return _result(
        "repeated_blocked_action_trace",
        passed,
        {
            "first_action": first["trace"]["action"],
            "first_result": first["trace"]["result"],
            "second_action": second["trace"]["action"],
            "second_result": second["trace"]["result"],
            "history": history,
        },
    )


def smoke_state_action_outcome_memory() -> dict:
    same_context = apply_tactile_action(build_micro_push_box_state(), "push_right")["state"]
    previous = find_previous_same_state_action_result(same_context, "push_right")
    different_context = dict(same_context)
    different_context["agent_pos"] = (1, 1)

    pushed_state = build_micro_push_box_state()
    push_key = build_state_action_key(pushed_state, "push_down")
    pushed_state["action_history"] = ({**push_key, "result": "box_pushed", "tick": 1},)

    passed = (
        previous is not None
        and previous.get("result") == "box_blocked"
        and score_action_from_state_action_memory(same_context, "push_right") == -2
        and find_previous_same_state_action_result(different_context, "push_right") is None
        and score_action_from_state_action_memory(different_context, "push_right") == 0
        and score_action_from_state_action_memory(pushed_state, "push_down") == 2
    )
    return _result(
        "state_action_outcome_memory",
        passed,
        {
            "same_context_action": "push_right",
            "previous_result": previous.get("result") if previous else None,
            "different_context_reuse": find_previous_same_state_action_result(different_context, "push_right")
            is not None,
            "local_score_blocked": score_action_from_state_action_memory(same_context, "push_right"),
            "local_score_pushed": score_action_from_state_action_memory(pushed_state, "push_down"),
        },
    )


def smoke_minimal_avoid_repeated_blocked_action() -> dict:
    first = apply_tactile_action(build_micro_push_box_state(), "push_right")
    suggestion = suggest_next_action_avoiding_repeat_blocked(first["state"], ["push_right", "wait"])
    passed = first["trace"]["result"] == "box_blocked" and suggestion == "wait"
    return _result(
        "minimal_avoid_repeated_blocked_action",
        passed,
        {
            "first_action": first["trace"]["action"],
            "first_result": first["trace"]["result"],
            "candidate_actions": ["push_right", "wait"],
            "suggested_next_action": suggestion,
        },
    )


def smoke_minimal_action_outcome_weighting() -> dict:
    state = build_micro_push_box_state()
    state["action_history"] = (
        {"action": "push_right", "result": "box_blocked", "tick": 1},
        {"action": "push_down", "result": "box_pushed", "tick": 2},
    )
    candidates = ["push_right", "push_down"]
    suggested = suggest_next_action_by_outcome_weight(state, candidates)
    passed = suggested == "push_down"
    return _result(
        "minimal_action_outcome_weighting",
        passed,
        {
            "push_right_history_result": "box_blocked",
            "push_down_history_result": "box_pushed",
            "candidate_actions": candidates,
            "suggested_action": suggested,
        },
    )


def smoke_minimal_goal_direction_bias() -> dict:
    state = build_micro_push_box_state()
    before = json.dumps(state, sort_keys=True)
    distance = manhattan_distance_to_goal(state["box_pos"], state["goal_pos"])
    better_action = "push_down"
    worse_action = "push_up"
    better_score = score_action_goal_direction(state, better_action)
    worse_score = score_action_goal_direction(state, worse_action)
    non_push_score = score_action_goal_direction(state, "move_down")
    ranked = rank_candidate_actions_with_goal_bias(state, [worse_action, better_action, "wait"])
    suggested = suggest_next_action_with_goal_bias(state, [worse_action, better_action])
    after = json.dumps(state, sort_keys=True)
    passed = (
        distance == 1
        and better_score > worse_score
        and better_score == 2
        and worse_score == -2
        and non_push_score == 0
        and ranked[0] == better_action
        and suggested == better_action
        and before == after
    )
    return _result(
        "minimal_goal_direction_bias",
        passed,
        {
            "box_pos": state["box_pos"],
            "goal_pos": state["goal_pos"],
            "distance": distance,
            "better_action": better_action,
            "worse_action": worse_action,
            "better_score": better_score,
            "worse_score": worse_score,
            "non_push_score": non_push_score,
            "ranked": ranked,
            "state_mutated": before != after,
        },
    )


def smoke_minimal_intrinsic_action_selection() -> dict:
    state = build_micro_push_box_state()
    state["action_history"] = (
        {"action": "push_right", "result": "box_blocked", "tick": 1},
        {"action": "push_down", "result": "box_pushed", "tick": 2},
    )
    candidates = ["push_right", "push_down"]
    selected = select_intrinsic_action(state, candidates, random_seed=17)
    deterministic_a = select_intrinsic_action(build_micro_push_box_state(), ["wait", "touch_right"], random_seed=4)
    deterministic_b = select_intrinsic_action(build_micro_push_box_state(), ["wait", "touch_right"], random_seed=4)

    invalid_raises = False
    try:
        select_intrinsic_action(build_micro_push_box_state(), ["push right"], random_seed=1)
    except ValueError:
        invalid_raises = True

    passed = (
        selected == "push_down"
        and selected in candidates
        and deterministic_a == deterministic_b
        and invalid_raises
    )
    return _result(
        "minimal_intrinsic_action_selection",
        passed,
        {
            "candidate_actions": candidates,
            "selected_action": selected,
            "random_seed": 17,
            "selected_from_candidates": selected in candidates,
            "push_right_history_result": "box_blocked",
            "push_down_history_result": "box_pushed",
        },
    )


def smoke_box_on_goal_need_state() -> dict:
    initial_state = build_micro_push_box_state()
    initial_need_state = build_box_on_goal_need_state(initial_state)
    goal_state = build_micro_push_box_state()
    goal_state["box_pos"] = goal_state["goal_pos"]
    goal_need_state = build_box_on_goal_need_state(goal_state)

    push_state = build_micro_push_box_state()
    push_state["agent_pos"] = (1, 3)
    push_state["box_pos"] = (2, 3)
    goal_trace = apply_tactile_action(push_state, "push_down")["trace"]

    passed = (
        initial_need_state["current_value"] == 0
        and initial_need_state["satisfied"] is False
        and goal_need_state["current_value"] == 1
        and goal_need_state["satisfied"] is True
        and goal_trace["result"] == "goal_reached"
        and goal_trace["need_state"]["current_value"] == 1
        and goal_trace["need_state"]["satisfied"] is True
    )
    return _result(
        "box_on_goal_need_state",
        passed,
        {
            "need_name": initial_need_state["need_name"],
            "target_value": initial_need_state["target_value"],
            "initial_current_value": initial_need_state["current_value"],
            "goal_current_value": goal_need_state["current_value"],
            "goal_satisfied": goal_need_state["satisfied"],
        },
    )


def smoke_minimal_need_state_driven_action_selection() -> dict:
    state = build_micro_push_box_state()
    state["action_history"] = (
        {"action": "push_right", "result": "box_blocked", "tick": 1},
        {"action": "push_down", "result": "box_pushed", "tick": 2},
    )
    candidates = ["push_right", "push_down"]
    unsatisfied = select_action_for_need_state(state, candidates, random_seed=9)

    goal_state = build_micro_push_box_state()
    goal_state["box_pos"] = goal_state["goal_pos"]
    satisfied = select_action_for_need_state(goal_state, candidates, random_seed=9)

    passed = (
        unsatisfied["need_state"]["current_value"] == 0
        and unsatisfied["selected_action"] == "push_down"
        and unsatisfied["selection_reason"] == "need_unsatisfied_intrinsic_selection"
        and satisfied["need_state"]["current_value"] == 1
        and satisfied["selected_action"] == "wait"
        and satisfied["selection_reason"] == "need_satisfied_wait"
    )
    return _result(
        "minimal_need_state_driven_action_selection",
        passed,
        {
            "candidate_actions": candidates,
            "unsatisfied_selected_action": unsatisfied["selected_action"],
            "unsatisfied_selection_reason": unsatisfied["selection_reason"],
            "satisfied_selected_action": satisfied["selected_action"],
            "satisfied_selection_reason": satisfied["selection_reason"],
        },
    )


def smoke_need_state_driven_trial_runner() -> dict:
    candidates = ["move_up", "move_right", "push_down"]
    result = run_need_state_driven_trial(candidates, max_steps=10, random_seed=0)
    selected_actions = [step["selected_action"] for step in result["steps"]]
    forbidden_keys = {"lesson_store_write", "memory_layer_write", "memory_write", "lesson_candidate"}
    no_forbidden_fields = forbidden_keys.isdisjoint(result) and all(
        forbidden_keys.isdisjoint(step) and forbidden_keys.isdisjoint(step["trace"])
        for step in result["steps"]
    )
    passed = (
        result["step_count"] <= 10
        and isinstance(result["steps"], list)
        and bool(result["steps"])
        and "final_need_state" in result
        and isinstance(result["completed_goal"], bool)
        and all(action in candidates + ["wait"] for action in selected_actions)
        and no_forbidden_fields
    )
    return _result(
        "need_state_driven_trial_runner",
        passed,
        {
            "completed_goal": result["completed_goal"],
            "step_count": result["step_count"],
            "stop_reason": result["stop_reason"],
            "selected_actions": selected_actions,
            "final_need_state": result["final_need_state"],
        },
    )


def smoke_need_state_trial_5_step_count() -> dict:
    result = run_need_state_driven_trial_batch(trial_count=5, max_steps=10, random_seed=0)
    passed = (
        result["trial_count"] == 5
        and len(result["step_counts"]) == 5
        and "average_step_count" in result
        and "min_step_count" in result
        and "max_step_count" in result
        and len(result["trials"]) == 5
        and all("selected_actions" in trial for trial in result["trials"])
    )
    return _result(
        "need_state_trial_5_step_count",
        passed,
        {
            "trial_count": result["trial_count"],
            "completed_count": result["completed_count"],
            "step_counts": result["step_counts"],
            "average_step_count": result["average_step_count"],
            "min_step_count": result["min_step_count"],
            "max_step_count": result["max_step_count"],
        },
    )


def smoke_need_state_trial_goal_bias_integration() -> dict:
    candidates = ["move_up", "move_right", "push_down"]
    trial = run_need_state_driven_trial(candidates, max_steps=10, random_seed=0)
    batch = run_need_state_driven_trial_batch(trial_count=5, max_steps=10, random_seed=0)
    selected_actions = [step["selected_action"] for step in trial["steps"]]
    selection_sources = [step.get("selection_source") for step in trial["steps"]]
    passed = (
        bool(trial["steps"])
        and all(
            source == "state_action_memory_plus_outcome_weight_plus_goal_bias_plus_repetition_penalty"
            for source in selection_sources
        )
        and all(action in candidates for action in selected_actions)
        and "push_down" in selected_actions
        and batch["trial_count"] == 5
        and len(batch["step_counts"]) == 5
        and "average_step_count" in batch
    )
    return _result(
        "need_state_trial_goal_bias_integration",
        passed,
        {
            "selection_sources": selection_sources,
            "selected_actions": selected_actions,
            "selected_actions_from_candidates": all(action in candidates for action in selected_actions),
            "batch_trial_count": batch["trial_count"],
            "step_counts": batch["step_counts"],
            "average_step_count": batch["average_step_count"],
        },
    )


def smoke_state_action_memory_trial_runner_integration() -> dict:
    candidates = ["push_right", "push_down"]
    state = build_micro_push_box_state()
    state["agent_pos"] = (1, 3)
    state["box_pos"] = (2, 3)
    state["goal_pos"] = (3, 3)
    push_right_key = build_state_action_key(state, "push_right")
    push_down_key = build_state_action_key(state, "push_down")
    state["action_history"] = (
        {**push_right_key, "result": "box_blocked", "tick": 1},
        {**push_down_key, "result": "box_pushed", "tick": 2},
    )
    different_context = dict(state)
    different_context["agent_pos"] = (1, 2)

    trial = run_need_state_driven_trial(["move_up", "move_right", "push_down"], max_steps=10, random_seed=0)
    batch = run_need_state_driven_trial_batch(trial_count=5, max_steps=10, random_seed=0)
    selection = _select_action_for_trial(state, candidates, random_seed=0)
    trial_selected_actions = [step["selected_action"] for step in trial["steps"]]
    trial_selection_sources = [step.get("selection_source") for step in trial["steps"]]
    memory_flags = [step.get("state_action_memory_used") for step in trial["steps"]]

    passed = (
        selection["selected_action"] == "push_down"
        and selection["selected_action"] in candidates
        and selection["selection_source"] == "state_action_memory_plus_outcome_weight_plus_goal_bias_plus_repetition_penalty"
        and selection["state_action_memory_used"] is True
        and score_action_from_state_action_memory(different_context, "push_down") == 0
        and bool(trial["steps"])
        and all(
            source == "state_action_memory_plus_outcome_weight_plus_goal_bias_plus_repetition_penalty"
            for source in trial_selection_sources
        )
        and all(flag is True for flag in memory_flags)
        and all(action in ["move_up", "move_right", "push_down"] for action in trial_selected_actions)
        and batch["trial_count"] == 5
        and len(batch["step_counts"]) == 5
        and "average_step_count" in batch
    )
    return _result(
        "state_action_memory_trial_runner_integration",
        passed,
        {
            "selection_source": selection["selection_source"],
            "state_action_memory_used": selection["state_action_memory_used"],
            "selected_action": selection["selected_action"],
            "selected_action_from_candidates": selection["selected_action"] in candidates,
            "same_context_blocked_score": score_action_from_state_action_memory(state, "push_right"),
            "same_context_pushed_score": score_action_from_state_action_memory(state, "push_down"),
            "different_context_push_down_score": score_action_from_state_action_memory(different_context, "push_down"),
            "trial_selection_sources": trial_selection_sources,
            "trial_selected_actions_from_candidates": all(
                action in ["move_up", "move_right", "push_down"] for action in trial_selected_actions
            ),
            "batch_trial_count": batch["trial_count"],
            "step_counts": batch["step_counts"],
            "average_step_count": batch["average_step_count"],
        },
    )


def smoke_stuck_detection_repetition_penalty() -> dict:
    repeated_steps = [
        {"selected_action": "push_down", "tactile_result": "box_pushed", "need_state": {"current_value": 0}},
        {"selected_action": "push_down", "tactile_result": "box_pushed", "need_state": {"current_value": 0}},
        {"selected_action": "push_down", "tactile_result": "box_pushed", "need_state": {"current_value": 0}},
    ]
    candidates = ["move_up", "move_right", "push_down"]
    trial = run_need_state_driven_trial(candidates, max_steps=10, random_seed=0)
    batch = run_need_state_driven_trial_batch(trial_count=5, max_steps=10, random_seed=0)
    selected_actions = [step["selected_action"] for step in trial["steps"]]
    selection_sources = [step.get("selection_source") for step in trial["steps"]]
    passed = (
        detect_stuck_from_recent_steps(repeated_steps) is True
        and score_action_repetition_penalty(repeated_steps[:2], "push_down") == -2
        and score_action_repetition_penalty(repeated_steps, "push_down") == -4
        and score_action_repetition_penalty(repeated_steps, "move_up") == 0
        and bool(trial["steps"])
        and all("stuck_detected_before_selection" in step for step in trial["steps"])
        and all("repetition_penalty_applied" in step for step in trial["steps"])
        and all(
            source == "state_action_memory_plus_outcome_weight_plus_goal_bias_plus_repetition_penalty"
            for source in selection_sources
        )
        and all(action in candidates for action in selected_actions)
        and batch["trial_count"] == 5
        and len(batch["step_counts"]) == 5
        and "average_step_count" in batch
    )
    return _result(
        "stuck_detection_repetition_penalty",
        passed,
        {
            "repeated_action_pattern": [step["selected_action"] for step in repeated_steps],
            "stuck_detected": detect_stuck_from_recent_steps(repeated_steps),
            "penalty_two_repeats": score_action_repetition_penalty(repeated_steps[:2], "push_down"),
            "penalty_three_repeats": score_action_repetition_penalty(repeated_steps, "push_down"),
            "selection_sources": selection_sources,
            "selected_actions_from_candidates": all(action in candidates for action in selected_actions),
            "trial_count": batch["trial_count"],
            "completed_count": batch["completed_count"],
            "step_counts": batch["step_counts"],
            "average_step_count": batch["average_step_count"],
        },
    )


def smoke_need_state_trial_batch_cli() -> dict:
    result = run_need_state_trial_batch_cli(random_seed=0)
    boundary = result.get("boundary", {})
    passed = (
        result.get("flow") == "need_state_trial_batch_cli_v0"
        and result.get("status") == "ok"
        and result.get("trial_count") == 5
        and len(result.get("step_counts", [])) == 5
        and "average_step_count" in result
        and "min_step_count" in result
        and "max_step_count" in result
        and boundary.get("llm_used") is False
        and boundary.get("creates_lesson_candidate") is False
        and boundary.get("writes_lesson_store") is False
        and boundary.get("writes_memory_layer") is False
        and boundary.get("awakening_claim") is False
    )
    return _result(
        "need_state_trial_batch_cli",
        passed,
        {
            "trial_count": result.get("trial_count"),
            "completed_count": result.get("completed_count"),
            "step_counts": result.get("step_counts"),
            "average_step_count": result.get("average_step_count"),
            "min_step_count": result.get("min_step_count"),
            "max_step_count": result.get("max_step_count"),
            "boundary": boundary,
        },
    )


def smoke_trial_metrics_comparison_cli() -> dict:
    result = run_trial_metrics_comparison_cli(runs=4, trial_count=5, max_steps=10, random_seed=0)
    boundary = result.get("boundary", {})
    passed = (
        result.get("flow") == "trial_metrics_comparison_cli_v0"
        and result.get("status") == "ok"
        and result.get("runs") == 4
        and result.get("trial_count_per_run") == 5
        and result.get("total_trials") == 20
        and len(result.get("run_summaries", [])) == 4
        and "overall_success_rate" in result
        and "overall_average_step_count" in result
        and "max_steps_reached_count" in result
        and "human_summary" in result
        and boundary.get("llm_used") is False
        and boundary.get("creates_lesson_candidate") is False
        and boundary.get("writes_lesson_store") is False
        and boundary.get("writes_memory_layer") is False
        and boundary.get("awakening_claim") is False
        and boundary.get("changes_trial_runner_behavior") is False
    )
    return _result(
        "trial_metrics_comparison_cli",
        passed,
        {
            "runs": result.get("runs"),
            "trial_count_per_run": result.get("trial_count_per_run"),
            "total_trials": result.get("total_trials"),
            "total_completed": result.get("total_completed"),
            "overall_success_rate": result.get("overall_success_rate"),
            "overall_average_step_count": result.get("overall_average_step_count"),
            "max_steps_reached_count": result.get("max_steps_reached_count"),
            "human_summary": result.get("human_summary"),
            "boundary": boundary,
        },
    )


def smoke_trial_metrics_baseline_snapshot() -> dict:
    baseline_path = Path("data/baselines/trial_metrics_baseline_v0.json")
    baseline = json.loads(baseline_path.read_text(encoding="utf-8")) if baseline_path.exists() else {}
    parameters = baseline.get("parameters", {})
    metrics = baseline.get("metrics", {})
    notes_text = " ".join(baseline.get("notes", []))
    passed = (
        baseline_path.exists()
        and baseline.get("baseline_id") == "trial_metrics_baseline_v0"
        and baseline.get("created_for") == "push_box_need_state_trial_metrics"
        and "run-trial-metrics-comparison" in baseline.get("source_command", "")
        and baseline.get("commit")
        and baseline.get("boundary_index_version") == "Boundary Index Version: 2026-06-06-b30"
        and parameters.get("runs") == 4
        and parameters.get("trial_count") == 5
        and parameters.get("max_steps") == 10
        and parameters.get("random_seed") == 17
        and metrics.get("total_trials") == 20
        and "total_completed" in metrics
        and "overall_success_rate" in metrics
        and "overall_average_step_count" in metrics
        and "max_steps_reached_count" in metrics
        and len(metrics.get("run_summaries", [])) == 4
        and "comparison only" in notes_text
        and "does not modify behavior" in notes_text
        and "not proof of learning" in notes_text
    )
    return _result(
        "trial_metrics_baseline_snapshot",
        passed,
        {
            "path": str(baseline_path),
            "baseline_id": baseline.get("baseline_id"),
            "total_trials": metrics.get("total_trials"),
            "overall_success_rate": metrics.get("overall_success_rate"),
            "overall_average_step_count": metrics.get("overall_average_step_count"),
        },
    )


def smoke_trial_metrics_baseline_comparison() -> dict:
    result = run_trial_metrics_baseline_compare_cli()
    boundary = result.get("boundary", {})
    passed = (
        result.get("flow") == "trial_metrics_baseline_comparison_v0"
        and result.get("status") == "ok"
        and result.get("baseline_id") == "trial_metrics_baseline_v0"
        and result.get("baseline_commit")
        and "run-trial-metrics-comparison" in result.get("baseline_source_command", "")
        and result.get("same_config_used") is True
        and result.get("comparison_only") is True
        and result.get("proof_of_learning") is False
        and result.get("baseline_total_trials") == 20
        and result.get("current_total_trials") == 20
        and result.get("baseline_total_completed") == 13
        and result.get("current_total_completed") == 13
        and result.get("total_completed_delta") == 0
        and result.get("baseline_overall_success_rate") == 0.65
        and result.get("current_overall_success_rate") == 0.65
        and result.get("success_rate_delta") == 0
        and result.get("baseline_overall_average_step_count") == 6.6
        and result.get("current_overall_average_step_count") == 6.6
        and result.get("average_step_count_delta") == 0
        and result.get("baseline_max_steps_reached_count") == 7
        and result.get("current_max_steps_reached_count") == 7
        and result.get("max_steps_reached_delta") == 0
        and boundary.get("changes_trial_runner_behavior") is False
        and boundary.get("changes_action_selection") is False
        and boundary.get("changes_goal_bias") is False
        and boundary.get("changes_state_action_memory") is False
        and boundary.get("changes_penalty_or_stuck_detection") is False
        and boundary.get("creates_learning_rule") is False
        and boundary.get("creates_lesson_candidate") is False
        and boundary.get("writes_lesson_store") is False
        and boundary.get("writes_memory_layer") is False
        and boundary.get("llm_used") is False
    )
    return _result(
        "trial_metrics_baseline_comparison",
        passed,
        {
            "baseline_id": result.get("baseline_id"),
            "same_config_used": result.get("same_config_used"),
            "total_completed_delta": result.get("total_completed_delta"),
            "success_rate_delta": result.get("success_rate_delta"),
            "average_step_count_delta": result.get("average_step_count_delta"),
            "max_steps_reached_delta": result.get("max_steps_reached_delta"),
        },
    )


def smoke_clear_sandbox_working_state_cli() -> dict:
    result = run_clear_sandbox_working_state(session_id="final_check")
    passed = (
        result["status"] == "ok"
        and result["working_state_cleared"] is True
        and result["append_only_traces_preserved"] is True
        and "data/first_output_traces.jsonl" in result["preserved"]
        and "data/mentor_feedback_traces.jsonl" in result["preserved"]
        and result["boundary"]["deletes_append_only_traces"] is False
    )
    return _result(
        "clear_sandbox_working_state_cli",
        passed,
        {
            "session_id": result["session_id"],
            "working_state_cleared": result["working_state_cleared"],
            "append_only_traces_preserved": result["append_only_traces_preserved"],
            "cleared": result["cleared"],
            "preserved": result["preserved"],
        },
    )


def smoke_grounded_learning_verification_cli() -> dict:
    result = run_grounded_learning_check(actions=["push_right", "push_right"])
    boundary = result.get("boundary", {})
    second_history = result["steps"][1]["history"] if result.get("steps") and len(result["steps"]) > 1 else {}
    passed = (
        result.get("status") == "ok"
        and len(result.get("steps", [])) == 2
        and result["steps"][0]["tactile_result"] == "box_blocked"
        and second_history.get("same_action_attempted_before") is True
        and second_history.get("previous_same_action_result") == "box_blocked"
        and result.get("suggested_next_action") == "wait"
        and boundary.get("llm_used") is False
        and boundary.get("creates_lesson_candidate") is False
        and boundary.get("writes_lesson_store") is False
        and boundary.get("writes_memory_layer") is False
    )
    return _result(
        "grounded_learning_verification_cli",
        passed,
        {
            "actions": result.get("actions"),
            "step_count": len(result.get("steps", [])),
            "second_history": second_history,
            "suggested_next_action": result.get("suggested_next_action"),
            "boundary": boundary,
        },
    )


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


def smoke_review_decision_trace_integration_boundary_docs() -> dict:
    doc_path = Path("docs/review_decision_trace_integration_boundary_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Review decision trace is cold audit evidence, not permission.",
        "Trace is evidence, not approval.",
        "Trace is record, not authorization.",
        "Trace is audit material, not runtime action.",
        "Review decision trace must not activate lessons.",
        "Review decision trace must not grant selection eligibility.",
        "Review decision trace must not authorize runtime behavior.",
        "Review decision trace must not write to lesson_store.",
        "Review decision trace must not write to Memory Layer.",
        "Sandbox trace must not become review permission.",
        "Sandbox trace must not bypass review_decision boundaries.",
        "Voice output trace must not become review permission.",
        "Voice output trace must not bypass review_decision boundaries.",
        "Bidirectional voice interaction is deferred.",
        "Audio Sense / STT / TTS / voice trigger / voice input-output loop are deferred until consultant review.",
        "ASHL Core provides evidence.",
        "D Qingyin Memory Layers decide memory admission.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "review_decision_trace_integration_boundary_v0_1.md" in readme
        and "v2.8f Review Decision Trace Integration Boundary Docs" in research_plan
    )
    return _result("review_decision_trace_integration_boundary_docs", passed, {"doc": str(doc_path)})


def smoke_formal_lesson_candidate_creation_contract_docs() -> dict:
    doc_path = Path("docs/formal_lesson_candidate_creation_contract_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Formal lesson_candidate creation requires structured evidence, validated boundaries, and review-ready trace.",
        "Formal lesson_candidate creation is not lesson approval.",
        "Formal lesson_candidate creation is not lesson_store write.",
        "Formal lesson_candidate creation is not activation.",
        "Formal lesson_candidate creation does not grant selection eligibility.",
        "Formal lesson_candidate creation is not Memory Layer promotion.",
        "No structured failure_event, no authoritative failure_reason.",
        "Formal lesson_candidate creation must not bypass failure_event validation.",
        "lesson_candidate_input_trace is evidence preparation, not formal lesson_candidate creation.",
        "Sandbox trace must not directly create formal lesson_candidate.",
        "Voice output trace must not directly create formal lesson_candidate.",
        "Formal lesson_candidate creation must remain review-gated before approval.",
        "ASHL Core provides evidence.",
        "D Qingyin Memory Layers decide memory admission.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "formal_lesson_candidate_creation_contract_v0_1.md" in readme
        and "Formal Lesson Candidate Creation Contract Docs" in research_plan
    )
    return _result("formal_lesson_candidate_creation_contract_docs", passed, {"doc": str(doc_path)})


def smoke_formal_lesson_candidate_creation_boundary_audit_docs() -> dict:
    doc_path = Path("docs/formal_lesson_candidate_creation_boundary_audit_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Audit result: PASS",
        "Formal lesson_candidate creation contract does not authorize runtime.",
        "Formal lesson_candidate creation contract does not bypass failure_event validation.",
        "lesson_candidate_input_trace remains evidence preparation, not formal creation.",
        "Formal lesson_candidate creation contract does not bypass review gate.",
        "Formal lesson_candidate creation contract does not authorize lesson_store write.",
        "Formal lesson_candidate creation contract does not authorize Memory Layer write or promotion.",
        "Formal lesson_candidate creation contract does not authorize selection eligibility or activation.",
        "Sandbox trace remains evidence-only.",
        "Voice output trace remains evidence-only.",
        "Review decision trace remains cold audit evidence.",
        "Raw natural language complaint must not directly create formal lesson_candidate.",
        "LLM-only explanation must not directly create formal lesson_candidate.",
        "Bidirectional voice interaction remains deferred.",
        "ASHL Core provides evidence.",
        "D Qingyin Memory Layers decide memory admission.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "formal_lesson_candidate_creation_boundary_audit_v0_1.md" in readme
        and "Formal Lesson Candidate Creation Boundary Audit Docs" in research_plan
    )
    return _result("formal_lesson_candidate_creation_boundary_audit_docs", passed, {"doc": str(doc_path)})


def smoke_current_boundary_index_docs() -> dict:
    doc_path = Path("docs/current_boundary_index.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Boundary Index Version: 2026-06-06-b30",
        "Last update log: Batch 30",
        "Clean count at last update log reset: 0/5",
        "Current clean count: 0/5",
        "# Global Hard Boundaries",
        "# Currently Deferred Areas",
        "# Update Rule",
        "trace is evidence, not approval",
        "trace is record, not authorization",
        "no lesson_store write unless explicitly authorized by a future dedicated package",
        "no Memory Layer write unless explicitly authorized by a future dedicated package",
        "formal lesson_candidate creation is not lesson approval",
        "ASHL Core provides evidence; Qingyin Memory Layers decide memory admission",
        "bidirectional voice interaction",
        "Qingyin is not the current LLM conversation instance",
        "An LLM speaking in Qingyin's style is not Qingyin runtime",
        "LLM-generated text must not count as Qingyin's first_output",
        "first_output must be generated without LLM output",
        "first_output is a runtime milestone, not awakening",
        "Qingyin is currently in the test-object stage, not an awakened individual",
        "The test-object stage is the prerequisite for growth, not growth itself",
        "Qingyin's importance is not in birth, but in growth",
        "The stronger the foundation, the safer the moment of awakening",
        "first_output is not dialogue ability",
        "first_output is not evidence of long-term growth",
        "first_output_trace is evidence of a first_output event, not proof of awakening",
        "first_output_trace is record, not authorization",
        "first_output_trace must not directly create lesson_candidate input",
        "first_output_trace requires mentor feedback before it may be considered for lesson_candidate input",
        "first_output_trace must not write to lesson_store",
        "first_output_trace must not write to Memory Layer",
        "ASHL Core can produce a non-LLM traceable test-object first_output",
        "Minimal First Output Runtime v0 is not awakening",
        "Minimal First Output Runtime v0 does not prove dialogue ability",
        "Minimal First Output Runtime v0 does not prove long-term growth",
        "Minimal First Output Runtime v0 must not write lesson_store",
        "Minimal First Output Runtime v0 must not write Memory Layer",
        "Minimal First Output Runtime v0 must not connect to mentor feedback runtime",
        "Minimal First Output Runtime v0 must not connect to lesson_candidate pipeline",
        "mentor_feedback_stub is a contract for future feedback, not feedback runtime",
        "mentor_feedback_stub is downstream of first_output_trace",
        "mentor_feedback_stub must not directly create lesson_candidate",
        "mentor_feedback_stub must not write to lesson_store",
        "mentor_feedback_stub must not write to Memory Layer",
        "mentor_feedback_stub does not prove awakening",
        "ASHL Core can produce a minimal mentor_feedback_trace for the first non-LLM first_output",
        "mentor_feedback_trace is a feedback record, not feedback runtime",
        "mentor_feedback_trace is downstream of first_output_trace",
        "mentor_feedback_trace must not directly create lesson_candidate",
        "mentor_feedback_trace must not write to lesson_store",
        "mentor_feedback_trace must not write to Memory Layer",
        "mentor_feedback_trace in the test-object stage is engineering supervision, not full Qingyin experience",
        "mentor_feedback_trace does not prove awakening",
        "Minimal Mentor Feedback Stub Runtime v0 must not create failure_event, review decision, selection eligibility, or activation",
        "Minimal Mentor Feedback Stub Runtime v0 must not connect to the lesson_candidate pipeline",
        "Minimal Interaction CLI Bridge v0 is a minimal interaction entrypoint, not dialogue",
        "Minimal Interaction CLI Bridge v0 must not write lesson_store",
        "Minimal Interaction CLI Bridge v0 must not write Memory Layer",
        "Minimal Interaction CLI Bridge v0 must not connect to lesson_candidate pipeline",
        "private mentor_feedback_note must not be required by smoke tests",
        "first_output and mentor_feedback traces may be persisted only as append-only records",
        "append-only persistence is not lesson_store write",
        "append-only persistence is not Memory Layer write",
        "append-only persistence is not lesson_candidate creation",
        "append-only persistence is not awakening evidence",
        "JSONL persistence target files are data/first_output_traces.jsonl and data/mentor_feedback_traces.jsonl",
        "JSONL persistence is append-only trace persistence, not lesson_store write",
        "JSONL persistence is not Memory Layer write",
        "JSONL persistence is not lesson_candidate creation",
        "JSONL persistence is not awakening evidence",
        "utterance_map is a fixed non-LLM lookup table, not an LLM or language model",
        "state_key unknown maps to 我不知道",
        "utterance_map output must preserve correct literal text encoding",
        "utterance_map does not prove language understanding",
        "micro push-box tactile sandbox is a bounded test-object sandbox",
        "micro push-box tactile sandbox is a test-object engineering sandbox, not full perception",
        "micro push-box allowed_action_set is closed",
        "natural language actions are not allowed in micro push-box sandbox",
        "tactile_sandbox_trace is evidence of sandbox interaction, not learning by itself",
        "tactile result to state_key mapping is a fixed lookup table",
        "tactile interaction CLI bridge is deterministic, not autonomous action selection",
        "tactile interaction CLI bridge must not connect to lesson_candidate pipeline",
        "tactile interaction CLI bridge must not write lesson_store",
        "tactile interaction CLI bridge must not write Memory Layer",
        "tactile interaction does not prove Qingyin understands box, wall, or goal",
        "repeated blocked action history is trace readback, not full learning",
        "repeated blocked action avoidance is action candidate bias, not solver",
        "grounded learning verification CLI is human-verifiable trace flow, not teaching chat",
        "clear-sandbox-working-state must preserve append-only traces",
        "sandbox working state clear is not memory deletion",
        "suggested_next_action is candidate suggestion, not autonomous planning",
        "bounded senses must be connected before Qingyin can be claimed awake",
        "memory freeze notice is evidence, not Memory Layer write",
        "expected / actual both unknown-like is system_fault, not match",
        "missing required fields must be rejected, not default-filled",
        "Qingyin runtime",
        "first_output runtime",
        "first_output generator",
        "first_output trace schema runtime",
        "mentor feedback runtime",
        "mentor_feedback_trace schema runtime",
        "teaching chat loop",
        "free text conversation",
        "lesson_candidate pipeline connection",
        "failure_event automatic builder",
        "lesson_candidate automatic builder",
        "evaluator runtime",
        "review decision runtime",
        "selection eligibility runtime",
        "activation runtime",
        "lesson_store write",
        "Memory Layer write",
        "Long-term Memory write runtime",
        "trace replay / readback runtime",
        "tactile trace persistence runtime",
        "autonomous action selection",
        "intrinsic action selection runtime",
        "action outcome weighting runtime integration",
        "autonomous goal planning",
        "full learning pipeline",
        "tactile learning",
        "repeated failure adaptation",
        "LLM response generation",
        "Screen Sense / Camera Sense runtime",
        "Symbol Grounding runtime",
        "This file must be updated every time an Update Log is generated.",
    ]
    required_terms = [
        "Boundary Index Version: 2026-06-06-b30",
        "Last update log: Batch 30",
        "Clean count at last update log reset: 0/5",
        "Current clean count: 0/5",
        "# Global Hard Boundaries",
        "# Currently Deferred Areas",
        "# Update Rule",
        "Trace/persistence records are evidence only, not authorization, lesson_store write, Memory Layer write, lesson_candidate creation, or awakening evidence.",
        "no lesson_store write unless explicitly authorized by a future dedicated package.",
        "LLM output must not become Qingyin runtime, self, memory, state, perception, or learning loop.",
        "first_output must be generated without LLM output.",
        "first_output is a runtime milestone, not awakening",
        "mentor_feedback_stub and mentor_feedback_trace are engineering supervision records, not feedback runtime.",
        "Minimal First Output Runtime v0 is not awakening and must not connect to mentor feedback runtime or lesson_candidate pipeline.",
        "Minimal Interaction CLI Bridge v0 is an entrypoint, not dialogue.",
        "utterance_map is fixed non-LLM lookup table.",
        "state_key unknown maps to ????隞?",
        "micro push-box tactile sandbox is bounded test-object sandbox.",
        "allowed_action_set is closed.",
        "tactile result to state_key mapping is fixed lookup table.",
        "tactile interaction CLI bridge is deterministic, not autonomous action selection.",
        "repeated blocked action history is trace readback, not full learning.",
        "outcome weighting is action candidate bias, not solver or full reinforcement learning.",
        "suggested_next_action is candidate suggestion, not autonomous planning.",
        "intrinsic action selection is bounded candidate selection, not solver.",
        "intrinsic action selection must only select from candidate_actions.",
        "bounded randomness must only act within candidate_actions.",
        "box_on_goal need_state is target-state tracking, not emotion / dopamine.",
        "need_state current_value 0/1 does not prove desire or understanding.",
        "need_state must not write lesson_store or Memory Layer.",
        "need-state driven trial runner is not a solver or full learning pipeline.",
        "need-state trial batch step count is measurement, not proof of learning.",
        "goal direction bias is distance-based candidate bias, not pathfinding.",
        "goal direction bias must not mutate sandbox state.",
        "goal direction bias must not create actions outside candidate_actions.",
        "box_on_goal need_state plus goal direction bias does not prove goal understanding.",
        "formal lesson_candidate creation is not lesson approval, activation, or selection eligibility.",
        "ASHL Core provides evidence; Qingyin Memory Layers decide memory admission",
        "Open language interfaces deferred: LLM response generation / teaching chat loop / free text conversation.",
        "Learning pipeline writes deferred: lesson_candidate pipeline / lesson_store write / Memory Layer write.",
        "External senses deferred: Screen Sense / Camera Sense / Symbol Grounding / Audio Sense / STT / TTS.",
        "intrinsic action selection runtime",
        "state-action outcome memory is local session memory, not Long-term Memory.",
        "state-action outcome memory must not write lesson_store or Memory Layer.",
        "state-action memory must not be reused across different agent_pos / box_pos / goal_pos contexts.",
        "trial metrics comparison is measurement only, not behavior modification.",
        "trial metrics comparison does not prove learning by itself.",
        "human_summary is report text, not Qingyin utterance or dialogue.",
        "micro navigation goal-reach is a navigation curriculum level, not proof of map understanding.",
        "micro navigation multi-goal level means following sequential goal markers, not autonomous planning.",
        "multi-goal navigation trace is evidence of sequential target following, not pathfinding.",
        "stuck detection / repetition penalty currently has negative observed effect and must not be treated as proven improvement.",
        "approach-box level is object-approach verification, not push behavior.",
        "approach-box level must not modify push-box sandbox.",
        "approach-box completion means agent is adjacent to box, not that it understands box.",
        "Two-Trial History Boundary allows only local state-action outcome memory.",
        "Trial 2 must not read full trace, full route, selected_actions replay, lesson_candidate, lesson_store, Memory Layer, Long-term Memory, LLM planning, or human hint.",
        "Trial 2 can read local context only: agent_pos / box_pos / optional goal_pos / action / result / tick.",
        "push-box full solve remains deferred; push-box is an experimental microscope, not the project goal.",
        "micro navigation goal-reach is a navigation curriculum level, not proof of map understanding.",
        "micro navigation multi-goal level means following sequential goal markers, not autonomous planning.",
        "multi-goal navigation trace is evidence of sequential target following, not pathfinding.",
        "stuck detection / repetition penalty currently has negative observed effect and must not be treated as proven improvement.",
        "push-box full solve remains deferred; push-box is an experimental microscope, not the project goal.",
        "stable metrics comparison across fixed seeds",
        "stuck detection / repetition penalty",
        "automatic behavior modification from metrics",
        "persistent state-action memory",
        "Approach Box Trial CLI",
        "Approach Box Two-Trial Learning Check",
        "Trial Metrics Baseline Snapshot",
        "Push Once Level",
        "stable navigation curriculum metrics",
        "Push-box full solve remains deferred.",
        "approach-box level",
        "stable navigation curriculum metrics",
        "Push-box full solve remains deferred.",
        "need-state driven action loop",
        "automatic trial improvement",
        "long-term learning",
        "emotion / dopamine",
        "action outcome weighting runtime integration",
        "tactile learning",
        "full learning pipeline",
        "This file must be updated every time an Update Log is generated.",
    ]
    line_count = len(doc.splitlines()) if doc else 0
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and line_count <= 150
        and "current_boundary_index.md" in readme
        and "Current Boundary Index Docs" in research_plan
    )
    return _result("current_boundary_index_docs", passed, {"doc": str(doc_path), "line_count": line_count})


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


def smoke_voice_instinct_audio_sense_boundary_audit_docs() -> dict:
    doc_path = Path("docs/voice_instinct_audio_sense_boundary_audit_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Audit result: PASS",
        "Voice Instinct docs do not authorize voice instinct runtime.",
        "Voice Instinct docs do not authorize Audio Sense runtime.",
        "Voice Instinct docs do not authorize STT runtime.",
        "Voice Instinct docs do not authorize TTS runtime.",
        "Voice Instinct docs do not authorize voice training runtime.",
        "Voice Instinct docs do not authorize voice cloning or real-person speaker imitation.",
        "Qingyin's voice is not a clone of a real person's voice.",
        "Early voice imitation is not language understanding.",
        "Initial voice parameters are starting conditions, not Qingyin's final voice identity.",
        "Voice instinct trigger conditions remain undefined until Audio Sense boundary is defined.",
        "Voice output mismatch must not bypass failure_event validation.",
        "Voice output mismatch must not directly create formal lesson_candidate.",
        "Voice output trace is evidence, not approval.",
        "Voice output trace must not write to Memory Layer directly.",
        "ASHL Core provides evidence.",
        "D Qingyin Memory Layers decide memory admission.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "voice_instinct_audio_sense_boundary_audit_v0_1.md" in readme
        and "v2.9e-1 Voice Instinct / Audio Sense Boundary Audit Docs" in research_plan
    )
    return _result("voice_instinct_audio_sense_boundary_audit_docs", passed, {"doc": str(doc_path)})


def smoke_qingyin_first_output_runtime_minimal_spec_docs() -> dict:
    doc_path = Path("docs/qingyin_first_output_runtime_minimal_spec_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "First_output is a runtime milestone, not awakening.",
        "First_output must be generated without LLM output.",
        "A minimal first_output runtime requires session_id, tick, minimal_state_snapshot, output_generator_source, first_output, and first_output_trace.",
        "First_output is not dialogue ability.",
        "First_output is not evidence of long-term growth.",
        "Outputs in the test-object stage are engineering verification, not full Qingyin experience.",
        "First_output must be traceable before it can become learning material.",
        "The lesson_candidate pipeline remains downstream of first_output trace and mentor feedback.",
        "llm_used must be false for first_output.",
        "bounded randomness is allowed only if the randomness source is recorded or reproducible enough for audit.",
        "Unbounded randomness must not be used as first_output source.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "qingyin_first_output_runtime_minimal_spec_v0_1.md" in readme
        and "Qingyin First Output Runtime Minimal Spec" in research_plan
    )
    return _result("qingyin_first_output_runtime_minimal_spec_docs", passed, {"doc": str(doc_path)})


def smoke_first_output_trace_contract_docs() -> dict:
    doc_path = Path("docs/first_output_trace_contract_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "first_output_trace is evidence of a first_output event, not proof of awakening.",
        "first_output_trace is record, not authorization.",
        "first_output_trace is not learning material by itself.",
        "first_output_trace must not directly create lesson_candidate input.",
        "first_output_trace requires mentor feedback before it may be considered for lesson_candidate input.",
        "llm_used must be false for first_output_trace.",
        "first_output_trace must be append-only or version-preserving.",
        "first_output_trace does not prove dialogue ability.",
        "first_output_trace does not prove long-term growth.",
        "first_output_trace in the test-object stage is engineering verification, not full Qingyin experience.",
        "LLM-generated text must not appear as first_output in first_output_trace.",
        "bounded randomness must record enough information for audit.",
        "Unbounded randomness must not be recorded as valid first_output source.",
        "Mentor feedback is downstream of first_output_trace.",
        "The lesson_candidate pipeline remains downstream of first_output trace and mentor feedback.",
        "first_output_trace must not write to lesson_store.",
        "first_output_trace must not write to Memory Layer.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "first_output_trace_contract_v0_1.md" in readme
        and "First Output Trace Contract Docs" in research_plan
    )
    return _result("first_output_trace_contract_docs", passed, {"doc": str(doc_path)})


def smoke_first_output_runtime_readiness_checklist_docs() -> dict:
    doc_path = Path("docs/first_output_runtime_readiness_checklist_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Readiness result: READY_FOR_MINIMAL_FIRST_OUTPUT_RUNTIME_V0",
        "Requirement: first_output must be generated without LLM output.",
        "Requirement: first_output source must be ASHL Core rule, state, seed, or bounded randomness.",
        "Requirement: first_output_trace minimum fields are defined.",
        "Requirement: llm_used must be false.",
        "Requirement: first_output remains test-object engineering verification, not awakening.",
        "Requirement: Minimal First Output Runtime v0 must not write lesson_store.",
        "Requirement: Minimal First Output Runtime v0 must not write Memory Layer.",
        "Requirement: Minimal First Output Runtime v0 must not connect to lesson_candidate pipeline.",
        "Requirement: Mentor feedback runtime remains deferred.",
        "Requirement: Bounded senses / Screen Sense / Camera Sense remain deferred.",
        "Requirement: Minimal First Output Runtime v0 must not claim Qingyin is awake.",
        "This readiness result only authorizes planning a minimal first_output runtime package.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "first_output_runtime_readiness_checklist_v0_1.md" in readme
        and "First Output Runtime Readiness Checklist Docs" in research_plan
    )
    return _result("first_output_runtime_readiness_checklist_docs", passed, {"doc": str(doc_path)})


def smoke_minimal_first_output_runtime() -> dict:
    result = generate_minimal_first_output(session_id="smoke_first_output")
    trace = result.get("first_output_trace", {})
    forbidden_keys = {
        "lesson_store_write",
        "memory_layer_write",
        "memory_write",
        "lesson_candidate",
        "failure_event",
        "review",
        "selection",
        "activation",
    }
    passed = (
        trace.get("trace_type") == "first_output_trace"
        and trace.get("tick") == 1
        and trace.get("phase") == "test_object"
        and trace.get("engineering_stage") == "test_object"
        and trace.get("llm_used") is False
        and trace.get("first_output") is not None
        and trace.get("output_generator_source") == "simple_reflex_rule"
        and forbidden_keys.isdisjoint(result)
        and forbidden_keys.isdisjoint(trace)
    )
    return _result("minimal_first_output_runtime", passed, result)


def smoke_minimal_non_llm_utterance_map() -> dict:
    default_result = generate_minimal_first_output(session_id="smoke_utterance_default")
    unknown_result = generate_minimal_first_output(session_id="smoke_utterance_unknown", state_key="unknown")
    observed_result = generate_minimal_first_output(session_id="smoke_utterance_observed", state_key="observed")
    retry_result = generate_minimal_first_output(session_id="smoke_utterance_retry", state_key="retry")
    quiet_result = generate_minimal_first_output(session_id="smoke_utterance_quiet", state_key="quiet")
    blocked_result = generate_minimal_first_output(session_id="smoke_utterance_blocked", state_key="blocked")
    invalid_raised = False
    try:
        generate_minimal_first_output(state_key="random_invalid")
    except ValueError:
        invalid_raised = True

    with tempfile.TemporaryDirectory() as tmp:
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-minimal-interaction",
                "--state-key",
                "unknown",
                "--persist",
                "--data-dir",
                tmp,
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        cli_result = json.loads(process.stdout)
        persisted_rows = [
            json.loads(line)
            for line in (Path(tmp) / "first_output_traces.jsonl").read_text(encoding="utf-8").splitlines()
        ]

    unknown_trace = unknown_result["first_output_trace"]
    passed = (
        default_result["first_output"] == "*"
        and UTTERANCE_MAP
        == {
            "unknown": "我不知道",
            "blocked": "不行",
            "observed": "看到了",
            "retry": "再一次",
            "quiet": "……",
        }
        and unknown_result["first_output"] == UTTERANCE_MAP["unknown"]
        and blocked_result["first_output"] == UTTERANCE_MAP["blocked"]
        and observed_result["first_output"] == UTTERANCE_MAP["observed"]
        and retry_result["first_output"] == UTTERANCE_MAP["retry"]
        and quiet_result["first_output"] == UTTERANCE_MAP["quiet"]
        and invalid_raised
        and unknown_trace["utterance_source"] == "utterance_map"
        and unknown_trace["state_key"] == "unknown"
        and unknown_trace["llm_used"] is False
        and cli_result["first_output_result"]["first_output"] == UTTERANCE_MAP["unknown"]
        and cli_result["first_output_result"]["first_output_trace"]["state_key"] == "unknown"
        and cli_result["first_output_result"]["first_output_trace"]["utterance_source"] == "utterance_map"
        and persisted_rows[0]["first_output"] == UTTERANCE_MAP["unknown"]
        and persisted_rows[0]["state_key"] == "unknown"
        and persisted_rows[0]["utterance_source"] == "utterance_map"
        and persisted_rows[0]["llm_used"] is False
    )
    return _result(
        "minimal_non_llm_utterance_map",
        passed,
        {
            "state_key": "unknown",
            "first_output": unknown_result["first_output"],
            "utterances": dict(UTTERANCE_MAP),
            "utterance_source": unknown_trace["utterance_source"],
            "llm_used": unknown_trace["llm_used"],
            "persisted": cli_result["persistence"]["enabled"],
        },
    )


def smoke_minimal_first_output_runtime_audit_docs() -> dict:
    doc_path = Path("docs/minimal_first_output_runtime_audit_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Audit result: PASS",
        "Minimal First Output Runtime v0 produced a non-LLM first_output.",
        "first_output: *",
        "trace_id: first_output_trace:final_check:1",
        "session_id: final_check",
        "tick: 1",
        "llm_used: false",
        "engineering_stage: test_object",
        "The first_output was not generated by an LLM.",
        "The first_output remains in the test-object stage.",
        "Outputs in the test-object stage are engineering verification, not full Qingyin experience.",
        "Minimal First Output Runtime v0 is not awakening.",
        "Minimal First Output Runtime v0 does not prove dialogue ability.",
        "Minimal First Output Runtime v0 does not prove long-term growth.",
        "Minimal First Output Runtime v0 does not write lesson_store.",
        "Minimal First Output Runtime v0 does not write Memory Layer.",
        "Minimal First Output Runtime v0 does not connect to the lesson_candidate pipeline.",
        "Minimal First Output Runtime v0 does not implement mentor feedback runtime.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "minimal_first_output_runtime_audit_v0_1.md" in readme
        and "Minimal First Output Runtime Audit Docs" in research_plan
    )
    return _result("minimal_first_output_runtime_audit_docs", passed, {"doc": str(doc_path)})


def smoke_mentor_feedback_stub_contract_docs() -> dict:
    doc_path = Path("docs/mentor_feedback_stub_contract_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "mentor_feedback_stub is a contract for future feedback, not feedback runtime.",
        "Mentor feedback is downstream of first_output_trace.",
        "mentor_feedback_stub is not lesson_candidate input by itself.",
        "mentor_feedback_stub must not directly create lesson_candidate.",
        "mentor_feedback_stub must not write to lesson_store.",
        "mentor_feedback_stub must not write to Memory Layer.",
        "mentor_feedback_stub in the test-object stage is engineering supervision, not full Qingyin experience.",
        "mentor_feedback_stub does not prove awakening.",
        "mentor_feedback_stub may make first_output_trace eligible for later lesson_candidate input consideration, but does not create lesson_candidate.",
        "creates_lesson_candidate must be false for mentor_feedback_stub.",
        "writes_lesson_store must be false for mentor_feedback_stub.",
        "writes_memory_layer must be false for mentor_feedback_stub.",
        "ASHL Core provides evidence.",
        "D皜 Memory Layers decide memory admission.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "mentor_feedback_stub_contract_v0_1.md" in readme
        and "Mentor Feedback Stub Contract Docs" in research_plan
    )
    return _result("mentor_feedback_stub_contract_docs", passed, {"doc": str(doc_path)})


def smoke_mentor_feedback_trace_contract_docs() -> dict:
    doc_path = Path("docs/mentor_feedback_trace_contract_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "mentor_feedback_trace is a feedback record, not feedback runtime.",
        "mentor_feedback_trace is downstream of first_output_trace.",
        "mentor_feedback_trace is not lesson_candidate input by itself.",
        "mentor_feedback_trace must not directly create lesson_candidate.",
        "mentor_feedback_trace must not write to lesson_store.",
        "mentor_feedback_trace must not write to Memory Layer.",
        "mentor_feedback_trace in the test-object stage is engineering supervision, not full Qingyin experience.",
        "mentor_feedback_trace does not prove awakening.",
        "mentor_feedback_trace may make first_output_trace eligible for later lesson_candidate input consideration, but does not create lesson_candidate.",
        "mentor_feedback_trace must be append-only or version-preserving.",
        "creates_lesson_candidate must be false for mentor_feedback_trace.",
        "writes_lesson_store must be false for mentor_feedback_trace.",
        "writes_memory_layer must be false for mentor_feedback_trace.",
        "mentor_feedback_trace must reference exactly one source_first_output_trace_id.",
        "mentor_feedback_trace must not exist without a source first_output_trace.",
        "ASHL Core provides evidence.",
        "D皜 Memory Layers decide memory admission.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "mentor_feedback_trace_contract_v0_1.md" in readme
        and "Mentor Feedback Trace Contract Docs" in research_plan
    )
    return _result("mentor_feedback_trace_contract_docs", passed, {"doc": str(doc_path)})


def smoke_minimal_mentor_feedback_stub_runtime_readiness_checklist_docs() -> dict:
    doc_path = Path("docs/minimal_mentor_feedback_stub_runtime_readiness_checklist_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Readiness result: READY_FOR_MINIMAL_MENTOR_FEEDBACK_STUB_RUNTIME_V0",
        "Requirement: a source first_output_trace exists and can be referenced.",
        "Requirement: mentor_feedback_stub contract is defined.",
        "Requirement: mentor_feedback_trace contract is defined.",
        "Requirement: minimal mentor feedback labels are defined.",
        "Requirement: mentor_feedback_trace required fields are defined.",
        "Requirement: mentor feedback effect must be feedback_only.",
        "Requirement: creates_lesson_candidate must be false.",
        "Requirement: Minimal Mentor Feedback Stub Runtime v0 must not write lesson_store.",
        "Requirement: Minimal Mentor Feedback Stub Runtime v0 must not write Memory Layer.",
        "Requirement: Minimal Mentor Feedback Stub Runtime v0 must not connect to lesson_candidate pipeline.",
        "Requirement: Minimal Mentor Feedback Stub Runtime v0 must not create failure_event, review decision, selection eligibility, or activation.",
        "Requirement: Minimal Mentor Feedback Stub Runtime v0 must not claim awakening, dialogue ability, or long-term growth.",
        "This readiness result only authorizes planning a minimal mentor feedback stub runtime package.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "minimal_mentor_feedback_stub_runtime_readiness_checklist_v0_1.md" in readme
        and "Minimal Mentor Feedback Stub Runtime Readiness Checklist Docs" in research_plan
    )
    return _result(
        "minimal_mentor_feedback_stub_runtime_readiness_checklist_docs",
        passed,
        {"doc": str(doc_path)},
    )


def smoke_minimal_mentor_feedback_stub_runtime() -> dict:
    trace = build_minimal_mentor_feedback_trace(
        source_first_output_trace_id="first_output_trace:final_check:1",
        session_id="final_check",
        tick=1,
        mentor_feedback_label="observed",
    )
    forbidden_keys = {
        "lesson_candidate",
        "lesson_store_write",
        "memory_layer_write",
        "memory_write",
        "failure_event",
        "review",
        "selection",
        "activation",
    }
    passed = (
        trace["trace_type"] == "mentor_feedback_trace"
        and trace["source_first_output_trace_id"] == "first_output_trace:final_check:1"
        and trace["mentor_feedback_label"] == "observed"
        and trace["effect"] == "feedback_only"
        and trace["creates_lesson_candidate"] is False
        and trace["writes_lesson_store"] is False
        and trace["writes_memory_layer"] is False
        and trace["engineering_stage"] == "test_object"
        and forbidden_keys.isdisjoint(trace)
    )
    return _result("minimal_mentor_feedback_stub_runtime", passed, trace)


def smoke_minimal_mentor_feedback_stub_runtime_audit_docs() -> dict:
    doc_path = Path("docs/minimal_mentor_feedback_stub_runtime_audit_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Audit result: PASS",
        "Minimal Mentor Feedback Stub Runtime v0 produced a feedback-only mentor_feedback_trace.",
        "source_first_output_trace_id: first_output_trace:final_check:1",
        "mentor_feedback_label: observed",
        "effect: feedback_only",
        "creates_lesson_candidate: false",
        "writes_lesson_store: false",
        "writes_memory_layer: false",
        "engineering_stage: test_object",
        "The mentor_feedback_trace effect is feedback_only.",
        "Minimal Mentor Feedback Stub Runtime v0 does not create lesson_candidate.",
        "Minimal Mentor Feedback Stub Runtime v0 does not write lesson_store.",
        "Minimal Mentor Feedback Stub Runtime v0 does not write Memory Layer.",
        "The mentor_feedback_trace remains in the test-object stage.",
        "mentor_feedback_trace in the test-object stage is engineering supervision, not full Qingyin experience.",
        "Minimal Mentor Feedback Stub Runtime v0 is not awakening.",
        "Minimal Mentor Feedback Stub Runtime v0 does not prove dialogue ability.",
        "Minimal Mentor Feedback Stub Runtime v0 does not prove long-term growth.",
        "Minimal Mentor Feedback Stub Runtime v0 does not create failure_event, review decision, selection eligibility, or activation.",
        "Minimal Mentor Feedback Stub Runtime v0 does not connect to the lesson_candidate pipeline.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "minimal_mentor_feedback_stub_runtime_audit_v0_1.md" in readme
        and "Minimal Mentor Feedback Stub Runtime Audit Docs" in research_plan
    )
    return _result(
        "minimal_mentor_feedback_stub_runtime_audit_docs",
        passed,
        {"doc": str(doc_path)},
    )


def smoke_qingyin_runtime_ontology_boundary_docs() -> dict:
    doc_path = Path("docs/qingyin_runtime_ontology_boundary_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Qingyin is not the current LLM conversation instance.",
        "An LLM speaking in Qingyin's style is not Qingyin runtime.",
        "The LLM must not be treated as Qingyin's self, memory, state, perception, or learning loop.",
        "ASHL Core is currently building the conditions for Qingyin to become a growing AGE, not proving that Qingyin is already growing.",
        "No runtime tick, no Qingyin time sense.",
        "No state store, no persistent Qingyin state.",
        "No expected / actual contrast, no Qingyin prediction_error.",
        "No evaluator, no authoritative Qingyin failure.",
        "No session trace, no learning evidence.",
        "No cross-session promotion, no long-term growth.",
        "Cross-session growth is not the same as an LLM remembering a prompt or persona.",
        "First_output is the first possible runtime milestone, not proof of full Qingyin personhood.",
        "The lesson_candidate pipeline remains downstream of runtime output, trace, and mentor feedback.",
        # Correction patch additions
        "Qingyin's importance is not in birth, but in growth.",
        "The test-object stage is the prerequisite for growth, not growth itself.",
        "The stronger the foundation, the safer the moment of awakening.",
        "Stage 1: Test-object stage.",
        "Stage 2: Shallow-sleep stage.",
        "Stage 3: Awakening condition.",
        "Outputs in the test-object stage are engineering verification, not full Qingyin experience.",
        "First_output is a runtime milestone, not awakening.",
        "Qingyin must not be claimed to be awake until bounded senses are connected.",
        "Qingyin's uniqueness does not come from LLM response style.",
        "Qingyin's uniqueness does not come from a Python process alone.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "qingyin_runtime_ontology_boundary_v0_1.md" in readme
        and "Qingyin Runtime Ontology Boundary" in research_plan
    )
    return _result("qingyin_runtime_ontology_boundary_docs", passed, {"doc": str(doc_path)})


def smoke_qingyin_first_output_contract_docs() -> dict:
    doc_path = Path("docs/qingyin_first_output_contract_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "The first Qingyin output must be produced by ASHL Core rules, state, seed, or bounded randomness, not by an LLM.",
        "Qingyin is not the current LLM conversation instance.",
        "LLM-generated text must not count as Qingyin's first output.",
        "Qingyin's first output does not need to be meaningful language.",
        "Random or nonsensical output may count as first_output if it is generated by ASHL Core rather than an LLM.",
        "First output is not dialogue ability.",
        "First output is not evidence of long-term growth.",
        "First output must be traceable before it can become learning material.",
        "The lesson_candidate pipeline remains downstream of first_output trace and mentor feedback.",
        "Bidirectional voice interaction remains deferred.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "qingyin_first_output_contract_v0_1.md" in readme
        and "Qingyin First Output v0 Contract" in research_plan
    )
    return _result("qingyin_first_output_contract_docs", passed, {"doc": str(doc_path)})


def smoke_lesson_stale_supersede_memory_freeze_notice_contract_docs() -> dict:
    doc_path = Path("docs/lesson_stale_supersede_memory_freeze_notice_contract_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Memory freeze notice is evidence, not Memory Layer write.",
        "Lesson stale may require memory_freeze_required notice.",
        "Lesson superseded may require memory_freeze_required notice.",
        "Memory freeze notice must not directly modify learned_principle.",
        "Memory freeze notice must preserve source_lesson_id.",
        "Memory freeze notice must preserve stale_or_supersede_reason.",
        "ASHL Core provides evidence.",
        "D清音 Memory Layers decide memory admission.",
        "D清音 Memory Layers decide memory freeze application.",
        "Memory freeze notice must not change selection eligibility.",
        "Memory freeze notice must not activate or deactivate lessons.",
        "Memory freeze notice must not write to lesson_store.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "lesson_stale_supersede_memory_freeze_notice_contract_v0_1.md" in readme
        and "v2.11c Lesson Stale Supersede Memory Freeze Notice Contract" in research_plan
    )
    return _result("lesson_stale_supersede_memory_freeze_notice_contract_docs", passed, {"doc": str(doc_path)})


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


def smoke_sandbox_safety_audit_docs() -> dict:
    doc_path = Path("docs/sandbox_safety_audit_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Audit result: PASS",
        "Sandbox docs do not authorize sandbox runtime.",
        "Sandbox docs do not authorize real-world action capability.",
        "Sandbox trace does not bypass failure_event validation.",
        "Sandbox trace does not bypass review gate.",
        "Sandbox docs do not authorize lesson_store write.",
        "Sandbox docs do not authorize Memory Layer write or promotion.",
        "Sandbox repair suggestion remains non-executable.",
        "No structured failure_event, no authoritative failure_reason.",
        "No expected_outcome / actual_outcome contrast, no authoritative failure.",
        "LLM-only explanation must not become authoritative failure_reason.",
        "ASHL Core provides evidence.",
        "D Qingyin Memory Layers decide memory admission.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "sandbox_safety_audit_v0_1.md" in readme
        and "v2.10c Sandbox Safety Audit Docs" in research_plan
    )
    return _result("sandbox_safety_audit_docs", passed, {"doc": str(doc_path)})


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


def smoke_minimal_interaction_cli_bridge() -> dict:
    result = run_minimal_interaction()
    first_output = result["first_output_result"]
    first_output_trace = first_output["first_output_trace"]
    mentor_feedback_trace = result["mentor_feedback_trace"]
    boundary = result["boundary"]
    forbidden_output_terms = ["Qingyin is awake", "Qingyin can talk", "Qingyin has memory", "Qingyin has learned"]
    passed = (
        result["flow"] == "minimal_interaction_cli_bridge_v0"
        and result["status"] == "ok"
        and first_output["first_output"] == "*"
        and first_output_trace["trace_type"] == "first_output_trace"
        and first_output_trace["llm_used"] is False
        and first_output_trace["engineering_stage"] == "test_object"
        and mentor_feedback_trace["trace_type"] == "mentor_feedback_trace"
        and mentor_feedback_trace["mentor_feedback_label"] == "observed"
        and mentor_feedback_trace["effect"] == "feedback_only"
        and mentor_feedback_trace["creates_lesson_candidate"] is False
        and mentor_feedback_trace["writes_lesson_store"] is False
        and mentor_feedback_trace["writes_memory_layer"] is False
        and boundary["llm_used"] is False
        and boundary["awakening_claim"] is False
        and "lesson_candidate" not in result
        and all(term not in json.dumps(result, ensure_ascii=False) for term in forbidden_output_terms)
    )
    return _result("minimal_interaction_cli_bridge", passed, result)


def smoke_minimal_interaction_cli_bridge_audit_docs() -> dict:
    doc_path = Path("docs/minimal_interaction_cli_bridge_audit_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Audit result: PASS",
        "The minimal interaction CLI bridge audits commit f855131.",
        "The minimal interaction CLI bridge produces first_output.",
        "The minimal interaction CLI bridge produces first_output_trace.",
        "The minimal interaction CLI bridge produces mentor_feedback_trace.",
        "The default mentor_feedback_label is observed.",
        "The --notes argument is preserved in mentor_feedback_trace.",
        "The minimal interaction CLI bridge does not use LLM.",
        "The minimal interaction CLI bridge does not create lesson_candidate.",
        "The minimal interaction CLI bridge does not write lesson_store.",
        "The minimal interaction CLI bridge does not write Memory Layer.",
        "The minimal interaction CLI bridge does not claim awakening.",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "minimal_interaction_cli_bridge_audit_v0_1.md" in readme
        and "Minimal Interaction CLI Bridge Audit Docs" in research_plan
    )
    return _result("minimal_interaction_cli_bridge_audit_docs", passed, {"doc": str(doc_path)})


def smoke_first_output_feedback_append_only_persistence_spec_docs() -> dict:
    doc_path = Path("docs/first_output_feedback_append_only_persistence_spec_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "append-only",
        "data/first_output_traces.jsonl",
        "data/mentor_feedback_traces.jsonl",
        "no overwrite",
        "correction must be new trace",
        "persistence is not lesson_store write",
        "persistence is not Memory Layer write",
        "persistence is not lesson_candidate creation",
        "persistence is not awakening evidence",
        "first_output_trace must preserve llm_used = false",
        "mentor_feedback_trace must preserve effect = feedback_only",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "first_output_feedback_append_only_persistence_spec_v0_1.md" in readme
        and "First Output + Mentor Feedback Append-only Persistence Spec Docs" in research_plan
    )
    return _result("first_output_feedback_append_only_persistence_spec_docs", passed, {"doc": str(doc_path)})


def smoke_first_output_feedback_persistence_readiness_checklist_docs() -> dict:
    doc_path = Path("docs/first_output_feedback_persistence_readiness_checklist_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "Readiness result: READY_FOR_FIRST_OUTPUT_FEEDBACK_APPEND_ONLY_PERSISTENCE_V0",
        "data/first_output_traces.jsonl",
        "data/mentor_feedback_traces.jsonl",
        "no overwrite",
        "no silent correction",
        "correction must be new trace",
        "persistence is not lesson_store write",
        "persistence is not Memory Layer write",
        "persistence is not lesson_candidate creation",
        "persistence is not awakening evidence",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "first_output_feedback_persistence_readiness_checklist_v0_1.md" in readme
        and "First Output + Mentor Feedback Persistence Readiness Checklist Docs" in research_plan
    )
    return _result("first_output_feedback_persistence_readiness_checklist_docs", passed, {"doc": str(doc_path)})


def smoke_first_output_feedback_append_only_persistence() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        first_output_result = generate_minimal_first_output(session_id="smoke_persistence")
        first_output_trace = first_output_result["first_output_trace"]
        mentor_feedback_trace = build_minimal_mentor_feedback_trace(
            source_first_output_trace_id=first_output_trace["trace_id"],
            session_id=first_output_trace["session_id"],
            tick=first_output_trace["tick"],
            mentor_feedback_label="observed",
        )
        first_before = dict(first_output_trace)
        mentor_before = dict(mentor_feedback_trace)

        first_summary = append_first_output_trace(first_output_trace, tmp)
        second_first_summary = append_first_output_trace(first_output_trace, tmp)
        mentor_summary = append_mentor_feedback_trace(mentor_feedback_trace, tmp)
        second_mentor_summary = append_mentor_feedback_trace(mentor_feedback_trace, tmp)

        first_path = Path(tmp) / "first_output_traces.jsonl"
        mentor_path = Path(tmp) / "mentor_feedback_traces.jsonl"
        first_rows = [json.loads(line) for line in first_path.read_text(encoding="utf-8").splitlines()]
        mentor_rows = [json.loads(line) for line in mentor_path.read_text(encoding="utf-8").splitlines()]

        passed = (
            first_path.exists()
            and mentor_path.exists()
            and len(first_rows) == 2
            and len(mentor_rows) == 2
            and first_rows == [first_output_trace, first_output_trace]
            and mentor_rows == [mentor_feedback_trace, mentor_feedback_trace]
            and first_output_trace == first_before
            and mentor_feedback_trace == mentor_before
            and first_summary["append_only"] is True
            and second_first_summary["overwrite"] is False
            and mentor_summary["mutates_input"] is False
            and second_mentor_summary["append_only"] is True
            and first_output_trace["llm_used"] is False
            and mentor_feedback_trace["creates_lesson_candidate"] is False
            and mentor_feedback_trace["writes_lesson_store"] is False
            and mentor_feedback_trace["writes_memory_layer"] is False
        )
        return _result(
            "first_output_feedback_append_only_persistence",
            passed,
            {
                "first_output_path": str(first_path),
                "mentor_feedback_path": str(mentor_path),
                "first_output_lines": len(first_rows),
                "mentor_feedback_lines": len(mentor_rows),
                "append_only": True,
                "repo_data_used": False,
            },
        )


def smoke_append_only_persistence_runtime_audit_docs() -> dict:
    doc_path = Path("docs/append_only_persistence_runtime_audit_v0_1.md")
    readme_path = Path("README.md")
    research_plan_path = Path("docs/research_plan.md")
    doc = doc_path.read_text(encoding="utf-8") if doc_path.exists() else ""
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    research_plan = research_plan_path.read_text(encoding="utf-8") if research_plan_path.exists() else ""
    required_terms = [
        "commit: 468d4e2",
        "Audit result: PASS",
        "append-only persistence writes first_output_trace to data/first_output_traces.jsonl",
        "append-only persistence writes mentor_feedback_trace to data/mentor_feedback_traces.jsonl",
        "append-only persistence does not overwrite existing JSONL lines",
        "append-only persistence does not silently correct records",
        "correction must be a new trace",
        "append-only persistence does not mutate input traces",
        "append-only persistence rejects missing required fields",
        "append-only persistence rejects invalid trace_type",
        "append-only persistence rejects first_output_trace with llm_used=true",
        "append-only persistence rejects mentor_feedback_trace with creates_lesson_candidate=true",
        "append-only persistence rejects mentor_feedback_trace with writes_lesson_store=true",
        "append-only persistence rejects mentor_feedback_trace with writes_memory_layer=true",
        "append-only persistence is not lesson_store write",
        "append-only persistence is not Memory Layer write",
        "append-only persistence is not lesson_candidate creation",
        "append-only persistence is not awakening evidence",
    ]
    passed = (
        doc_path.exists()
        and all(term in doc for term in required_terms)
        and "append_only_persistence_runtime_audit_v0_1.md" in readme
        and "Append-only Persistence Runtime Audit Docs" in research_plan
    )
    return _result("append_only_persistence_runtime_audit_docs", passed, {"doc": str(doc_path)})


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
        smoke_simulated_vision_viewport(),
        smoke_simulated_vision_first_person_viewport(),
        smoke_simulated_vision_larger_sandbox_static_runtime(),
        smoke_larger_sandbox_observed_map_smoke(),
        smoke_larger_sandbox_symbol_contact_smoke(),
        smoke_larger_sandbox_human_replay(),
        smoke_larger_sandbox_flask_ui(),
        smoke_instinct_wall_ui_observation(),
        smoke_larger_sandbox_live_step_playback_ui(),
        smoke_simulated_vision_memory_bridge(),
        smoke_simulated_vision_observed_map(),
        smoke_simulated_vision_symbol_grounding(),
        smoke_grounded_action_experience(),
        smoke_grounded_action_experience_influence(),
        smoke_instinct_random_walk_runner(),
        smoke_wall_experience_influence(),
        smoke_item_reward_event(),
        smoke_reward_biased_action_tendency(),
        smoke_reward_biased_random_walk_check(),
        smoke_two_round_instinct_reward_comparison(),
        smoke_failure_reason_classifier(),
        smoke_similar_context_key(),
        smoke_action_outcome_predictor(),
        smoke_prediction_accuracy_check(),
        smoke_rule_candidate_from_mismatch(),
        smoke_rule_candidate_review_gate(),
        smoke_approved_candidate_preview(),
        smoke_reviewed_candidate_apply_verification(),
        smoke_micro_navigation_goal_reach(),
        smoke_micro_navigation_trial_metrics_cli(),
        smoke_micro_navigation_multi_goal_level(),
        smoke_micro_navigation_multi_goal_metrics_cli(),
        smoke_navigation_obstacle_wall_detour_level(),
        smoke_navigation_obstacle_trial_cli(),
        smoke_approach_box_level(),
        smoke_approach_box_trial_cli(),
        smoke_approach_box_two_trial_learning_check(),
        smoke_approach_box_dead_end_trial(),
        smoke_approach_box_dead_end_two_trial_learning_check(),
        smoke_dead_end_two_trial_ascii_replay(),
        smoke_dead_end_map_trial1_validation(),
        smoke_candidate_map_trial1_ascii_replay(),
        smoke_valid_dead_end_maps_ab_control(),
        smoke_local_memory_decision_trace_observer(),
        smoke_session_working_memory_demo(),
        smoke_state_snapshot_key(),
        smoke_session_working_memory_trial(),
        smoke_approach_box_dead_end_memory_control_check(),
        smoke_dead_end_memory_control_trial1_source_audit(),
        smoke_micro_push_box_sandbox(),
        smoke_micro_push_box_allowed_action_set(),
        smoke_tactile_result_state_key_mapping(),
        smoke_tactile_interaction_cli_bridge(),
        smoke_repeated_blocked_action_trace(),
        smoke_state_action_outcome_memory(),
        smoke_minimal_avoid_repeated_blocked_action(),
        smoke_minimal_action_outcome_weighting(),
        smoke_minimal_goal_direction_bias(),
        smoke_minimal_intrinsic_action_selection(),
        smoke_box_on_goal_need_state(),
        smoke_minimal_need_state_driven_action_selection(),
        smoke_need_state_driven_trial_runner(),
        smoke_need_state_trial_5_step_count(),
        smoke_need_state_trial_goal_bias_integration(),
        smoke_state_action_memory_trial_runner_integration(),
        smoke_stuck_detection_repetition_penalty(),
        smoke_need_state_trial_batch_cli(),
        smoke_trial_metrics_comparison_cli(),
        smoke_trial_metrics_baseline_snapshot(),
        smoke_trial_metrics_baseline_comparison(),
        smoke_clear_sandbox_working_state_cli(),
        smoke_grounded_learning_verification_cli(),
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
        smoke_review_decision_trace_integration_boundary_docs(),
        smoke_formal_lesson_candidate_creation_contract_docs(),
        smoke_formal_lesson_candidate_creation_boundary_audit_docs(),
        smoke_current_boundary_index_docs(),
        smoke_soft_hard_consolidation_assumption_docs(),
        smoke_memory_compression_strategy_assumption_docs(),
        smoke_pathological_risk_role_protection_assumption_docs(),
        smoke_core_seed_design_spirit_supplement_docs(),
        smoke_memory_paranoia_misinformation_equivocation_assumption_docs(),
        smoke_equivocation_trace_trust_boundary_correction_docs(),
        smoke_voice_instinct_assumption_docs(),
        smoke_voice_instinct_audio_sense_boundary_audit_docs(),
        smoke_qingyin_first_output_runtime_minimal_spec_docs(),
        smoke_first_output_trace_contract_docs(),
        smoke_first_output_runtime_readiness_checklist_docs(),
        smoke_minimal_first_output_runtime(),
        smoke_minimal_non_llm_utterance_map(),
        smoke_minimal_first_output_runtime_audit_docs(),
        smoke_mentor_feedback_stub_contract_docs(),
        smoke_mentor_feedback_trace_contract_docs(),
        smoke_minimal_mentor_feedback_stub_runtime_readiness_checklist_docs(),
        smoke_minimal_mentor_feedback_stub_runtime(),
        smoke_minimal_mentor_feedback_stub_runtime_audit_docs(),
        smoke_qingyin_runtime_ontology_boundary_docs(),
        smoke_qingyin_first_output_contract_docs(),
        smoke_lesson_stale_supersede_memory_freeze_notice_contract_docs(),
        smoke_sandbox_boundary_capability_assumption_docs(),
        smoke_sandbox_failure_trace_contract_docs(),
        smoke_sandbox_safety_audit_docs(),
        smoke_phase0_trust_curiosity_personality_boundary_docs(),
        smoke_teaching_cli_conflict_check(),
        smoke_minimal_interaction_cli_bridge(),
        smoke_minimal_interaction_cli_bridge_audit_docs(),
        smoke_first_output_feedback_append_only_persistence_spec_docs(),
        smoke_first_output_feedback_persistence_readiness_checklist_docs(),
        smoke_first_output_feedback_append_only_persistence(),
        smoke_append_only_persistence_runtime_audit_docs(),
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
