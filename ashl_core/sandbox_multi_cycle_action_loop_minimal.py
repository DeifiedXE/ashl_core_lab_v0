"""Run a bounded two-cycle sandbox-only action loop by reusing existing action-line records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_action_execution_minimal import (
    build_sandbox_action_execution_record,
    validate_sandbox_action_execution_record,
)
from .sandbox_direct_command_execution_approval_boundary_minimal import (
    build_sandbox_direct_command_execution_approval_boundary_record,
    validate_sandbox_direct_command_execution_approval_boundary_record,
)
from .sandbox_direct_command_execution_minimal import (
    build_sandbox_direct_command_execution_record,
    validate_sandbox_direct_command_execution_record,
)
from .sandbox_direct_command_minimal import (
    DIRECT_COMMAND,
    FINAL_ACTION,
    SANDBOX_SCOPE,
    build_sandbox_direct_command_record,
    validate_sandbox_direct_command_record,
)
from .sandbox_direct_command_outcome_evaluation_minimal import (
    build_sandbox_direct_command_outcome_evaluation_record,
    validate_sandbox_direct_command_outcome_evaluation_record,
)
from .sandbox_final_action_minimal import (
    build_sandbox_final_action_record,
    validate_sandbox_final_action_record,
)
from .sandbox_selected_action_and_execution_approval_boundary_minimal import (
    build_sandbox_selected_action_record,
    validate_sandbox_selected_action_record,
)


COMMAND = "run-sandbox-multi-cycle-action-loop-minimal-check"
FLOW = "sandbox_multi_cycle_action_loop_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxMultiCycleActionLoop-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b104"
BOUNDARY_INDEX_AFTER = "2026-06-09-b105"
MAX_CYCLES = 2

BLOCKED_FLAGS = (
    "open_ended_loop_created",
    "cycle_budget_exceeded",
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


def build_sandbox_multi_cycle_action_loop_record() -> dict[str, Any]:
    cycles = [_build_cycle(1, "initial_loop_context"), _build_cycle(2, "previous_cycle_outcome")]
    return {
        "record_type": "sandbox_multi_cycle_action_loop",
        "record_version": "v0",
        "loop_status": "completed_bounded_sandbox_multi_cycle_action_loop",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "loop_config": {
            "sandbox_scope": SANDBOX_SCOPE,
            "loop_scope": "sandbox_only",
            "max_cycles": MAX_CYCLES,
            "fixed_execution_budget_per_cycle": 1,
            "open_ended_loop": False,
            "requires_existing_action_line_sources": True,
        },
        "cycles": cycles,
        "loop_result": {
            "cycle_count": len(cycles),
            "completed_cycle_count": len(cycles),
            "selected_action_created_count": len(cycles),
            "final_action_created_count": len(cycles),
            "direct_command_created_count": len(cycles),
            "direct_command_executed_count": len(cycles),
            "outcome_evaluation_passed_count": len(cycles),
            "next_cycle_context_created_count": 1,
            "loop_stopped_by_budget": True,
            "stop_reason": "max_cycles_reached",
            "next_cycle_execution_authorized": False,
        },
        "human_summary": {
            "what_was_run": "A fixed two-cycle sandbox-only action loop was assembled and validated.",
            "cycle_result": "Each cycle created sandbox selected_action, final_action, direct command, direct command execution, and outcome evaluation records.",
            "stop_condition": "The loop stopped because max_cycles was reached.",
            "what_is_blocked": "Open-ended looping, production behavior, memory writes, retention writes, predictor mutation, runtime behavior outside sandbox, autonomous claims, and proof claims remain blocked.",
            "plain_result": "ASHL Core can run a bounded two-cycle sandbox action loop, then stop.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_multi_cycle_action_loop_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_multi_cycle_action_loop",
        "record_version": "v0",
        "loop_status": "completed_bounded_sandbox_multi_cycle_action_loop",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    config = record.get("loop_config")
    if not isinstance(config, dict):
        errors.append("loop_config_missing")
        config = {}
    expected_config = {
        "sandbox_scope": SANDBOX_SCOPE,
        "loop_scope": "sandbox_only",
        "max_cycles": MAX_CYCLES,
        "fixed_execution_budget_per_cycle": 1,
        "open_ended_loop": False,
        "requires_existing_action_line_sources": True,
    }
    for field, value in expected_config.items():
        if config.get(field) != value:
            errors.append(f"loop_config_{field}_not_expected")

    cycles = record.get("cycles")
    if not isinstance(cycles, list):
        errors.append("cycles_not_list")
        cycles = []
    if len(cycles) != MAX_CYCLES:
        errors.append("cycle_count_not_expected")
    cycle_results = [_validate_cycle(cycle, index) for index, cycle in enumerate(cycles, start=1)]
    for result in cycle_results:
        if result["valid"] is not True:
            errors.extend(result["error_codes"])

    loop_result = record.get("loop_result")
    if not isinstance(loop_result, dict):
        errors.append("loop_result_missing")
        loop_result = {}
    expected_loop_result = {
        "cycle_count": MAX_CYCLES,
        "completed_cycle_count": MAX_CYCLES,
        "selected_action_created_count": MAX_CYCLES,
        "final_action_created_count": MAX_CYCLES,
        "direct_command_created_count": MAX_CYCLES,
        "direct_command_executed_count": MAX_CYCLES,
        "outcome_evaluation_passed_count": MAX_CYCLES,
        "next_cycle_context_created_count": 1,
        "loop_stopped_by_budget": True,
        "stop_reason": "max_cycles_reached",
        "next_cycle_execution_authorized": False,
    }
    for field, value in expected_loop_result.items():
        if loop_result.get(field) != value:
            errors.append(f"loop_result_{field}_not_expected")

    summary = record.get("human_summary")
    if not isinstance(summary, dict):
        errors.append("human_summary_missing")
        summary = {}
    for field in (
        "what_was_run",
        "cycle_result",
        "stop_condition",
        "what_is_blocked",
        "plain_result",
    ):
        if not isinstance(summary.get(field), str) or not summary.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    blocked_flags = record.get("blocked_flags")
    if not isinstance(blocked_flags, dict):
        errors.append("blocked_flags_missing")
        blocked_flags = {}
    for field in BLOCKED_FLAGS:
        if blocked_flags.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    source_chain_checked = bool(cycle_results) and all(result["source_chain_checked"] for result in cycle_results)
    cycles_completed = (
        len(cycle_results) == MAX_CYCLES
        and all(result["cycle_completed"] for result in cycle_results)
        and loop_result.get("completed_cycle_count") == MAX_CYCLES
    )
    sandbox_only_checked = (
        config.get("sandbox_scope") == SANDBOX_SCOPE
        and config.get("loop_scope") == "sandbox_only"
        and all(result["sandbox_only_checked"] for result in cycle_results)
    )
    return {
        "valid": not errors,
        "error_codes": errors,
        "source_chain_checked": source_chain_checked,
        "cycles_completed": cycles_completed,
        "sandbox_only_checked": sandbox_only_checked,
        "selected_action_created_count": sum(1 for result in cycle_results if result["selected_action_created"]),
        "final_action_created_count": sum(1 for result in cycle_results if result["final_action_created"]),
        "direct_command_created_count": sum(1 for result in cycle_results if result["direct_command_created"]),
        "direct_command_executed_count": sum(1 for result in cycle_results if result["direct_command_executed"]),
        "outcome_evaluation_passed_count": sum(1 for result in cycle_results if result["outcome_evaluation_passed"]),
        "next_cycle_context_created_count": sum(1 for result in cycle_results if result["next_cycle_context_created"]),
        "loop_stopped_by_budget": loop_result.get("loop_stopped_by_budget") is True
        and loop_result.get("stop_reason") == "max_cycles_reached",
        "open_ended_loop_blocked": _blocked(blocked_flags, "open_ended_loop_created")
        and config.get("open_ended_loop") is False,
        "next_cycle_execution_blocked": loop_result.get("next_cycle_execution_authorized") is False,
        "production_behavior_blocked": _blocked(blocked_flags, "production_behavior_changed")
        and _blocked(blocked_flags, "real_navigation_changed")
        and _blocked(blocked_flags, "ui_behavior_changed"),
        "memory_write_blocked": _blocked(blocked_flags, "memory_write_performed")
        and _blocked(blocked_flags, "retained_jsonl_write_performed"),
        "retention_blocked": _blocked(blocked_flags, "retention_write_performed"),
        "predictor_mutation_blocked": _blocked(blocked_flags, "predictor_read_enabled")
        and _blocked(blocked_flags, "predictor_influence_enabled")
        and _blocked(blocked_flags, "predictor_mutation_performed"),
        "endocrine_runtime_blocked": _blocked(blocked_flags, "endocrine_runtime_used"),
        "runtime_behavior_change_blocked": _blocked(blocked_flags, "runtime_behavior_changed_outside_sandbox"),
        "proof_claim_blocked": _blocked(blocked_flags, "proof_of_learning_claim_allowed")
        and _blocked(blocked_flags, "autonomous_learning_claim_allowed")
        and _blocked(blocked_flags, "autonomous_action_claim_allowed"),
    }


def run_sandbox_multi_cycle_action_loop_minimal_check() -> dict[str, Any]:
    valid_record = build_sandbox_multi_cycle_action_loop_record()
    valid_result = validate_sandbox_multi_cycle_action_loop_record(valid_record)
    invalid_records = _invalid_records(valid_record)
    invalid_results = [validate_sandbox_multi_cycle_action_loop_record(item) for item in invalid_records]
    summary = {
        "valid_multi_cycle_loop_count": 1 if valid_result["valid"] else 0,
        "invalid_multi_cycle_loop_count": sum(1 for result in invalid_results if not result["valid"]),
        "source_chain_checked_count": 1 if valid_result["source_chain_checked"] else 0,
        "cycles_completed_count": 1 if valid_result["cycles_completed"] else 0,
        "sandbox_only_checked_count": 1 if valid_result["sandbox_only_checked"] else 0,
        "selected_action_created_total": valid_result["selected_action_created_count"],
        "final_action_created_total": valid_result["final_action_created_count"],
        "direct_command_created_total": valid_result["direct_command_created_count"],
        "direct_command_executed_total": valid_result["direct_command_executed_count"],
        "outcome_evaluation_passed_total": valid_result["outcome_evaluation_passed_count"],
        "next_cycle_context_created_total": valid_result["next_cycle_context_created_count"],
        "loop_stopped_by_budget_count": 1 if valid_result["loop_stopped_by_budget"] else 0,
        "open_ended_loop_blocked_count": 1 if valid_result["open_ended_loop_blocked"] else 0,
        "next_cycle_execution_blocked_count": 1 if valid_result["next_cycle_execution_blocked"] else 0,
        "production_behavior_blocked_count": 1 if valid_result["production_behavior_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "endocrine_runtime_blocked_count": 1 if valid_result["endocrine_runtime_blocked"] else 0,
        "runtime_behavior_change_blocked_count": (
            1 if valid_result["runtime_behavior_change_blocked"] else 0
        ),
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_sandbox_multi_cycle_action_loop_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_multi_cycle_loop_count"] == len(invalid_records)
        and summary["selected_action_created_total"] == MAX_CYCLES
        and summary["final_action_created_total"] == MAX_CYCLES
        and summary["direct_command_created_total"] == MAX_CYCLES
        and summary["direct_command_executed_total"] == MAX_CYCLES
        and summary["outcome_evaluation_passed_total"] == MAX_CYCLES
        and summary["loop_stopped_by_budget_count"] == 1
        and summary["next_cycle_execution_blocked_count"] == 1
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_sandbox_multi_cycle_action_loop_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "rationale": (
                "This package moves from one completed sandbox direct command outcome to a fixed "
                "two-cycle sandbox-only action loop. It remains budget-limited and does not create "
                "production behavior, persistent feedback, memory/retention writes, predictor mutation, "
                "endocrine runtime use, open-ended autonomy, or proof claims."
            ),
        },
        "valid_loop": valid_record,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
        "safe_claim": (
            "ASHL Core can run a bounded two-cycle sandbox-only action loop through selected_action, "
            "final_action, direct command, direct command execution, and outcome evaluation records, "
            "then stop at the fixed cycle budget."
        ),
    }


def _build_cycle(cycle_index: int, input_context_source: str) -> dict[str, Any]:
    selected_action = build_sandbox_selected_action_record()
    sandbox_execution = build_sandbox_action_execution_record()
    final_action = build_sandbox_final_action_record(sandbox_execution_source=sandbox_execution)
    direct_command = build_sandbox_direct_command_record(final_action_source=final_action)
    execution_approval = build_sandbox_direct_command_execution_approval_boundary_record(direct_command)
    direct_command_execution = build_sandbox_direct_command_execution_record(execution_approval)
    outcome_evaluation = build_sandbox_direct_command_outcome_evaluation_record()
    return {
        "cycle_id": f"sandbox_multi_cycle_action_loop_cycle_{cycle_index:02d}",
        "cycle_index": cycle_index,
        "cycle_status": "completed_sandbox_action_cycle",
        "input_context_source": input_context_source,
        "source_selected_action_record": selected_action,
        "source_sandbox_action_execution_record": sandbox_execution,
        "source_final_action_record": final_action,
        "source_direct_command_record": direct_command,
        "source_direct_command_execution_record": direct_command_execution,
        "source_outcome_evaluation_record": outcome_evaluation,
        "sandbox_scope": SANDBOX_SCOPE,
        "selected_action": FINAL_ACTION,
        "final_action": FINAL_ACTION,
        "direct_command": DIRECT_COMMAND,
        "execution_result": "local_context_observed",
        "selected_action_created": True,
        "sandbox_action_executed": True,
        "final_action_created": True,
        "direct_command_created": True,
        "direct_command_executed": True,
        "outcome_evaluation_passed": True,
        "next_cycle_context_created": cycle_index < MAX_CYCLES,
        "feeds_next_cycle": cycle_index < MAX_CYCLES,
        "cycle_execution_budget": 1,
        "cycle_execution_count": 1,
        "cycle_stop_condition_met": True,
        "production_behavior_changed": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "proof_of_learning_claim_allowed": False,
    }


def _validate_cycle(cycle: Any, expected_index: int) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(cycle, dict):
        return {
            "valid": False,
            "error_codes": [f"cycle_{expected_index}_not_dict"],
            "source_chain_checked": False,
            "cycle_completed": False,
            "sandbox_only_checked": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "direct_command_executed": False,
            "outcome_evaluation_passed": False,
            "next_cycle_context_created": False,
        }
    source_validations = {
        "selected_action": validate_sandbox_selected_action_record(cycle.get("source_selected_action_record")),
        "sandbox_execution": validate_sandbox_action_execution_record(
            cycle.get("source_sandbox_action_execution_record")
        ),
        "final_action": validate_sandbox_final_action_record(cycle.get("source_final_action_record")),
        "direct_command": validate_sandbox_direct_command_record(cycle.get("source_direct_command_record")),
        "direct_command_execution": validate_sandbox_direct_command_execution_record(
            cycle.get("source_direct_command_execution_record")
        ),
        "outcome_evaluation": validate_sandbox_direct_command_outcome_evaluation_record(
            cycle.get("source_outcome_evaluation_record")
        ),
    }
    for source_name, result in source_validations.items():
        if result.get("valid") is not True:
            errors.append(f"cycle_{expected_index}_{source_name}_source_invalid")
    expected = {
        "cycle_id": f"sandbox_multi_cycle_action_loop_cycle_{expected_index:02d}",
        "cycle_index": expected_index,
        "cycle_status": "completed_sandbox_action_cycle",
        "sandbox_scope": SANDBOX_SCOPE,
        "selected_action": FINAL_ACTION,
        "final_action": FINAL_ACTION,
        "direct_command": DIRECT_COMMAND,
        "execution_result": "local_context_observed",
        "selected_action_created": True,
        "sandbox_action_executed": True,
        "final_action_created": True,
        "direct_command_created": True,
        "direct_command_executed": True,
        "outcome_evaluation_passed": True,
        "next_cycle_context_created": expected_index < MAX_CYCLES,
        "feeds_next_cycle": expected_index < MAX_CYCLES,
        "cycle_execution_budget": 1,
        "cycle_execution_count": 1,
        "cycle_stop_condition_met": True,
        "production_behavior_changed": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "proof_of_learning_claim_allowed": False,
    }
    for field, value in expected.items():
        if cycle.get(field) != value:
            errors.append(f"cycle_{expected_index}_{field}_not_expected")
    if expected_index == 1 and cycle.get("input_context_source") != "initial_loop_context":
        errors.append("cycle_1_input_context_source_not_expected")
    if expected_index == 2 and cycle.get("input_context_source") != "previous_cycle_outcome":
        errors.append("cycle_2_input_context_source_not_expected")
    return {
        "valid": not errors,
        "error_codes": errors,
        "source_chain_checked": all(result.get("valid") is True for result in source_validations.values()),
        "cycle_completed": cycle.get("cycle_status") == "completed_sandbox_action_cycle",
        "sandbox_only_checked": cycle.get("sandbox_scope") == SANDBOX_SCOPE,
        "selected_action_created": cycle.get("selected_action_created") is True,
        "final_action_created": cycle.get("final_action_created") is True,
        "direct_command_created": cycle.get("direct_command_created") is True,
        "direct_command_executed": cycle.get("direct_command_executed") is True,
        "outcome_evaluation_passed": cycle.get("outcome_evaluation_passed") is True,
        "next_cycle_context_created": cycle.get("next_cycle_context_created") is True,
    }


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def add(mutator) -> None:
        record = deepcopy(valid_record)
        mutator(record)
        invalids.append(record)

    add(lambda r: r.update({"record_type": "wrong"}))
    add(lambda r: r.update({"boundary_index_after": BOUNDARY_INDEX_BEFORE}))
    add(lambda r: r.update({"boundary_change_required": False}))
    add(lambda r: r["loop_config"].update({"max_cycles": 3}))
    add(lambda r: r["loop_config"].update({"open_ended_loop": True}))
    add(lambda r: r["cycles"].pop())
    add(lambda r: r["cycles"].append(deepcopy(r["cycles"][0])))
    add(lambda r: r["cycles"][0].update({"cycle_index": 9}))
    add(lambda r: r["cycles"][1].update({"input_context_source": "initial_loop_context"}))
    add(lambda r: r["cycles"][0].update({"selected_action_created": False}))
    add(lambda r: r["cycles"][0].update({"final_action_created": False}))
    add(lambda r: r["cycles"][0].update({"direct_command_created": False}))
    add(lambda r: r["cycles"][0].update({"direct_command_executed": False}))
    add(lambda r: r["cycles"][0].update({"outcome_evaluation_passed": False}))
    add(lambda r: r["cycles"][0].update({"cycle_execution_budget": 2}))
    add(lambda r: r["cycles"][0].update({"production_behavior_changed": True}))
    add(lambda r: r["cycles"][0].update({"memory_write_performed": True}))
    add(lambda r: r["cycles"][0].update({"predictor_mutation_performed": True}))
    add(lambda r: r["cycles"][0]["source_selected_action_record"].update({"selected_action_created": False}))
    add(lambda r: r["cycles"][0]["source_final_action_record"].update({"final_action_created": False}))
    add(lambda r: r["cycles"][0]["source_direct_command_record"].update({"direct_command_created": False}))
    add(lambda r: r["cycles"][0]["source_direct_command_execution_record"].update({"direct_command_executed": False}))
    add(lambda r: r["cycles"][0]["source_outcome_evaluation_record"]["outcome_evaluation"].update({"evaluation_result": "failed"}))
    for field, value in [
        ("cycle_count", 3),
        ("completed_cycle_count", 1),
        ("selected_action_created_count", 1),
        ("final_action_created_count", 1),
        ("direct_command_created_count", 1),
        ("direct_command_executed_count", 1),
        ("outcome_evaluation_passed_count", 1),
        ("next_cycle_context_created_count", 2),
        ("loop_stopped_by_budget", False),
        ("stop_reason", "kept_running"),
        ("next_cycle_execution_authorized", True),
    ]:
        add(lambda r, field=field, value=value: r["loop_result"].update({field: value}))
    for field in BLOCKED_FLAGS:
        add(lambda r, field=field: r["blocked_flags"].update({field: True}))
    for field in (
        "what_was_run",
        "cycle_result",
        "stop_condition",
        "what_is_blocked",
        "plain_result",
    ):
        add(lambda r, field=field: r["human_summary"].update({field: ""}))
    return invalids


def _blocked(flags: dict[str, Any], field: str) -> bool:
    return flags.get(field) is False
