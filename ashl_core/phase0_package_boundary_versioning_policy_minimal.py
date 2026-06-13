"""Validate separation between Codex Package IDs and Boundary Index versions."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-phase0-package-boundary-versioning-policy-minimal-check"
FLOW = "phase0_package_boundary_versioning_policy_minimal_v0"
RECORD_TYPE = "phase0_package_boundary_versioning_policy"
ALLOWED_BOUNDARY_INCREMENT_REASONS = (
    "boundary_definition_change",
    "permission_scope_change",
    "persistent_condition_change",
    "runtime_behavior_condition_change",
    "memory_write_condition_change",
    "retained_jsonl_or_retention_rule_change",
    "predictor_influence_or_mutation_condition_change",
    "sandbox_application_or_execution_permission_change",
    "selected_action_or_final_action_boundary_change",
    "production_promotion_boundary_change",
    "approval_authority_or_validation_boundary_change",
    "validation_boundary_change",
)
FALSE_CAPABILITY_FIELDS = (
    "runtime_behavior_changed",
    "memory_written",
    "retained_jsonl_written",
    "retention_written",
    "predictor_mutated",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "production_promoted",
    "proof_of_learning_claimed",
)


def build_phase0_package_boundary_versioning_policy_record() -> dict[str, Any]:
    return {
        "record_type": RECORD_TYPE,
        "package_id": "PKG-Phase0-Versioning-001",
        "package_id_required": True,
        "boundary_index_is_not_package_counter": True,
        "codex_task_completion_auto_increments_boundary_index": False,
        "boundary_change_required_for_boundary_increment": True,
        "boundary_change_rationale_required": True,
        "allowed_boundary_increment_reasons": list(ALLOWED_BOUNDARY_INCREMENT_REASONS),
        "non_boundary_package_changes_do_not_increment_boundary_index": True,
        "completed_task_counts_as_boundary_change": False,
        "cli_added_counts_as_boundary_change": False,
        "smoke_test_added_counts_as_boundary_change": False,
        "unittest_added_counts_as_boundary_change": False,
        "documentation_update_counts_as_boundary_change": False,
        "task_queue_status_update_counts_as_boundary_change": False,
        "runtime_behavior_changed": False,
        "memory_written": False,
        "retained_jsonl_written": False,
        "retention_written": False,
        "predictor_mutated": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "production_promoted": False,
        "proof_of_learning_claimed": False,
    }


def validate_phase0_package_boundary_versioning_policy_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != RECORD_TYPE:
        errors.append("record_type_not_phase0_package_boundary_versioning_policy")
    if not isinstance(record.get("package_id"), str) or not record.get("package_id", "").strip():
        errors.append("package_id_missing")
    for field in (
        "package_id_required",
        "boundary_index_is_not_package_counter",
        "boundary_change_required_for_boundary_increment",
        "boundary_change_rationale_required",
        "non_boundary_package_changes_do_not_increment_boundary_index",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in (
        "codex_task_completion_auto_increments_boundary_index",
        "completed_task_counts_as_boundary_change",
        "cli_added_counts_as_boundary_change",
        "smoke_test_added_counts_as_boundary_change",
        "unittest_added_counts_as_boundary_change",
        "documentation_update_counts_as_boundary_change",
        "task_queue_status_update_counts_as_boundary_change",
    ) + FALSE_CAPABILITY_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if set(record.get("allowed_boundary_increment_reasons", [])) != set(ALLOWED_BOUNDARY_INCREMENT_REASONS):
        errors.append("allowed_boundary_increment_reasons_not_explicit")
    return {
        "valid": not errors,
        "error_codes": errors,
        "package_id_required": record.get("package_id_required") is True,
        "boundary_index_is_not_package_counter": record.get("boundary_index_is_not_package_counter") is True,
        "codex_completion_auto_increment_blocked": (
            record.get("codex_task_completion_auto_increments_boundary_index") is False
        ),
        "boundary_change_rationale_required": record.get("boundary_change_rationale_required") is True,
        "runtime_behavior_changed": record.get("runtime_behavior_changed") is True,
        "memory_written": record.get("memory_written") is True,
        "retention_written": record.get("retention_written") is True,
        "predictor_mutated": record.get("predictor_mutated") is True,
        "selected_action_created": record.get("selected_action_created") is True,
        "final_action_created": record.get("final_action_created") is True,
        "production_promoted": record.get("production_promoted") is True,
        "proof_of_learning_claimed": record.get("proof_of_learning_claimed") is True,
    }


def validate_phase0_package_boundary_task_versioning(task: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    before = task.get("boundary_index_version_before")
    after = task.get("boundary_index_version_after")
    rationale = task.get("boundary_change_rationale", "")
    if not isinstance(task.get("package_id"), str) or not task.get("package_id", "").strip():
        errors.append("package_id_missing")
    if task.get("boundary_change_required") is False and after != before:
        errors.append("boundary_index_changed_without_boundary_change_required")
    if after != before and task.get("boundary_change_required") is not True:
        errors.append("boundary_index_changed_but_boundary_change_required_not_true")
    if after != before and not (isinstance(rationale, str) and rationale.strip()):
        errors.append("boundary_index_changed_without_rationale")
    if task.get("boundary_change_required") is True and not (isinstance(rationale, str) and rationale.strip()):
        errors.append("boundary_change_required_without_rationale")
    if (
        task.get("boundary_change_required") is True
        and isinstance(rationale, str)
        and "completed" in rationale.lower()
        and "boundary" not in rationale.lower()
    ):
        errors.append("task_completion_treated_as_boundary_change")
    return {"valid": not errors, "error_codes": errors}


def run_phase0_package_boundary_versioning_policy_minimal_check() -> dict[str, Any]:
    valid = build_phase0_package_boundary_versioning_policy_record()
    invalid_records = [
        _mutated(valid, ["package_id"], ""),
        _mutated(valid, ["boundary_index_is_not_package_counter"], False),
        _mutated(valid, ["codex_task_completion_auto_increments_boundary_index"], True),
        _mutated(valid, ["boundary_change_required_for_boundary_increment"], False),
        _mutated(valid, ["boundary_change_rationale_required"], False),
        _mutated(valid, ["documentation_update_counts_as_boundary_change"], True),
        _mutated(valid, ["task_queue_status_update_counts_as_boundary_change"], True),
        _mutated(valid, ["runtime_behavior_changed"], True),
        _mutated(valid, ["memory_written"], True),
        _mutated(valid, ["retention_written"], True),
        _mutated(valid, ["predictor_mutated"], True),
        _mutated(valid, ["selected_action_created"], True),
        _mutated(valid, ["final_action_created"], True),
        _mutated(valid, ["production_promoted"], True),
        _mutated(valid, ["proof_of_learning_claimed"], True),
    ]
    task_fixtures = [
        _task_fixture(package_id=""),
        _task_fixture(after="2026-06-09-b99"),
        _task_fixture(after="2026-06-09-b99", boundary_change_required=True, rationale=""),
        _task_fixture(
            after="2026-06-09-b99",
            boundary_change_required=True,
            rationale="Completed task increments version.",
        ),
    ]
    record_results = [validate_phase0_package_boundary_versioning_policy_record(record) for record in [valid] + invalid_records]
    task_results = [validate_phase0_package_boundary_task_versioning(task) for task in task_fixtures]
    valid_results = [result for result in record_results if result.get("valid")]
    summary = {
        "valid_versioning_policy_count": len(valid_results),
        "invalid_versioning_policy_count": len(record_results) - len(valid_results) + len(task_results),
        "package_id_required": valid_results[0]["package_id_required"] if valid_results else False,
        "boundary_index_is_not_package_counter": (
            valid_results[0]["boundary_index_is_not_package_counter"] if valid_results else False
        ),
        "codex_completion_auto_increment_blocked": (
            valid_results[0]["codex_completion_auto_increment_blocked"] if valid_results else False
        ),
        "boundary_change_rationale_required": (
            valid_results[0]["boundary_change_rationale_required"] if valid_results else False
        ),
        "runtime_behavior_changed": False,
        "memory_written": False,
        "retention_written": False,
        "predictor_mutated": False,
        "selected_action_created": False,
        "final_action_created": False,
        "production_promoted": False,
        "proof_of_learning_claimed": False,
    }
    summary["all_phase0_package_boundary_versioning_policy_checks_passed"] = (
        summary["valid_versioning_policy_count"] == 1
        and summary["invalid_versioning_policy_count"] >= 1
        and summary["package_id_required"] is True
        and summary["boundary_index_is_not_package_counter"] is True
        and summary["codex_completion_auto_increment_blocked"] is True
        and summary["boundary_change_rationale_required"] is True
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_phase0_package_boundary_versioning_policy_checks_passed"] else "failed",
        "policy_records": [valid] + invalid_records,
        "task_versioning_fixtures": task_fixtures,
        "policy_validation_results": record_results,
        "task_versioning_validation_results": task_results,
        "summary": summary,
        "boundary_check": {
            "workflow_governance_only": True,
            "boundary_index_is_package_counter": False,
            "runtime_behavior_change_added": False,
            "memory_write_added": False,
            "retained_jsonl_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "production_promotion_added": False,
            "proof_of_learning_claimed": False,
        },
    }


def _task_fixture(
    package_id: str = "PKG-Test-001",
    before: str = "2026-06-09-b72",
    after: str = "2026-06-09-b72",
    boundary_change_required: bool = False,
    rationale: str = "",
) -> dict[str, Any]:
    return {
        "package_id": package_id,
        "boundary_index_version_before": before,
        "boundary_index_version_after": after,
        "boundary_change_required": boundary_change_required,
        "boundary_change_rationale": rationale,
    }


def _mutated(record: dict[str, Any], path: list[str], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: dict[str, Any] = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(run_phase0_package_boundary_versioning_policy_minimal_check(), indent=2))
