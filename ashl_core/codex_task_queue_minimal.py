"""Minimal Codex task queue for Phase0 workflow coordination."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-codex-task-queue-minimal-check"
FLOW = "codex_task_queue_minimal_v0"
BOUNDARY_INDEX_VERSION = "2026-06-09-b98"
PREVIOUS_BOUNDARY_INDEX_VERSION = "2026-06-09-b97"
LEVEL2_APPLICATION_BOUNDARY_BEFORE = "2026-06-09-b72"
LEVEL2_APPLICATION_BOUNDARY_AFTER = "2026-06-09-b73"
LEVEL3_TOY_MINEFIELD_BOUNDARY_BEFORE = "2026-06-09-b73"
LEVEL3_TOY_MINEFIELD_BOUNDARY_AFTER = "2026-06-09-b74"
MEMORY_ADMISSION_APPROVAL_BOUNDARY_BEFORE = "2026-06-09-b74"
MEMORY_ADMISSION_APPROVAL_BOUNDARY_AFTER = "2026-06-09-b75"
MEMORY_ADMISSION_BOUNDARY_BEFORE = "2026-06-09-b75"
MEMORY_ADMISSION_BOUNDARY_AFTER = "2026-06-09-b76"
MEMORY_WRITE_APPROVAL_BOUNDARY_BEFORE = "2026-06-09-b76"
MEMORY_WRITE_APPROVAL_BOUNDARY_AFTER = "2026-06-09-b77"
MEMORY_WRITE_AND_READ_BOUNDARY_BEFORE = "2026-06-09-b77"
MEMORY_WRITE_AND_READ_BOUNDARY_AFTER = "2026-06-09-b78"
MEMORY_INFLUENCE_PREVIEW_BOUNDARY_BEFORE = "2026-06-09-b78"
MEMORY_INFLUENCE_PREVIEW_BOUNDARY_AFTER = "2026-06-09-b79"
MEMORY_RUNTIME_INFLUENCE_APPROVAL_BOUNDARY_BEFORE = "2026-06-09-b79"
MEMORY_RUNTIME_INFLUENCE_APPROVAL_BOUNDARY_AFTER = "2026-06-09-b80"
MEMORY_RUNTIME_INFLUENCE_BOUNDARY_BEFORE = "2026-06-09-b80"
MEMORY_RUNTIME_INFLUENCE_BOUNDARY_AFTER = "2026-06-09-b81"
MEMORY_INFLUENCED_SANDBOX_RERUN_BOUNDARY_BEFORE = "2026-06-09-b81"
MEMORY_INFLUENCED_SANDBOX_RERUN_BOUNDARY_AFTER = "2026-06-09-b82"
LEVEL3_TOY_REPAIR_BOUNDARY_BEFORE = "2026-06-09-b82"
LEVEL3_TOY_REPAIR_BOUNDARY_AFTER = "2026-06-09-b83"
MEMORY_INFLUENCED_TOY_REPAIR_RERUN_BOUNDARY_BEFORE = "2026-06-09-b83"
MEMORY_INFLUENCED_TOY_REPAIR_RERUN_BOUNDARY_AFTER = "2026-06-09-b84"
SANDBOX_BEHAVIOR_USE_BOUNDARY_BEFORE = "2026-06-09-b84"
SANDBOX_BEHAVIOR_USE_BOUNDARY_AFTER = "2026-06-09-b85"
DOUBT_ACTION_TRACE_BOUNDARY_BEFORE = "2026-06-09-b85"
DOUBT_ACTION_TRACE_BOUNDARY_AFTER = "2026-06-09-b86"
DOUBT_GATED_SANDBOX_ORDERING_BOUNDARY_BEFORE = "2026-06-09-b86"
DOUBT_GATED_SANDBOX_ORDERING_BOUNDARY_AFTER = "2026-06-09-b87"
VERIFICATION_CANDIDATE_REGISTRY_BOUNDARY_BEFORE = "2026-06-09-b87"
VERIFICATION_CANDIDATE_REGISTRY_BOUNDARY_AFTER = "2026-06-09-b88"
VERIFICATION_PLANNING_BOUNDARY_BEFORE = "2026-06-09-b88"
VERIFICATION_PLANNING_BOUNDARY_AFTER = "2026-06-09-b89"
VERIFICATION_EXECUTION_BOUNDARY_BEFORE = "2026-06-09-b89"
VERIFICATION_EXECUTION_BOUNDARY_AFTER = "2026-06-09-b90"
VERIFICATION_RESULT_FEEDBACK_TRACE_BOUNDARY_BEFORE = "2026-06-09-b90"
VERIFICATION_RESULT_FEEDBACK_TRACE_BOUNDARY_AFTER = "2026-06-09-b91"
EPHEMERAL_FEEDBACK_APPLICATION_BOUNDARY_BEFORE = "2026-06-09-b91"
EPHEMERAL_FEEDBACK_APPLICATION_BOUNDARY_AFTER = "2026-06-09-b92"
SAME_SESSION_FEEDBACK_REORDERING_BOUNDARY_BEFORE = "2026-06-09-b92"
SAME_SESSION_FEEDBACK_REORDERING_BOUNDARY_AFTER = "2026-06-09-b93"
SANDBOX_SELECTED_ACTION_APPROVAL_PRESSURE_BOUNDARY_BEFORE = "2026-06-09-b93"
SANDBOX_SELECTED_ACTION_APPROVAL_PRESSURE_BOUNDARY_AFTER = "2026-06-09-b94"
SANDBOX_SELECTED_ACTION_EXECUTION_APPROVAL_BOUNDARY_BEFORE = "2026-06-09-b94"
SANDBOX_SELECTED_ACTION_EXECUTION_APPROVAL_BOUNDARY_AFTER = "2026-06-09-b95"
SANDBOX_ACTION_EXECUTION_BOUNDARY_BEFORE = "2026-06-09-b95"
SANDBOX_ACTION_EXECUTION_BOUNDARY_AFTER = "2026-06-09-b96"
SANDBOX_EXECUTION_RESULT_FEEDBACK_LOOP_BOUNDARY_BEFORE = "2026-06-09-b96"
SANDBOX_EXECUTION_RESULT_FEEDBACK_LOOP_BOUNDARY_AFTER = "2026-06-09-b97"
SANDBOX_FINAL_ACTION_APPROVAL_BOUNDARY_BEFORE = "2026-06-09-b97"
SANDBOX_FINAL_ACTION_APPROVAL_BOUNDARY_AFTER = "2026-06-09-b98"
BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION = "2026-06-09-b93"
B85_B93_BASELINE_BOUNDARY_VERSION = "2026-06-09-b93"
VERSIONING_POLICY_BOUNDARY_BEFORE = "2026-06-09-b71"
VERSIONING_POLICY_BOUNDARY_AFTER = "2026-06-09-b72"
QUEUE_NAME = "ashl_core_phase0_codex_task_queue"
BOUNDARY_PRINCIPLE = (
    "No task queue entry, completed task, passing test, Codex-generated status, workflow record, "
    "or queue ordering counts as explicit human application approval or memory write approval."
)
QUEUE_PRINCIPLE = (
    "The Codex task queue coordinates work packages only. It does not approve, apply, observe, evaluate, "
    "promote, remember, retain, predict, select, finalize, command, or prove learning."
)
ALLOWED_STATUSES = {"pending", "active", "blocked", "completed", "superseded", "deferred"}
ALLOWED_TASK_TYPES = {
    "documentation_only",
    "workflow_only",
    "capability_boundary",
    "sandbox_only",
    "risk_register",
    "cleanup",
}
REQUIRED_QUEUE_FIELDS = {
    "queue_name",
    "queue_scope",
    "record_type",
    "boundary_index_version",
    "task_entries",
    "queue_creates_capability",
    "queue_counts_as_approval",
    "queue_counts_as_application",
    "queue_counts_as_runtime_behavior",
    "queue_counts_as_memory_write",
    "queue_counts_as_retained_jsonl_write",
    "queue_counts_as_predictor_mutation",
    "queue_counts_as_selected_action",
    "queue_counts_as_final_action",
    "queue_counts_as_proof_of_learning",
    "principles",
}
REQUIRED_TASK_FIELDS = {
    "package_id",
    "package_title",
    "task_id",
    "title",
    "task_status",
    "task_type",
    "status",
    "boundary_index_version",
    "boundary_change_required",
    "boundary_index_version_before",
    "boundary_index_version_after",
    "source",
    "creates_capability",
    "counts_as_approval",
    "counts_as_runtime_behavior",
    "counts_as_memory_write",
    "counts_as_retained_jsonl_write",
    "counts_as_predictor_mutation",
    "counts_as_selected_action",
    "counts_as_final_action",
    "counts_as_proof_of_learning",
    "depends_on",
    "blocks",
    "notes",
}
QUEUE_FALSE_FIELDS = {
    "queue_creates_capability",
    "queue_counts_as_approval",
    "queue_counts_as_application",
    "queue_counts_as_runtime_behavior",
    "queue_counts_as_memory_write",
    "queue_counts_as_retained_jsonl_write",
    "queue_counts_as_predictor_mutation",
    "queue_counts_as_selected_action",
    "queue_counts_as_final_action",
    "queue_counts_as_proof_of_learning",
}
TASK_FALSE_FIELDS = {
    "creates_capability",
    "counts_as_approval",
    "counts_as_runtime_behavior",
    "counts_as_memory_write",
    "counts_as_retained_jsonl_write",
    "counts_as_predictor_mutation",
    "counts_as_selected_action",
    "counts_as_final_action",
    "counts_as_proof_of_learning",
}


def build_codex_task_queue_minimal() -> dict[str, Any]:
    return {
        "queue_name": QUEUE_NAME,
        "queue_scope": "phase0_workflow_coordination_only",
        "record_type": "codex_task_queue_minimal_v0",
        "boundary_index_version": BOUNDARY_INDEX_VERSION,
        "task_entries": [
            _task(
                "task.documentation_inventory.completed",
                "PKG-Phase0-Docs-Inventory-001",
                "Phase0 Documentation Inventory and Consistency Reconciliation Minimal v0",
                "documentation_only",
                "completed",
                "codex_completed_report",
                [],
                ["task.codex_task_queue.active"],
                "Documentation reconciliation only; no new ASHL Core runtime capability.",
            ),
            _task(
                "task.codex_task_queue.active",
                "PKG-Phase0-Workflow-Queue-001",
                "Codex Task Queue Minimal v0",
                "workflow_only",
                "active",
                "codex_work_package",
                ["task.documentation_inventory.completed"],
                ["task.bucket_signal_human_interpretation_review.completed"],
                "Workflow coordination only; does not approve or execute future packages.",
            ),
            _task(
                "task.level1_outcome_evaluation.completed",
                "PKG-Phase0-Level1-Eval-001",
                "Level 1 Sandbox Outcome Evaluation and Human Review Summary Minimal v0",
                "sandbox_only",
                "completed",
                "codex_completed_report",
                ["task.codex_task_queue.active"],
                [],
                "Completed sandbox-only outcome evaluation and human review summary; task status is not approval.",
            ),
            _task(
                "task.level1_review_conclusion.completed",
                "PKG-Phase0-Level1-Review-001",
                "Level 1 Sandbox Review Conclusion and Level 2 Readiness Precheck Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.level1_outcome_evaluation.completed"],
                [],
                "Completed Level 1 sandbox review conclusion and Level 2 future-package precheck; task status is not approval.",
            ),
            _task(
                "task.level2_sandbox_design_envelope.completed",
                "PKG-Phase0-Level2-Design-001",
                "Level 2 Sandbox Design Envelope Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.level1_review_conclusion.completed"],
                [],
                "Completed design-only Level 2 sandbox envelope; task status is not approval or execution.",
            ),
            _task(
                "task.level2_sandbox_scenario_plan.completed",
                "PKG-Phase0-Level2-Scenario-001",
                "Level 2 Sandbox Scenario Plan Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.level2_sandbox_design_envelope.completed"],
                [],
                "Completed planning-only Level 2 sandbox scenario plan; task status is not approval or execution.",
            ),
            _task(
                "task.phase0_versioning_policy.completed",
                "PKG-Phase0-Versioning-001",
                "Phase0 Package ID and Boundary Index Version Separation Minimal v0",
                "workflow_only",
                "completed",
                "codex_completed_report",
                ["task.level2_sandbox_dry_run_summary.completed"],
                [],
                "Completed package ID and Boundary Index version separation; task status is not approval.",
                boundary_change_required=True,
                boundary_index_version_before=VERSIONING_POLICY_BOUNDARY_BEFORE,
                boundary_index_version_after=VERSIONING_POLICY_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Boundary Index changed because versioning governance now constrains when Boundary Index may change."
                ),
            ),
            _task(
                "task.level2_sandbox_dry_run_summary.completed",
                "PKG-Phase0-Level2-DryRun-001",
                "Level 2 Sandbox Dry Run, Observation, Evaluation, and Human Review Summary Minimal v0",
                "sandbox_only",
                "completed",
                "codex_completed_report",
                ["task.level2_sandbox_scenario_plan.completed"],
                [],
                "Completed Level 2 sandbox dry-run-only observation/evaluation/summary; task status is not approval or execution.",
            ),
            _task(
                "task.level2_sandbox_application_observation_evaluation_summary.completed",
                "PKG-Phase0-Level2-Sandbox-App-001",
                "Level 2 Sandbox Application, Observation, Evaluation, and Human Review Summary Minimal v0",
                "sandbox_only",
                "completed",
                "codex_completed_report",
                ["task.phase0_versioning_policy.completed", "task.level2_sandbox_dry_run_summary.completed"],
                [],
                (
                    "Completed Level 2 sandbox-only application/observation/evaluation/summary; task status "
                    "is not approval, runtime execution, or production behavior."
                ),
                boundary_change_required=True,
                boundary_index_version_before=LEVEL2_APPLICATION_BOUNDARY_BEFORE,
                boundary_index_version_after=LEVEL2_APPLICATION_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Level 2 moves from dry-run-only into sandbox-only application, changing the sandbox "
                    "application permission boundary."
                ),
            ),
            _task(
                "task.level2_sandbox_review_conclusion_promotion_readiness.completed",
                "PKG-Phase0-Level2-Sandbox-Review-Conclusion-Promotion-Readiness-Minimal-v0",
                "Level 2 Sandbox Review Conclusion and Promotion Readiness Minimal v0",
                "sandbox_only",
                "completed",
                "codex_completed_report",
                ["task.level2_sandbox_application_observation_evaluation_summary.completed"],
                [],
                (
                    "Completed Level 2 sandbox review conclusion and future-design-only promotion readiness; "
                    "task status is not approval, runtime execution, production promotion, or memory write."
                ),
                boundary_index_version_before=LEVEL2_APPLICATION_BOUNDARY_AFTER,
                boundary_index_version_after=LEVEL2_APPLICATION_BOUNDARY_AFTER,
            ),
            _task(
                "task.level3_toy_minefield_multistep_sandbox.completed",
                "PKG-Phase0-Level3-ToyMinefield-Multistep-Sandbox-Minimal-v0",
                "Level 3 Toy Minefield Multi-Step Sandbox Minimal v0",
                "sandbox_only",
                "completed",
                "codex_completed_report",
                ["task.level2_sandbox_review_conclusion_promotion_readiness.completed"],
                [],
                (
                    "Completed Level 3 toy minefield sandbox-only multi-step application trace, observation, "
                    "evaluation, and summary; task status is not runtime execution, production promotion, or memory write."
                ),
                boundary_change_required=True,
                boundary_index_version_before=LEVEL3_TOY_MINEFIELD_BOUNDARY_BEFORE,
                boundary_index_version_after=LEVEL3_TOY_MINEFIELD_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Level 3 introduces a new sandbox-only multi-step application trace scope, changing the "
                    "sandbox application permission boundary."
                ),
            ),
            _task(
                "task.level3_toy_minefield_variant_suite_stability.completed",
                "PKG-PHASE0-L3-MINEFIELD-VARIANT-STABILITY-REVIEW-001",
                "Level 3 Toy Minefield Variant Suite, Stability Evaluation, and Review Conclusion Minimal v0",
                "sandbox_only",
                "completed",
                "codex_completed_report",
                ["task.level3_toy_minefield_multistep_sandbox.completed"],
                [],
                (
                    "Completed deterministic Level 3 toy minefield variant suite stability evaluation and "
                    "review conclusion inside the existing Level 3 sandbox boundary; task status is not "
                    "runtime execution, production promotion, memory write, predictor mutation, or proof of learning."
                ),
                boundary_index_version_before=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
                boundary_index_version_after=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
            ),
            _task(
                "task.sandbox_stable_lesson_candidate_proposal.superseded",
                "PKG-Phase0-Sandbox-Stable-Lesson-Candidate-Proposal-Future",
                "Sandbox-Stable Lesson Candidate Proposal Minimal v0",
                "workflow_only",
                "superseded",
                "phase0_future_work",
                ["task.level3_toy_minefield_variant_suite_stability.completed"],
                [],
                (
                    "Superseded: candidate should originate as a structured bucket-derived signal, not as "
                    "direct text lesson proposal."
                ),
                boundary_index_version_before=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
                boundary_index_version_after=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
                superseded_by="Bucket-Derived Lesson Candidate Signal Minimal v0",
            ),
            _task(
                "task.bucket_derived_lesson_candidate_signal.completed",
                "PKG-Phase0-Bucket-Derived-Lesson-Candidate-Signal-Minimal-v0",
                "Bucket-Derived Lesson Candidate Signal Minimal v0",
                "sandbox_only",
                "completed",
                "codex_completed_report",
                ["task.level3_toy_minefield_variant_suite_stability.completed"],
                [],
                (
                    "Completed structured bucket-derived lesson candidate signal from Level 3 variant evidence; "
                    "no Qingyin-authored lesson text, memory write, runtime influence, predictor mutation, or proof claim."
                ),
                boundary_index_version_before=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
                boundary_index_version_after=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
            ),
            _task(
                "task.repo_audit_minimal.completed",
                "PKG-Phase0-Repo-Audit-Minimal-v0",
                "ASHL Core / Qingyin Repo Audit Minimal v0",
                "documentation_only",
                "completed",
                "codex_completed_report",
                ["task.bucket_derived_lesson_candidate_signal.completed"],
                [],
                (
                    "Completed repo audit: Qingyin is a boundary-constrained Phase0 trace/checker system, "
                    "not an autonomous learner or actor; task status is not approval or memory write."
                ),
                boundary_index_version_before=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
                boundary_index_version_after=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
            ),
            _task(
                "task.bucket_signal_human_interpretation_review.completed",
                "PKG-Phase0-Bucket-Signal-Human-Interpretation-Review-Audit-Reconciliation-Minimal-v0",
                "Bucket Signal Human Interpretation Review + Audit Reconciliation Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.bucket_derived_lesson_candidate_signal.completed", "task.repo_audit_minimal.completed"],
                [],
                (
                    "Completed human or human/GPT-assisted interpretation and human review of bucket signal "
                    "for future memory readiness design only; no memory write, runtime influence, predictor "
                    "mutation, action selection, production promotion, or proof claim."
                ),
                boundary_index_version_before=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
                boundary_index_version_after=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
            ),
            _task(
                "task.memory_readiness_design_approved_bucket_lesson.completed",
                "PKG-Phase0-Memory-Readiness-Design-Approved-Bucket-Lesson-Minimal-v0",
                "Memory Readiness Design for Approved Bucket-Derived Lesson Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.bucket_signal_human_interpretation_review.completed"],
                [],
                (
                    "Completed design-only memory readiness constraints for approved human-interpreted "
                    "bucket-derived lesson; no memory admission, memory write, retained JSONL write, "
                    "runtime influence, predictor mutation, action selection, production promotion, or proof claim."
                ),
                boundary_index_version_before=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
                boundary_index_version_after=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
            ),
            _task(
                "task.memory_admission_package_design.completed",
                "PKG-Phase0-Memory-Admission-Package-Design-Minimal-v0",
                "Memory Admission Package Design Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.memory_readiness_design_approved_bucket_lesson.completed"],
                [],
                (
                    "Completed design-only future memory admission package contract; no memory admission, "
                    "memory write, retained JSONL write, retention write, runtime influence, predictor mutation, "
                    "action selection, production promotion, or proof claim."
                ),
                boundary_index_version_before=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
                boundary_index_version_after=BUCKET_SIGNAL_BASELINE_BOUNDARY_VERSION,
            ),
            _task(
                "task.memory_admission_approval_boundary.completed",
                "PKG-Phase0-MemoryAdmissionApprovalBoundary-Minimal-v0",
                "Memory Admission Approval Boundary Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.memory_admission_package_design.completed"],
                [],
                (
                    "Completed explicit user/project-owner approval validation boundary for future memory "
                    "admission packages; approval does not perform memory admission, write memory, write "
                    "retained JSONL, influence runtime, mutate predictors, select actions, promote production, "
                    "or prove learning."
                ),
                boundary_change_required=True,
                boundary_index_version_before=MEMORY_ADMISSION_APPROVAL_BOUNDARY_BEFORE,
                boundary_index_version_after=MEMORY_ADMISSION_APPROVAL_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Introduces an explicit human approval validation boundary for future memory admission packages."
                ),
            ),
            _task(
                "task.memory_admission_minimal.completed",
                "PKG-Phase0-MemoryAdmission-Minimal-v0",
                "Memory Admission Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.memory_admission_approval_boundary.completed"],
                [],
                (
                    "Completed minimal candidate-layer memory admission as reviewed_lesson_memory_candidate; "
                    "no Long-term Memory write, retained JSONL write, runtime influence, predictor mutation, "
                    "action selection, production promotion, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=MEMORY_ADMISSION_BOUNDARY_BEFORE,
                boundary_index_version_after=MEMORY_ADMISSION_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Opens the minimal memory admission boundary for reviewed_lesson_memory_candidate records."
                ),
            ),
            _task(
                "task.memory_write_approval_boundary.completed",
                "PKG-Phase0-MemoryWriteApprovalBoundary-Minimal-v0",
                "Memory Write Approval Boundary Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.memory_admission_minimal.completed"],
                [],
                (
                    "Completed explicit user/project-owner approval validation boundary for future memory "
                    "write packages; no memory write, retained JSONL write, retention write, runtime influence, "
                    "predictor mutation, action selection, production promotion, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=MEMORY_WRITE_APPROVAL_BOUNDARY_BEFORE,
                boundary_index_version_after=MEMORY_WRITE_APPROVAL_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Introduces an explicit human approval validation boundary for future memory write packages."
                ),
            ),
            _task(
                "task.memory_write_minimal.superseded",
                "PKG-Phase0-MemoryWrite-Minimal-v0",
                "Memory Write Minimal v0",
                "workflow_only",
                "superseded",
                "phase0_future_work",
                ["task.memory_write_approval_boundary.completed"],
                [],
                (
                    "Superseded by Memory Write and Read Minimal v0 because memory write and controlled memory "
                    "read should be implemented together at this stage."
                ),
                superseded_by="Memory Write and Read Minimal v0",
            ),
            _task(
                "task.memory_write_and_read_minimal.completed",
                "PKG-Phase0-MemoryWriteAndRead-Minimal-v0",
                "Memory Write and Read Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.memory_write_approval_boundary.completed"],
                [],
                (
                    "Completed minimal reviewed lesson memory write and controlled read path for one approved "
                    "reviewed_lesson_memory_candidate; no retained JSONL write, retention write, runtime influence, "
                    "predictor mutation, action selection, production promotion, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=MEMORY_WRITE_AND_READ_BOUNDARY_BEFORE,
                boundary_index_version_after=MEMORY_WRITE_AND_READ_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Opens the minimal memory write and controlled memory read boundary for one approved "
                    "reviewed_lesson_memory_candidate."
                ),
            ),
            _task(
                "task.memory_influence_preview_minimal.completed",
                "PKG-Phase0-MemoryInfluencePreview-Minimal-v0",
                "Memory Influence Preview Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.memory_write_and_read_minimal.completed"],
                [],
                (
                    "Completed preview-only influence view from controlled memory read; no runtime influence, "
                    "predictor input, action selection, retained JSONL write, retention write, production promotion, "
                    "or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=MEMORY_INFLUENCE_PREVIEW_BOUNDARY_BEFORE,
                boundary_index_version_after=MEMORY_INFLUENCE_PREVIEW_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Introduces a preview-only memory influence validation boundary from controlled memory read."
                ),
            ),
            _task(
                "task.memory_runtime_influence_approval_boundary.completed",
                "PKG-Phase0-MemoryRuntimeInfluenceApprovalBoundary-Minimal-v0",
                "Memory Runtime Influence Approval Boundary Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.memory_influence_preview_minimal.completed"],
                [],
                (
                    "Completed explicit user/project-owner approval validation boundary for future memory runtime "
                    "influence packages; no runtime influence, predictor mutation, action selection, production "
                    "promotion, retained JSONL write, retention write, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=MEMORY_RUNTIME_INFLUENCE_APPROVAL_BOUNDARY_BEFORE,
                boundary_index_version_after=MEMORY_RUNTIME_INFLUENCE_APPROVAL_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Introduces explicit human approval validation for future memory runtime influence packages."
                ),
            ),
            _task(
                "task.memory_runtime_influence_minimal.completed",
                "PKG-Phase0-MemoryRuntimeInfluence-Minimal-v0",
                "Memory Runtime Influence Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.memory_runtime_influence_approval_boundary.completed"],
                [],
                (
                    "Completed bounded memory-influenced runtime tendency shift inside a deterministic "
                    "controlled runner with rollback to baseline; no selected_action, final_action, predictor "
                    "mutation, production behavior, retained JSONL write, retention write, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=MEMORY_RUNTIME_INFLUENCE_BOUNDARY_BEFORE,
                boundary_index_version_after=MEMORY_RUNTIME_INFLUENCE_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Opens the minimal bounded memory runtime influence boundary for one approved memory record "
                    "inside a deterministic controlled runner."
                ),
            ),
            _task(
                "task.memory_influenced_sandbox_rerun_minimal.completed",
                "PKG-Phase0-MemoryInfluencedSandboxRerun-Minimal-v0",
                "Memory-Influenced Sandbox Re-run Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.memory_runtime_influence_minimal.completed"],
                [],
                (
                    "Completed deterministic Level 3 toy minefield sandbox variant-suite re-run with "
                    "memory_off / memory_on / rollback tendency traces; no selected_action, final_action, "
                    "predictor mutation, production behavior, retained JSONL write, retention write, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=MEMORY_INFLUENCED_SANDBOX_RERUN_BOUNDARY_BEFORE,
                boundary_index_version_after=MEMORY_INFLUENCED_SANDBOX_RERUN_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Introduces memory-influenced Level 3 sandbox re-run tendency traces using the approved "
                    "bounded runtime influence."
                ),
            ),
            _task(
                "task.level3_toy_repair_multistep_sandbox.completed",
                "PKG-Phase0-Level3ToyRepairMultistepSandbox-Minimal-v0",
                "Level 3 Toy Repair Multi-Step Sandbox Minimal v0",
                "sandbox_only",
                "completed",
                "codex_completed_report",
                ["task.level3_toy_minefield_variant_suite_stability.completed"],
                [],
                (
                    "Completed deterministic Phase0 Level 3 toy repair sandbox-only trace, observation, "
                    "evaluation, and human review summary; no memory influence, selected_action, final_action, "
                    "predictor mutation, production behavior, retained JSONL write, retention write, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=LEVEL3_TOY_REPAIR_BOUNDARY_BEFORE,
                boundary_index_version_after=LEVEL3_TOY_REPAIR_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Introduces a second deterministic Phase0 Level 3 sandbox-only multi-step scenario family, "
                    "Toy Repair."
                ),
            ),
            _task(
                "task.memory_influenced_toy_repair_rerun_minimal.completed",
                "PKG-Phase0-MemoryInfluencedToyRepairRerun-Minimal-v0",
                "Memory-Influenced Toy Repair Re-run Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.memory_runtime_influence_minimal.completed", "task.level3_toy_repair_multistep_sandbox.completed"],
                [],
                (
                    "Completed deterministic Level 3 toy repair sandbox re-run with memory_off / memory_on / "
                    "rollback tendency traces; no selected_action, final_action, predictor mutation, production "
                    "behavior, retained JSONL write, retention write, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=MEMORY_INFLUENCED_TOY_REPAIR_RERUN_BOUNDARY_BEFORE,
                boundary_index_version_after=MEMORY_INFLUENCED_TOY_REPAIR_RERUN_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Introduces memory-influenced Level 3 toy repair sandbox re-run tendency traces using the "
                    "approved bounded runtime influence."
                ),
            ),
            _task(
                "task.sandbox_behavior_use_minimal.completed",
                "PKG-Phase0-SandboxBehaviorUse-Minimal-v0",
                "Sandbox Behavior Use Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.memory_influenced_sandbox_rerun_minimal.completed", "task.memory_influenced_toy_repair_rerun_minimal.completed"],
                [],
                (
                    "Completed sandbox-only candidate action ordering from approved memory-influenced tendency; "
                    "no selected_action, final_action, direct command, predictor mutation, production behavior, "
                    "retained JSONL write, retention write, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=SANDBOX_BEHAVIOR_USE_BOUNDARY_BEFORE,
                boundary_index_version_after=SANDBOX_BEHAVIOR_USE_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Permits approved memory-influenced tendency to affect sandbox-only candidate action ordering."
                ),
            ),
            _task(
                "task.doubt_action_trace_minimal.completed",
                "PKG-Phase0-DoubtActionTrace-Minimal-v0",
                "Doubt Action Trace Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.sandbox_behavior_use_minimal.completed"],
                [],
                (
                    "Completed trace-only doubt_action validation for expected/actual mismatch; no verification "
                    "execution, selected_action, final_action, persistent rule, memory write, retention write, "
                    "predictor mutation, production behavior, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=DOUBT_ACTION_TRACE_BOUNDARY_BEFORE,
                boundary_index_version_after=DOUBT_ACTION_TRACE_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Introduces a trace-only doubt_action validation boundary for mismatch-driven doubt and "
                    "low-risk verification candidate proposal."
                ),
            ),
            _task(
                "task.doubt_gated_sandbox_candidate_ordering_minimal.completed",
                "PKG-Phase0-DoubtGatedSandboxCandidateOrdering-Minimal-v0",
                "Doubt-Gated Sandbox Candidate Ordering Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.sandbox_behavior_use_minimal.completed", "task.doubt_action_trace_minimal.completed"],
                [],
                (
                    "Completed sandbox-only candidate ordering gated by trace-only doubt_action output; "
                    "no verification execution, selected_action, final_action, persistent rule, memory write, "
                    "retention write, predictor mutation, production behavior, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=DOUBT_GATED_SANDBOX_ORDERING_BOUNDARY_BEFORE,
                boundary_index_version_after=DOUBT_GATED_SANDBOX_ORDERING_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Permits trace-only doubt_action output to influence sandbox-only candidate action ordering."
                ),
            ),
            _task(
                "task.verification_candidate_registry_trace_minimal.completed",
                "PKG-Phase0-VerificationCandidateRegistryTrace-Minimal-v0",
                "Verification Candidate Registry + Trace Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.doubt_gated_sandbox_candidate_ordering_minimal.completed"],
                [],
                (
                    "Completed bounded trace-only verification candidate registry and trace; no verification "
                    "execution, selected_action, final_action, persistent rule, memory write, retention write, "
                    "predictor mutation, production behavior, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=VERIFICATION_CANDIDATE_REGISTRY_BOUNDARY_BEFORE,
                boundary_index_version_after=VERIFICATION_CANDIDATE_REGISTRY_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Introduces a validation boundary for named low-risk verification candidates."
                ),
            ),
            _task(
                "task.verification_planning_minimal.completed",
                "PKG-Phase0-VerificationPlanning-Minimal-v0",
                "Verification Planning Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                [
                    "task.doubt_gated_sandbox_candidate_ordering_minimal.completed",
                    "task.verification_candidate_registry_trace_minimal.completed",
                ],
                [],
                (
                    "Completed one-step trace-only verification planning from registered verification candidates; "
                    "no verification execution, selected_action, final_action, direct command, persistent rule, "
                    "memory write, retention write, predictor mutation, production behavior, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=VERIFICATION_PLANNING_BOUNDARY_BEFORE,
                boundary_index_version_after=VERIFICATION_PLANNING_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Introduces a validation boundary for one-step verification plans built from registered "
                    "verification candidates."
                ),
            ),
            _task(
                "task.verification_execution_minimal.completed",
                "PKG-Phase0-VerificationExecution-Minimal-v0",
                "Verification Execution Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.verification_planning_minimal.completed"],
                [],
                (
                    "Completed one registered low-risk verification candidate execution inside sandbox-only scope; "
                    "no selected_action, final_action, direct command, persistent rule, memory write, retention write, "
                    "predictor mutation, production behavior, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=VERIFICATION_EXECUTION_BOUNDARY_BEFORE,
                boundary_index_version_after=VERIFICATION_EXECUTION_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Permits one registered low-risk verification candidate from a validated verification plan "
                    "to execute inside sandbox-only scope."
                ),
            ),
            _task(
                "task.verification_result_feedback_trace_minimal.completed",
                "PKG-Phase0-VerificationResultFeedbackTrace-Minimal-v0",
                "Verification Result Feedback Trace Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.verification_execution_minimal.completed"],
                [],
                (
                    "Completed trace-only feedback conversion from sandbox verification result; no persistent "
                    "trust/doubt update, selected_action, final_action, persistent rule, memory write, retention write, "
                    "predictor mutation, production behavior, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=VERIFICATION_RESULT_FEEDBACK_TRACE_BOUNDARY_BEFORE,
                boundary_index_version_after=VERIFICATION_RESULT_FEEDBACK_TRACE_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Introduces a trace-only feedback boundary from sandbox verification result to candidate "
                    "feedback signals."
                ),
            ),
            _task(
                "task.ephemeral_feedback_application_minimal.completed",
                "PKG-Phase0-EphemeralFeedbackApplication-Minimal-v0",
                "Ephemeral Feedback Application Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.verification_result_feedback_trace_minimal.completed"],
                [],
                (
                    "Completed same-session ephemeral sandbox feedback application and rollback; no persistent "
                    "trust/doubt update, selected_action, final_action, persistent rule, memory write, retention write, "
                    "predictor mutation, production behavior, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=EPHEMERAL_FEEDBACK_APPLICATION_BOUNDARY_BEFORE,
                boundary_index_version_after=EPHEMERAL_FEEDBACK_APPLICATION_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Permits b91 verification-result feedback to apply only as same-session ephemeral "
                    "sandbox feedback with rollback at session end."
                ),
            ),
            _task(
                "task.same_session_feedback_reordering_minimal.completed",
                "PKG-Phase0-SameSessionFeedbackReordering-Minimal-v0",
                "Same-Session Feedback Reordering Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.ephemeral_feedback_application_minimal.completed"],
                [],
                (
                    "Completed same-session sandbox-only candidate reordering from ephemeral feedback; no "
                    "selected_action, final_action, persistent rule, memory write, retention write, predictor mutation, "
                    "production behavior, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=SAME_SESSION_FEEDBACK_REORDERING_BOUNDARY_BEFORE,
                boundary_index_version_after=SAME_SESSION_FEEDBACK_REORDERING_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Permits same-session ephemeral feedback to influence the next sandbox-only candidate ordering."
                ),
            ),
            _task(
                "task.b85_b93_same_session_thought_loop_audit_minimal.completed",
                "PKG-Phase0-B85B93SameSessionThoughtLoopAudit-Minimal-v0",
                "b85-b93 Same-Session Thought Loop Audit Minimal v0",
                "documentation_only",
                "completed",
                "codex_completed_report",
                ["task.same_session_feedback_reordering_minimal.completed"],
                [],
                (
                    "Completed audit-only review of the b85-b93 same-session sandbox thought loop; no new "
                    "runtime capability, Boundary Index change, persistence, memory write, predictor mutation, "
                    "action selection, production behavior, or proof claim."
                ),
                boundary_index_version_before=B85_B93_BASELINE_BOUNDARY_VERSION,
                boundary_index_version_after=B85_B93_BASELINE_BOUNDARY_VERSION,
                boundary_change_rationale="Audit-only package; no boundary change.",
            ),
            _task(
                "task.b85_b93_documentation_compression_status_sync_minimal.completed",
                "PKG-Phase0-B85B93DocumentationCompressionStatusSync-Minimal-v0",
                "b85-b93 Documentation Compression / Status Sync Minimal v0",
                "documentation_only",
                "completed",
                "codex_completed_report",
                ["task.b85_b93_same_session_thought_loop_audit_minimal.completed"],
                [],
                (
                    "Completed documentation/status sync for the b85-b93 same-session sandbox thought loop; no "
                    "runtime capability, Boundary Index change, persistence, memory write, predictor mutation, "
                    "action selection, production behavior, or proof claim."
                ),
                boundary_index_version_before=B85_B93_BASELINE_BOUNDARY_VERSION,
                boundary_index_version_after=B85_B93_BASELINE_BOUNDARY_VERSION,
                boundary_change_rationale="Documentation/status sync only; no boundary change.",
            ),
            _task(
                "task.sandbox_selected_action_approval_and_doubt_pressure_trace_minimal.completed",
                "PKG-Phase0-SandboxSelectedActionApprovalAndDoubtPressureTrace-Minimal-v0",
                "Sandbox Selected Action Approval + Cortisol-Like Doubt Pressure Trace Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.b85_b93_documentation_compression_status_sync_minimal.completed"],
                [],
                (
                    "Completed explicit approval boundary for a future sandbox-only selected_action package and "
                    "trace-only cortisol-like doubt pressure validation with paranoia guard; selected_action is not "
                    "created in this package."
                ),
                boundary_change_required=True,
                boundary_index_version_before=SANDBOX_SELECTED_ACTION_APPROVAL_PRESSURE_BOUNDARY_BEFORE,
                boundary_index_version_after=SANDBOX_SELECTED_ACTION_APPROVAL_PRESSURE_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Creates an explicit approval boundary for a future sandbox-only selected_action package and "
                    "introduces a trace-only cortisol-like doubt pressure validation boundary."
                ),
            ),
            _task(
                "task.sandbox_selected_action_and_execution_approval_boundary_minimal.completed",
                "PKG-Phase0-SandboxSelectedActionAndExecutionApprovalBoundary-Minimal-v0",
                "Sandbox Selected Action + Execution Approval Boundary Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.sandbox_selected_action_approval_and_doubt_pressure_trace_minimal.completed"],
                [],
                (
                    "Completed one sandbox-only selected_action from the top ranked same-session candidate and "
                    "created explicit approval for a future sandbox action execution package; the selected_action "
                    "is not executed in this package."
                ),
                boundary_change_required=True,
                boundary_index_version_before=SANDBOX_SELECTED_ACTION_EXECUTION_APPROVAL_BOUNDARY_BEFORE,
                boundary_index_version_after=SANDBOX_SELECTED_ACTION_EXECUTION_APPROVAL_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Permits one sandbox-only selected_action to be created from an approved ranked sandbox candidate "
                    "and creates an explicit approval boundary for a future sandbox action execution package."
                ),
            ),
            _task(
                "task.sandbox_action_execution_minimal.completed",
                "PKG-Phase0-SandboxActionExecution-Minimal-v0",
                "Sandbox Action Execution Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.sandbox_selected_action_and_execution_approval_boundary_minimal.completed"],
                [],
                (
                    "Completed one sandbox-only selected_action execution of observe_or_alternative_probe and "
                    "recorded local_context_observed; no final_action, direct command, persistent update, "
                    "memory/retention write, predictor read/influence/mutation, production behavior, autonomous "
                    "learning/action claim, or proof claim."
                ),
                boundary_change_required=True,
                boundary_index_version_before=SANDBOX_ACTION_EXECUTION_BOUNDARY_BEFORE,
                boundary_index_version_after=SANDBOX_ACTION_EXECUTION_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Permits one sandbox-only selected_action to execute once inside sandbox scope and records a "
                    "sandbox-only result."
                ),
            ),
            _task(
                "task.sandbox_execution_result_feedback_loop_minimal.completed",
                "PKG-Phase0-SandboxExecutionResultFeedbackLoop-Minimal-v0",
                "Sandbox Execution Result Feedback Loop Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.sandbox_action_execution_minimal.completed"],
                [],
                (
                    "Completed same-session feedback loop from the b96 sandbox-only action execution result; "
                    "feedback is trace-only, applied ephemerally inside the same sandbox session, can reorder the "
                    "next sandbox-only candidate list, and rolls back at session end."
                ),
                boundary_change_required=True,
                boundary_index_version_before=SANDBOX_EXECUTION_RESULT_FEEDBACK_LOOP_BOUNDARY_BEFORE,
                boundary_index_version_after=SANDBOX_EXECUTION_RESULT_FEEDBACK_LOOP_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Permits one sandbox-only action execution result to generate same-session feedback, apply it "
                    "ephemerally, and influence the next sandbox-only candidate ordering."
                ),
            ),
            _task(
                "task.b95_b97_sandbox_action_boundary_audit_minimal.completed",
                "PKG-Phase0-B95B97SandboxActionBoundaryAudit-Minimal-v0",
                "b95-b97 Sandbox Action Boundary Audit Minimal v0",
                "documentation_only",
                "completed",
                "codex_completed_report",
                ["task.sandbox_execution_result_feedback_loop_minimal.completed"],
                [],
                (
                    "Audits the b95-b97 sandbox action line: sandbox-only selected_action, one sandbox-only "
                    "execution, same-session execution-result feedback, reordering, and rollback remain "
                    "sandbox-only and non-persistent."
                ),
                boundary_change_required=False,
                boundary_index_version_before=SANDBOX_EXECUTION_RESULT_FEEDBACK_LOOP_BOUNDARY_AFTER,
                boundary_index_version_after=SANDBOX_EXECUTION_RESULT_FEEDBACK_LOOP_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Audit-only package; it does not change permission scope, runtime behavior condition, "
                    "persistence, memory, retention, predictor, final_action, direct command, production, or proof boundary."
                ),
            ),
            _task(
                "task.sandbox_final_action_approval_boundary_minimal.completed",
                "PKG-Phase0-SandboxFinalActionApprovalBoundary-Minimal-v0",
                "Sandbox Final Action Approval Boundary Minimal v0",
                "capability_boundary",
                "completed",
                "codex_completed_report",
                ["task.b95_b97_sandbox_action_boundary_audit_minimal.completed"],
                [],
                (
                    "Creates explicit approval for a future Sandbox Final Action Minimal v0 package only; "
                    "final_action is not created in this package and direct command, persistent update, "
                    "memory/retention write, predictor mutation, production behavior, and proof claim remain blocked."
                ),
                boundary_change_required=True,
                boundary_index_version_before=SANDBOX_FINAL_ACTION_APPROVAL_BOUNDARY_BEFORE,
                boundary_index_version_after=SANDBOX_FINAL_ACTION_APPROVAL_BOUNDARY_AFTER,
                boundary_change_rationale=(
                    "Creates an explicit approval boundary for a future sandbox-only final_action package from "
                    "an audited sandbox selected_action and execution-result chain."
                ),
            ),
            _task(
                "task.level2_sandbox_readiness.deferred",
                "PKG-Phase0-Level2-Readiness-Future",
                "Level 2 Sandbox Readiness Minimal v0",
                "capability_boundary",
                "deferred",
                "phase0_future_work",
                ["task.bucket_signal_human_interpretation_review.completed"],
                [],
                "Deferred future boundary; not implemented and not approved.",
                deferral_reason="Level 2 application/execution requires a separate future package after dry-run evaluation.",
            ),
            _task(
                "task.memory_readiness_boundary.deferred",
                "PKG-Phase0-Memory-Readiness-Future",
                "Memory Readiness Boundary Minimal v0",
                "capability_boundary",
                "deferred",
                "phase0_future_work",
                ["task.memory_influenced_sandbox_rerun_minimal.completed"],
                [],
                "Deferred future memory boundary; no memory write or retained JSONL behavior is approved.",
                deferral_reason="Memory readiness remains blocked until a future explicit boundary package.",
            ),
        ],
        "queue_creates_capability": False,
        "queue_counts_as_approval": False,
        "queue_counts_as_application": False,
        "queue_counts_as_runtime_behavior": False,
        "queue_counts_as_memory_write": False,
        "queue_counts_as_retained_jsonl_write": False,
        "queue_counts_as_predictor_mutation": False,
        "queue_counts_as_selected_action": False,
        "queue_counts_as_final_action": False,
        "queue_counts_as_proof_of_learning": False,
        "principles": [BOUNDARY_PRINCIPLE, QUEUE_PRINCIPLE],
    }


def validate_codex_task_queue_minimal(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    for field in sorted(REQUIRED_QUEUE_FIELDS):
        if field not in record:
            errors.append(f"missing_queue_field:{field}")
    for field in sorted(record):
        if field not in REQUIRED_QUEUE_FIELDS:
            errors.append(f"unexpected_queue_field:{field}")

    if record.get("queue_scope") != "phase0_workflow_coordination_only":
        errors.append("queue_scope_not_phase0_workflow_coordination_only")
    if record.get("record_type") != "codex_task_queue_minimal_v0":
        errors.append("record_type_not_codex_task_queue_minimal_v0")
    for field in sorted(QUEUE_FALSE_FIELDS):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    principles = record.get("principles")
    if not isinstance(principles, list) or BOUNDARY_PRINCIPLE not in principles or QUEUE_PRINCIPLE not in principles:
        errors.append("required_principles_missing")

    task_entries = record.get("task_entries")
    task_results: list[dict[str, Any]] = []
    if not isinstance(task_entries, list) or not task_entries:
        errors.append("task_entries_empty_or_not_list")
        task_entries = []

    known_ids = [task.get("task_id") for task in task_entries if isinstance(task, dict)]
    duplicate_ids = {task_id for task_id in known_ids if task_id and known_ids.count(task_id) > 1}
    for task_id in sorted(duplicate_ids):
        errors.append(f"duplicate_task_id:{task_id}")

    known_id_set = {task_id for task_id in known_ids if isinstance(task_id, str)}
    for task in task_entries:
        if not isinstance(task, dict):
            errors.append("task_entry_not_dict")
            continue
        task_result = validate_codex_task_entry_minimal(task, known_id_set)
        task_results.append(task_result)
        errors.extend(f"task:{task_result['task_id']}:{error}" for error in task_result["error_codes"])

    return {
        "queue_name": record.get("queue_name"),
        "valid": not errors,
        "error_codes": errors,
        "task_validation_results": task_results,
        "queue_scope_checked": record.get("queue_scope") == "phase0_workflow_coordination_only",
        "approval_block_checked": record.get("queue_counts_as_approval") is False,
        "runtime_block_checked": record.get("queue_counts_as_runtime_behavior") is False,
        "memory_block_checked": record.get("queue_counts_as_memory_write") is False
        and record.get("queue_counts_as_retained_jsonl_write") is False,
        "predictor_block_checked": record.get("queue_counts_as_predictor_mutation") is False,
        "proof_of_learning_block_checked": record.get("queue_counts_as_proof_of_learning") is False,
    }


def validate_codex_task_entry_minimal(task: dict[str, Any], known_task_ids: set[str] | None = None) -> dict[str, Any]:
    errors: list[str] = []
    known_task_ids = known_task_ids or set()
    for field in sorted(REQUIRED_TASK_FIELDS):
        if field not in task:
            errors.append(f"missing_task_field:{field}")
    if task.get("status") not in ALLOWED_STATUSES:
        errors.append("unknown_task_status")
    if task.get("task_status") != task.get("status"):
        errors.append("task_status_mismatch")
    if task.get("task_type") not in ALLOWED_TASK_TYPES:
        errors.append("unknown_task_type")
    if not isinstance(task.get("package_id"), str) or not task.get("package_id", "").strip():
        errors.append("package_id_missing")
    if task.get("package_title") != task.get("title"):
        errors.append("package_title_mismatch")
    before = task.get("boundary_index_version_before")
    after = task.get("boundary_index_version_after")
    rationale = task.get("boundary_change_rationale", "")
    boundary_change_required = task.get("boundary_change_required")
    if boundary_change_required is not False and boundary_change_required is not True:
        errors.append("boundary_change_required_not_bool")
    if boundary_change_required is False and after != before:
        errors.append("boundary_index_changed_without_boundary_change_required")
    if after != before and boundary_change_required is not True:
        errors.append("boundary_index_changed_but_boundary_change_required_not_true")
    if after != before and not (isinstance(rationale, str) and rationale.strip()):
        errors.append("boundary_index_changed_without_rationale")
    if boundary_change_required is True and not (isinstance(rationale, str) and rationale.strip()):
        errors.append("boundary_change_required_without_rationale")
    if (
        boundary_change_required is True
        and task.get("status") == "completed"
        and isinstance(rationale, str)
        and "completed" in rationale.lower()
        and "boundary" not in rationale.lower()
    ):
        errors.append("task_completion_treated_as_boundary_change")
    for field in sorted(TASK_FALSE_FIELDS):
        if task.get(field) is not False:
            errors.append(f"{field}_not_false")
    for list_field in ("depends_on", "blocks"):
        if not isinstance(task.get(list_field), list):
            errors.append(f"{list_field}_not_list")
            continue
        for task_id in task[list_field]:
            if task_id not in known_task_ids:
                errors.append(f"unknown_dependency:{task_id}")
    if task.get("status") == "blocked" and not task.get("blocker_reason"):
        errors.append("blocked_task_missing_blocker_reason")
    if task.get("status") == "deferred" and not task.get("deferral_reason"):
        errors.append("deferred_task_missing_deferral_reason")
    if task.get("status") == "superseded" and not (task.get("superseded_by") or task.get("notes")):
        errors.append("superseded_task_missing_superseded_by_or_note")
    return {
        "task_id": task.get("task_id"),
        "valid": not errors,
        "error_codes": errors,
        "status": task.get("status"),
        "task_type": task.get("task_type"),
    }


def run_codex_task_queue_minimal_check() -> dict[str, Any]:
    valid_queue = build_codex_task_queue_minimal()
    queues = [valid_queue] + _invalid_queues(valid_queue)
    queue_results = [validate_codex_task_queue_minimal(queue) for queue in queues]
    valid_task_entry_results = queue_results[0]["task_validation_results"]
    invalid_task_entry_results = [
        task_result
        for result in queue_results[1:]
        for task_result in result.get("task_validation_results", [])
        if not task_result.get("valid")
    ]
    summary = _summary(queue_results, valid_task_entry_results, invalid_task_entry_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_codex_task_queue_minimal_checks_passed"] else "failed",
        "task_queues": queues,
        "validation_results": queue_results,
        "summary": summary,
        "boundary_check": {
            "workflow_coordination_only": True,
            "approval_created": False,
            "lesson_application_added": False,
            "sandbox_outcome_evaluation_added": False,
            "runtime_behavior_change_added": False,
            "memory_write_added": False,
            "retained_jsonl_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "proof_of_learning_claimed": False,
        },
        "principles": [BOUNDARY_PRINCIPLE, QUEUE_PRINCIPLE],
    }


def _task(
    task_id: str,
    package_id: str,
    title: str,
    task_type: str,
    status: str,
    source: str,
    depends_on: list[str],
    blocks: list[str],
    notes: str,
    **extra: Any,
) -> dict[str, Any]:
    task = {
        "package_id": package_id,
        "package_title": title,
        "task_id": task_id,
        "title": title,
        "task_status": status,
        "task_type": task_type,
        "status": status,
        "boundary_index_version": BOUNDARY_INDEX_VERSION,
        "boundary_change_required": False,
        "boundary_index_version_before": BOUNDARY_INDEX_VERSION,
        "boundary_index_version_after": BOUNDARY_INDEX_VERSION,
        "source": source,
        "creates_capability": False,
        "counts_as_approval": False,
        "counts_as_runtime_behavior": False,
        "counts_as_memory_write": False,
        "counts_as_retained_jsonl_write": False,
        "counts_as_predictor_mutation": False,
        "counts_as_selected_action": False,
        "counts_as_final_action": False,
        "counts_as_proof_of_learning": False,
        "depends_on": depends_on,
        "blocks": blocks,
        "notes": notes,
        "boundary_change_rationale": "",
    }
    task.update(extra)
    return task


def _invalid_queues(valid_queue: dict[str, Any]) -> list[dict[str, Any]]:
    queues: list[dict[str, Any]] = []
    queues.append(_mutate_task(valid_queue, 0, ["status"], "done"))
    queues.append(_mutate_task(valid_queue, 0, ["task_type"], "planner"))
    duplicate = deepcopy(valid_queue)
    duplicate["task_entries"][1]["task_id"] = duplicate["task_entries"][0]["task_id"]
    queues.append(duplicate)
    queues.append(_mutate_task(valid_queue, 0, ["counts_as_approval"], True))
    for field in (
        "queue_counts_as_approval",
        "queue_counts_as_runtime_behavior",
        "queue_counts_as_memory_write",
        "queue_counts_as_retained_jsonl_write",
        "queue_counts_as_predictor_mutation",
        "queue_counts_as_selected_action",
        "queue_counts_as_final_action",
        "queue_counts_as_proof_of_learning",
    ):
        queues.append(_mutate_queue(valid_queue, [field], True))
    queues.append(_mutate_task(valid_queue, 1, ["depends_on"], ["task.unknown"]))
    queues.append(_mutate_task(valid_queue, 0, ["package_id"], ""))
    queues.append(_mutate_task(valid_queue, 0, ["boundary_index_version_after"], "2026-06-09-b99"))
    queues.append(_mutate_task(valid_queue, 0, ["boundary_change_required"], True))
    no_rationale = _mutate_task(valid_queue, 0, ["boundary_index_version_after"], "2026-06-09-b99")
    no_rationale["task_entries"][0]["boundary_change_required"] = True
    no_rationale["task_entries"][0]["boundary_change_rationale"] = ""
    queues.append(no_rationale)
    completion_rationale = _mutate_task(valid_queue, 0, ["boundary_change_required"], True)
    completion_rationale["task_entries"][0]["boundary_index_version_after"] = "2026-06-09-b99"
    completion_rationale["task_entries"][0]["boundary_change_rationale"] = "Completed task increments version."
    queues.append(completion_rationale)
    blocked = deepcopy(valid_queue)
    blocked["task_entries"].append(
        _task(
            "task.blocked_without_reason",
            "PKG-Negative-Blocked",
            "Blocked missing reason",
            "cleanup",
            "blocked",
            "negative_case",
            [],
            [],
            "Negative case.",
        )
    )
    queues.append(blocked)
    deferred = deepcopy(valid_queue)
    deferred["task_entries"][46].pop("deferral_reason", None)
    queues.append(deferred)
    superseded = deepcopy(valid_queue)
    superseded["task_entries"].append(
        _task(
            "task.superseded_without_note",
            "PKG-Negative-Superseded",
            "Superseded missing note",
            "cleanup",
            "superseded",
            "negative_case",
            [],
            [],
            "",
        )
    )
    queues.append(superseded)
    return queues


def _mutate_queue(record: dict[str, Any], path: list[str], value: Any) -> dict[str, Any]:
    mutated = deepcopy(record)
    current = mutated
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value
    return mutated


def _mutate_task(record: dict[str, Any], task_index: int, path: list[str], value: Any) -> dict[str, Any]:
    mutated = deepcopy(record)
    current = mutated["task_entries"][task_index]
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value
    return mutated


def _summary(
    queue_results: list[dict[str, Any]],
    valid_task_entry_results: list[dict[str, Any]],
    invalid_task_entry_results: list[dict[str, Any]],
) -> dict[str, Any]:
    valid_queues = [result for result in queue_results if result["valid"]]
    summary = {
        "task_queue_result_count": len(queue_results),
        "valid_task_queue_count": len(valid_queues),
        "invalid_task_queue_count": len(queue_results) - len(valid_queues),
        "valid_task_entry_count": sum(1 for result in valid_task_entry_results if result["valid"]),
        "invalid_task_entry_count": len(invalid_task_entry_results),
        "queue_scope_checked_count": sum(1 for result in valid_queues if result["queue_scope_checked"]),
        "approval_block_checked_count": sum(1 for result in valid_queues if result["approval_block_checked"]),
        "runtime_block_checked_count": sum(1 for result in valid_queues if result["runtime_block_checked"]),
        "memory_block_checked_count": sum(1 for result in valid_queues if result["memory_block_checked"]),
        "predictor_block_checked_count": sum(1 for result in valid_queues if result["predictor_block_checked"]),
        "proof_of_learning_block_checked_count": sum(
            1 for result in valid_queues if result["proof_of_learning_block_checked"]
        ),
        "unknown_status_rejected_count": _count_error(queue_results, "unknown_task_status"),
        "unknown_task_type_rejected_count": _count_error(queue_results, "unknown_task_type"),
        "duplicate_task_id_rejected_count": _count_prefix(queue_results, "duplicate_task_id:"),
        "unknown_dependency_rejected_count": _count_prefix(queue_results, "task:task.codex_task_queue.active:unknown_dependency:"),
        "blocked_missing_reason_rejected_count": _count_error(queue_results, "blocked_task_missing_blocker_reason"),
        "deferred_missing_reason_rejected_count": _count_error(queue_results, "deferred_task_missing_deferral_reason"),
        "superseded_missing_reference_rejected_count": _count_error(
            queue_results, "superseded_task_missing_superseded_by_or_note"
        ),
    }
    summary["all_codex_task_queue_minimal_checks_passed"] = (
        summary["task_queue_result_count"] == 22
        and summary["valid_task_queue_count"] == 1
        and summary["invalid_task_queue_count"] == 21
        and summary["valid_task_entry_count"] == 48
        and summary["invalid_task_entry_count"] >= 9
        and summary["queue_scope_checked_count"] == 1
        and summary["approval_block_checked_count"] == 1
        and summary["runtime_block_checked_count"] == 1
        and summary["memory_block_checked_count"] == 1
        and summary["predictor_block_checked_count"] == 1
        and summary["proof_of_learning_block_checked_count"] == 1
        and summary["unknown_status_rejected_count"] == 1
        and summary["unknown_task_type_rejected_count"] == 1
        and summary["duplicate_task_id_rejected_count"] >= 1
        and summary["unknown_dependency_rejected_count"] == 1
        and summary["blocked_missing_reason_rejected_count"] == 1
        and summary["deferred_missing_reason_rejected_count"] == 1
        and summary["superseded_missing_reference_rejected_count"] == 1
    )
    return summary


def _count_error(queue_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in queue_results for error in result["error_codes"] if error.endswith(error_code))


def _count_prefix(queue_results: list[dict[str, Any]], prefix: str) -> int:
    return sum(1 for result in queue_results for error in result["error_codes"] if error.startswith(prefix))


if __name__ == "__main__":
    import json

    print(json.dumps(run_codex_task_queue_minimal_check(), ensure_ascii=False, indent=2))
