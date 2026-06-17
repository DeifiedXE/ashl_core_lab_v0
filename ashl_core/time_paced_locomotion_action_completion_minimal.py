"""Complete time-paced sandbox locomotion steps through the sandbox action line."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .temporal_candy_loop_sandbox_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    MAX_ACTION_STEPS,
    MIN_IDLE_TICKS_BETWEEN_ACTIONS,
    build_temporal_candy_loop_sandbox_record,
    validate_temporal_candy_loop_sandbox_record,
)


COMMAND = "run-time-paced-locomotion-action-completion-minimal-check"
FLOW = "time_paced_locomotion_action_completion_minimal_v0"
PACKAGE_ID = "PKG-Phase0-TimePacedLocomotionActionCompletion-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b106"
BOUNDARY_INDEX_AFTER = "2026-06-09-b107"
SANDBOX_SCOPE = "temporal_candy_loop_sandbox_v0"
SUPPORTED_LOCOMOTION_ACTIONS = ("move_forward", "turn_left", "turn_right", "look")

BLOCKED_FLAGS = (
    "background_autonomy_started",
    "free_choice_added",
    "pathfinding_used",
    "open_ended_loop_created",
    "too_fast_action_allowed",
    "cooldown_bypassed",
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_feedback_created",
    "cross_session_feedback_persistence",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "endocrine_runtime_used",
    "runtime_behavior_changed_outside_sandbox",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
    "proof_of_learning_claim_allowed",
)


def build_time_paced_locomotion_action_completion_record(
    temporal_loop_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_loop = deepcopy(temporal_loop_record) if temporal_loop_record is not None else build_temporal_candy_loop_sandbox_record()
    action_lines = [
        _build_action_line_from_temporal_step(step)
        for step in source_loop.get("steps", [])
    ]
    return {
        "record_type": "time_paced_locomotion_action_completion",
        "record_version": "v0",
        "completion_status": "completed_sandbox_locomotion_action_line_for_time_paced_loop",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "source_temporal_loop": {
            "record_type": source_loop.get("record_type"),
            "source_boundary_index": SOURCE_BOUNDARY_INDEX,
            "source_loop_status": source_loop.get("loop_status"),
            "source_sandbox_id": source_loop.get("sandbox_context", {}).get("sandbox_id"),
            "source_time_model": source_loop.get("sandbox_context", {}).get("time_model"),
            "source_active_step_count": source_loop.get("time_summary", {}).get("active_step_count"),
            "source_idle_tick_total": source_loop.get("time_summary", {}).get("idle_tick_total"),
            "source_loop_stopped_by_budget": source_loop.get("time_summary", {}).get("loop_stopped_by_budget"),
            "source_validated": validate_temporal_candy_loop_sandbox_record(source_loop).get("valid") is True,
        },
        "completion_config": {
            "sandbox_scope": SANDBOX_SCOPE,
            "completion_scope": "sandbox_only",
            "supported_locomotion_actions": list(SUPPORTED_LOCOMOTION_ACTIONS),
            "manual_action_plan_reused": True,
            "free_choice_added": False,
            "background_autonomy_started": False,
            "pathfinding_used": False,
            "open_ended_loop": False,
            "active_steps_required": MAX_ACTION_STEPS,
            "min_idle_ticks_between_actions": MIN_IDLE_TICKS_BETWEEN_ACTIONS,
        },
        "action_lines": action_lines,
        "completion_summary": {
            "active_step_count": len(action_lines),
            "selected_action_created_count": len(action_lines),
            "final_action_created_count": len(action_lines),
            "direct_command_created_count": len(action_lines),
            "direct_command_executed_count": len(action_lines),
            "outcome_evaluation_created_count": len(action_lines),
            "cooldown_satisfied_count": sum(1 for line in action_lines if line["cooldown_satisfied"]),
            "candy_contact_action_line_count": sum(1 for line in action_lines if line["outcome_evaluation"]["candy_contact"]),
            "loop_stopped_by_budget": True,
            "next_action_authorized_after_budget": False,
        },
        "human_summary": {
            "what_was_completed": "Each ACTIVE step from the time-paced candy loop was completed through the sandbox action line.",
            "what_the_action_line_contains": "Every step has sandbox selected_action, final_action, direct command, execution, and outcome evaluation records.",
            "what_remains_manual": "The locomotion plan remains a fixed manual sandbox plan; no free choice or pathfinding was added.",
            "what_is_blocked": "Background autonomy, production behavior, real navigation/UI changes, memory writes, retention writes, predictor mutation, endocrine runtime, and proof claims remain blocked.",
            "plain_result": "The time-paced candy loop now has complete sandbox action-line records for each locomotion step.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_time_paced_locomotion_action_completion_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "time_paced_locomotion_action_completion",
        "record_version": "v0",
        "completion_status": "completed_sandbox_locomotion_action_line_for_time_paced_loop",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _dict(record.get("source_temporal_loop"), errors, "source_temporal_loop_missing")
    expected_source = {
        "record_type": "temporal_candy_loop_sandbox",
        "source_boundary_index": SOURCE_BOUNDARY_INDEX,
        "source_loop_status": "completed_time_paced_sandbox_candy_loop",
        "source_sandbox_id": SANDBOX_SCOPE,
        "source_time_model": "OFFLINE_IDLE_ACTIVE_trace",
        "source_active_step_count": MAX_ACTION_STEPS,
        "source_idle_tick_total": MAX_ACTION_STEPS * MIN_IDLE_TICKS_BETWEEN_ACTIONS,
        "source_loop_stopped_by_budget": True,
        "source_validated": True,
    }
    for field, value in expected_source.items():
        if source.get(field) != value:
            errors.append(f"source_temporal_loop_{field}_not_expected")

    config = _dict(record.get("completion_config"), errors, "completion_config_missing")
    expected_config = {
        "sandbox_scope": SANDBOX_SCOPE,
        "completion_scope": "sandbox_only",
        "supported_locomotion_actions": list(SUPPORTED_LOCOMOTION_ACTIONS),
        "manual_action_plan_reused": True,
        "free_choice_added": False,
        "background_autonomy_started": False,
        "pathfinding_used": False,
        "open_ended_loop": False,
        "active_steps_required": MAX_ACTION_STEPS,
        "min_idle_ticks_between_actions": MIN_IDLE_TICKS_BETWEEN_ACTIONS,
    }
    for field, value in expected_config.items():
        if config.get(field) != value:
            errors.append(f"completion_config_{field}_not_expected")

    lines = record.get("action_lines")
    if not isinstance(lines, list):
        errors.append("action_lines_not_list")
        lines = []
    if len(lines) != MAX_ACTION_STEPS:
        errors.append("action_line_count_not_expected")
    line_results = [_validate_action_line(line, index) for index, line in enumerate(lines, start=1)]
    for result in line_results:
        errors.extend(result["error_codes"])

    summary = _dict(record.get("completion_summary"), errors, "completion_summary_missing")
    expected_summary = {
        "active_step_count": MAX_ACTION_STEPS,
        "selected_action_created_count": MAX_ACTION_STEPS,
        "final_action_created_count": MAX_ACTION_STEPS,
        "direct_command_created_count": MAX_ACTION_STEPS,
        "direct_command_executed_count": MAX_ACTION_STEPS,
        "outcome_evaluation_created_count": MAX_ACTION_STEPS,
        "cooldown_satisfied_count": MAX_ACTION_STEPS,
        "candy_contact_action_line_count": 1,
        "loop_stopped_by_budget": True,
        "next_action_authorized_after_budget": False,
    }
    for field, value in expected_summary.items():
        if summary.get(field) != value:
            errors.append(f"completion_summary_{field}_not_expected")

    human_summary = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in (
        "what_was_completed",
        "what_the_action_line_contains",
        "what_remains_manual",
        "what_is_blocked",
        "plain_result",
    ):
        if not isinstance(human_summary.get(field), str) or not human_summary.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    blocked_flags = _dict(record.get("blocked_flags"), errors, "blocked_flags_missing")
    for field in BLOCKED_FLAGS:
        if blocked_flags.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "source_temporal_loop_checked": source.get("source_validated") is True,
        "action_line_completed": all(result["action_line_completed"] for result in line_results),
        "cooldown_checked": all(result["cooldown_satisfied"] for result in line_results),
        "selected_action_created_count": sum(1 for result in line_results if result["selected_action_created"]),
        "final_action_created_count": sum(1 for result in line_results if result["final_action_created"]),
        "direct_command_created_count": sum(1 for result in line_results if result["direct_command_created"]),
        "direct_command_executed_count": sum(1 for result in line_results if result["direct_command_executed"]),
        "outcome_evaluation_created_count": sum(1 for result in line_results if result["outcome_evaluation_created"]),
        "candy_contact_action_line_count": sum(1 for result in line_results if result["candy_contact"]),
        "loop_stopped_by_budget": summary.get("loop_stopped_by_budget") is True
        and summary.get("next_action_authorized_after_budget") is False,
        "free_choice_blocked": config.get("free_choice_added") is False and blocked_flags.get("free_choice_added") is False,
        "background_autonomy_blocked": config.get("background_autonomy_started") is False
        and blocked_flags.get("background_autonomy_started") is False,
        "pathfinding_blocked": config.get("pathfinding_used") is False and blocked_flags.get("pathfinding_used") is False,
        "open_ended_loop_blocked": config.get("open_ended_loop") is False
        and blocked_flags.get("open_ended_loop_created") is False,
        "too_fast_action_blocked": blocked_flags.get("too_fast_action_allowed") is False
        and blocked_flags.get("cooldown_bypassed") is False,
        "production_behavior_blocked": blocked_flags.get("production_behavior_changed") is False
        and blocked_flags.get("real_navigation_changed") is False
        and blocked_flags.get("ui_behavior_changed") is False,
        "memory_write_blocked": blocked_flags.get("memory_write_performed") is False
        and blocked_flags.get("retained_jsonl_write_performed") is False,
        "retention_blocked": blocked_flags.get("retention_write_performed") is False,
        "predictor_mutation_blocked": blocked_flags.get("predictor_read_enabled") is False
        and blocked_flags.get("predictor_influence_enabled") is False
        and blocked_flags.get("predictor_mutation_performed") is False,
        "endocrine_runtime_blocked": blocked_flags.get("endocrine_runtime_used") is False,
        "proof_claim_blocked": blocked_flags.get("proof_of_learning_claim_allowed") is False
        and blocked_flags.get("autonomous_learning_claim_allowed") is False
        and blocked_flags.get("autonomous_action_claim_allowed") is False,
    }


def run_time_paced_locomotion_action_completion_minimal_check() -> dict[str, Any]:
    valid_record = build_time_paced_locomotion_action_completion_record()
    valid_result = validate_time_paced_locomotion_action_completion_record(valid_record)
    invalid_results = [validate_time_paced_locomotion_action_completion_record(item) for item in _invalid_records(valid_record)]
    summary = {
        "valid_time_paced_locomotion_completion_count": 1 if valid_result["valid"] else 0,
        "invalid_time_paced_locomotion_completion_count": sum(1 for result in invalid_results if not result["valid"]),
        "source_temporal_loop_checked_count": 1 if valid_result["source_temporal_loop_checked"] else 0,
        "action_line_completed_count": 1 if valid_result["action_line_completed"] else 0,
        "cooldown_checked_count": 1 if valid_result["cooldown_checked"] else 0,
        "selected_action_created_total": valid_result["selected_action_created_count"],
        "final_action_created_total": valid_result["final_action_created_count"],
        "direct_command_created_total": valid_result["direct_command_created_count"],
        "direct_command_executed_total": valid_result["direct_command_executed_count"],
        "outcome_evaluation_created_total": valid_result["outcome_evaluation_created_count"],
        "candy_contact_action_line_total": valid_result["candy_contact_action_line_count"],
        "loop_stopped_by_budget_count": 1 if valid_result["loop_stopped_by_budget"] else 0,
        "free_choice_blocked_count": 1 if valid_result["free_choice_blocked"] else 0,
        "background_autonomy_blocked_count": 1 if valid_result["background_autonomy_blocked"] else 0,
        "pathfinding_blocked_count": 1 if valid_result["pathfinding_blocked"] else 0,
        "open_ended_loop_blocked_count": 1 if valid_result["open_ended_loop_blocked"] else 0,
        "too_fast_action_blocked_count": 1 if valid_result["too_fast_action_blocked"] else 0,
        "production_behavior_blocked_count": 1 if valid_result["production_behavior_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "endocrine_runtime_blocked_count": 1 if valid_result["endocrine_runtime_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_time_paced_locomotion_action_completion_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_time_paced_locomotion_completion_count"] == 39
        and summary["selected_action_created_total"] == MAX_ACTION_STEPS
        and summary["final_action_created_total"] == MAX_ACTION_STEPS
        and summary["direct_command_created_total"] == MAX_ACTION_STEPS
        and summary["direct_command_executed_total"] == MAX_ACTION_STEPS
        and summary["outcome_evaluation_created_total"] == MAX_ACTION_STEPS
        and summary["candy_contact_action_line_total"] == 1
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_time_paced_locomotion_action_completion_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Completes each time-paced sandbox locomotion step through selected_action, final_action, direct command, execution, and outcome evaluation records.",
        },
        "valid_completion": valid_record,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
    }


def _build_action_line_from_temporal_step(step: dict[str, Any]) -> dict[str, Any]:
    action = step["action"]
    direct_command = f"sandbox.{action}"
    result = step["result"]
    return {
        "line_id": f"time_paced_locomotion_action_line_{step['step_index']:03d}",
        "source_temporal_step_index": step["step_index"],
        "source_runtime_tick_after_action": step["runtime_tick_after_action"],
        "source_action_tick": step["action_tick"],
        "source_idle_ticks_before_action": step["idle_ticks_before_action"],
        "cooldown_satisfied": step["cooldown_satisfied"],
        "mode_during_action": "ACTIVE",
        "selected_action": {
            "record_type": "sandbox_locomotion_selected_action",
            "selected_action_created": True,
            "selected_action": action,
            "selection_source": "manual_time_paced_sandbox_plan",
            "free_choice_added": False,
            "sandbox_scope": SANDBOX_SCOPE,
        },
        "final_action": {
            "record_type": "sandbox_locomotion_final_action",
            "final_action_created": True,
            "final_action": action,
            "source_selected_action": action,
            "sandbox_scope": SANDBOX_SCOPE,
        },
        "direct_command": {
            "record_type": "sandbox_locomotion_direct_command",
            "direct_command_created": True,
            "direct_command": direct_command,
            "direct_command_scope": "sandbox_only",
            "command_payload": {
                "sandbox_scope": SANDBOX_SCOPE,
                "operation": action,
                "source_temporal_step_index": step["step_index"],
            },
        },
        "execution": {
            "record_type": "sandbox_locomotion_direct_command_execution",
            "direct_command_executed": True,
            "execution_scope": "sandbox_only",
            "execution_budget": 1,
            "execution_count": 1,
            "budget_remaining": 0,
            "execution_result": result,
            "sandbox_action_trace": step["sandbox_action_trace"],
            "production_behavior_changed": False,
            "real_navigation_changed": False,
            "ui_behavior_changed": False,
        },
        "outcome_evaluation": {
            "record_type": "sandbox_locomotion_outcome_evaluation",
            "outcome_evaluation_created": True,
            "evaluation_result": "passed",
            "observed_result": result,
            "front_symbol": step["front_symbol"],
            "candy_contact": step["candy_contact"],
            "movement_or_turn_recorded": result in {"item_contact", "moved", "turned"},
            "memory_write": False,
            "retention_write": False,
            "predictor_modified": False,
            "proof_of_learning_claim": False,
        },
    }


def _validate_action_line(line: Any, expected_index: int) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(line, dict):
        return {
            "error_codes": [f"action_line_{expected_index}_not_dict"],
            "action_line_completed": False,
            "cooldown_satisfied": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "direct_command_executed": False,
            "outcome_evaluation_created": False,
            "candy_contact": False,
        }
    action = line.get("selected_action", {}).get("selected_action")
    if line.get("source_temporal_step_index") != expected_index:
        errors.append(f"action_line_{expected_index}_source_step_not_expected")
    if line.get("cooldown_satisfied") is not True:
        errors.append(f"action_line_{expected_index}_cooldown_not_satisfied")
    if line.get("mode_during_action") != "ACTIVE":
        errors.append(f"action_line_{expected_index}_mode_not_active")
    if action not in SUPPORTED_LOCOMOTION_ACTIONS:
        errors.append(f"action_line_{expected_index}_unsupported_action")
    selected = _nested(line, "selected_action", errors, expected_index)
    final = _nested(line, "final_action", errors, expected_index)
    command = _nested(line, "direct_command", errors, expected_index)
    execution = _nested(line, "execution", errors, expected_index)
    evaluation = _nested(line, "outcome_evaluation", errors, expected_index)

    if selected.get("selected_action_created") is not True:
        errors.append(f"action_line_{expected_index}_selected_action_not_created")
    if selected.get("selection_source") != "manual_time_paced_sandbox_plan":
        errors.append(f"action_line_{expected_index}_selection_source_not_expected")
    if selected.get("free_choice_added") is not False:
        errors.append(f"action_line_{expected_index}_free_choice_added")
    if final.get("final_action_created") is not True or final.get("final_action") != action:
        errors.append(f"action_line_{expected_index}_final_action_not_expected")
    if command.get("direct_command_created") is not True:
        errors.append(f"action_line_{expected_index}_direct_command_not_created")
    if command.get("direct_command") != f"sandbox.{action}":
        errors.append(f"action_line_{expected_index}_direct_command_not_expected")
    if execution.get("direct_command_executed") is not True:
        errors.append(f"action_line_{expected_index}_direct_command_not_executed")
    if execution.get("execution_scope") != "sandbox_only":
        errors.append(f"action_line_{expected_index}_execution_scope_not_sandbox")
    if execution.get("execution_count") != 1 or execution.get("execution_budget") != 1:
        errors.append(f"action_line_{expected_index}_execution_budget_not_expected")
    if execution.get("production_behavior_changed") is not False:
        errors.append(f"action_line_{expected_index}_production_behavior_changed")
    if evaluation.get("outcome_evaluation_created") is not True:
        errors.append(f"action_line_{expected_index}_outcome_evaluation_not_created")
    if evaluation.get("evaluation_result") != "passed":
        errors.append(f"action_line_{expected_index}_evaluation_not_passed")
    if evaluation.get("observed_result") != execution.get("execution_result"):
        errors.append(f"action_line_{expected_index}_evaluation_execution_mismatch")
    for field in ("memory_write", "retention_write", "predictor_modified", "proof_of_learning_claim"):
        if evaluation.get(field) is not False:
            errors.append(f"action_line_{expected_index}_{field}_not_false")
    if expected_index == 1 and evaluation.get("candy_contact") is not True:
        errors.append("action_line_1_candy_contact_missing")
    if expected_index != 1 and evaluation.get("candy_contact") is not False:
        errors.append(f"action_line_{expected_index}_unexpected_candy_contact")

    return {
        "error_codes": errors,
        "action_line_completed": not errors,
        "cooldown_satisfied": line.get("cooldown_satisfied") is True,
        "selected_action_created": selected.get("selected_action_created") is True,
        "final_action_created": final.get("final_action_created") is True,
        "direct_command_created": command.get("direct_command_created") is True,
        "direct_command_executed": execution.get("direct_command_executed") is True,
        "outcome_evaluation_created": evaluation.get("outcome_evaluation_created") is True,
        "candy_contact": evaluation.get("candy_contact") is True,
    }


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def add(mutator) -> None:
        item = deepcopy(valid_record)
        mutator(item)
        invalids.append(item)

    add(lambda r: r.update({"record_type": "wrong"}))
    add(lambda r: r.update({"boundary_index_after": "2026-06-09-b106"}))
    add(lambda r: r["source_temporal_loop"].update({"source_validated": False}))
    add(lambda r: r["source_temporal_loop"].update({"source_active_step_count": 5}))
    add(lambda r: r["completion_config"].update({"completion_scope": "production"}))
    add(lambda r: r["completion_config"].update({"manual_action_plan_reused": False}))
    add(lambda r: r["completion_config"].update({"free_choice_added": True}))
    add(lambda r: r["completion_config"].update({"background_autonomy_started": True}))
    add(lambda r: r["completion_config"].update({"pathfinding_used": True}))
    add(lambda r: r["completion_config"].update({"open_ended_loop": True}))
    add(lambda r: r["completion_config"].update({"active_steps_required": 7}))
    add(lambda r: r.update({"action_lines": r["action_lines"][:-1]}))
    add(lambda r: r["action_lines"][0].update({"cooldown_satisfied": False}))
    add(lambda r: r["action_lines"][0].update({"mode_during_action": "IDLE"}))
    add(lambda r: r["action_lines"][0]["selected_action"].update({"selected_action_created": False}))
    add(lambda r: r["action_lines"][0]["selected_action"].update({"selected_action": "unsupported"}))
    add(lambda r: r["action_lines"][0]["selected_action"].update({"selection_source": "free_choice"}))
    add(lambda r: r["action_lines"][0]["selected_action"].update({"free_choice_added": True}))
    add(lambda r: r["action_lines"][0]["final_action"].update({"final_action_created": False}))
    add(lambda r: r["action_lines"][0]["final_action"].update({"final_action": "turn_left"}))
    add(lambda r: r["action_lines"][0]["direct_command"].update({"direct_command_created": False}))
    add(lambda r: r["action_lines"][0]["direct_command"].update({"direct_command": "sandbox.unsupported"}))
    add(lambda r: r["action_lines"][0]["execution"].update({"direct_command_executed": False}))
    add(lambda r: r["action_lines"][0]["execution"].update({"execution_scope": "production"}))
    add(lambda r: r["action_lines"][0]["execution"].update({"execution_count": 2}))
    add(lambda r: r["action_lines"][0]["execution"].update({"production_behavior_changed": True}))
    add(lambda r: r["action_lines"][0]["outcome_evaluation"].update({"outcome_evaluation_created": False}))
    add(lambda r: r["action_lines"][0]["outcome_evaluation"].update({"evaluation_result": "failed"}))
    add(lambda r: r["action_lines"][0]["outcome_evaluation"].update({"observed_result": "wrong"}))
    add(lambda r: r["action_lines"][0]["outcome_evaluation"].update({"candy_contact": False}))
    add(lambda r: r["action_lines"][1]["outcome_evaluation"].update({"candy_contact": True}))
    add(lambda r: r["action_lines"][0]["outcome_evaluation"].update({"memory_write": True}))
    add(lambda r: r["completion_summary"].update({"selected_action_created_count": 5}))
    add(lambda r: r["completion_summary"].update({"direct_command_executed_count": 5}))
    add(lambda r: r["completion_summary"].update({"candy_contact_action_line_count": 0}))
    add(lambda r: r["completion_summary"].update({"next_action_authorized_after_budget": True}))
    add(lambda r: r["human_summary"].update({"plain_result": ""}))
    add(lambda r: r["blocked_flags"].update({"background_autonomy_started": True}))
    add(lambda r: r["blocked_flags"].update({"proof_of_learning_claim_allowed": True}))
    return invalids


def _dict(value: Any, errors: list[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(code)
        return {}
    return value


def _nested(line: dict[str, Any], field: str, errors: list[str], index: int) -> dict[str, Any]:
    value = line.get(field)
    if not isinstance(value, dict):
        errors.append(f"action_line_{index}_{field}_missing")
        return {}
    return value

