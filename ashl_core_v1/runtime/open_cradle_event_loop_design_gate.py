"""Combined design gate for future ASHL Core v1 open-cradle event loops."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_REPORT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "reports"
    / "v1_open_cradle_event_loop_combined_design_gate_v0.md"
)

CURRENT_ALLOWED_CLAIM = (
    "ASHL Core v1 can define a combined open-cradle event-loop design gate "
    "describing future event-loop modes, environment tick inputs/outputs, caregiver "
    "intervention conditions, memory promotion review prerequisites, and runtime "
    "boundary gaps."
)

CURRENT_NOT_YET_CLAIM = (
    "This is not open cradle runtime.",
    "This is not automatic ticking.",
    "This is not free action selection.",
    "This is not long-term memory promotion.",
    "This is not autonomous growth.",
    "This is not Unity Home, voice, or external bridge operation.",
)

NEXT_RECOMMENDED_PACKAGES = {
    "Package 32": "ASHL Core v1 Open Cradle Tick Context Stub Minimal v0",
    "Package 33": "ASHL Core v1 Open Cradle Teacher-Gated Tick Dry Run Minimal v0",
    "Package 34": "ASHL Core v1 Open Cradle Runtime Stub Readiness Review Minimal v0",
}

RUNTIME_BOUNDARY_GAPS = (
    "no_automatic_environment_scheduler",
    "no_autonomous_tick_executor",
    "no_free_action_policy",
    "no_long_horizon_memory_promotion_implementation",
    "no_caregiver_quality_workflow_beyond_cli",
    "no_open_ended_environment_event_source",
    "no_Unity_Home_integration",
    "no_voice_or_expression_channel",
    "no_external_bridge_operation",
)


def build_event_loop_plan() -> dict[str, Any]:
    return {
        "plan_id": "open_cradle_event_loop_plan_v0",
        "loop_steps": [
            "load_session_state",
            "read_cradle_environment_state",
            "collect_pending_teacher_notes_followups_and_promotion_queue_candidates",
            "build_tick_context",
            "decide_tick_mode",
            "produce_tick_proposal",
            "require_teacher_gate_when_needed",
            "write_trace_summary",
            "stop_or_wait",
        ],
        "tick_modes": [
            _tick_mode(
                "observe_only",
                "refresh environment state without action",
                ("cradle_environment_state", "session_summary"),
                ("tick_context", "trace_summary"),
                False,
                "one_tick_only",
            ),
            _tick_mode(
                "teacher_wait",
                "hold the loop until a teacher note or review exists",
                ("daily_teacher_note", "pending_review_summary"),
                ("tick_context", "trace_summary"),
                True,
                "teacher_response_required",
            ),
            _tick_mode(
                "review_pending",
                "surface unresolved reviews before any future runtime step",
                ("first_output_followup", "memory_promotion_queue"),
                ("pending_review_summary", "trace_summary"),
                True,
                "review_queue_empty_or_deferred",
            ),
            _tick_mode(
                "manual_daily_case",
                "run only a fixed manual cradle case through existing daily-operation tools",
                ("session_summary", "fixed_cradle_case_id"),
                ("daily_run_ref", "trace_summary"),
                True,
                "manual_case_complete",
            ),
            _tick_mode(
                "environment_state_refresh",
                "rebuild cradle environment state from existing fixed-case evidence",
                ("last_cradle_environment_state", "last_trace_summary"),
                ("cradle_environment_state", "trace_summary"),
                False,
                "state_refresh_record_written",
            ),
            _tick_mode(
                "promotion_review_pending",
                "hold long-horizon memory candidates for teacher review",
                ("memory_promotion_queue", "daily_teacher_note"),
                ("pending_review_summary", "trace_summary"),
                True,
                "promotion_queue_reviewed_or_held",
            ),
            _tick_mode(
                "stop",
                "stop the future loop when safety or missing evidence requires it",
                ("runtime_boundary_review", "pending_review_summary"),
                ("trace_summary",),
                False,
                "stopped",
            ),
        ],
        "runtime_created": False,
        "automatic_tick_created": False,
    }


def build_environment_tick_plan() -> dict[str, Any]:
    return {
        "plan_id": "open_cradle_environment_tick_plan_v0",
        "read_sources": [
            "state_snapshot",
            "session_summary",
            "last_trace_summary",
            "last_cradle_environment_state",
            "daily_teacher_note",
            "first_output_followup",
            "memory_promotion_queue",
        ],
        "outputs": [
            "tick_context",
            "environment_observation_summary",
            "pending_review_summary",
            "trace_summary",
        ],
        "forbidden_outputs": [
            "new_runtime_action",
            "candidate_ordering",
            "memory_promotion",
            "first_output_generation",
            "external_environment_operation",
        ],
        "tick_reads_environment_state": True,
        "tick_executes_environment_action": False,
        "tick_promotes_memory": False,
        "tick_generates_first_output": False,
    }


def build_caregiver_intervention_plan() -> dict[str, Any]:
    conditions = {
        "first_output_needs_review": (
            "first output cannot become an approved public trace without teacher review",
            "review first-output candidate or defer it",
        ),
        "memory_promotion_candidate_present": (
            "long-horizon memory candidates require human review before any future promotion",
            "inspect promotion queue and write teacher note",
        ),
        "conflict_detected": (
            "conflicting evidence cannot be treated as a stable pattern",
            "mark conflict and collect clarifying observation",
        ),
        "unknown_feedback": (
            "unknown feedback needs more evidence before future influence",
            "request observation-only tick context",
        ),
        "teacher_rejected_or_deferred": (
            "teacher rejection or deferral must block runtime escalation",
            "hold or close the pending item",
        ),
        "environment_state_unknown": (
            "unknown environment state cannot support a future open runtime decision",
            "refresh environment state",
        ),
        "stress_mismatch_detected": (
            "continuity mismatch means the substrate cannot be trusted for runtime planning",
            "run state continuity stress and inspect mismatches",
        ),
        "backup_missing_after_daily_run": (
            "caregiver operation quality should not depend on unbacked state",
            "create backup or mark the day incomplete",
        ),
    }
    return {
        "plan_id": "open_cradle_caregiver_intervention_plan_v0",
        "conditions": [
            {
                "condition": condition,
                "why_teacher_needed": values[0],
                "suggested_console_action": values[1],
            }
            for condition, values in conditions.items()
        ],
        "teacher_gate_required_for_runtime_escalation": True,
    }


def build_memory_promotion_review_plan() -> dict[str, Any]:
    return {
        "plan_id": "open_cradle_memory_promotion_review_plan_v0",
        "review_statuses": [
            "queued",
            "held_for_more_evidence",
            "teacher_marked_interesting",
            "teacher_rejected",
            "conflict_detected",
        ],
        "review_principles": [
            "promotion_queue_candidate_is_not_memory",
            "teacher_marked_interesting_is_not_memory_write",
            "multiple_day_evidence_required_before_future_promotion",
            "conflict_stale_supersede_handling_required_before_future_memory_write",
        ],
        "long_term_memory_write_created": False,
        "runtime_influence_created": False,
    }


def build_runtime_boundary_review() -> dict[str, Any]:
    return {
        "review_id": "open_cradle_runtime_boundary_review_v0",
        "runtime_implementation_ready": False,
        "missing_runtime_prerequisites": list(RUNTIME_BOUNDARY_GAPS),
        "runtime_created": False,
        "automatic_tick_created": False,
        "scheduler_created": False,
        "free_action_policy_created": False,
        "long_term_memory_promotion_created": False,
        "autonomous_growth_created": False,
        "Unity_Home_integration_created": False,
        "voice_or_expression_channel_created": False,
        "external_bridge_operation_created": False,
    }


def build_open_cradle_event_loop_design_gate(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    del base_dir
    event_loop_plan = build_event_loop_plan()
    environment_tick_plan = build_environment_tick_plan()
    caregiver_intervention_plan = build_caregiver_intervention_plan()
    memory_promotion_review_plan = build_memory_promotion_review_plan()
    runtime_boundary_review = build_runtime_boundary_review()
    checks = {
        "event_loop_design_defined": bool(event_loop_plan["loop_steps"])
        and bool(event_loop_plan["tick_modes"]),
        "environment_tick_plan_defined": bool(environment_tick_plan["read_sources"])
        and bool(environment_tick_plan["outputs"]),
        "caregiver_intervention_plan_defined": bool(caregiver_intervention_plan["conditions"]),
        "memory_promotion_review_plan_defined": bool(
            memory_promotion_review_plan["review_statuses"]
        ),
        "runtime_boundary_review_defined": bool(
            runtime_boundary_review["missing_runtime_prerequisites"]
        ),
    }
    design_ready = all(checks.values())
    ready_items = [key for key, value in checks.items() if value]
    missing_items = [key for key, value in checks.items() if not value]
    missing_items.extend(runtime_boundary_review["missing_runtime_prerequisites"])
    return {
        "gate_id": _new_gate_id(),
        "status": "design_ready" if design_ready else "design_not_ready",
        **checks,
        "open_cradle_runtime_design_ready": design_ready,
        "open_cradle_runtime_implementation_ready": False,
        "event_loop_plan": event_loop_plan,
        "environment_tick_plan": environment_tick_plan,
        "caregiver_intervention_plan": caregiver_intervention_plan,
        "memory_promotion_review_plan": memory_promotion_review_plan,
        "runtime_boundary_review": runtime_boundary_review,
        "ready_items": ready_items,
        "missing_items": missing_items,
        "current_allowed_claim": CURRENT_ALLOWED_CLAIM,
        "current_not_yet_claim": list(CURRENT_NOT_YET_CLAIM),
        "next_recommended_packages": dict(NEXT_RECOMMENDED_PACKAGES),
        "created_at": _now(),
    }


def write_open_cradle_event_loop_design_gate_report(
    path: str | Path | None = None,
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    gate = build_open_cradle_event_loop_design_gate(base_dir)
    output_path = Path(path) if path is not None else DEFAULT_REPORT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_markdown(gate), encoding="utf-8", newline="\n")
    return {
        "path": str(output_path),
        "gate": gate,
    }


def _tick_mode(
    mode: str,
    purpose: str,
    allowed_inputs: tuple[str, ...],
    allowed_outputs: tuple[str, ...],
    requires_teacher: bool,
    stop_condition: str,
) -> dict[str, Any]:
    return {
        "mode": mode,
        "purpose": purpose,
        "allowed_inputs": list(allowed_inputs),
        "allowed_outputs": list(allowed_outputs),
        "requires_teacher": requires_teacher,
        "stop_condition": stop_condition,
    }


def _render_markdown(gate: dict[str, Any]) -> str:
    lines = [
        "# ASHL Core v1 Open Cradle Event Loop Combined Design Gate Minimal v0",
        "",
        f"gate_id: {gate['gate_id']}",
        f"status: {gate['status']}",
        f"open_cradle_runtime_design_ready: {gate['open_cradle_runtime_design_ready']}",
        (
            "open_cradle_runtime_implementation_ready: "
            f"{gate['open_cradle_runtime_implementation_ready']}"
        ),
        "",
        "## Event Loop Plan",
        "",
        "Loop steps:",
        "",
    ]
    lines.extend(f"- {step}" for step in gate["event_loop_plan"]["loop_steps"])
    lines.extend(["", "Tick modes:", ""])
    for mode in gate["event_loop_plan"]["tick_modes"]:
        lines.append(
            f"- {mode['mode']}: {mode['purpose']} "
            f"(requires_teacher={mode['requires_teacher']})"
        )
    lines.extend(["", "## Environment Tick Plan", ""])
    lines.append("Read sources:")
    lines.extend(f"- {item}" for item in gate["environment_tick_plan"]["read_sources"])
    lines.extend(["", "Outputs:"])
    lines.extend(f"- {item}" for item in gate["environment_tick_plan"]["outputs"])
    lines.extend(["", "## Caregiver Intervention Plan", ""])
    for item in gate["caregiver_intervention_plan"]["conditions"]:
        lines.append(f"- {item['condition']}: {item['suggested_console_action']}")
    lines.extend(["", "## Memory Promotion Review Plan", ""])
    lines.extend(
        f"- {item}" for item in gate["memory_promotion_review_plan"]["review_principles"]
    )
    lines.extend(["", "## Runtime Boundary Review", ""])
    lines.extend(f"- {item}" for item in gate["runtime_boundary_review"]["missing_runtime_prerequisites"])
    lines.extend(["", "## Current Allowed Claim", "", gate["current_allowed_claim"]])
    lines.extend(["", "## Current Not Yet Claim", ""])
    lines.extend(f"- {item}" for item in gate["current_not_yet_claim"])
    lines.extend(["", "## Next Recommended Packages", ""])
    lines.extend(
        f"- {name}: {title}" for name, title in gate["next_recommended_packages"].items()
    )
    lines.append("")
    return "\n".join(lines)


def _new_gate_id() -> str:
    return "open_cradle_event_loop_design_gate_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
