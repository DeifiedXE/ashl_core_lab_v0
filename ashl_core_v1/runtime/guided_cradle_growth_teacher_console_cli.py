"""CLI for the guided ASHL Core v1 cradle growth teacher console."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    apply_advisory_readback_ordering_demo_from_guided_cradle_growth_console,
    apply_final_action_demo_from_guided_cradle_growth_console,
    apply_selected_action_demo_from_guided_cradle_growth_console,
    audit_reviewed_concept_readback_loop_demo_from_guided_cradle_growth_console,
    admit_reviewed_concept_memory_demo_from_guided_cradle_growth_console,
    audit_reviewed_concept_readback_hint_influence_demo_from_guided_cradle_growth_console,
    apply_reviewed_concept_readback_hints_demo_from_guided_cradle_growth_console,
    apply_readback_from_guided_cradle_growth_console,
    audit_first_action_reviewed_concept_loop_demo_from_guided_cradle_growth_console,
    audit_continuous_event_loop_timeline_from_guided_cradle_growth_console,
    build_reviewed_concept_hint_candidates_demo_from_guided_cradle_growth_console,
    build_state_handoff_from_guided_cradle_growth_console,
    build_loop_evidence_from_guided_cradle_growth_console,
    build_memory_trace_from_guided_cradle_growth_console,
    build_reviewed_concept_demo_from_guided_cradle_growth_console,
    bridge_reviewed_concept_memory_demo_from_guided_cradle_growth_console,
    build_feedback_candidate_from_task_closure_demo_from_guided_cradle_growth_console,
    build_concept_candidate_from_feedback_demo_from_guided_cradle_growth_console,
    build_state_restore_preview_from_guided_cradle_growth_console,
    close_from_outcome_demo_from_guided_cradle_growth_console,
    close_last_run_from_guided_cradle_growth_console,
    create_reviewed_concept_hint_records_demo_from_guided_cradle_growth_console,
    create_state_resume_handoff_from_guided_cradle_growth_console,
    draft_demo_concept_from_guided_cradle_growth_console,
    evaluate_sense_outcome_demo_from_guided_cradle_growth_console,
    execute_direct_command_demo_from_guided_cradle_growth_console,
    get_guided_cradle_growth_status,
    guided_cradle_growth_next_step,
    list_state_handoff_bookmarks_from_guided_cradle_growth_console,
    list_candidates_from_guided_cradle_growth_console,
    preview_reviewed_concept_hint_application_demo_from_guided_cradle_growth_console,
    preview_readback_from_guided_cradle_growth_console,
    propose_selected_action_demo_from_guided_cradle_growth_console,
    preview_reviewed_concept_readback_demo_from_guided_cradle_growth_console,
    preview_reviewed_concept_application_data_from_guided_cradle_growth_console,
    preview_reviewed_concept_memory_trace_from_guided_cradle_growth_console,
    preview_reviewed_concept_routing_from_guided_cradle_growth_console,
    prepare_reviewed_concept_hints_demo_from_guided_cradle_growth_console,
    prepare_reviewed_concept_hint_application_demo_from_guided_cradle_growth_console,
    prepare_reviewed_concept_demo_from_guided_cradle_growth_console,
    refine_demo_concept_from_guided_cradle_growth_console,
    review_candidate_from_guided_cradle_growth_console,
    replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console,
    review_reviewed_concept_hint_candidates_demo_from_guided_cradle_growth_console,
    review_reviewed_concept_hint_application_demo_from_guided_cradle_growth_console,
    refine_feedback_concept_candidate_demo_from_guided_cradle_growth_console,
    integrate_feedback_reviewed_concept_demo_from_guided_cradle_growth_console,
    rollback_advisory_readback_ordering_demo_from_guided_cradle_growth_console,
    rollback_selected_action_proposal_demo_from_guided_cradle_growth_console,
    rollback_selected_action_demo_from_guided_cradle_growth_console,
    rollback_final_action_demo_from_guided_cradle_growth_console,
    observe_sandbox_execution_demo_from_guided_cradle_growth_console,
    restore_sandbox_execution_demo_from_guided_cradle_growth_console,
    run_case_from_guided_cradle_growth_console,
    run_growth_readiness_audit_from_guided_cradle_growth_console,
    run_readback_contrast_from_guided_cradle_growth_console,
    run_state_resume_continuity_audit_from_guided_cradle_growth_console,
    run_state_resume_precheck_from_guided_cradle_growth_console,
    show_host_body_camera_port_demo_from_guided_cradle_growth_console,
    show_host_body_camera_change_event_demo_from_guided_cradle_growth_console,
    show_host_body_camera_frame_event_demo_from_guided_cradle_growth_console,
    show_host_body_idle_event_demo_from_guided_cradle_growth_console,
    show_host_body_camera_runtime_bridge_demo_from_guided_cradle_growth_console,
    show_host_body_idle_runtime_bridge_demo_from_guided_cradle_growth_console,
    show_host_body_home_empty_surface_demo_from_guided_cradle_growth_console,
    show_host_body_home_event_surface_demo_from_guided_cradle_growth_console,
    show_host_body_home_port_surface_demo_from_guided_cradle_growth_console,
    show_host_body_home_runtime_bridge_surface_demo_from_guided_cradle_growth_console,
    show_host_body_home_status_lights_demo_from_guided_cradle_growth_console,
    show_host_body_home_surface_demo_from_guided_cradle_growth_console,
    show_host_body_home_surface_readiness_from_guided_cradle_growth_console,
    show_host_body_home_teacher_surface_demo_from_guided_cradle_growth_console,
    show_host_body_trace_history_empty_demo_from_guided_cradle_growth_console,
    show_host_body_trace_history_full_demo_from_guided_cradle_growth_console,
    show_host_body_trace_history_index_demo_from_guided_cradle_growth_console,
    show_host_body_trace_history_readiness_from_guided_cradle_growth_console,
    show_host_body_trace_history_recent_demo_from_guided_cradle_growth_console,
    show_host_body_trace_history_render_demo_from_guided_cradle_growth_console,
    show_host_body_internal_action_camera_interesting_demo_from_guided_cradle_growth_console,
    show_host_body_internal_action_observe_again_demo_from_guided_cradle_growth_console,
    show_host_body_internal_action_readiness_from_guided_cradle_growth_console,
    show_host_body_internal_action_teacher_review_demo_from_guided_cradle_growth_console,
    show_host_body_internal_action_uncertain_demo_from_guided_cradle_growth_console,
    show_host_body_internal_action_update_home_status_demo_from_guided_cradle_growth_console,
    show_host_body_identity_demo_from_guided_cradle_growth_console,
    show_host_body_internal_action_demo_from_guided_cradle_growth_console,
    show_host_body_internal_space_demo_from_guided_cradle_growth_console,
    show_host_body_mic_port_demo_from_guided_cradle_growth_console,
    show_host_body_mic_level_event_demo_from_guided_cradle_growth_console,
    show_host_body_mic_peak_event_demo_from_guided_cradle_growth_console,
    show_host_body_mic_runtime_bridge_demo_from_guided_cradle_growth_console,
    show_host_body_mixed_sensor_event_set_demo_from_guided_cradle_growth_console,
    show_host_body_mixed_runtime_bridge_demo_from_guided_cradle_growth_console,
    show_host_body_output_surface_demo_from_guided_cradle_growth_console,
    show_host_body_port_map_demo_from_guided_cradle_growth_console,
    show_host_body_readiness_demo_from_guided_cradle_growth_console,
    show_host_body_sensor_event_readiness_from_guided_cradle_growth_console,
    show_host_body_runtime_bridge_readiness_from_guided_cradle_growth_console,
    show_growth_readiness_from_guided_cradle_growth_console,
    show_concept_teaching_test_seed_from_guided_cradle_growth_console,
    show_concept_review_task_from_guided_cradle_growth_console,
    show_reviewed_concept_preparation_demo_from_guided_cradle_growth_console,
    show_reviewed_concept_demo_from_guided_cradle_growth_console,
    show_reviewed_concept_memory_candidates_from_guided_cradle_growth_console,
    show_reviewed_concept_application_data_from_guided_cradle_growth_console,
    show_reviewed_concept_hint_candidates_from_guided_cradle_growth_console,
    show_reviewed_concept_hint_candidate_review_from_guided_cradle_growth_console,
    show_reviewed_concept_hint_preparation_from_guided_cradle_growth_console,
    show_reviewed_concept_hint_preview_from_guided_cradle_growth_console,
    show_reviewed_concept_hint_records_from_guided_cradle_growth_console,
    show_reviewed_concept_hint_application_preview_from_guided_cradle_growth_console,
    show_reviewed_concept_hint_application_review_from_guided_cradle_growth_console,
    show_reviewed_concept_hint_application_preparation_from_guided_cradle_growth_console,
    show_reviewed_concept_readback_hint_application_from_guided_cradle_growth_console,
    show_reviewed_concept_readback_hint_influence_report_from_guided_cradle_growth_console,
    show_reviewed_concept_readback_hint_non_influence_audit_from_guided_cradle_growth_console,
    show_reviewed_concept_readback_hint_visibility_audit_from_guided_cradle_growth_console,
    show_reviewed_concept_readback_loop_boundary_from_guided_cradle_growth_console,
    show_reviewed_concept_readback_loop_evidence_chain_from_guided_cradle_growth_console,
    show_reviewed_concept_readback_loop_milestone_from_guided_cradle_growth_console,
    show_reviewed_concept_readback_loop_next_stage_readiness_from_guided_cradle_growth_console,
    show_first_action_reviewed_concept_loop_boundary_from_guided_cradle_growth_console,
    show_first_action_reviewed_concept_loop_evidence_chain_from_guided_cradle_growth_console,
    show_first_action_reviewed_concept_loop_milestone_from_guided_cradle_growth_console,
    show_first_action_reviewed_concept_loop_next_stage_readiness_from_guided_cradle_growth_console,
    show_first_action_reviewed_concept_loop_replay_verification_from_guided_cradle_growth_console,
    show_continuous_loop_event_tree_demo_from_guided_cradle_growth_console,
    show_continuous_loop_idle_demo_from_guided_cradle_growth_console,
    show_continuous_loop_nested_demo_from_guided_cradle_growth_console,
    show_continuous_loop_power_off_demo_from_guided_cradle_growth_console,
    show_event_dispatch_learning_demo_from_guided_cradle_growth_console,
    show_event_dispatch_memory_demo_from_guided_cradle_growth_console,
    show_event_dispatch_output_demo_from_guided_cradle_growth_console,
    show_event_dispatch_sense_demo_from_guided_cradle_growth_console,
    show_event_dispatch_state_demo_from_guided_cradle_growth_console,
    show_event_dispatch_task_demo_from_guided_cradle_growth_console,
    show_event_dispatch_thought_deferred_demo_from_guided_cradle_growth_console,
    show_bounded_handler_binding_learning_demo_from_guided_cradle_growth_console,
    show_bounded_handler_binding_memory_demo_from_guided_cradle_growth_console,
    show_bounded_handler_binding_outcome_demo_from_guided_cradle_growth_console,
    show_bounded_handler_binding_readiness_from_guided_cradle_growth_console,
    show_bounded_handler_binding_selected_trace_demo_from_guided_cradle_growth_console,
    show_bounded_handler_binding_sense_demo_from_guided_cradle_growth_console,
    show_fixed_closed_loop_playback_demo_from_guided_cradle_growth_console,
    show_fixed_closed_loop_playback_grouped_demo_from_guided_cradle_growth_console,
    show_fixed_closed_loop_playback_readiness_from_guided_cradle_growth_console,
    show_fixed_closed_loop_playback_render_from_guided_cradle_growth_console,
    show_integrated_loop_four_level_demo_from_guided_cradle_growth_console,
    show_integrated_loop_nested_sense_demo_from_guided_cradle_growth_console,
    show_integrated_loop_readiness_demo_from_guided_cradle_growth_console,
    show_integrated_loop_render_demo_from_guided_cradle_growth_console,
    show_integrated_loop_simple_demo_from_guided_cradle_growth_console,
    show_integrated_loop_thought_deferred_demo_from_guided_cradle_growth_console,
    show_nested_return_resume_demo_from_guided_cradle_growth_console,
    show_parent_resume_blocked_demo_from_guided_cradle_growth_console,
    show_parent_resume_fault_demo_from_guided_cradle_growth_console,
    show_parent_resume_success_demo_from_guided_cradle_growth_console,
    show_parent_resume_unknown_demo_from_guided_cradle_growth_console,
    show_reviewed_concept_readback_snapshot_from_guided_cradle_growth_console,
    show_advisory_readback_ordering_application_from_guided_cradle_growth_console,
    show_advisory_readback_ordering_audit_from_guided_cradle_growth_console,
    show_advisory_readback_ordering_rollback_from_guided_cradle_growth_console,
    show_advisory_readback_ordering_teacher_gate_from_guided_cradle_growth_console,
    show_selected_action_proposal_audit_from_guided_cradle_growth_console,
    show_selected_action_proposal_from_guided_cradle_growth_console,
    show_selected_action_proposal_rollback_from_guided_cradle_growth_console,
    show_selected_action_proposal_teacher_gate_from_guided_cradle_growth_console,
    show_selected_action_application_audit_from_guided_cradle_growth_console,
    show_selected_action_application_from_guided_cradle_growth_console,
    show_selected_action_application_teacher_gate_from_guided_cradle_growth_console,
    show_selected_action_rollback_from_guided_cradle_growth_console,
    show_final_action_application_audit_from_guided_cradle_growth_console,
    show_final_action_application_from_guided_cradle_growth_console,
    show_final_action_application_teacher_gate_from_guided_cradle_growth_console,
    show_final_action_rollback_from_guided_cradle_growth_console,
    show_direct_command_execution_audit_from_guided_cradle_growth_console,
    show_direct_command_execution_teacher_gate_from_guided_cradle_growth_console,
    show_direct_command_from_guided_cradle_growth_console,
    show_pre_execution_snapshot_from_guided_cradle_growth_console,
    show_sandbox_execution_from_guided_cradle_growth_console,
    show_sandbox_restore_from_guided_cradle_growth_console,
    show_sandbox_observation_from_guided_cradle_growth_console,
    show_sandbox_state_delta_from_guided_cradle_growth_console,
    show_observation_handoff_from_guided_cradle_growth_console,
    show_observation_safety_audit_from_guided_cradle_growth_console,
    show_outcome_task_closure_from_guided_cradle_growth_console,
    show_outcome_task_closure_rollback_from_guided_cradle_growth_console,
    show_outcome_task_closure_safety_audit_from_guided_cradle_growth_console,
    show_outcome_task_closure_summary_from_guided_cradle_growth_console,
    show_expected_effect_reference_from_guided_cradle_growth_console,
    show_feedback_candidate_evidence_from_guided_cradle_growth_console,
    show_feedback_candidate_from_guided_cradle_growth_console,
    show_feedback_candidate_safety_audit_from_guided_cradle_growth_console,
    show_feedback_candidate_set_from_guided_cradle_growth_console,
    show_feedback_concept_candidate_draft_from_guided_cradle_growth_console,
    show_feedback_concept_candidate_counterexample_check_from_guided_cradle_growth_console,
    show_feedback_concept_candidate_refinement_from_guided_cradle_growth_console,
    show_feedback_concept_candidate_refinement_safety_audit_from_guided_cradle_growth_console,
    show_feedback_concept_candidate_review_from_guided_cradle_growth_console,
    show_feedback_concept_candidate_rollback_from_guided_cradle_growth_console,
    show_feedback_concept_candidate_scope_check_from_guided_cradle_growth_console,
    show_feedback_concept_candidate_safety_audit_from_guided_cradle_growth_console,
    show_feedback_teacher_review_from_guided_cradle_growth_console,
    show_feedback_reviewed_concept_from_guided_cradle_growth_console,
    show_feedback_reviewed_concept_gate_from_guided_cradle_growth_console,
    show_feedback_reviewed_concept_readback_seed_from_guided_cradle_growth_console,
    show_feedback_reviewed_concept_rollback_from_guided_cradle_growth_console,
    show_feedback_reviewed_concept_safety_audit_from_guided_cradle_growth_console,
    show_feedback_reviewed_concept_working_readback_from_guided_cradle_growth_console,
    show_feedback_replay_action_chain_from_guided_cradle_growth_console,
    show_feedback_replay_audit_from_guided_cradle_growth_console,
    show_feedback_replay_contrast_from_guided_cradle_growth_console,
    show_feedback_replay_execution_from_guided_cradle_growth_console,
    show_feedback_replay_gate_from_guided_cradle_growth_console,
    show_feedback_replay_outcome_from_guided_cradle_growth_console,
    show_feedback_replay_rollback_from_guided_cradle_growth_console,
    show_feedback_replay_task_initialization_from_guided_cradle_growth_console,
    show_goal_delta_evaluation_from_guided_cradle_growth_console,
    show_outcome_evaluation_from_guided_cradle_growth_console,
    show_outcome_evaluation_safety_audit_from_guided_cradle_growth_console,
    show_reviewed_concept_memory_admission_from_guided_cradle_growth_console,
    show_loop_evidence_from_guided_cradle_growth_console,
    show_reviewed_concept_readback_preview_from_guided_cradle_growth_console,
    show_state_resume_precheck_from_guided_cradle_growth_console,
    show_state_handoff_from_guided_cradle_growth_console,
    list_state_resume_options_from_guided_cradle_growth_console,
    validate_state_resume_precheck_from_guided_cradle_growth_console,
    validate_state_handoff_from_guided_cradle_growth_console,
    select_authorize_state_resume_from_guided_cradle_growth_console,
    show_state_resume_authorization_from_guided_cradle_growth_console,
    show_state_restore_preview_from_guided_cradle_growth_console,
    show_state_resume_handoff_from_guided_cradle_growth_console,
    show_state_resume_continuity_audit_from_guided_cradle_growth_console,
    show_state_resume_selection_from_guided_cradle_growth_console,
    validate_state_resume_authorization_from_guided_cradle_growth_console,
    validate_state_resume_continuity_audit_from_guided_cradle_growth_console,
    validate_state_resume_handoff_from_guided_cradle_growth_console,
    validate_demo_concept_draft_from_guided_cradle_growth_console,
    validate_sandbox_observation_from_guided_cradle_growth_console,
    validate_sense_outcome_evaluation_from_guided_cradle_growth_console,
    validate_outcome_task_closure_from_guided_cradle_growth_console,
    validate_feedback_candidate_from_guided_cradle_growth_console,
    validate_feedback_concept_candidate_from_guided_cradle_growth_console,
    validate_feedback_concept_candidate_refinement_from_guided_cradle_growth_console,
    validate_feedback_reviewed_concept_integration_from_guided_cradle_growth_console,
    validate_feedback_reviewed_concept_replay_from_guided_cradle_growth_console,
    review_demo_concept_from_guided_cradle_growth_console,
    validate_demo_concept_review_from_guided_cradle_growth_console,
    validate_demo_refinement_from_guided_cradle_growth_console,
    validate_reviewed_concept_preparation_demo_from_guided_cradle_growth_console,
    validate_reviewed_concept_demo_from_guided_cradle_growth_console,
    validate_reviewed_concept_memory_preview_from_guided_cradle_growth_console,
    validate_reviewed_concept_memory_bridge_from_guided_cradle_growth_console,
    validate_reviewed_concept_admission_from_guided_cradle_growth_console,
    validate_reviewed_concept_hint_candidates_from_guided_cradle_growth_console,
    validate_reviewed_concept_hint_candidate_review_from_guided_cradle_growth_console,
    validate_reviewed_concept_hint_preparation_from_guided_cradle_growth_console,
    validate_reviewed_concept_hint_records_from_guided_cradle_growth_console,
    validate_reviewed_concept_hint_application_preview_from_guided_cradle_growth_console,
    validate_reviewed_concept_hint_application_review_from_guided_cradle_growth_console,
    validate_reviewed_concept_hint_application_preparation_from_guided_cradle_growth_console,
    validate_reviewed_concept_readback_hint_application_from_guided_cradle_growth_console,
    validate_reviewed_concept_readback_hint_influence_audit_from_guided_cradle_growth_console,
    validate_reviewed_concept_readback_loop_from_guided_cradle_growth_console,
    validate_first_action_reviewed_concept_loop_from_guided_cradle_growth_console,
    validate_continuous_event_loop_demo_from_guided_cradle_growth_console,
    validate_event_dispatch_demo_from_guided_cradle_growth_console,
    validate_bounded_handler_binding_from_guided_cradle_growth_console,
    validate_integrated_event_loop_demo_from_guided_cradle_growth_console,
    validate_host_body_port_map_from_guided_cradle_growth_console,
    validate_host_body_sensor_event_from_guided_cradle_growth_console,
    validate_host_body_runtime_bridge_from_guided_cradle_growth_console,
    validate_host_body_home_surface_from_guided_cradle_growth_console,
    validate_host_body_trace_history_from_guided_cradle_growth_console,
    validate_host_body_internal_action_choice_from_guided_cradle_growth_console,
    validate_parent_frame_resume_demo_from_guided_cradle_growth_console,
    validate_reviewed_concept_readback_preview_from_guided_cradle_growth_console,
    validate_advisory_readback_ordering_application_from_guided_cradle_growth_console,
    validate_selected_action_proposal_from_guided_cradle_growth_console,
    validate_selected_action_application_from_guided_cradle_growth_console,
    validate_final_action_application_from_guided_cradle_growth_console,
    validate_direct_command_execution_from_guided_cradle_growth_console,
    validate_fixed_closed_loop_playback_from_guided_cradle_growth_console,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 guided growth console")
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--state-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("growth-status")
    subparsers.add_parser("next-step")
    run_case = subparsers.add_parser("run-case")
    run_case.add_argument("--case-id", default="blocked_front_obstacle")
    run_case.add_argument("--max-ticks", type=int, default=5)
    subparsers.add_parser("close-last-run")
    subparsers.add_parser("list-candidates")
    review = subparsers.add_parser("review-candidate")
    review.add_argument("--candidate-id", required=True)
    review.add_argument("--status", required=True)
    review.add_argument("--note", default="")
    trace = subparsers.add_parser("build-memory-trace")
    trace.add_argument("--reviewed-id", required=True)
    preview = subparsers.add_parser("preview-readback")
    preview.add_argument("--memory-application-data-id", required=True)
    apply = subparsers.add_parser("apply-readback")
    apply.add_argument("--preview-id", required=True)
    apply.add_argument("--active-task-frame-id", required=True)
    contrast = subparsers.add_parser("run-readback-contrast")
    contrast.add_argument("--case-id", default="blocked_front_obstacle")
    subparsers.add_parser("build-loop-evidence")
    subparsers.add_parser("show-loop-evidence")
    subparsers.add_parser("run-growth-readiness-audit")
    subparsers.add_parser("show-growth-readiness")
    subparsers.add_parser("state-handoff-build")
    subparsers.add_parser("state-handoff-show")
    subparsers.add_parser("state-handoff-bookmarks")
    subparsers.add_parser("state-handoff-validate")
    subparsers.add_parser("state-resume-precheck")
    subparsers.add_parser("state-resume-show")
    subparsers.add_parser("state-resume-options")
    subparsers.add_parser("state-resume-validate")
    select_authorize = subparsers.add_parser("state-resume-select-authorize")
    select_authorize.add_argument("--resume-option-id", required=True)
    select_authorize.add_argument("--teacher-selection-text", required=True)
    subparsers.add_parser("state-resume-show-selection")
    subparsers.add_parser("state-resume-show-authorization")
    subparsers.add_parser("state-resume-validate-authorization")
    subparsers.add_parser("state-restore-preview")
    subparsers.add_parser("state-restore-show-preview")
    resume_handoff = subparsers.add_parser("state-resume-create-handoff")
    resume_handoff.add_argument("--teacher-confirmation-text", required=True)
    subparsers.add_parser("state-resume-show-handoff")
    subparsers.add_parser("state-resume-validate-handoff")
    subparsers.add_parser("state-resume-continuity-audit")
    subparsers.add_parser("state-resume-continuity-show")
    subparsers.add_parser("state-resume-continuity-validate")
    learning_draft = subparsers.add_parser("learning-draft-demo-concept")
    learning_draft.add_argument("--demo", required=True)
    learning_seed = subparsers.add_parser("learning-show-teaching-test-seed")
    learning_seed.add_argument("--demo", required=True)
    learning_validate = subparsers.add_parser("learning-validate-demo-draft")
    learning_validate.add_argument("--demo", required=True)
    learning_review_task = subparsers.add_parser("learning-show-concept-review-task")
    learning_review_task.add_argument("--demo", required=True)
    learning_review = subparsers.add_parser("learning-review-demo-concept")
    learning_review.add_argument("--demo", required=True)
    learning_review.add_argument("--decision", required=True)
    learning_review.add_argument("--teacher-note", required=True)
    learning_review_validate = subparsers.add_parser(
        "learning-validate-demo-concept-review"
    )
    learning_review_validate.add_argument("--decision", required=True)
    learning_review_validate.add_argument("--demo", default="blocked")
    learning_refine = subparsers.add_parser("learning-refine-demo-concept")
    learning_refine.add_argument("--decision", required=True)
    learning_refine_validate = subparsers.add_parser(
        "learning-validate-demo-refinement"
    )
    learning_refine_validate.add_argument("--decision", required=True)
    subparsers.add_parser("learning-prepare-reviewed-concept-demo")
    subparsers.add_parser("learning-show-reviewed-concept-preparation-demo")
    subparsers.add_parser("learning-validate-reviewed-concept-preparation-demo")
    subparsers.add_parser("learning-build-reviewed-concept-demo")
    subparsers.add_parser("learning-show-reviewed-concept-demo")
    subparsers.add_parser("learning-validate-reviewed-concept-demo")
    subparsers.add_parser("learning-preview-reviewed-concept-memory-trace")
    subparsers.add_parser("learning-preview-reviewed-concept-routing")
    subparsers.add_parser("learning-preview-reviewed-concept-application-data")
    subparsers.add_parser("learning-validate-reviewed-concept-memory-preview")
    subparsers.add_parser("learning-bridge-reviewed-concept-memory-demo")
    subparsers.add_parser("learning-show-reviewed-concept-memory-candidates")
    subparsers.add_parser("learning-validate-reviewed-concept-memory-bridge")
    subparsers.add_parser("memory-admit-reviewed-concept-demo")
    subparsers.add_parser("memory-show-reviewed-concept-admission")
    subparsers.add_parser("memory-show-reviewed-concept-application-data")
    subparsers.add_parser("memory-validate-reviewed-concept-admission")
    subparsers.add_parser("memory-preview-reviewed-concept-readback-demo")
    subparsers.add_parser("memory-show-reviewed-concept-readback-preview")
    subparsers.add_parser("memory-show-reviewed-concept-hint-preview")
    subparsers.add_parser("memory-validate-reviewed-concept-readback-preview")
    subparsers.add_parser("memory-build-reviewed-concept-hint-candidates-demo")
    subparsers.add_parser("memory-show-reviewed-concept-hint-candidates")
    subparsers.add_parser("memory-validate-reviewed-concept-hint-candidates")
    subparsers.add_parser("memory-review-reviewed-concept-hint-candidates-demo")
    subparsers.add_parser("memory-show-reviewed-concept-hint-candidate-review")
    subparsers.add_parser("memory-validate-reviewed-concept-hint-candidate-review")
    subparsers.add_parser("memory-prepare-reviewed-concept-hints-demo")
    subparsers.add_parser("memory-show-reviewed-concept-hint-preparation")
    subparsers.add_parser("memory-validate-reviewed-concept-hint-preparation")
    subparsers.add_parser("task-create-reviewed-concept-hint-records-demo")
    subparsers.add_parser("task-show-reviewed-concept-hint-records")
    subparsers.add_parser("task-validate-reviewed-concept-hint-records")
    subparsers.add_parser("task-preview-reviewed-concept-hint-application-demo")
    subparsers.add_parser("task-show-reviewed-concept-hint-application-preview")
    subparsers.add_parser("task-validate-reviewed-concept-hint-application-preview")
    subparsers.add_parser("task-review-reviewed-concept-hint-application-demo")
    subparsers.add_parser("task-show-reviewed-concept-hint-application-review")
    subparsers.add_parser("task-validate-reviewed-concept-hint-application-review")
    subparsers.add_parser("task-prepare-reviewed-concept-hint-application-demo")
    subparsers.add_parser("task-show-reviewed-concept-hint-application-preparation")
    subparsers.add_parser("task-validate-reviewed-concept-hint-application-preparation")
    subparsers.add_parser("task-apply-reviewed-concept-readback-hints-demo")
    subparsers.add_parser("task-show-reviewed-concept-readback-hint-application")
    subparsers.add_parser("task-show-reviewed-concept-readback-snapshot")
    subparsers.add_parser("task-validate-reviewed-concept-readback-hint-application")
    subparsers.add_parser("task-audit-reviewed-concept-readback-hint-influence-demo")
    subparsers.add_parser("task-show-reviewed-concept-readback-hint-visibility-audit")
    subparsers.add_parser("task-show-reviewed-concept-readback-hint-non-influence-audit")
    subparsers.add_parser("task-show-reviewed-concept-readback-hint-influence-report")
    subparsers.add_parser("task-validate-reviewed-concept-readback-hint-influence-audit")
    subparsers.add_parser("audit-reviewed-concept-readback-loop-demo")
    subparsers.add_parser("audit-show-reviewed-concept-readback-loop-evidence-chain")
    subparsers.add_parser("audit-show-reviewed-concept-readback-loop-boundary")
    subparsers.add_parser("audit-show-reviewed-concept-readback-loop-milestone")
    subparsers.add_parser("audit-show-reviewed-concept-readback-loop-next-stage-readiness")
    subparsers.add_parser("audit-validate-reviewed-concept-readback-loop")
    subparsers.add_parser("audit-first-action-reviewed-concept-loop-demo")
    subparsers.add_parser("audit-show-first-loop-evidence-chain")
    subparsers.add_parser("audit-show-first-loop-boundary")
    subparsers.add_parser("audit-show-first-loop-replay-verification")
    subparsers.add_parser("audit-show-first-loop-milestone")
    subparsers.add_parser("audit-show-first-loop-next-stage-readiness")
    subparsers.add_parser("audit-validate-first-action-reviewed-concept-loop")
    subparsers.add_parser("runtime-show-continuous-loop-idle-demo")
    subparsers.add_parser("runtime-show-continuous-loop-power-off-demo")
    subparsers.add_parser("runtime-show-continuous-loop-nested-demo")
    subparsers.add_parser("runtime-show-continuous-loop-event-tree-demo")
    subparsers.add_parser("runtime-validate-continuous-event-loop-demo")
    runtime_audit_timeline = subparsers.add_parser(
        "runtime-audit-continuous-event-loop-timeline"
    )
    runtime_audit_timeline.add_argument("--timeline", default=None)
    subparsers.add_parser("runtime-show-event-dispatch-task-demo")
    subparsers.add_parser("runtime-show-event-dispatch-sense-demo")
    subparsers.add_parser("runtime-show-event-dispatch-learning-demo")
    subparsers.add_parser("runtime-show-event-dispatch-memory-demo")
    subparsers.add_parser("runtime-show-event-dispatch-state-demo")
    subparsers.add_parser("runtime-show-event-dispatch-output-demo")
    subparsers.add_parser("runtime-show-event-dispatch-thought-deferred-demo")
    subparsers.add_parser("runtime-validate-event-dispatch-demo")
    subparsers.add_parser("runtime-show-parent-resume-success-demo")
    subparsers.add_parser("runtime-show-parent-resume-blocked-demo")
    subparsers.add_parser("runtime-show-parent-resume-unknown-demo")
    subparsers.add_parser("runtime-show-parent-resume-fault-demo")
    subparsers.add_parser("runtime-show-nested-return-resume-demo")
    subparsers.add_parser("runtime-validate-parent-frame-resume-demo")
    subparsers.add_parser("runtime-show-integrated-loop-simple-demo")
    subparsers.add_parser("runtime-show-integrated-loop-nested-sense-demo")
    subparsers.add_parser("runtime-show-integrated-loop-four-level-demo")
    subparsers.add_parser("runtime-show-integrated-loop-thought-deferred-demo")
    subparsers.add_parser("runtime-show-integrated-loop-render-demo")
    subparsers.add_parser("runtime-show-integrated-loop-readiness-demo")
    subparsers.add_parser("runtime-validate-integrated-event-loop-demo")
    subparsers.add_parser("runtime-show-fixed-closed-loop-playback-demo")
    subparsers.add_parser("runtime-show-fixed-closed-loop-playback-grouped-demo")
    subparsers.add_parser("runtime-show-fixed-closed-loop-playback-render")
    subparsers.add_parser("runtime-show-fixed-closed-loop-playback-readiness")
    subparsers.add_parser("runtime-validate-fixed-closed-loop-playback")
    subparsers.add_parser("runtime-show-bounded-handler-binding-sense-demo")
    subparsers.add_parser("runtime-show-bounded-handler-binding-outcome-demo")
    subparsers.add_parser("runtime-show-bounded-handler-binding-learning-demo")
    subparsers.add_parser("runtime-show-bounded-handler-binding-memory-demo")
    subparsers.add_parser("runtime-show-bounded-handler-binding-selected-trace-demo")
    subparsers.add_parser("runtime-show-bounded-handler-binding-readiness")
    subparsers.add_parser("runtime-validate-bounded-handler-binding-demo")
    subparsers.add_parser("host-body-show-port-map-demo")
    subparsers.add_parser("host-body-show-identity-demo")
    subparsers.add_parser("host-body-show-camera-port-demo")
    subparsers.add_parser("host-body-show-mic-port-demo")
    subparsers.add_parser("host-body-show-internal-space-demo")
    subparsers.add_parser("host-body-show-output-surface-demo")
    subparsers.add_parser("host-body-show-internal-action-demo")
    subparsers.add_parser("host-body-show-readiness-demo")
    subparsers.add_parser("host-body-validate-port-map-demo")
    subparsers.add_parser("host-body-show-camera-frame-event-demo")
    subparsers.add_parser("host-body-show-camera-change-event-demo")
    subparsers.add_parser("host-body-show-mic-level-event-demo")
    subparsers.add_parser("host-body-show-mic-peak-event-demo")
    subparsers.add_parser("host-body-show-idle-event-demo")
    subparsers.add_parser("host-body-show-mixed-sensor-event-set-demo")
    subparsers.add_parser("host-body-show-sensor-event-readiness")
    subparsers.add_parser("host-body-validate-sensor-event-demo")
    subparsers.add_parser("host-body-show-camera-runtime-bridge-demo")
    subparsers.add_parser("host-body-show-mic-runtime-bridge-demo")
    subparsers.add_parser("host-body-show-idle-runtime-bridge-demo")
    subparsers.add_parser("host-body-show-mixed-runtime-bridge-demo")
    subparsers.add_parser("host-body-show-runtime-bridge-readiness")
    subparsers.add_parser("host-body-validate-runtime-bridge-demo")
    subparsers.add_parser("host-body-show-home-surface-demo")
    subparsers.add_parser("host-body-show-home-empty-surface-demo")
    subparsers.add_parser("host-body-show-home-port-surface-demo")
    subparsers.add_parser("host-body-show-home-event-surface-demo")
    subparsers.add_parser("host-body-show-home-runtime-bridge-surface-demo")
    subparsers.add_parser("host-body-show-home-status-lights-demo")
    subparsers.add_parser("host-body-show-home-teacher-surface-demo")
    subparsers.add_parser("host-body-show-home-surface-readiness")
    subparsers.add_parser("host-body-validate-home-surface-demo")
    subparsers.add_parser("host-body-show-trace-history-full-demo")
    subparsers.add_parser("host-body-show-trace-history-empty-demo")
    subparsers.add_parser("host-body-show-trace-history-recent-demo")
    subparsers.add_parser("host-body-show-trace-history-index-demo")
    subparsers.add_parser("host-body-show-trace-history-render-demo")
    subparsers.add_parser("host-body-show-trace-history-readiness")
    subparsers.add_parser("host-body-validate-trace-history-demo")
    subparsers.add_parser("host-body-show-internal-action-camera-interesting-demo")
    subparsers.add_parser("host-body-show-internal-action-uncertain-demo")
    subparsers.add_parser("host-body-show-internal-action-teacher-review-demo")
    subparsers.add_parser("host-body-show-internal-action-observe-again-demo")
    subparsers.add_parser("host-body-show-internal-action-update-home-status-demo")
    subparsers.add_parser("host-body-show-internal-action-readiness")
    subparsers.add_parser("host-body-validate-internal-action-choice-demo")
    subparsers.add_parser("task-apply-advisory-readback-ordering-demo")
    subparsers.add_parser("task-show-advisory-readback-ordering-teacher-gate")
    subparsers.add_parser("task-show-advisory-readback-ordering-application")
    subparsers.add_parser("task-show-advisory-readback-ordering-rollback")
    subparsers.add_parser("task-show-advisory-readback-ordering-audit")
    subparsers.add_parser("task-validate-advisory-readback-ordering-application")
    subparsers.add_parser("task-rollback-advisory-readback-ordering-demo")
    subparsers.add_parser("task-propose-selected-action-demo")
    subparsers.add_parser("task-show-selected-action-proposal-teacher-gate")
    subparsers.add_parser("task-show-selected-action-proposal")
    subparsers.add_parser("task-show-selected-action-proposal-rollback")
    subparsers.add_parser("task-show-selected-action-proposal-audit")
    subparsers.add_parser("task-validate-selected-action-proposal")
    subparsers.add_parser("task-rollback-selected-action-proposal-demo")
    subparsers.add_parser("task-apply-selected-action-demo")
    subparsers.add_parser("task-show-selected-action-application-teacher-gate")
    subparsers.add_parser("task-show-selected-action-application")
    subparsers.add_parser("task-show-selected-action-rollback")
    subparsers.add_parser("task-show-selected-action-application-audit")
    subparsers.add_parser("task-validate-selected-action-application")
    subparsers.add_parser("task-rollback-selected-action-demo")
    subparsers.add_parser("task-apply-final-action-demo")
    subparsers.add_parser("task-show-final-action-application-teacher-gate")
    subparsers.add_parser("task-show-final-action-application")
    subparsers.add_parser("task-show-final-action-rollback")
    subparsers.add_parser("task-show-final-action-application-audit")
    subparsers.add_parser("task-validate-final-action-application")
    subparsers.add_parser("task-rollback-final-action-demo")
    subparsers.add_parser("task-execute-direct-command-demo")
    subparsers.add_parser("task-show-direct-command-execution-teacher-gate")
    subparsers.add_parser("task-show-direct-command")
    subparsers.add_parser("task-show-pre-execution-snapshot")
    subparsers.add_parser("task-show-sandbox-execution")
    subparsers.add_parser("task-show-sandbox-restore")
    subparsers.add_parser("task-show-direct-command-execution-audit")
    subparsers.add_parser("task-validate-direct-command-execution")
    subparsers.add_parser("task-restore-sandbox-execution-demo")
    subparsers.add_parser("sense-observe-sandbox-execution-demo")
    subparsers.add_parser("sense-show-sandbox-observation")
    subparsers.add_parser("sense-show-sandbox-state-delta")
    subparsers.add_parser("sense-show-observation-handoff")
    subparsers.add_parser("sense-show-observation-safety-audit")
    subparsers.add_parser("sense-validate-sandbox-observation")
    subparsers.add_parser("task-evaluate-sense-outcome-demo")
    subparsers.add_parser("task-show-expected-effect-reference")
    subparsers.add_parser("task-show-outcome-evaluation")
    subparsers.add_parser("task-show-goal-delta-evaluation")
    subparsers.add_parser("task-show-outcome-evaluation-safety-audit")
    subparsers.add_parser("task-validate-sense-outcome-evaluation")
    subparsers.add_parser("task-close-from-outcome-demo")
    subparsers.add_parser("task-show-outcome-task-closure")
    subparsers.add_parser("task-show-outcome-task-closure-summary")
    subparsers.add_parser("task-show-outcome-task-closure-rollback")
    subparsers.add_parser("task-show-outcome-task-closure-safety-audit")
    subparsers.add_parser("task-validate-outcome-task-closure")
    subparsers.add_parser("learning-build-feedback-candidate-from-task-closure-demo")
    subparsers.add_parser("learning-show-feedback-candidate")
    subparsers.add_parser("learning-show-feedback-candidate-evidence")
    subparsers.add_parser("learning-show-feedback-candidate-set")
    subparsers.add_parser("learning-show-feedback-candidate-safety-audit")
    subparsers.add_parser("learning-validate-feedback-candidate")
    subparsers.add_parser("learning-build-concept-candidate-from-feedback-demo")
    subparsers.add_parser("learning-show-feedback-teacher-review")
    subparsers.add_parser("learning-show-feedback-concept-candidate-draft")
    subparsers.add_parser("learning-show-feedback-concept-candidate-rollback")
    subparsers.add_parser("learning-show-feedback-concept-candidate-safety-audit")
    subparsers.add_parser("learning-validate-feedback-concept-candidate")
    subparsers.add_parser("learning-refine-feedback-concept-candidate-demo")
    subparsers.add_parser("learning-show-feedback-concept-candidate-review")
    subparsers.add_parser("learning-show-feedback-concept-candidate-scope-check")
    subparsers.add_parser("learning-show-feedback-concept-candidate-counterexample-check")
    subparsers.add_parser("learning-show-feedback-concept-candidate-refinement")
    subparsers.add_parser("learning-show-feedback-concept-candidate-refinement-safety-audit")
    subparsers.add_parser("learning-validate-feedback-concept-candidate-refinement")
    subparsers.add_parser("learning-integrate-feedback-reviewed-concept-demo")
    subparsers.add_parser("learning-show-feedback-reviewed-concept-gate")
    subparsers.add_parser("learning-show-feedback-reviewed-concept")
    subparsers.add_parser("learning-show-feedback-reviewed-concept-working-readback")
    subparsers.add_parser("learning-show-feedback-reviewed-concept-readback-seed")
    subparsers.add_parser("learning-show-feedback-reviewed-concept-rollback")
    subparsers.add_parser("learning-show-feedback-reviewed-concept-safety-audit")
    subparsers.add_parser("learning-validate-feedback-reviewed-concept-integration")
    subparsers.add_parser("audit-replay-feedback-reviewed-concept-loop-demo")
    subparsers.add_parser("audit-show-feedback-replay-gate")
    subparsers.add_parser("audit-show-feedback-replay-task-initialization")
    subparsers.add_parser("audit-show-feedback-replay-action-chain")
    subparsers.add_parser("audit-show-feedback-replay-execution")
    subparsers.add_parser("audit-show-feedback-replay-outcome")
    subparsers.add_parser("audit-show-feedback-replay-contrast")
    subparsers.add_parser("audit-show-feedback-replay-rollback")
    subparsers.add_parser("audit-show-feedback-replay-audit")
    subparsers.add_parser("audit-validate-feedback-reviewed-concept-replay")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "growth-status":
            return _print_json(
                get_guided_cradle_growth_status(args.data_dir, args.state_dir)
            )
        if args.command == "next-step":
            return _print_json(
                {"suggested_next_step": guided_cradle_growth_next_step(base_dir=args.data_dir)}
            )
        if args.command == "run-case":
            return _print_json(
                run_case_from_guided_cradle_growth_console(
                    case_id=args.case_id,
                    max_ticks=args.max_ticks,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "close-last-run":
            return _print_json(close_last_run_from_guided_cradle_growth_console(args.data_dir))
        if args.command == "list-candidates":
            return _print_json(list_candidates_from_guided_cradle_growth_console(args.data_dir))
        if args.command == "review-candidate":
            return _print_json(
                review_candidate_from_guided_cradle_growth_console(
                    candidate_id=args.candidate_id,
                    status=args.status,
                    note=args.note,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "build-memory-trace":
            return _print_json(
                build_memory_trace_from_guided_cradle_growth_console(
                    reviewed_id=args.reviewed_id,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "preview-readback":
            return _print_json(
                preview_readback_from_guided_cradle_growth_console(
                    memory_application_data_id=args.memory_application_data_id,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "apply-readback":
            return _print_json(
                apply_readback_from_guided_cradle_growth_console(
                    preview_id=args.preview_id,
                    active_task_frame_id=args.active_task_frame_id,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "run-readback-contrast":
            return _print_json(
                run_readback_contrast_from_guided_cradle_growth_console(
                    case_id=args.case_id,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "build-loop-evidence":
            return _print_json(build_loop_evidence_from_guided_cradle_growth_console(args.data_dir))
        if args.command == "show-loop-evidence":
            return _print_json(show_loop_evidence_from_guided_cradle_growth_console(args.data_dir))
        if args.command == "run-growth-readiness-audit":
            return _print_json(
                run_growth_readiness_audit_from_guided_cradle_growth_console(args.data_dir)
            )
        if args.command == "show-growth-readiness":
            return _print_json(show_growth_readiness_from_guided_cradle_growth_console(args.data_dir))
        if args.command == "state-handoff-build":
            _require_state_dir(args.state_dir)
            return _print_json(
                build_state_handoff_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                    base_dir=args.data_dir,
                )
            )
        if args.command == "state-handoff-show":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_handoff_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-handoff-bookmarks":
            _require_state_dir(args.state_dir)
            return _print_json(
                list_state_handoff_bookmarks_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-handoff-validate":
            _require_state_dir(args.state_dir)
            return _print_json(
                validate_state_handoff_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-precheck":
            _require_state_dir(args.state_dir)
            return _print_json(
                run_state_resume_precheck_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-show":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_resume_precheck_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-options":
            _require_state_dir(args.state_dir)
            return _print_json(
                list_state_resume_options_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-validate":
            _require_state_dir(args.state_dir)
            return _print_json(
                validate_state_resume_precheck_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-select-authorize":
            _require_state_dir(args.state_dir)
            return _print_json(
                select_authorize_state_resume_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                    resume_option_id=args.resume_option_id,
                    teacher_selection_text=args.teacher_selection_text,
                )
            )
        if args.command == "state-resume-show-selection":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_resume_selection_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-show-authorization":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_resume_authorization_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-validate-authorization":
            _require_state_dir(args.state_dir)
            return _print_json(
                validate_state_resume_authorization_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-restore-preview":
            _require_state_dir(args.state_dir)
            return _print_json(
                build_state_restore_preview_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-restore-show-preview":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_restore_preview_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-create-handoff":
            _require_state_dir(args.state_dir)
            return _print_json(
                create_state_resume_handoff_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                    teacher_confirmation_text=args.teacher_confirmation_text,
                )
            )
        if args.command == "state-resume-show-handoff":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_resume_handoff_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-validate-handoff":
            _require_state_dir(args.state_dir)
            return _print_json(
                validate_state_resume_handoff_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-continuity-audit":
            _require_state_dir(args.state_dir)
            return _print_json(
                run_state_resume_continuity_audit_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-continuity-show":
            _require_state_dir(args.state_dir)
            return _print_json(
                show_state_resume_continuity_audit_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "state-resume-continuity-validate":
            _require_state_dir(args.state_dir)
            return _print_json(
                validate_state_resume_continuity_audit_from_guided_cradle_growth_console(
                    state_dir=args.state_dir,
                )
            )
        if args.command == "learning-draft-demo-concept":
            return _print_json(
                draft_demo_concept_from_guided_cradle_growth_console(demo=args.demo)
            )
        if args.command == "learning-show-teaching-test-seed":
            return _print_json(
                show_concept_teaching_test_seed_from_guided_cradle_growth_console(
                    demo=args.demo,
                )
            )
        if args.command == "learning-validate-demo-draft":
            return _print_json(
                validate_demo_concept_draft_from_guided_cradle_growth_console(
                    demo=args.demo,
                )
            )
        if args.command == "learning-show-concept-review-task":
            return _print_json(
                show_concept_review_task_from_guided_cradle_growth_console(
                    demo=args.demo,
                )
            )
        if args.command == "learning-review-demo-concept":
            return _print_json(
                review_demo_concept_from_guided_cradle_growth_console(
                    demo=args.demo,
                    decision=args.decision,
                    teacher_note=args.teacher_note,
                )
            )
        if args.command == "learning-validate-demo-concept-review":
            return _print_json(
                validate_demo_concept_review_from_guided_cradle_growth_console(
                    demo=args.demo,
                    decision=args.decision,
                )
            )
        if args.command == "learning-refine-demo-concept":
            return _print_json(
                refine_demo_concept_from_guided_cradle_growth_console(
                    decision=args.decision,
                )
            )
        if args.command == "learning-validate-demo-refinement":
            return _print_json(
                validate_demo_refinement_from_guided_cradle_growth_console(
                    decision=args.decision,
                )
            )
        if args.command == "learning-prepare-reviewed-concept-demo":
            return _print_json(
                prepare_reviewed_concept_demo_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-reviewed-concept-preparation-demo":
            return _print_json(
                show_reviewed_concept_preparation_demo_from_guided_cradle_growth_console()
            )
        if args.command == "learning-validate-reviewed-concept-preparation-demo":
            return _print_json(
                validate_reviewed_concept_preparation_demo_from_guided_cradle_growth_console()
            )
        if args.command == "learning-build-reviewed-concept-demo":
            return _print_json(
                build_reviewed_concept_demo_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-reviewed-concept-demo":
            return _print_json(
                show_reviewed_concept_demo_from_guided_cradle_growth_console()
            )
        if args.command == "learning-validate-reviewed-concept-demo":
            return _print_json(
                validate_reviewed_concept_demo_from_guided_cradle_growth_console()
            )
        if args.command == "learning-preview-reviewed-concept-memory-trace":
            return _print_json(
                preview_reviewed_concept_memory_trace_from_guided_cradle_growth_console()
            )
        if args.command == "learning-preview-reviewed-concept-routing":
            return _print_json(
                preview_reviewed_concept_routing_from_guided_cradle_growth_console()
            )
        if args.command == "learning-preview-reviewed-concept-application-data":
            return _print_json(
                preview_reviewed_concept_application_data_from_guided_cradle_growth_console()
            )
        if args.command == "learning-validate-reviewed-concept-memory-preview":
            return _print_json(
                validate_reviewed_concept_memory_preview_from_guided_cradle_growth_console()
            )
        if args.command == "learning-bridge-reviewed-concept-memory-demo":
            return _print_json(
                bridge_reviewed_concept_memory_demo_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-reviewed-concept-memory-candidates":
            return _print_json(
                show_reviewed_concept_memory_candidates_from_guided_cradle_growth_console()
            )
        if args.command == "learning-validate-reviewed-concept-memory-bridge":
            return _print_json(
                validate_reviewed_concept_memory_bridge_from_guided_cradle_growth_console()
            )
        if args.command == "memory-admit-reviewed-concept-demo":
            return _print_json(
                admit_reviewed_concept_memory_demo_from_guided_cradle_growth_console()
            )
        if args.command == "memory-show-reviewed-concept-admission":
            return _print_json(
                show_reviewed_concept_memory_admission_from_guided_cradle_growth_console()
            )
        if args.command == "memory-show-reviewed-concept-application-data":
            return _print_json(
                show_reviewed_concept_application_data_from_guided_cradle_growth_console()
            )
        if args.command == "memory-validate-reviewed-concept-admission":
            return _print_json(
                validate_reviewed_concept_admission_from_guided_cradle_growth_console()
            )
        if args.command == "memory-preview-reviewed-concept-readback-demo":
            return _print_json(
                preview_reviewed_concept_readback_demo_from_guided_cradle_growth_console()
            )
        if args.command == "memory-show-reviewed-concept-readback-preview":
            return _print_json(
                show_reviewed_concept_readback_preview_from_guided_cradle_growth_console()
            )
        if args.command == "memory-show-reviewed-concept-hint-preview":
            return _print_json(
                show_reviewed_concept_hint_preview_from_guided_cradle_growth_console()
            )
        if args.command == "memory-validate-reviewed-concept-readback-preview":
            return _print_json(
                validate_reviewed_concept_readback_preview_from_guided_cradle_growth_console()
            )
        if args.command == "memory-build-reviewed-concept-hint-candidates-demo":
            return _print_json(
                build_reviewed_concept_hint_candidates_demo_from_guided_cradle_growth_console()
            )
        if args.command == "memory-show-reviewed-concept-hint-candidates":
            return _print_json(
                show_reviewed_concept_hint_candidates_from_guided_cradle_growth_console()
            )
        if args.command == "memory-validate-reviewed-concept-hint-candidates":
            return _print_json(
                validate_reviewed_concept_hint_candidates_from_guided_cradle_growth_console()
            )
        if args.command == "memory-review-reviewed-concept-hint-candidates-demo":
            return _print_json(
                review_reviewed_concept_hint_candidates_demo_from_guided_cradle_growth_console()
            )
        if args.command == "memory-show-reviewed-concept-hint-candidate-review":
            return _print_json(
                show_reviewed_concept_hint_candidate_review_from_guided_cradle_growth_console()
            )
        if args.command == "memory-validate-reviewed-concept-hint-candidate-review":
            return _print_json(
                validate_reviewed_concept_hint_candidate_review_from_guided_cradle_growth_console()
            )
        if args.command == "memory-prepare-reviewed-concept-hints-demo":
            return _print_json(
                prepare_reviewed_concept_hints_demo_from_guided_cradle_growth_console()
            )
        if args.command == "memory-show-reviewed-concept-hint-preparation":
            return _print_json(
                show_reviewed_concept_hint_preparation_from_guided_cradle_growth_console()
            )
        if args.command == "memory-validate-reviewed-concept-hint-preparation":
            return _print_json(
                validate_reviewed_concept_hint_preparation_from_guided_cradle_growth_console()
            )
        if args.command == "task-create-reviewed-concept-hint-records-demo":
            return _print_json(
                create_reviewed_concept_hint_records_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-reviewed-concept-hint-records":
            return _print_json(
                show_reviewed_concept_hint_records_from_guided_cradle_growth_console()
            )
        if args.command == "task-validate-reviewed-concept-hint-records":
            return _print_json(
                validate_reviewed_concept_hint_records_from_guided_cradle_growth_console()
            )
        if args.command == "task-preview-reviewed-concept-hint-application-demo":
            return _print_json(
                preview_reviewed_concept_hint_application_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-reviewed-concept-hint-application-preview":
            return _print_json(
                show_reviewed_concept_hint_application_preview_from_guided_cradle_growth_console()
            )
        if args.command == "task-validate-reviewed-concept-hint-application-preview":
            return _print_json(
                validate_reviewed_concept_hint_application_preview_from_guided_cradle_growth_console()
            )
        if args.command == "task-review-reviewed-concept-hint-application-demo":
            return _print_json(
                review_reviewed_concept_hint_application_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-reviewed-concept-hint-application-review":
            return _print_json(
                show_reviewed_concept_hint_application_review_from_guided_cradle_growth_console()
            )
        if args.command == "task-validate-reviewed-concept-hint-application-review":
            return _print_json(
                validate_reviewed_concept_hint_application_review_from_guided_cradle_growth_console()
            )
        if args.command == "task-prepare-reviewed-concept-hint-application-demo":
            return _print_json(
                prepare_reviewed_concept_hint_application_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-reviewed-concept-hint-application-preparation":
            return _print_json(
                show_reviewed_concept_hint_application_preparation_from_guided_cradle_growth_console()
            )
        if args.command == "task-validate-reviewed-concept-hint-application-preparation":
            return _print_json(
                validate_reviewed_concept_hint_application_preparation_from_guided_cradle_growth_console()
            )
        if args.command == "task-apply-reviewed-concept-readback-hints-demo":
            return _print_json(
                apply_reviewed_concept_readback_hints_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-reviewed-concept-readback-hint-application":
            return _print_json(
                show_reviewed_concept_readback_hint_application_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-reviewed-concept-readback-snapshot":
            return _print_json(
                show_reviewed_concept_readback_snapshot_from_guided_cradle_growth_console()
            )
        if args.command == "task-validate-reviewed-concept-readback-hint-application":
            return _print_json(
                validate_reviewed_concept_readback_hint_application_from_guided_cradle_growth_console()
            )
        if args.command == "task-audit-reviewed-concept-readback-hint-influence-demo":
            return _print_json(
                audit_reviewed_concept_readback_hint_influence_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-reviewed-concept-readback-hint-visibility-audit":
            return _print_json(
                show_reviewed_concept_readback_hint_visibility_audit_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-reviewed-concept-readback-hint-non-influence-audit":
            return _print_json(
                show_reviewed_concept_readback_hint_non_influence_audit_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-reviewed-concept-readback-hint-influence-report":
            return _print_json(
                show_reviewed_concept_readback_hint_influence_report_from_guided_cradle_growth_console()
            )
        if args.command == "task-validate-reviewed-concept-readback-hint-influence-audit":
            return _print_json(
                validate_reviewed_concept_readback_hint_influence_audit_from_guided_cradle_growth_console()
            )
        if args.command == "audit-reviewed-concept-readback-loop-demo":
            return _print_json(
                audit_reviewed_concept_readback_loop_demo_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-reviewed-concept-readback-loop-evidence-chain":
            return _print_json(
                show_reviewed_concept_readback_loop_evidence_chain_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-reviewed-concept-readback-loop-boundary":
            return _print_json(
                show_reviewed_concept_readback_loop_boundary_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-reviewed-concept-readback-loop-milestone":
            return _print_json(
                show_reviewed_concept_readback_loop_milestone_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-reviewed-concept-readback-loop-next-stage-readiness":
            return _print_json(
                show_reviewed_concept_readback_loop_next_stage_readiness_from_guided_cradle_growth_console()
            )
        if args.command == "audit-validate-reviewed-concept-readback-loop":
            return _print_json(
                validate_reviewed_concept_readback_loop_from_guided_cradle_growth_console()
            )
        if args.command == "audit-first-action-reviewed-concept-loop-demo":
            return _print_json(
                audit_first_action_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-first-loop-evidence-chain":
            return _print_json(
                show_first_action_reviewed_concept_loop_evidence_chain_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-first-loop-boundary":
            return _print_json(
                show_first_action_reviewed_concept_loop_boundary_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-first-loop-replay-verification":
            return _print_json(
                show_first_action_reviewed_concept_loop_replay_verification_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-first-loop-milestone":
            return _print_json(
                show_first_action_reviewed_concept_loop_milestone_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-first-loop-next-stage-readiness":
            return _print_json(
                show_first_action_reviewed_concept_loop_next_stage_readiness_from_guided_cradle_growth_console()
            )
        if args.command == "audit-validate-first-action-reviewed-concept-loop":
            return _print_json(
                validate_first_action_reviewed_concept_loop_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-continuous-loop-idle-demo":
            return _print_json(
                show_continuous_loop_idle_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-continuous-loop-power-off-demo":
            return _print_json(
                show_continuous_loop_power_off_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-continuous-loop-nested-demo":
            return _print_json(
                show_continuous_loop_nested_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-continuous-loop-event-tree-demo":
            return _print_json(
                show_continuous_loop_event_tree_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-validate-continuous-event-loop-demo":
            return _print_json(
                validate_continuous_event_loop_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-audit-continuous-event-loop-timeline":
            return _print_json(
                audit_continuous_event_loop_timeline_from_guided_cradle_growth_console(
                    args.timeline
                )
            )
        if args.command == "runtime-show-event-dispatch-task-demo":
            return _print_json(
                show_event_dispatch_task_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-event-dispatch-sense-demo":
            return _print_json(
                show_event_dispatch_sense_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-event-dispatch-learning-demo":
            return _print_json(
                show_event_dispatch_learning_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-event-dispatch-memory-demo":
            return _print_json(
                show_event_dispatch_memory_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-event-dispatch-state-demo":
            return _print_json(
                show_event_dispatch_state_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-event-dispatch-output-demo":
            return _print_json(
                show_event_dispatch_output_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-event-dispatch-thought-deferred-demo":
            return _print_json(
                show_event_dispatch_thought_deferred_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-validate-event-dispatch-demo":
            return _print_json(
                validate_event_dispatch_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-parent-resume-success-demo":
            return _print_json(
                show_parent_resume_success_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-parent-resume-blocked-demo":
            return _print_json(
                show_parent_resume_blocked_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-parent-resume-unknown-demo":
            return _print_json(
                show_parent_resume_unknown_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-parent-resume-fault-demo":
            return _print_json(
                show_parent_resume_fault_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-nested-return-resume-demo":
            return _print_json(
                show_nested_return_resume_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-validate-parent-frame-resume-demo":
            return _print_json(
                validate_parent_frame_resume_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-integrated-loop-simple-demo":
            return _print_json(
                show_integrated_loop_simple_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-integrated-loop-nested-sense-demo":
            return _print_json(
                show_integrated_loop_nested_sense_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-integrated-loop-four-level-demo":
            return _print_json(
                show_integrated_loop_four_level_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-integrated-loop-thought-deferred-demo":
            return _print_json(
                show_integrated_loop_thought_deferred_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-integrated-loop-render-demo":
            return _print_json(
                show_integrated_loop_render_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-integrated-loop-readiness-demo":
            return _print_json(
                show_integrated_loop_readiness_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-validate-integrated-event-loop-demo":
            return _print_json(
                validate_integrated_event_loop_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-fixed-closed-loop-playback-demo":
            return _print_json(
                show_fixed_closed_loop_playback_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-fixed-closed-loop-playback-grouped-demo":
            return _print_json(
                show_fixed_closed_loop_playback_grouped_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-fixed-closed-loop-playback-render":
            return _print_json(
                show_fixed_closed_loop_playback_render_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-fixed-closed-loop-playback-readiness":
            return _print_json(
                show_fixed_closed_loop_playback_readiness_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-validate-fixed-closed-loop-playback":
            return _print_json(
                validate_fixed_closed_loop_playback_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-bounded-handler-binding-sense-demo":
            return _print_json(
                show_bounded_handler_binding_sense_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-bounded-handler-binding-outcome-demo":
            return _print_json(
                show_bounded_handler_binding_outcome_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-bounded-handler-binding-learning-demo":
            return _print_json(
                show_bounded_handler_binding_learning_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-bounded-handler-binding-memory-demo":
            return _print_json(
                show_bounded_handler_binding_memory_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-bounded-handler-binding-selected-trace-demo":
            return _print_json(
                show_bounded_handler_binding_selected_trace_demo_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-show-bounded-handler-binding-readiness":
            return _print_json(
                show_bounded_handler_binding_readiness_from_guided_cradle_growth_console()
            )
        if args.command == "runtime-validate-bounded-handler-binding-demo":
            return _print_json(
                validate_bounded_handler_binding_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-port-map-demo":
            return _print_json(
                show_host_body_port_map_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-identity-demo":
            return _print_json(
                show_host_body_identity_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-camera-port-demo":
            return _print_json(
                show_host_body_camera_port_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-mic-port-demo":
            return _print_json(
                show_host_body_mic_port_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-internal-space-demo":
            return _print_json(
                show_host_body_internal_space_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-output-surface-demo":
            return _print_json(
                show_host_body_output_surface_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-internal-action-demo":
            return _print_json(
                show_host_body_internal_action_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-readiness-demo":
            return _print_json(
                show_host_body_readiness_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-validate-port-map-demo":
            return _print_json(
                validate_host_body_port_map_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-camera-frame-event-demo":
            return _print_json(
                show_host_body_camera_frame_event_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-camera-change-event-demo":
            return _print_json(
                show_host_body_camera_change_event_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-mic-level-event-demo":
            return _print_json(
                show_host_body_mic_level_event_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-mic-peak-event-demo":
            return _print_json(
                show_host_body_mic_peak_event_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-idle-event-demo":
            return _print_json(
                show_host_body_idle_event_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-mixed-sensor-event-set-demo":
            return _print_json(
                show_host_body_mixed_sensor_event_set_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-sensor-event-readiness":
            return _print_json(
                show_host_body_sensor_event_readiness_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-validate-sensor-event-demo":
            return _print_json(
                validate_host_body_sensor_event_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-camera-runtime-bridge-demo":
            return _print_json(
                show_host_body_camera_runtime_bridge_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-mic-runtime-bridge-demo":
            return _print_json(
                show_host_body_mic_runtime_bridge_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-idle-runtime-bridge-demo":
            return _print_json(
                show_host_body_idle_runtime_bridge_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-mixed-runtime-bridge-demo":
            return _print_json(
                show_host_body_mixed_runtime_bridge_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-runtime-bridge-readiness":
            return _print_json(
                show_host_body_runtime_bridge_readiness_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-validate-runtime-bridge-demo":
            return _print_json(
                validate_host_body_runtime_bridge_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-home-surface-demo":
            return _print_json(
                show_host_body_home_surface_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-home-empty-surface-demo":
            return _print_json(
                show_host_body_home_empty_surface_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-home-port-surface-demo":
            return _print_json(
                show_host_body_home_port_surface_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-home-event-surface-demo":
            return _print_json(
                show_host_body_home_event_surface_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-home-runtime-bridge-surface-demo":
            return _print_json(
                show_host_body_home_runtime_bridge_surface_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-home-status-lights-demo":
            return _print_json(
                show_host_body_home_status_lights_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-home-teacher-surface-demo":
            return _print_json(
                show_host_body_home_teacher_surface_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-home-surface-readiness":
            return _print_json(
                show_host_body_home_surface_readiness_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-validate-home-surface-demo":
            return _print_json(
                validate_host_body_home_surface_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-trace-history-full-demo":
            return _print_json(
                show_host_body_trace_history_full_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-trace-history-empty-demo":
            return _print_json(
                show_host_body_trace_history_empty_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-trace-history-recent-demo":
            return _print_json(
                show_host_body_trace_history_recent_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-trace-history-index-demo":
            return _print_json(
                show_host_body_trace_history_index_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-trace-history-render-demo":
            return _print_json(
                show_host_body_trace_history_render_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-trace-history-readiness":
            return _print_json(
                show_host_body_trace_history_readiness_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-validate-trace-history-demo":
            return _print_json(
                validate_host_body_trace_history_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-internal-action-camera-interesting-demo":
            return _print_json(
                show_host_body_internal_action_camera_interesting_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-internal-action-uncertain-demo":
            return _print_json(
                show_host_body_internal_action_uncertain_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-internal-action-teacher-review-demo":
            return _print_json(
                show_host_body_internal_action_teacher_review_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-internal-action-observe-again-demo":
            return _print_json(
                show_host_body_internal_action_observe_again_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-internal-action-update-home-status-demo":
            return _print_json(
                show_host_body_internal_action_update_home_status_demo_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-show-internal-action-readiness":
            return _print_json(
                show_host_body_internal_action_readiness_from_guided_cradle_growth_console()
            )
        if args.command == "host-body-validate-internal-action-choice-demo":
            return _print_json(
                validate_host_body_internal_action_choice_from_guided_cradle_growth_console()
            )
        if args.command == "task-apply-advisory-readback-ordering-demo":
            return _print_json(
                apply_advisory_readback_ordering_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-advisory-readback-ordering-teacher-gate":
            return _print_json(
                show_advisory_readback_ordering_teacher_gate_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-advisory-readback-ordering-application":
            return _print_json(
                show_advisory_readback_ordering_application_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-advisory-readback-ordering-rollback":
            return _print_json(
                show_advisory_readback_ordering_rollback_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-advisory-readback-ordering-audit":
            return _print_json(
                show_advisory_readback_ordering_audit_from_guided_cradle_growth_console()
            )
        if args.command == "task-validate-advisory-readback-ordering-application":
            return _print_json(
                validate_advisory_readback_ordering_application_from_guided_cradle_growth_console()
            )
        if args.command == "task-rollback-advisory-readback-ordering-demo":
            return _print_json(
                rollback_advisory_readback_ordering_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-propose-selected-action-demo":
            return _print_json(
                propose_selected_action_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-selected-action-proposal-teacher-gate":
            return _print_json(
                show_selected_action_proposal_teacher_gate_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-selected-action-proposal":
            return _print_json(
                show_selected_action_proposal_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-selected-action-proposal-rollback":
            return _print_json(
                show_selected_action_proposal_rollback_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-selected-action-proposal-audit":
            return _print_json(
                show_selected_action_proposal_audit_from_guided_cradle_growth_console()
            )
        if args.command == "task-validate-selected-action-proposal":
            return _print_json(
                validate_selected_action_proposal_from_guided_cradle_growth_console()
            )
        if args.command == "task-rollback-selected-action-proposal-demo":
            return _print_json(
                rollback_selected_action_proposal_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-apply-selected-action-demo":
            return _print_json(
                apply_selected_action_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-selected-action-application-teacher-gate":
            return _print_json(
                show_selected_action_application_teacher_gate_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-selected-action-application":
            return _print_json(
                show_selected_action_application_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-selected-action-rollback":
            return _print_json(
                show_selected_action_rollback_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-selected-action-application-audit":
            return _print_json(
                show_selected_action_application_audit_from_guided_cradle_growth_console()
            )
        if args.command == "task-validate-selected-action-application":
            return _print_json(
                validate_selected_action_application_from_guided_cradle_growth_console()
            )
        if args.command == "task-rollback-selected-action-demo":
            return _print_json(
                rollback_selected_action_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-apply-final-action-demo":
            return _print_json(
                apply_final_action_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-final-action-application-teacher-gate":
            return _print_json(
                show_final_action_application_teacher_gate_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-final-action-application":
            return _print_json(
                show_final_action_application_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-final-action-rollback":
            return _print_json(
                show_final_action_rollback_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-final-action-application-audit":
            return _print_json(
                show_final_action_application_audit_from_guided_cradle_growth_console()
            )
        if args.command == "task-validate-final-action-application":
            return _print_json(
                validate_final_action_application_from_guided_cradle_growth_console()
            )
        if args.command == "task-rollback-final-action-demo":
            return _print_json(
                rollback_final_action_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-execute-direct-command-demo":
            return _print_json(
                execute_direct_command_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-direct-command-execution-teacher-gate":
            return _print_json(
                show_direct_command_execution_teacher_gate_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-direct-command":
            return _print_json(show_direct_command_from_guided_cradle_growth_console())
        if args.command == "task-show-pre-execution-snapshot":
            return _print_json(
                show_pre_execution_snapshot_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-sandbox-execution":
            return _print_json(show_sandbox_execution_from_guided_cradle_growth_console())
        if args.command == "task-show-sandbox-restore":
            return _print_json(show_sandbox_restore_from_guided_cradle_growth_console())
        if args.command == "task-show-direct-command-execution-audit":
            return _print_json(
                show_direct_command_execution_audit_from_guided_cradle_growth_console()
            )
        if args.command == "task-validate-direct-command-execution":
            return _print_json(
                validate_direct_command_execution_from_guided_cradle_growth_console()
            )
        if args.command == "task-restore-sandbox-execution-demo":
            return _print_json(
                restore_sandbox_execution_demo_from_guided_cradle_growth_console()
            )
        if args.command == "sense-observe-sandbox-execution-demo":
            return _print_json(
                observe_sandbox_execution_demo_from_guided_cradle_growth_console()
            )
        if args.command == "sense-show-sandbox-observation":
            return _print_json(show_sandbox_observation_from_guided_cradle_growth_console())
        if args.command == "sense-show-sandbox-state-delta":
            return _print_json(show_sandbox_state_delta_from_guided_cradle_growth_console())
        if args.command == "sense-show-observation-handoff":
            return _print_json(show_observation_handoff_from_guided_cradle_growth_console())
        if args.command == "sense-show-observation-safety-audit":
            return _print_json(
                show_observation_safety_audit_from_guided_cradle_growth_console()
            )
        if args.command == "sense-validate-sandbox-observation":
            return _print_json(
                validate_sandbox_observation_from_guided_cradle_growth_console()
            )
        if args.command == "task-evaluate-sense-outcome-demo":
            return _print_json(
                evaluate_sense_outcome_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-expected-effect-reference":
            return _print_json(
                show_expected_effect_reference_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-outcome-evaluation":
            return _print_json(show_outcome_evaluation_from_guided_cradle_growth_console())
        if args.command == "task-show-goal-delta-evaluation":
            return _print_json(show_goal_delta_evaluation_from_guided_cradle_growth_console())
        if args.command == "task-show-outcome-evaluation-safety-audit":
            return _print_json(
                show_outcome_evaluation_safety_audit_from_guided_cradle_growth_console()
            )
        if args.command == "task-validate-sense-outcome-evaluation":
            return _print_json(
                validate_sense_outcome_evaluation_from_guided_cradle_growth_console()
            )
        if args.command == "task-close-from-outcome-demo":
            return _print_json(
                close_from_outcome_demo_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-outcome-task-closure":
            return _print_json(
                show_outcome_task_closure_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-outcome-task-closure-summary":
            return _print_json(
                show_outcome_task_closure_summary_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-outcome-task-closure-rollback":
            return _print_json(
                show_outcome_task_closure_rollback_from_guided_cradle_growth_console()
            )
        if args.command == "task-show-outcome-task-closure-safety-audit":
            return _print_json(
                show_outcome_task_closure_safety_audit_from_guided_cradle_growth_console()
            )
        if args.command == "task-validate-outcome-task-closure":
            return _print_json(
                validate_outcome_task_closure_from_guided_cradle_growth_console()
            )
        if args.command == "learning-build-feedback-candidate-from-task-closure-demo":
            return _print_json(
                build_feedback_candidate_from_task_closure_demo_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-candidate":
            return _print_json(show_feedback_candidate_from_guided_cradle_growth_console())
        if args.command == "learning-show-feedback-candidate-evidence":
            return _print_json(
                show_feedback_candidate_evidence_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-candidate-set":
            return _print_json(show_feedback_candidate_set_from_guided_cradle_growth_console())
        if args.command == "learning-show-feedback-candidate-safety-audit":
            return _print_json(
                show_feedback_candidate_safety_audit_from_guided_cradle_growth_console()
            )
        if args.command == "learning-validate-feedback-candidate":
            return _print_json(
                validate_feedback_candidate_from_guided_cradle_growth_console()
            )
        if args.command == "learning-build-concept-candidate-from-feedback-demo":
            return _print_json(
                build_concept_candidate_from_feedback_demo_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-teacher-review":
            return _print_json(
                show_feedback_teacher_review_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-concept-candidate-draft":
            return _print_json(
                show_feedback_concept_candidate_draft_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-concept-candidate-rollback":
            return _print_json(
                show_feedback_concept_candidate_rollback_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-concept-candidate-safety-audit":
            return _print_json(
                show_feedback_concept_candidate_safety_audit_from_guided_cradle_growth_console()
            )
        if args.command == "learning-validate-feedback-concept-candidate":
            return _print_json(
                validate_feedback_concept_candidate_from_guided_cradle_growth_console()
            )
        if args.command == "learning-refine-feedback-concept-candidate-demo":
            return _print_json(
                refine_feedback_concept_candidate_demo_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-concept-candidate-review":
            return _print_json(
                show_feedback_concept_candidate_review_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-concept-candidate-scope-check":
            return _print_json(
                show_feedback_concept_candidate_scope_check_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-concept-candidate-counterexample-check":
            return _print_json(
                show_feedback_concept_candidate_counterexample_check_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-concept-candidate-refinement":
            return _print_json(
                show_feedback_concept_candidate_refinement_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-concept-candidate-refinement-safety-audit":
            return _print_json(
                show_feedback_concept_candidate_refinement_safety_audit_from_guided_cradle_growth_console()
            )
        if args.command == "learning-validate-feedback-concept-candidate-refinement":
            return _print_json(
                validate_feedback_concept_candidate_refinement_from_guided_cradle_growth_console()
            )
        if args.command == "learning-integrate-feedback-reviewed-concept-demo":
            return _print_json(
                integrate_feedback_reviewed_concept_demo_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-reviewed-concept-gate":
            return _print_json(
                show_feedback_reviewed_concept_gate_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-reviewed-concept":
            return _print_json(
                show_feedback_reviewed_concept_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-reviewed-concept-working-readback":
            return _print_json(
                show_feedback_reviewed_concept_working_readback_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-reviewed-concept-readback-seed":
            return _print_json(
                show_feedback_reviewed_concept_readback_seed_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-reviewed-concept-rollback":
            return _print_json(
                show_feedback_reviewed_concept_rollback_from_guided_cradle_growth_console()
            )
        if args.command == "learning-show-feedback-reviewed-concept-safety-audit":
            return _print_json(
                show_feedback_reviewed_concept_safety_audit_from_guided_cradle_growth_console()
            )
        if args.command == "learning-validate-feedback-reviewed-concept-integration":
            return _print_json(
                validate_feedback_reviewed_concept_integration_from_guided_cradle_growth_console()
            )
        if args.command == "audit-replay-feedback-reviewed-concept-loop-demo":
            return _print_json(
                replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-feedback-replay-gate":
            return _print_json(show_feedback_replay_gate_from_guided_cradle_growth_console())
        if args.command == "audit-show-feedback-replay-task-initialization":
            return _print_json(
                show_feedback_replay_task_initialization_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-feedback-replay-action-chain":
            return _print_json(
                show_feedback_replay_action_chain_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-feedback-replay-execution":
            return _print_json(
                show_feedback_replay_execution_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-feedback-replay-outcome":
            return _print_json(show_feedback_replay_outcome_from_guided_cradle_growth_console())
        if args.command == "audit-show-feedback-replay-contrast":
            return _print_json(
                show_feedback_replay_contrast_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-feedback-replay-rollback":
            return _print_json(
                show_feedback_replay_rollback_from_guided_cradle_growth_console()
            )
        if args.command == "audit-show-feedback-replay-audit":
            return _print_json(show_feedback_replay_audit_from_guided_cradle_growth_console())
        if args.command == "audit-validate-feedback-reviewed-concept-replay":
            return _print_json(
                validate_feedback_reviewed_concept_replay_from_guided_cradle_growth_console()
            )
    except (FileNotFoundError, LookupError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


def _require_state_dir(state_dir: Path | None) -> None:
    if state_dir is None:
        raise ValueError("--state-dir is required for state handoff commands")


if __name__ == "__main__":
    raise SystemExit(main())
