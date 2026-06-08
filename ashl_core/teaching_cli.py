"""Minimal Teaching CLI wrapper for existing lesson flows."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .fake_sandbox import build_initial_sandbox_state, observe, pick_up
from .first_output_runtime import generate_minimal_first_output
from .lesson_runner import run_lesson_causality_test, run_session_2a_with_lesson
from .lesson_store import (
    build_lesson_from_failure,
    generate_lesson_from_failure,
    select_lesson_for_context,
    select_lesson_for_decision_point,
)
from .manual_review import build_review_trace, create_review_item, get_review_item, mark_review_approved, mark_review_rejected
from .mentor_feedback_runtime import build_minimal_mentor_feedback_trace
from .micro_push_box_sandbox import (
    apply_tactile_action,
    build_initial_state as build_micro_push_box_state,
    suggest_next_action_avoiding_repeat_blocked,
)
from .micro_push_box_trial_runner import run_need_state_driven_trial_batch
from .tactile_state_mapping import map_tactile_result_to_state_key
from .trace_persistence import append_first_output_trace, append_mentor_feedback_trace


DECISION_POINT = "before_retry_pick_up_cube"
UNKNOWN_FAILURE_REASON = "unmapped_obstacle_shadow"


def _unknown_failure_result() -> dict[str, Any]:
    return {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": UNKNOWN_FAILURE_REASON,
        "state": build_initial_sandbox_state(),
    }


def _west_failure_result() -> dict[str, Any]:
    return {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }


def _format_conflict_check(selection: dict[str, Any]) -> dict[str, Any]:
    return {
        "implemented": True,
        "conflict_detected": selection["conflict_detected"],
        "conflict_resolution": selection.get("conflict_resolution"),
        "review_required": selection.get("review_required", False),
        "review_status": selection.get("review_status"),
        "conflicting_lesson_ids": selection.get("conflicting_lesson_ids", []),
        "conflicting_actions": selection.get("conflicting_actions", []),
        "selected_lesson_id": selection.get("selected_lesson_id"),
        "selected_action": selection.get("selected_action"),
        "behavior_changed": selection.get("behavior_changed", False),
    }


def _default_lifecycle_lessons() -> list[dict[str, Any]]:
    old_lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    old_lesson["object_id"] = "cube_001"
    old_lesson["stale"] = True
    old_lesson["stale_reason"] = "manual: obsolete wording"
    old_lesson["superseded_by"] = "lesson_004"
    new_lesson = {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": DECISION_POINT,
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "inactive",
        "stale": False,
        "stale_reason": None,
        "supersedes": "lesson_001",
        "confidence": "manual_fixture",
    }
    return [old_lesson, new_lesson]


def _lesson_lifecycle_entry(
    lesson: dict[str, Any],
    selection: dict[str, Any] | None = None,
    conflict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    lesson_id = lesson.get("lesson_id")
    skipped_reason = None
    if selection is not None:
        skipped_reason = next(
            (
                item.get("skipped_reason")
                for item in selection.get("skipped_lessons", [])
                if item.get("lesson_id") == lesson_id
            ),
            None,
        )
    if skipped_reason is None and lesson.get("status") != "active":
        skipped_reason = "inactive"

    participates_in_conflict = False
    if conflict is not None:
        participates_in_conflict = lesson_id in conflict.get("conflicting_lesson_ids", [])

    return {
        "lesson_id": lesson_id,
        "status": lesson.get("status"),
        "stale": lesson.get("stale", False),
        "stale_reason": lesson.get("stale_reason"),
        "superseded_by": lesson.get("superseded_by"),
        "supersedes": lesson.get("supersedes"),
        "eligible_for_selection": lesson_id == (selection or {}).get("selected_lesson_id"),
        "skipped_reason": skipped_reason,
        "participates_in_conflict": participates_in_conflict,
    }


def _format_lifecycle_display(entries: list[dict[str, Any]], suggestions: list[dict[str, Any]] | None = None) -> str:
    lines = ["Lesson Lifecycle"]
    for entry in entries:
        lines.extend(
            [
                "",
                f"- id: {entry['lesson_id']}",
                f"  status: {entry['status']}",
                f"  stale: {str(entry['stale']).lower()}",
                f"  stale_reason: {entry['stale_reason'] or 'none'}",
                f"  superseded_by: {entry['superseded_by'] or 'none'}",
                f"  supersedes: {entry['supersedes'] or 'none'}",
                f"  eligible_for_selection: {str(entry['eligible_for_selection']).lower()}",
                f"  skipped_reason: {entry['skipped_reason'] or 'none'}",
                f"  participates_in_conflict: {str(entry['participates_in_conflict']).lower()}",
            ]
        )
    if suggestions:
        lines.extend(["", "Replacement Suggestions"])
        for suggestion in suggestions:
            lines.extend(
                [
                    "",
                    f"- source_lesson_id: {suggestion['source_lesson_id']}",
                    f"  superseded_by: {suggestion['superseded_by']}",
                    f"  candidate_lesson_id: {suggestion['candidate_lesson_id']}",
                    f"  candidate_exists: {str(suggestion['candidate_exists']).lower()}",
                    f"  candidate_status: {suggestion['candidate_status'] or 'none'}",
                    f"  candidate_stale: {str(suggestion['candidate_stale']).lower()}",
                    f"  candidate_eligible: {str(suggestion['candidate_eligible']).lower()}",
                    f"  activation_applied: {str(suggestion['activation_applied']).lower()}",
                    f"  reason: {suggestion['reason']}",
                ]
            )
    return "\n".join(lines)


def _default_review_items() -> list[dict[str, Any]]:
    return [
        create_review_item(
            target_type="conflict",
            target_id="conflict_001",
            source_lesson_id="lesson_001",
            candidate_lesson_id="lesson_004",
            reason="conflict_requires_manual_review",
            review_id="review_001",
        )
    ]


def _format_review_display(items: list[dict[str, Any]]) -> str:
    if not items:
        return "No manual review items."

    lines = ["Manual Review Items"]
    for item in items:
        lines.extend(
            [
                "",
                f"- id: {item.get('id')}",
                f"  target_type: {item.get('target_type')}",
                f"  target_id: {item.get('target_id')}",
                f"  source_lesson_id: {item.get('source_lesson_id')}",
                f"  candidate_lesson_id: {item.get('candidate_lesson_id')}",
                f"  review_state: {item.get('review_state')}",
                f"  approval_state: {item.get('approval_state')}",
                f"  reason: {item.get('reason')}",
                f"  notes: {item.get('notes') or 'none'}",
            ]
        )
    return "\n".join(lines)


def run_review_display(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    review_items = [dict(item) for item in (items if items is not None else _default_review_items())]
    traces = [build_review_trace(item) for item in review_items]
    return {
        "command": "run-review-display",
        "status": "ok",
        "read_only": True,
        "review_items": review_items,
        "review_traces": traces,
        "display": _format_review_display(review_items),
        "notes": ["Manual review display is read-only and does not mutate review or lesson metadata."],
    }


def _run_review_decision(
    command: str,
    decision: str,
    items: list[dict[str, Any]] | None = None,
    review_id: str = "review_001",
    notes: str | None = None,
) -> dict[str, Any]:
    review_items = [dict(item) for item in (items if items is not None else _default_review_items())]
    item = get_review_item(review_items, review_id)
    if item is None:
        return {
            "command": command,
            "status": "not_found",
            "error": f"Review item not found: {review_id}",
            "review_id": review_id,
            "review_items": review_items,
            "read_only_lessons": True,
            "notes": ["Review decision did not mutate lessons, selection, conflict, or activation."],
        }

    updated = mark_review_approved(item, notes) if decision == "approved" else mark_review_rejected(item, notes)
    updated_items = [updated if existing.get("id") == review_id else dict(existing) for existing in review_items]
    display = run_review_display(updated_items)
    return {
        "command": command,
        "status": "ok",
        "decision": decision,
        "review_id": review_id,
        "review_item": updated,
        "review_items": updated_items,
        "display": display["display"],
        "review_trace": build_review_trace(updated),
        "read_only_lessons": True,
        "selection_behavior_changed": False,
        "conflict_behavior_changed": False,
        "activation_behavior_changed": False,
        "notes": ["Review decision is metadata-only and does not mutate lesson behavior."],
    }


def run_review_approve(
    items: list[dict[str, Any]] | None = None,
    review_id: str = "review_001",
    notes: str | None = None,
) -> dict[str, Any]:
    return _run_review_decision("run-review-approve", "approved", items, review_id, notes)


def run_review_reject(
    items: list[dict[str, Any]] | None = None,
    review_id: str = "review_001",
    notes: str | None = None,
) -> dict[str, Any]:
    return _run_review_decision("run-review-reject", "rejected", items, review_id, notes)


def run_lifecycle_display(
    lessons: list[dict[str, Any]] | None = None,
    context: dict[str, Any] | None = None,
    decision_point: str = DECISION_POINT,
) -> dict[str, Any]:
    lesson_snapshot = [dict(lesson) for lesson in (lessons if lessons is not None else _default_lifecycle_lessons())]
    context = context or {"task": "pick_up", "object_id": "cube_001", "decision_point": decision_point}
    selection = select_lesson_for_context(lesson_snapshot, context)
    conflict = select_lesson_for_decision_point(lesson_snapshot, decision_point)
    replacement_suggestions = selection.get("replacement_suggestions", [])
    entries = [_lesson_lifecycle_entry(lesson, selection=selection, conflict=conflict) for lesson in lesson_snapshot]
    return {
        "command": "run-lifecycle-display",
        "status": "ok",
        "read_only": True,
        "lessons": entries,
        "replacement_suggestions": replacement_suggestions,
        "display": _format_lifecycle_display(entries, replacement_suggestions),
        "selection_trace": selection,
        "conflict_check": _format_conflict_check(conflict),
        "notes": ["Lifecycle display is read-only and does not mutate lesson metadata."],
    }


def run_known_flow() -> dict[str, Any]:
    state = build_initial_sandbox_state()
    observation = observe(state)
    task_attempt = pick_up(state, "cube_001")
    generation = generate_lesson_from_failure("session_1", task_attempt)
    lesson = generation["lesson"]
    conflict_check = _format_conflict_check(select_lesson_for_decision_point([lesson], DECISION_POINT))
    rerun = run_session_2a_with_lesson(lesson)
    return {
        "command": "run-known-flow",
        "status": "ok" if lesson is not None and rerun["success"] else "failed",
        "failure_reason": task_attempt["failure_reason"],
        "observe": observation,
        "task_attempt": task_attempt,
        "lesson": lesson,
        "generation_status": generation["trace"]["generation_status"],
        "lesson_review": {
            "status": "reviewed",
            "conflict_check": conflict_check,
        },
        "conflict_check": conflict_check,
        "behavior_before": task_attempt["result"],
        "behavior_after": rerun["final_result"]["result"],
        "rerun": rerun,
        "notes": ["Conflict check is implemented in v1.9c."],
    }


def run_unknown_flow() -> dict[str, Any]:
    failure_result = _unknown_failure_result()
    generation = generate_lesson_from_failure("session_unknown", failure_result)
    control_attempt = pick_up(build_initial_sandbox_state(), "cube_001")
    return {
        "command": "run-unknown-flow",
        "status": "ok",
        "failure_reason": failure_result["failure_reason"],
        "lesson": generation["lesson"],
        "generation_status": generation["trace"]["generation_status"],
        "executable_action": generation["trace"]["executable_action"],
        "behavior_before": control_attempt["result"],
        "behavior_after": control_attempt["result"],
        "behavior_changed": False,
        "actions": ["observe()", "pick_up(cube_001)"],
        "trace": generation["trace"],
        "conflict_check": _format_conflict_check(select_lesson_for_decision_point([], DECISION_POINT)),
        "notes": ["Unknown failure reason uses v1.7b boundary behavior."],
    }


def run_disable_reenable_flow() -> dict[str, Any]:
    causality = run_lesson_causality_test()
    return {
        "command": "run-disable-reenable-flow",
        "status": "ok" if causality["passed"] else "failed",
        "enabled_result": causality["active"]["result"],
        "disabled_result": causality["disabled"]["result"],
        "reenabled_result": causality["re_enabled"]["result"],
        "removed_result": causality["removed"]["result"],
        "causality": causality,
        "conflict_check": {
            "implemented": True,
            "conflict_detected": False,
            "conflict_resolution": None,
            "review_required": False,
            "review_status": None,
            "conflicting_lesson_ids": [],
            "conflicting_actions": [],
        },
        "notes": ["CLI wrapper preserves v1.6 causal control."],
    }


def run_conflict_check_flow() -> dict[str, Any]:
    east_failure = pick_up(build_initial_sandbox_state(), "cube_001")
    lesson_east = build_lesson_from_failure("session_east", east_failure)
    lesson_west = build_lesson_from_failure("session_west", _west_failure_result())
    selection = select_lesson_for_decision_point([lesson_east, lesson_west], DECISION_POINT)
    return {
        "command": "run-conflict-check-flow",
        "status": "ok",
        "conflict_check": _format_conflict_check(selection),
        "selection_trace": selection,
        "notes": ["Conflict requires human review; no lesson action is applied."],
    }


def run_minimal_interaction(
    session_id: str = "final_check",
    feedback_label: str = "observed",
    mentor_source: str = "mentor",
    note: str | None = None,
    persist: bool = False,
    data_dir: str = "data",
    state_key: str | None = None,
) -> dict[str, Any]:
    first_output_result = generate_minimal_first_output(session_id=session_id, state_key=state_key)
    first_output_trace = first_output_result["first_output_trace"]
    mentor_feedback_trace = build_minimal_mentor_feedback_trace(
        source_first_output_trace_id=first_output_trace["trace_id"],
        session_id=first_output_trace["session_id"],
        tick=first_output_trace["tick"],
        mentor_feedback_label=feedback_label,
        mentor_source=mentor_source,
        mentor_feedback_note=note,
    )
    persistence = {"enabled": False}
    if persist:
        first_output_append = append_first_output_trace(first_output_trace, data_dir)
        mentor_feedback_append = append_mentor_feedback_trace(mentor_feedback_trace, data_dir)
        persistence = {
            "enabled": True,
            "first_output": first_output_append,
            "mentor_feedback": mentor_feedback_append,
            "append_only": True,
            "writes_lesson_store": False,
            "writes_memory_layer": False,
            "creates_lesson_candidate": False,
        }
    return {
        "command": "run-minimal-interaction",
        "flow": "minimal_interaction_cli_bridge_v0",
        "status": "ok",
        "first_output_result": first_output_result,
        "mentor_feedback_trace": mentor_feedback_trace,
        "persistence": persistence,
        "boundary": {
            "llm_used": first_output_result["llm_used"],
            "writes_lesson_store": mentor_feedback_trace["writes_lesson_store"],
            "writes_memory_layer": mentor_feedback_trace["writes_memory_layer"],
            "creates_lesson_candidate": mentor_feedback_trace["creates_lesson_candidate"],
            "engineering_stage": mentor_feedback_trace["engineering_stage"],
            "awakening_claim": False,
        },
        "notes": ["Minimal interaction flow is test-object engineering verification, not dialogue or learning."],
    }


def run_tactile_interaction(action: str | None = None) -> dict[str, Any]:
    if action is None:
        return {
            "command": "run-tactile-interaction",
            "flow": "tactile_interaction_cli_bridge_v0",
            "status": "error",
            "error": "missing_action",
            "boundary": _tactile_interaction_boundary(),
        }

    try:
        tactile_result = apply_tactile_action(build_micro_push_box_state(), action)
        tactile_trace = tactile_result["trace"]
        state_key = map_tactile_result_to_state_key(tactile_trace["result"])
        first_output_result = generate_minimal_first_output(state_key=state_key)
    except ValueError as exc:
        return {
            "command": "run-tactile-interaction",
            "flow": "tactile_interaction_cli_bridge_v0",
            "status": "error",
            "action": action,
            "error": str(exc),
            "boundary": _tactile_interaction_boundary(),
        }

    return {
        "command": "run-tactile-interaction",
        "flow": "tactile_interaction_cli_bridge_v0",
        "status": "ok",
        "action": action,
        "tactile_result": tactile_trace["result"],
        "state_key": state_key,
        "utterance": first_output_result["first_output"],
        "tactile_sandbox_trace": tactile_trace,
        "boundary": _tactile_interaction_boundary(llm_used=first_output_result["llm_used"]),
        "notes": ["Tactile interaction CLI is deterministic and does not create lesson or memory outputs."],
    }


def run_clear_sandbox_working_state(
    session_id: str = "final_check",
    working_state: dict[str, Any] | None = None,
    data_dir: str = "data",
) -> dict[str, Any]:
    clearable_keys = ("action_history", "sandbox_session_state", "temporary_session_state")
    state = dict(working_state or {})
    cleared = [key for key in clearable_keys if key in state]
    reason = None if cleared else "no_persistent_working_state_found"
    preserved_data_dir = data_dir.rstrip("/\\") or "data"
    return {
        "command": "clear-sandbox-working-state",
        "status": "ok",
        "session_id": session_id,
        "working_state_cleared": True,
        "append_only_traces_preserved": True,
        "cleared": cleared,
        "preserved": [
            f"{preserved_data_dir}/first_output_traces.jsonl",
            f"{preserved_data_dir}/mentor_feedback_traces.jsonl",
        ],
        "reason": reason,
        "boundary": {
            "deletes_append_only_traces": False,
            "deletes_data_dir": False,
            "writes_lesson_store": False,
            "writes_memory_layer": False,
            "creates_lesson_candidate": False,
            "llm_used": False,
        },
        "notes": ["Sandbox working state clear does not delete append-only trace files."],
    }


def run_grounded_learning_check(actions: list[str] | tuple[str, ...] | None = None) -> dict[str, Any]:
    action_sequence = list(actions or ["push_right", "push_right"])
    state = build_micro_push_box_state()
    steps = []
    try:
        for index, action in enumerate(action_sequence, start=1):
            tactile_result = apply_tactile_action(state, action)
            state = tactile_result["state"]
            trace = tactile_result["trace"]
            state_key = map_tactile_result_to_state_key(trace["result"])
            first_output_result = generate_minimal_first_output(state_key=state_key)
            steps.append(
                {
                    "step_index": index,
                    "action": action,
                    "tactile_result": trace["result"],
                    "state_key": state_key,
                    "utterance": first_output_result["first_output"],
                    "history": trace["history"],
                    "trace": trace,
                }
            )
        suggested_next_action = suggest_next_action_avoiding_repeat_blocked(state, ["push_right", "wait"])
    except ValueError as exc:
        return {
            "command": "run-grounded-learning-check",
            "flow": "grounded_learning_verification_cli_v0",
            "status": "error",
            "actions": action_sequence,
            "steps": steps,
            "error": str(exc),
            "boundary": _verification_boundary(),
        }

    return {
        "command": "run-grounded-learning-check",
        "flow": "grounded_learning_verification_cli_v0",
        "status": "ok",
        "actions": action_sequence,
        "steps": steps,
        "suggested_next_action": suggested_next_action,
        "boundary": _verification_boundary(),
        "notes": ["Grounded learning verification is evidence-only and does not create learning outputs."],
    }


def run_need_state_trial_batch_cli(
    trial_count: int = 5,
    max_steps: int = 10,
    random_seed: int | None = None,
) -> dict[str, Any]:
    batch = run_need_state_driven_trial_batch(
        trial_count=trial_count,
        max_steps=max_steps,
        random_seed=random_seed,
    )
    return {
        "command": "run-need-state-trial-batch",
        "flow": "need_state_trial_batch_cli_v0",
        "status": "ok",
        **batch,
        "boundary": {
            "llm_used": False,
            "creates_lesson_candidate": False,
            "writes_lesson_store": False,
            "writes_memory_layer": False,
            "awakening_claim": False,
        },
        "notes": ["Need-state trial batch CLI only wraps the existing deterministic batch runner."],
    }


def _verification_boundary() -> dict[str, bool]:
    return {
        "llm_used": False,
        "creates_lesson_candidate": False,
        "writes_lesson_store": False,
        "writes_memory_layer": False,
        "learning_pipeline_used": False,
        "teaching_chat_loop_used": False,
        "awakening_claim": False,
    }


def _tactile_interaction_boundary(llm_used: bool = False) -> dict[str, bool]:
    return {
        "llm_used": llm_used,
        "creates_lesson_candidate": False,
        "writes_lesson_store": False,
        "writes_memory_layer": False,
        "awakening_claim": False,
    }


def run_command(command: str) -> dict[str, Any]:
    if command == "run-known-flow":
        return run_known_flow()
    if command == "run-unknown-flow":
        return run_unknown_flow()
    if command == "run-disable-reenable-flow":
        return run_disable_reenable_flow()
    if command == "run-conflict-check-flow":
        return run_conflict_check_flow()
    if command == "run-lifecycle-display":
        return run_lifecycle_display()
    if command == "run-review-display":
        return run_review_display()
    if command == "run-review-approve":
        return run_review_approve()
    if command == "run-review-reject":
        return run_review_reject()
    if command == "run-minimal-interaction":
        return run_minimal_interaction()
    if command == "run-tactile-interaction":
        return run_tactile_interaction()
    if command == "clear-sandbox-working-state":
        return run_clear_sandbox_working_state()
    if command == "run-grounded-learning-check":
        return run_grounded_learning_check()
    if command == "run-need-state-trial-batch":
        return run_need_state_trial_batch_cli()
    return {
        "command": command,
        "status": "error",
        "error": "unknown_command",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ASHL Core minimal teaching CLI")
    parser.add_argument(
        "command",
        choices=[
            "run-known-flow",
            "run-unknown-flow",
            "run-disable-reenable-flow",
            "run-conflict-check-flow",
            "run-lifecycle-display",
            "run-review-display",
            "run-review-approve",
            "run-review-reject",
            "run-minimal-interaction",
            "run-tactile-interaction",
            "clear-sandbox-working-state",
            "run-grounded-learning-check",
            "run-need-state-trial-batch",
        ],
    )
    parser.add_argument("--review-id", default="review_001")
    parser.add_argument("--notes", default=None)
    parser.add_argument("--session-id", default="final_check")
    parser.add_argument("--feedback-label", default="observed")
    parser.add_argument("--mentor-source", default="mentor")
    parser.add_argument("--persist", action="store_true")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--state-key", default=None)
    parser.add_argument("--action", default=None)
    parser.add_argument("--actions", nargs="*", default=None)
    parser.add_argument("--trial-count", type=int, default=5)
    parser.add_argument("--max-steps", type=int, default=10)
    parser.add_argument("--random-seed", type=int, default=None)
    args = parser.parse_args(argv)
    if args.command == "run-review-approve":
        result = run_review_approve(review_id=args.review_id, notes=args.notes)
    elif args.command == "run-review-reject":
        result = run_review_reject(review_id=args.review_id, notes=args.notes)
    elif args.command == "run-minimal-interaction":
        result = run_minimal_interaction(
            session_id=args.session_id,
            feedback_label=args.feedback_label,
            mentor_source=args.mentor_source,
            note=args.notes,
            persist=args.persist,
            data_dir=args.data_dir,
            state_key=args.state_key,
        )
    elif args.command == "run-tactile-interaction":
        result = run_tactile_interaction(action=args.action)
    elif args.command == "clear-sandbox-working-state":
        result = run_clear_sandbox_working_state(session_id=args.session_id, data_dir=args.data_dir)
    elif args.command == "run-grounded-learning-check":
        result = run_grounded_learning_check(actions=args.actions)
    elif args.command == "run-need-state-trial-batch":
        result = run_need_state_trial_batch_cli(
            trial_count=args.trial_count,
            max_steps=args.max_steps,
            random_seed=args.random_seed,
        )
    else:
        result = run_command(args.command)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
