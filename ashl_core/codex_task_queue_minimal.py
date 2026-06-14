"""Minimal Codex task queue for Phase0 workflow coordination."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-codex-task-queue-minimal-check"
FLOW = "codex_task_queue_minimal_v0"
BOUNDARY_INDEX_VERSION = "2026-06-09-b75"
PREVIOUS_BOUNDARY_INDEX_VERSION = "2026-06-09-b74"
LEVEL2_APPLICATION_BOUNDARY_BEFORE = "2026-06-09-b72"
LEVEL2_APPLICATION_BOUNDARY_AFTER = "2026-06-09-b73"
LEVEL3_TOY_MINEFIELD_BOUNDARY_BEFORE = "2026-06-09-b73"
LEVEL3_TOY_MINEFIELD_BOUNDARY_AFTER = "2026-06-09-b74"
MEMORY_ADMISSION_APPROVAL_BOUNDARY_BEFORE = "2026-06-09-b74"
MEMORY_ADMISSION_APPROVAL_BOUNDARY_AFTER = "2026-06-09-b75"
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
                ["task.memory_admission_approval_boundary.completed"],
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
    deferred["task_entries"][19].pop("deferral_reason", None)
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
        and summary["valid_task_entry_count"] == 21
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
