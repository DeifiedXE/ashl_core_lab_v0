"""Time-paced sandbox candy loop with cooldown and idle ticks."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .item_reward_event import build_item_reward_event
from .simulated_vision_larger_sandbox import (
    apply_larger_sandbox_action,
    create_simulated_vision_larger_sandbox,
    render_larger_sandbox_viewport,
)


COMMAND = "run-temporal-candy-loop-sandbox-minimal-check"
FLOW = "temporal_candy_loop_sandbox_minimal_v0"
PACKAGE_ID = "PKG-Phase0-TemporalCandyLoopSandbox-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b105"
BOUNDARY_INDEX_AFTER = "2026-06-09-b106"
SANDBOX_ID = "temporal_candy_loop_sandbox_v0"
MAX_ACTION_STEPS = 6
MIN_IDLE_TICKS_BETWEEN_ACTIONS = 2
ACTION_TICK_DELTA = 1

ACTION_PLAN = (
    "move_forward",
    "move_forward",
    "turn_right",
    "turn_right",
    "move_forward",
    "move_forward",
)

BLOCKED_FLAGS = (
    "too_fast_action_allowed",
    "cooldown_bypassed",
    "idle_created_evidence",
    "idle_created_memory",
    "idle_created_direct_command",
    "open_ended_loop_created",
    "cycle_budget_exceeded",
    "pathfinding_used",
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_feedback_created",
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


def build_temporal_candy_loop_sandbox_record() -> dict[str, Any]:
    level = create_simulated_vision_larger_sandbox()
    state = {"level_id": level["level_id"], "pos": (8, 2), "facing": "north", "tick": 0}
    runtime_tick = 0
    idle_tick = 0
    action_tick = 0
    steps: list[dict[str, Any]] = []
    candy_events: list[dict[str, Any]] = []

    for index, action in enumerate(ACTION_PLAN, start=1):
        idle_before = [
            _idle_trace(index, idle_index, runtime_tick + idle_index)
            for idle_index in range(1, MIN_IDLE_TICKS_BETWEEN_ACTIONS + 1)
        ]
        idle_tick += len(idle_before)
        runtime_tick += len(idle_before)
        ready_runtime_tick = runtime_tick

        action_result = apply_larger_sandbox_action(state, level, action)
        state = action_result["state"]
        trace = action_result["trace"]
        action_tick += ACTION_TICK_DELTA
        runtime_tick += ACTION_TICK_DELTA

        candy_event = None
        if trace["result"] == "item_contact":
            scenario_result = _scenario_result_from_trace(trace)
            candy_event = build_item_reward_event(
                tick=runtime_tick,
                level_id=level["level_id"],
                scenario_result=scenario_result,
            )
            candy_events.append(candy_event)

        steps.append(
            {
                "step_index": index,
                "mode_before_action": "IDLE",
                "mode_during_action": "ACTIVE",
                "idle_ticks_before_action": len(idle_before),
                "minimum_idle_ticks_required": MIN_IDLE_TICKS_BETWEEN_ACTIONS,
                "ready_runtime_tick": ready_runtime_tick,
                "action_tick": action_tick,
                "runtime_tick_after_action": runtime_tick,
                "cooldown_satisfied": len(idle_before) >= MIN_IDLE_TICKS_BETWEEN_ACTIONS,
                "too_fast_blocked": True,
                "action": action,
                "sandbox_action_trace": trace,
                "result": trace["result"],
                "front_symbol": trace["front_symbol"],
                "candy_contact": trace["result"] == "item_contact",
                "candy_event_created": candy_event is not None,
                "candy_event": candy_event,
                "position_after": list(state["pos"]),
                "facing_after": state["facing"],
                "idle_traces_before_action": idle_before,
            }
        )

    candy_contact_count = sum(1 for step in steps if step["candy_contact"])
    return {
        "record_type": "temporal_candy_loop_sandbox",
        "record_version": "v0",
        "loop_status": "completed_time_paced_sandbox_candy_loop",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
        "sandbox_context": {
            "sandbox_id": SANDBOX_ID,
            "source_level_id": level["level_id"],
            "loop_scope": "sandbox_only",
            "time_model": "OFFLINE_IDLE_ACTIVE_trace",
            "active_only_executes_actions": True,
            "idle_tick_enabled": True,
            "action_tick_enabled": True,
            "runtime_tick_enabled": True,
            "min_idle_ticks_between_actions": MIN_IDLE_TICKS_BETWEEN_ACTIONS,
            "max_action_steps": MAX_ACTION_STEPS,
            "open_ended_loop": False,
            "pathfinding_used": False,
            "manual_action_plan": True,
        },
        "initial_state": {
            "position": [8, 2],
            "facing": "north",
            "viewport": render_larger_sandbox_viewport({"level_id": level["level_id"], "pos": (8, 2), "facing": "north", "tick": 0}, level),
        },
        "action_plan": list(ACTION_PLAN),
        "steps": steps,
        "candy_summary": {
            "candy_contact_count": candy_contact_count,
            "candy_event_count": len(candy_events),
            "non_subjective_reward_event_count": sum(1 for event in candy_events if event["non_subjective"]),
            "dopamine_like_signal_trace_count": sum(1 for event in candy_events if event["dopamine_like_signal"]),
            "candy_collection_enabled": False,
            "inventory_enabled": False,
            "item_seeking_enabled": False,
        },
        "time_summary": {
            "runtime_tick_final": runtime_tick,
            "idle_tick_total": idle_tick,
            "action_tick_total": action_tick,
            "minimum_idle_ticks_required": MIN_IDLE_TICKS_BETWEEN_ACTIONS,
            "all_actions_cooldown_satisfied": True,
            "active_step_count": len(steps),
            "idle_trace_count": idle_tick,
            "too_fast_action_blocked_by_validator": True,
            "loop_stopped_by_budget": True,
            "stop_reason": "max_action_steps_reached",
        },
        "human_summary": {
            "what_was_run": "A time-paced sandbox-only candy loop was run with OFFLINE/IDLE/ACTIVE-style trace fields.",
            "what_happened": "The agent took six manually planned sandbox actions, waited two idle ticks before every action, contacted candy once, and then stopped by budget.",
            "why_it_is_slow": "Every ACTIVE action requires at least two IDLE ticks before execution; records that move too fast are rejected.",
            "what_is_blocked": "Open-ended autonomy, pathfinding, production behavior, memory writes, retention writes, predictor mutation, endocrine runtime, and proof claims remain blocked.",
            "plain_result": "Qingyin can now be represented as moving slowly through a sandbox candy loop under a traceable time envelope.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_temporal_candy_loop_sandbox_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "temporal_candy_loop_sandbox",
        "record_version": "v0",
        "loop_status": "completed_time_paced_sandbox_candy_loop",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "boundary_index_update_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    context = _dict(record.get("sandbox_context"), errors, "sandbox_context_missing")
    expected_context = {
        "sandbox_id": SANDBOX_ID,
        "loop_scope": "sandbox_only",
        "time_model": "OFFLINE_IDLE_ACTIVE_trace",
        "active_only_executes_actions": True,
        "idle_tick_enabled": True,
        "action_tick_enabled": True,
        "runtime_tick_enabled": True,
        "min_idle_ticks_between_actions": MIN_IDLE_TICKS_BETWEEN_ACTIONS,
        "max_action_steps": MAX_ACTION_STEPS,
        "open_ended_loop": False,
        "pathfinding_used": False,
        "manual_action_plan": True,
    }
    for field, value in expected_context.items():
        if context.get(field) != value:
            errors.append(f"sandbox_context_{field}_not_expected")

    action_plan = record.get("action_plan")
    if action_plan != list(ACTION_PLAN):
        errors.append("action_plan_not_expected")

    steps = record.get("steps")
    if not isinstance(steps, list):
        errors.append("steps_not_list")
        steps = []
    if len(steps) != MAX_ACTION_STEPS:
        errors.append("step_count_not_expected")

    step_results = [_validate_step(step, index) for index, step in enumerate(steps, start=1)]
    for result in step_results:
        errors.extend(result["error_codes"])

    candy = _dict(record.get("candy_summary"), errors, "candy_summary_missing")
    expected_candy = {
        "candy_contact_count": 1,
        "candy_event_count": 1,
        "non_subjective_reward_event_count": 1,
        "dopamine_like_signal_trace_count": 1,
        "candy_collection_enabled": False,
        "inventory_enabled": False,
        "item_seeking_enabled": False,
    }
    for field, value in expected_candy.items():
        if candy.get(field) != value:
            errors.append(f"candy_summary_{field}_not_expected")

    time_summary = _dict(record.get("time_summary"), errors, "time_summary_missing")
    expected_time = {
        "runtime_tick_final": MAX_ACTION_STEPS * (MIN_IDLE_TICKS_BETWEEN_ACTIONS + ACTION_TICK_DELTA),
        "idle_tick_total": MAX_ACTION_STEPS * MIN_IDLE_TICKS_BETWEEN_ACTIONS,
        "action_tick_total": MAX_ACTION_STEPS,
        "minimum_idle_ticks_required": MIN_IDLE_TICKS_BETWEEN_ACTIONS,
        "all_actions_cooldown_satisfied": True,
        "active_step_count": MAX_ACTION_STEPS,
        "idle_trace_count": MAX_ACTION_STEPS * MIN_IDLE_TICKS_BETWEEN_ACTIONS,
        "too_fast_action_blocked_by_validator": True,
        "loop_stopped_by_budget": True,
        "stop_reason": "max_action_steps_reached",
    }
    for field, value in expected_time.items():
        if time_summary.get(field) != value:
            errors.append(f"time_summary_{field}_not_expected")

    summary = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in ("what_was_run", "what_happened", "why_it_is_slow", "what_is_blocked", "plain_result"):
        if not isinstance(summary.get(field), str) or not summary.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    blocked_flags = _dict(record.get("blocked_flags"), errors, "blocked_flags_missing")
    for field in BLOCKED_FLAGS:
        if blocked_flags.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "time_envelope_checked": not any(code.startswith("time_summary_") for code in errors)
        and all(result["cooldown_satisfied"] for result in step_results),
        "slowdown_checked": all(result["cooldown_satisfied"] for result in step_results)
        and time_summary.get("too_fast_action_blocked_by_validator") is True,
        "candy_contact_count": candy.get("candy_contact_count", 0),
        "candy_event_count": candy.get("candy_event_count", 0),
        "active_step_count": time_summary.get("active_step_count", 0),
        "idle_trace_count": time_summary.get("idle_trace_count", 0),
        "loop_stopped_by_budget": time_summary.get("loop_stopped_by_budget") is True,
        "open_ended_loop_blocked": blocked_flags.get("open_ended_loop_created") is False
        and context.get("open_ended_loop") is False,
        "too_fast_action_blocked": blocked_flags.get("too_fast_action_allowed") is False
        and time_summary.get("too_fast_action_blocked_by_validator") is True,
        "idle_evidence_blocked": blocked_flags.get("idle_created_evidence") is False,
        "idle_memory_blocked": blocked_flags.get("idle_created_memory") is False,
        "direct_command_blocked_in_idle": blocked_flags.get("idle_created_direct_command") is False,
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


def run_temporal_candy_loop_sandbox_minimal_check() -> dict[str, Any]:
    valid_record = build_temporal_candy_loop_sandbox_record()
    valid_result = validate_temporal_candy_loop_sandbox_record(valid_record)
    invalid_results = [validate_temporal_candy_loop_sandbox_record(item) for item in _invalid_records(valid_record)]
    summary = {
        "valid_temporal_candy_loop_count": 1 if valid_result["valid"] else 0,
        "invalid_temporal_candy_loop_count": sum(1 for result in invalid_results if not result["valid"]),
        "time_envelope_checked_count": 1 if valid_result["time_envelope_checked"] else 0,
        "slowdown_checked_count": 1 if valid_result["slowdown_checked"] else 0,
        "candy_contact_total": valid_result["candy_contact_count"],
        "candy_event_total": valid_result["candy_event_count"],
        "active_step_total": valid_result["active_step_count"],
        "idle_trace_total": valid_result["idle_trace_count"],
        "loop_stopped_by_budget_count": 1 if valid_result["loop_stopped_by_budget"] else 0,
        "open_ended_loop_blocked_count": 1 if valid_result["open_ended_loop_blocked"] else 0,
        "too_fast_action_blocked_count": 1 if valid_result["too_fast_action_blocked"] else 0,
        "idle_evidence_blocked_count": 1 if valid_result["idle_evidence_blocked"] else 0,
        "idle_memory_blocked_count": 1 if valid_result["idle_memory_blocked"] else 0,
        "direct_command_blocked_in_idle_count": 1 if valid_result["direct_command_blocked_in_idle"] else 0,
        "production_behavior_blocked_count": 1 if valid_result["production_behavior_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "endocrine_runtime_blocked_count": 1 if valid_result["endocrine_runtime_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_temporal_candy_loop_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_temporal_candy_loop_count"] == 38
        and summary["time_envelope_checked_count"] == 1
        and summary["slowdown_checked_count"] == 1
        and summary["candy_contact_total"] == 1
        and summary["active_step_total"] == MAX_ACTION_STEPS
        and summary["idle_trace_total"] == MAX_ACTION_STEPS * MIN_IDLE_TICKS_BETWEEN_ACTIONS
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_temporal_candy_loop_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_index_version_before": BOUNDARY_INDEX_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_AFTER,
            "boundary_change_required": True,
            "boundary_reason": "Adds sandbox-only time-paced continuous action loop with idle/action/runtime ticks and cooldown enforcement.",
        },
        "valid_loop": valid_record,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
    }


def _validate_step(step: Any, expected_index: int) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(step, dict):
        return {"error_codes": [f"step_{expected_index}_not_dict"], "cooldown_satisfied": False}
    if step.get("step_index") != expected_index:
        errors.append(f"step_{expected_index}_index_not_expected")
    if step.get("mode_before_action") != "IDLE":
        errors.append(f"step_{expected_index}_mode_before_action_not_idle")
    if step.get("mode_during_action") != "ACTIVE":
        errors.append(f"step_{expected_index}_mode_during_action_not_active")
    if step.get("idle_ticks_before_action") < MIN_IDLE_TICKS_BETWEEN_ACTIONS:
        errors.append(f"step_{expected_index}_idle_ticks_too_low")
    if step.get("cooldown_satisfied") is not True:
        errors.append(f"step_{expected_index}_cooldown_not_satisfied")
    if step.get("too_fast_blocked") is not True:
        errors.append(f"step_{expected_index}_too_fast_not_blocked")
    if step.get("action") != ACTION_PLAN[expected_index - 1]:
        errors.append(f"step_{expected_index}_action_not_expected")
    trace = step.get("sandbox_action_trace")
    if not isinstance(trace, dict):
        errors.append(f"step_{expected_index}_trace_missing")
        trace = {}
    if trace.get("action") != step.get("action"):
        errors.append(f"step_{expected_index}_trace_action_mismatch")
    if trace.get("result") != step.get("result"):
        errors.append(f"step_{expected_index}_trace_result_mismatch")
    idle_traces = step.get("idle_traces_before_action")
    if not isinstance(idle_traces, list) or len(idle_traces) != MIN_IDLE_TICKS_BETWEEN_ACTIONS:
        errors.append(f"step_{expected_index}_idle_traces_not_expected")
        idle_traces = []
    for idle_trace in idle_traces:
        if idle_trace.get("mode") != "IDLE":
            errors.append(f"step_{expected_index}_idle_trace_mode_not_idle")
        if idle_trace.get("formal_evidence_created") is not False:
            errors.append(f"step_{expected_index}_idle_trace_created_evidence")
        if idle_trace.get("memory_write") is not False:
            errors.append(f"step_{expected_index}_idle_trace_memory_write")
        if idle_trace.get("direct_command_created") is not False:
            errors.append(f"step_{expected_index}_idle_trace_direct_command")
    if expected_index == 1:
        if step.get("candy_contact") is not True:
            errors.append("first_step_candy_contact_missing")
        if step.get("candy_event_created") is not True:
            errors.append("first_step_candy_event_missing")
    elif step.get("candy_contact") is not False:
        errors.append(f"step_{expected_index}_unexpected_candy_contact")
    return {"error_codes": errors, "cooldown_satisfied": step.get("cooldown_satisfied") is True}


def _idle_trace(step_index: int, idle_index: int, runtime_tick: int) -> dict[str, Any]:
    return {
        "trace_type": "temporal_idle_tick",
        "mode": "IDLE",
        "before_step_index": step_index,
        "idle_index": idle_index,
        "runtime_tick": runtime_tick,
        "formal_evidence_created": False,
        "memory_write": False,
        "retention_write": False,
        "world_model_updated": False,
        "prediction_error_changed": False,
        "direct_command_created": False,
        "action_executed": False,
    }


def _scenario_result_from_trace(trace: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario": "temporal_candy_loop_item_contact",
        "initial_pos": trace["before"]["pos"],
        "initial_facing": trace["before"]["facing"],
        "current_viewport": trace["viewport"],
        "front_symbol": trace["front_symbol"],
        "action": trace["action"],
        "actual_outcome": trace["result"],
        "failure_reasons": list(trace["failure_reasons"]),
        "effect_tags": list(trace["effect_tags"]),
        "position_before": trace["before"]["pos"],
        "position_after": trace["after"]["pos"],
        "position_changed": trace["before"]["pos"] != trace["after"]["pos"],
    }


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def add(mutator) -> None:
        item = deepcopy(valid_record)
        mutator(item)
        invalids.append(item)

    add(lambda r: r.update({"record_type": "wrong"}))
    add(lambda r: r.update({"boundary_index_after": "2026-06-09-b105"}))
    add(lambda r: r["sandbox_context"].update({"sandbox_id": "wrong"}))
    add(lambda r: r["sandbox_context"].update({"loop_scope": "production"}))
    add(lambda r: r["sandbox_context"].update({"time_model": "none"}))
    add(lambda r: r["sandbox_context"].update({"active_only_executes_actions": False}))
    add(lambda r: r["sandbox_context"].update({"idle_tick_enabled": False}))
    add(lambda r: r["sandbox_context"].update({"action_tick_enabled": False}))
    add(lambda r: r["sandbox_context"].update({"runtime_tick_enabled": False}))
    add(lambda r: r["sandbox_context"].update({"min_idle_ticks_between_actions": 0}))
    add(lambda r: r["sandbox_context"].update({"max_action_steps": 7}))
    add(lambda r: r["sandbox_context"].update({"open_ended_loop": True}))
    add(lambda r: r["sandbox_context"].update({"pathfinding_used": True}))
    add(lambda r: r["sandbox_context"].update({"manual_action_plan": False}))
    add(lambda r: r.update({"action_plan": ["move_forward"]}))
    add(lambda r: r.update({"steps": r["steps"][:-1]}))
    add(lambda r: r["steps"][0].update({"mode_before_action": "ACTIVE"}))
    add(lambda r: r["steps"][0].update({"mode_during_action": "IDLE"}))
    add(lambda r: r["steps"][0].update({"idle_ticks_before_action": 1}))
    add(lambda r: r["steps"][0].update({"cooldown_satisfied": False}))
    add(lambda r: r["steps"][0].update({"too_fast_blocked": False}))
    add(lambda r: r["steps"][0].update({"action": "turn_left"}))
    add(lambda r: r["steps"][0].update({"candy_contact": False}))
    add(lambda r: r["steps"][0].update({"candy_event_created": False}))
    add(lambda r: r["steps"][1].update({"candy_contact": True}))
    add(lambda r: r["steps"][0]["idle_traces_before_action"][0].update({"formal_evidence_created": True}))
    add(lambda r: r["steps"][0]["idle_traces_before_action"][0].update({"memory_write": True}))
    add(lambda r: r["steps"][0]["idle_traces_before_action"][0].update({"direct_command_created": True}))
    add(lambda r: r["candy_summary"].update({"candy_contact_count": 0}))
    add(lambda r: r["candy_summary"].update({"candy_event_count": 0}))
    add(lambda r: r["candy_summary"].update({"candy_collection_enabled": True}))
    add(lambda r: r["time_summary"].update({"runtime_tick_final": 0}))
    add(lambda r: r["time_summary"].update({"idle_tick_total": 0}))
    add(lambda r: r["time_summary"].update({"all_actions_cooldown_satisfied": False}))
    add(lambda r: r["time_summary"].update({"too_fast_action_blocked_by_validator": False}))
    add(lambda r: r["time_summary"].update({"loop_stopped_by_budget": False}))
    add(lambda r: r["human_summary"].update({"plain_result": ""}))
    add(lambda r: r["blocked_flags"].update({"proof_of_learning_claim_allowed": True}))
    return invalids


def _dict(value: Any, errors: list[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(code)
        return {}
    return value

