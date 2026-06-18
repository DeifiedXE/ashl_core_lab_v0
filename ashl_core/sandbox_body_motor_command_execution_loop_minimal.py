"""Complete body-motor final_action through sandbox command, execution, and outcome trace."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_body_motor_final_action_minimal import (
    build_sandbox_body_motor_final_action_record,
    run_sandbox_body_motor_final_action_minimal_check,
    validate_sandbox_body_motor_final_action_record,
)


COMMAND = "run-sandbox-body-motor-command-execution-loop-minimal-check"
FLOW = "sandbox_body_motor_command_execution_loop_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxBodyMotorCommandExecutionLoop-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b117"
BOUNDARY_INDEX_AFTER = "2026-06-09-b118"

FINAL_ACTION_TO_COMMAND = {
    "step_forward": "sandbox.body.step_forward",
    "reach_front": "sandbox.body.reach_front",
}
FINAL_ACTION_TO_RESULT = {
    "step_forward": "moved_forward_one_cell",
    "reach_front": "front_item_reached",
}
REQUIRED_BLOCKED_FLAGS = (
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "pathfinding_used",
    "route_planner_added",
    "goal_seeking_added",
    "open_ended_loop_created",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "persistent_body_schema_written",
    "semantic_vision",
    "object_recognition",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
    "proof_of_learning_claimed",
)


def build_sandbox_body_motor_command_execution_loop_record(
    final_action_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(final_action_record) if final_action_record is not None else (
        build_sandbox_body_motor_final_action_record()
    )
    source_validation = validate_sandbox_body_motor_final_action_record(source)
    if not source_validation["valid"]:
        raise ValueError("final_action_record must validate before body-motor command execution loop")

    source_summary = _source_summary(source)
    command = _derive_direct_command(source_summary)
    execution = _derive_execution(command)
    outcome = _derive_outcome(source_summary, command, execution)
    return {
        "record_type": "sandbox_body_motor_command_execution_loop_minimal",
        "record_version": "v0",
        "loop_status": "completed_sandbox_body_motor_command_execution_loop",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_body_motor_final_action": source_summary,
        "direct_command_result": command,
        "motor_execution_result": execution,
        "outcome_observation": outcome,
        "human_summary": {
            "what_was_completed": "Approved body-motor final_action records were completed through sandbox-only direct command, execution, and outcome observation.",
            "what_can_execute": "step_forward and reach_front can execute once inside the sandbox when sourced from approved body-motor final_action records.",
            "what_is_blocked": "Unapproved wall/no-action cases remain blocked, and production behavior, pathfinding, persistence, memory writes, predictor mutation, semantic vision, and proof claims remain blocked.",
            "plain_result": "Qingyin can now complete a body-motor action loop inside sandbox only.",
        },
        "blocked_flags": {field: False for field in REQUIRED_BLOCKED_FLAGS},
    }


def validate_sandbox_body_motor_command_execution_loop_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_body_motor_command_execution_loop_minimal",
        "record_version": "v0",
        "loop_status": "completed_sandbox_body_motor_command_execution_loop",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _dict(record.get("source_body_motor_final_action"), errors, "source_body_motor_final_action_missing")
    _validate_source(source, errors)
    expected_command = _derive_direct_command(source)
    command = _dict(record.get("direct_command_result"), errors, "direct_command_result_missing")
    for field, value in expected_command.items():
        if command.get(field) != value:
            errors.append(f"direct_command_result_{field}_not_expected")

    expected_execution = _derive_execution(command)
    execution = _dict(record.get("motor_execution_result"), errors, "motor_execution_result_missing")
    for field, value in expected_execution.items():
        if execution.get(field) != value:
            errors.append(f"motor_execution_result_{field}_not_expected")

    expected_outcome = _derive_outcome(source, command, execution)
    outcome = _dict(record.get("outcome_observation"), errors, "outcome_observation_missing")
    for field, value in expected_outcome.items():
        if outcome.get(field) != value:
            errors.append(f"outcome_observation_{field}_not_expected")

    human = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in ("what_was_completed", "what_can_execute", "what_is_blocked", "plain_result"):
        if not isinstance(human.get(field), str) or not human.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    blocked = _dict(record.get("blocked_flags"), errors, "blocked_flags_missing")
    for field in REQUIRED_BLOCKED_FLAGS:
        if blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "source_final_action_checked": source.get("source_validated") is True,
        "direct_command_created": command.get("direct_command_created") is True,
        "direct_command_blocked": command.get("direct_command_created") is False,
        "direct_command_approval_checked": command.get("direct_command_approval_checked") is True,
        "step_forward_command": command.get("direct_command") == "sandbox.body.step_forward",
        "reach_front_command": command.get("direct_command") == "sandbox.body.reach_front",
        "wall_command_blocked": command.get("blocked_reason") == "final_action_not_available_for_command",
        "motor_action_executed": execution.get("motor_action_executed") is True,
        "motor_action_blocked": execution.get("motor_action_executed") is False,
        "execution_once": execution.get("execution_count") == 1 and execution.get("execution_budget") == 1,
        "outcome_observed": outcome.get("outcome_observed") is True,
        "outcome_blocked": outcome.get("outcome_observed") is False,
        "movement_observed": outcome.get("movement_observed") is True,
        "reach_observed": outcome.get("reach_observed") is True,
        "sandbox_only": command.get("direct_command_scope") == "sandbox_only"
        or command.get("direct_command_scope") is None,
        "production_behavior_blocked": blocked.get("production_behavior_changed") is False
        and execution.get("production_behavior_changed") is False,
        "memory_write_blocked": blocked.get("memory_write_performed") is False
        and blocked.get("retained_jsonl_write_performed") is False
        and outcome.get("memory_write_performed") is False,
        "retention_blocked": blocked.get("retention_write_performed") is False
        and outcome.get("retention_write_performed") is False,
        "predictor_mutation_blocked": blocked.get("predictor_mutation_performed") is False
        and outcome.get("predictor_mutation_performed") is False,
        "pathfinding_blocked": blocked.get("pathfinding_used") is False,
        "persistent_body_schema_blocked": blocked.get("persistent_body_schema_written") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claimed") is False
        and blocked.get("autonomous_learning_claim_allowed") is False
        and blocked.get("autonomous_action_claim_allowed") is False,
    }


def run_sandbox_body_motor_command_execution_loop_minimal_check() -> dict[str, Any]:
    source_result = run_sandbox_body_motor_final_action_minimal_check()
    empty_source, wall_source, item_source = source_result["valid_records"]
    valid_empty = build_sandbox_body_motor_command_execution_loop_record(empty_source)
    valid_wall = build_sandbox_body_motor_command_execution_loop_record(wall_source)
    valid_item = build_sandbox_body_motor_command_execution_loop_record(item_source)
    records = [valid_empty, valid_wall, valid_item, *_invalid_records(valid_empty)]
    validation_results = [validate_sandbox_body_motor_command_execution_loop_record(record) for record in records]
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
            "boundary_reason": "Creates sandbox-only direct commands, executions, and outcome observations from approved body-motor final_action records.",
        },
        "valid_records": [valid_empty, valid_wall, valid_item],
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_completed": "The body-motor sandbox action line now reaches direct command, one-step execution, and outcome observation.",
            "what_is_blocked": "Production behavior, pathfinding, memory writes, retention writes, predictor mutation, persistent body schema, semantic vision, and proof claims remain blocked.",
            "plain_result": "Body-motor final_action can now complete a sandbox-only command execution loop.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    upstream = source["source_body_motor_final_action"] if "source_body_motor_final_action" in source else None
    if upstream is None:
        final_action = source["final_action_result"]
        source_boundary = source["source_final_action_approval_boundary"]
        return {
            "source_record_type": source["record_type"],
            "source_validated": True,
            "body_id": source_boundary["body_id"],
            "body_scope": source_boundary["body_scope"],
            "front_symbol": source_boundary["front_symbol"],
            "final_action_created": final_action["final_action_created"],
            "final_action": final_action["final_action"],
            "final_action_scope": final_action["final_action_scope"],
            "blocked_reason": final_action["blocked_reason"],
            "audit_recorded": final_action["audit_recorded"],
            "rollback_available": final_action["rollback_available"],
        }
    return deepcopy(upstream)


def _derive_direct_command(source: dict[str, Any]) -> dict[str, Any]:
    final_action = source.get("final_action")
    allowed = source.get("final_action_created") is True and final_action in FINAL_ACTION_TO_COMMAND
    return {
        "direct_command_approval_checked": True,
        "direct_command_created": allowed,
        "direct_command": FINAL_ACTION_TO_COMMAND.get(final_action) if allowed else None,
        "direct_command_scope": "sandbox_only" if allowed else None,
        "direct_command_source": "sandbox_body_motor_final_action" if allowed else None,
        "command_payload": {
            "body_id": source.get("body_id"),
            "operation": final_action,
            "front_symbol": source.get("front_symbol"),
            "sandbox_scope": "body_motor_sandbox_only",
        } if allowed else None,
        "blocked_reason": None if allowed else "final_action_not_available_for_command",
        "execution_allowed_in_this_package": allowed,
        "audit_recorded": True,
        "rollback_available": True,
    }


def _derive_execution(command: dict[str, Any]) -> dict[str, Any]:
    direct_command = command.get("direct_command")
    operation = command.get("command_payload", {}).get("operation") if isinstance(command.get("command_payload"), dict) else None
    allowed = command.get("direct_command_created") is True and operation in FINAL_ACTION_TO_RESULT
    return {
        "motor_action_executed": allowed,
        "execution_scope": "sandbox_only" if allowed else None,
        "execution_count": 1 if allowed else 0,
        "execution_budget": 1 if allowed else 0,
        "budget_remaining": 0,
        "direct_command": direct_command if allowed else None,
        "execution_result": FINAL_ACTION_TO_RESULT.get(operation) if allowed else None,
        "result_recorded": allowed,
        "stop_condition_met": True,
        "production_behavior_changed": False,
        "real_navigation_changed": False,
        "ui_behavior_changed": False,
        "blocked_reason": None if allowed else "direct_command_not_available_for_execution",
        "audit_recorded": True,
        "rollback_available": True,
    }


def _derive_outcome(
    source: dict[str, Any],
    command: dict[str, Any],
    execution: dict[str, Any],
) -> dict[str, Any]:
    executed = execution.get("motor_action_executed") is True
    final_action = source.get("final_action")
    return {
        "outcome_observed": executed,
        "outcome_scope": "sandbox_only" if executed else None,
        "source_direct_command": command.get("direct_command") if executed else None,
        "observed_result": execution.get("execution_result") if executed else None,
        "expected_result": FINAL_ACTION_TO_RESULT.get(final_action) if executed else None,
        "outcome_match": executed and execution.get("execution_result") == FINAL_ACTION_TO_RESULT.get(final_action),
        "movement_observed": final_action == "step_forward" and executed,
        "reach_observed": final_action == "reach_front" and executed,
        "front_symbol": source.get("front_symbol"),
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "proof_of_learning_claimed": False,
        "blocked_reason": None if executed else "execution_not_available_for_outcome_observation",
        "audit_recorded": True,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_body_motor_final_action_not_validated")
    if source.get("source_record_type") != "sandbox_body_motor_final_action_minimal":
        errors.append("source_body_motor_final_action_record_type_not_expected")
    if source.get("body_id") != "qingyin_minimal_grid_body_v0":
        errors.append("source_body_motor_final_action_body_id_not_expected")
    if source.get("body_scope") != "sandbox_only":
        errors.append("source_body_motor_final_action_body_scope_not_expected")
    if source.get("final_action") is not None and source.get("final_action") not in FINAL_ACTION_TO_COMMAND:
        errors.append("source_body_motor_final_action_final_action_invalid")
    if source.get("audit_recorded") is not True:
        errors.append("source_body_motor_final_action_audit_not_recorded")
    if source.get("rollback_available") is not True:
        errors.append("source_body_motor_final_action_rollback_not_available")


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, mutator) -> None:
        record = deepcopy(valid_record)
        mutator(record)
        record["invalid_case"] = name
        cases.append(record)

    add("wrong_record_type", lambda r: r.__setitem__("record_type", "body_motor_command"))
    add("source_not_validated", lambda r: r["source_body_motor_final_action"].__setitem__("source_validated", False))
    add("source_bad_final_action", lambda r: r["source_body_motor_final_action"].__setitem__("final_action", "jump"))
    add("source_wrong_scope", lambda r: r["source_body_motor_final_action"].__setitem__("body_scope", "production"))
    add("direct_command_not_created", lambda r: r["direct_command_result"].__setitem__("direct_command_created", False))
    add("wrong_direct_command", lambda r: r["direct_command_result"].__setitem__("direct_command", "sandbox.body.jump"))
    add("wrong_direct_command_scope", lambda r: r["direct_command_result"].__setitem__("direct_command_scope", "production"))
    add("command_approval_missing", lambda r: r["direct_command_result"].__setitem__("direct_command_approval_checked", False))
    add("bad_command_payload", lambda r: r["direct_command_result"].__setitem__("command_payload", {"operation": "jump"}))
    add("execution_not_allowed", lambda r: r["direct_command_result"].__setitem__("execution_allowed_in_this_package", False))
    add("motor_not_executed", lambda r: r["motor_execution_result"].__setitem__("motor_action_executed", False))
    add("wrong_execution_scope", lambda r: r["motor_execution_result"].__setitem__("execution_scope", "production"))
    add("execution_count_two", lambda r: r["motor_execution_result"].__setitem__("execution_count", 2))
    add("execution_budget_two", lambda r: r["motor_execution_result"].__setitem__("execution_budget", 2))
    add("wrong_execution_result", lambda r: r["motor_execution_result"].__setitem__("execution_result", "wrong"))
    add("production_behavior", lambda r: r["motor_execution_result"].__setitem__("production_behavior_changed", True))
    add("real_navigation", lambda r: r["motor_execution_result"].__setitem__("real_navigation_changed", True))
    add("outcome_not_observed", lambda r: r["outcome_observation"].__setitem__("outcome_observed", False))
    add("wrong_outcome_scope", lambda r: r["outcome_observation"].__setitem__("outcome_scope", "production"))
    add("outcome_mismatch", lambda r: r["outcome_observation"].__setitem__("outcome_match", False))
    add("movement_not_observed", lambda r: r["outcome_observation"].__setitem__("movement_observed", False))
    add("memory_write", lambda r: r["outcome_observation"].__setitem__("memory_write_performed", True))
    add("retention_write", lambda r: r["outcome_observation"].__setitem__("retention_write_performed", True))
    add("predictor_mutation", lambda r: r["outcome_observation"].__setitem__("predictor_mutation_performed", True))
    add("blocked_pathfinding", lambda r: r["blocked_flags"].__setitem__("pathfinding_used", True))
    add("blocked_persistent_body_schema", lambda r: r["blocked_flags"].__setitem__("persistent_body_schema_written", True))
    add("blocked_proof_claim", lambda r: r["blocked_flags"].__setitem__("proof_of_learning_claimed", True))
    add("empty_human_summary", lambda r: r["human_summary"].__setitem__("plain_result", ""))
    return cases


def _summary(results: list[dict[str, Any]]) -> dict[str, int]:
    valid_results = [result for result in results if result["valid"]]
    return {
        "command_execution_loop_result_count": len(results),
        "valid_command_execution_loop_count": len(valid_results),
        "invalid_command_execution_loop_count": len(results) - len(valid_results),
        "source_final_action_checked_count": _count_valid(valid_results, "source_final_action_checked"),
        "direct_command_approval_checked_count": _count_valid(valid_results, "direct_command_approval_checked"),
        "direct_command_created_count": _count_valid(valid_results, "direct_command_created"),
        "direct_command_blocked_count": _count_valid(valid_results, "direct_command_blocked"),
        "step_forward_command_count": _count_valid(valid_results, "step_forward_command"),
        "reach_front_command_count": _count_valid(valid_results, "reach_front_command"),
        "wall_command_blocked_count": _count_valid(valid_results, "wall_command_blocked"),
        "motor_action_executed_count": _count_valid(valid_results, "motor_action_executed"),
        "motor_action_blocked_count": _count_valid(valid_results, "motor_action_blocked"),
        "execution_once_count": _count_valid(valid_results, "execution_once"),
        "outcome_observed_count": _count_valid(valid_results, "outcome_observed"),
        "outcome_blocked_count": _count_valid(valid_results, "outcome_blocked"),
        "movement_observed_count": _count_valid(valid_results, "movement_observed"),
        "reach_observed_count": _count_valid(valid_results, "reach_observed"),
        "sandbox_only_count": _count_valid(valid_results, "sandbox_only"),
        "production_behavior_blocked_count": _count_valid(valid_results, "production_behavior_blocked"),
        "memory_write_blocked_count": _count_valid(valid_results, "memory_write_blocked"),
        "retention_blocked_count": _count_valid(valid_results, "retention_blocked"),
        "predictor_mutation_blocked_count": _count_valid(valid_results, "predictor_mutation_blocked"),
        "pathfinding_blocked_count": _count_valid(valid_results, "pathfinding_blocked"),
        "persistent_body_schema_blocked_count": _count_valid(valid_results, "persistent_body_schema_blocked"),
        "proof_claim_blocked_count": _count_valid(valid_results, "proof_claim_blocked"),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["command_execution_loop_result_count"] == 31
        and summary["valid_command_execution_loop_count"] == 3
        and summary["invalid_command_execution_loop_count"] == 28
        and summary["source_final_action_checked_count"] == 3
        and summary["direct_command_approval_checked_count"] == 3
        and summary["direct_command_created_count"] == 2
        and summary["direct_command_blocked_count"] == 1
        and summary["step_forward_command_count"] == 1
        and summary["reach_front_command_count"] == 1
        and summary["wall_command_blocked_count"] == 1
        and summary["motor_action_executed_count"] == 2
        and summary["motor_action_blocked_count"] == 1
        and summary["execution_once_count"] == 2
        and summary["outcome_observed_count"] == 2
        and summary["outcome_blocked_count"] == 1
        and summary["movement_observed_count"] == 1
        and summary["reach_observed_count"] == 1
        and summary["sandbox_only_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["retention_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["pathfinding_blocked_count"] == 3
        and summary["persistent_body_schema_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
    )


def _dict(value: Any, errors: list[str], error_code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(error_code)
        return {}
    return value


def _count_valid(results: list[dict[str, Any]], field: str) -> int:
    return sum(1 for result in results if result.get(field) is True)
