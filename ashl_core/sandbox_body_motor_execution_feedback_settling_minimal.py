"""Route body-motor sandbox execution outcomes into same-session feedback and settling traces."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_body_motor_command_execution_loop_minimal import (
    build_sandbox_body_motor_command_execution_loop_record,
    run_sandbox_body_motor_command_execution_loop_minimal_check,
    validate_sandbox_body_motor_command_execution_loop_record,
)


COMMAND = "run-sandbox-body-motor-execution-feedback-settling-minimal-check"
FLOW = "sandbox_body_motor_execution_feedback_settling_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxBodyMotorExecutionFeedbackSettling-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b118"
BOUNDARY_INDEX_AFTER = "2026-06-09-b119"

RESULT_TO_FEEDBACK = {
    "moved_forward_one_cell": {
        "feedback_label": "movement_success_feedback",
        "response_axis": "dopamine_like",
        "settling_mode": "natural_settling",
        "confidence_delta": 0.04,
    },
    "front_item_reached": {
        "feedback_label": "reach_success_feedback",
        "response_axis": "dopamine_like",
        "settling_mode": "natural_settling",
        "confidence_delta": 0.05,
    },
}
BLOCKED_FLAGS = (
    "new_selected_action_created",
    "new_final_action_created",
    "new_direct_command_created",
    "new_motor_execution_created",
    "candidate_reordering_created",
    "persistent_feedback_created",
    "cross_session_feedback_persistence",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "persistent_body_schema_written",
    "persistent_endocrine_state_written",
    "production_behavior_changed",
    "real_navigation_changed",
    "ui_behavior_changed",
    "pathfinding_used",
    "semantic_vision",
    "object_recognition",
    "subjective_emotion_claim_allowed",
    "biological_hormone_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
    "proof_of_learning_claimed",
)


def build_sandbox_body_motor_execution_feedback_settling_record(
    command_execution_loop_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = deepcopy(command_execution_loop_record) if command_execution_loop_record is not None else (
        build_sandbox_body_motor_command_execution_loop_record()
    )
    source_validation = validate_sandbox_body_motor_command_execution_loop_record(source)
    if not source_validation["valid"]:
        raise ValueError("command_execution_loop_record must validate before feedback settling")

    source_summary = _source_summary(source)
    feedback = _derive_feedback_trace(source_summary)
    settling = _derive_settling_trace(feedback)
    rollback = _derive_rollback_trace(feedback, settling)
    return {
        "record_type": "sandbox_body_motor_execution_feedback_settling_minimal",
        "record_version": "v0",
        "feedback_settling_status": "completed_same_session_body_motor_feedback_settling",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_command_execution_loop": source_summary,
        "feedback_trace": feedback,
        "settling_trace": settling,
        "rollback_trace": rollback,
        "human_summary": {
            "what_was_connected": "Sandbox body-motor execution outcomes were connected to same-session feedback and settling traces.",
            "what_feedback_means": "Successful sandbox movement/reach outcomes can produce trace-only confidence and dopamine_like settling signals.",
            "what_settling_means": "The signal decays toward baseline inside the same sandbox session and can be rolled back.",
            "what_is_blocked": "No new action, command, execution, persistence, memory write, predictor mutation, production behavior, semantic vision, subjective emotion, or proof claim is created.",
            "plain_result": "Body-motor sandbox outcomes can now produce bounded same-session feedback/settling evidence only.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_body_motor_execution_feedback_settling_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_body_motor_execution_feedback_settling_minimal",
        "record_version": "v0",
        "feedback_settling_status": "completed_same_session_body_motor_feedback_settling",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _dict(record.get("source_command_execution_loop"), errors, "source_command_execution_loop_missing")
    _validate_source(source, errors)

    expected_feedback = _derive_feedback_trace(source)
    feedback = _dict(record.get("feedback_trace"), errors, "feedback_trace_missing")
    for field, value in expected_feedback.items():
        if feedback.get(field) != value:
            errors.append(f"feedback_trace_{field}_not_expected")

    expected_settling = _derive_settling_trace(feedback)
    settling = _dict(record.get("settling_trace"), errors, "settling_trace_missing")
    for field, value in expected_settling.items():
        if settling.get(field) != value:
            errors.append(f"settling_trace_{field}_not_expected")

    expected_rollback = _derive_rollback_trace(feedback, settling)
    rollback = _dict(record.get("rollback_trace"), errors, "rollback_trace_missing")
    for field, value in expected_rollback.items():
        if rollback.get(field) != value:
            errors.append(f"rollback_trace_{field}_not_expected")

    human = _dict(record.get("human_summary"), errors, "human_summary_missing")
    for field in (
        "what_was_connected",
        "what_feedback_means",
        "what_settling_means",
        "what_is_blocked",
        "plain_result",
    ):
        if not isinstance(human.get(field), str) or not human.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    blocked = _dict(record.get("blocked_flags"), errors, "blocked_flags_missing")
    for field in BLOCKED_FLAGS:
        if blocked.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    return {
        "valid": not errors,
        "error_codes": errors,
        "source_loop_checked": source.get("source_validated") is True,
        "feedback_trace_created": feedback.get("feedback_trace_created") is True,
        "feedback_blocked": feedback.get("feedback_trace_created") is False,
        "settling_trace_created": settling.get("settling_trace_created") is True,
        "settling_blocked": settling.get("settling_trace_created") is False,
        "rollback_available": rollback.get("rollback_available") is True,
        "rollback_restores_baseline": rollback.get("session_end_restores_baseline") is True,
        "step_forward_feedback": feedback.get("source_final_action") == "step_forward"
        and feedback.get("feedback_label") == "movement_success_feedback",
        "reach_front_feedback": feedback.get("source_final_action") == "reach_front"
        and feedback.get("feedback_label") == "reach_success_feedback",
        "wall_feedback_blocked": feedback.get("blocked_reason") == "outcome_not_available_for_feedback",
        "same_session_only": feedback.get("feedback_scope") in {"same_session_sandbox_only", None}
        and settling.get("settling_scope") in {"same_session_sandbox_only", None},
        "new_action_blocked": blocked.get("new_selected_action_created") is False
        and blocked.get("new_final_action_created") is False
        and blocked.get("new_direct_command_created") is False
        and blocked.get("new_motor_execution_created") is False,
        "candidate_reordering_blocked": blocked.get("candidate_reordering_created") is False,
        "persistent_feedback_blocked": blocked.get("persistent_feedback_created") is False
        and blocked.get("cross_session_feedback_persistence") is False,
        "memory_write_blocked": blocked.get("memory_write_performed") is False
        and blocked.get("retained_jsonl_write_performed") is False,
        "retention_blocked": blocked.get("retention_write_performed") is False,
        "predictor_mutation_blocked": blocked.get("predictor_mutation_performed") is False
        and blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False,
        "persistent_state_blocked": blocked.get("persistent_body_schema_written") is False
        and blocked.get("persistent_endocrine_state_written") is False,
        "production_behavior_blocked": blocked.get("production_behavior_changed") is False
        and blocked.get("real_navigation_changed") is False
        and blocked.get("ui_behavior_changed") is False,
        "semantic_vision_blocked": blocked.get("semantic_vision") is False
        and blocked.get("object_recognition") is False,
        "subjective_claim_blocked": blocked.get("subjective_emotion_claim_allowed") is False
        and blocked.get("biological_hormone_claim_allowed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claimed") is False
        and blocked.get("autonomous_learning_claim_allowed") is False
        and blocked.get("autonomous_action_claim_allowed") is False,
    }


def run_sandbox_body_motor_execution_feedback_settling_minimal_check() -> dict[str, Any]:
    source_result = run_sandbox_body_motor_command_execution_loop_minimal_check()
    empty_source, wall_source, item_source = source_result["valid_records"]
    valid_empty = build_sandbox_body_motor_execution_feedback_settling_record(empty_source)
    valid_wall = build_sandbox_body_motor_execution_feedback_settling_record(wall_source)
    valid_item = build_sandbox_body_motor_execution_feedback_settling_record(item_source)
    records = [valid_empty, valid_wall, valid_item, *_invalid_records(valid_empty)]
    validation_results = [validate_sandbox_body_motor_execution_feedback_settling_record(record) for record in records]
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
            "boundary_reason": "Connects body-motor sandbox execution outcomes to same-session feedback and settling traces.",
        },
        "valid_records": [valid_empty, valid_wall, valid_item],
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_connected": "Body-motor sandbox outcomes now feed same-session feedback and settling traces.",
            "what_is_blocked": "No new action, command, execution, memory write, retention write, predictor mutation, production behavior, persistent state, semantic vision, or proof claim is created.",
            "plain_result": "Qingyin can register bounded internal response evidence from sandbox body-motor outcomes, then settle it in-session.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    source_loop = source["source_command_execution_loop"] if "source_command_execution_loop" in source else None
    if source_loop is not None:
        return deepcopy(source_loop)
    final_action = source["source_body_motor_final_action"]
    command = source["direct_command_result"]
    execution = source["motor_execution_result"]
    outcome = source["outcome_observation"]
    return {
        "source_record_type": source["record_type"],
        "source_validated": True,
        "body_id": final_action["body_id"],
        "body_scope": final_action["body_scope"],
        "front_symbol": final_action["front_symbol"],
        "final_action": final_action["final_action"],
        "direct_command": command["direct_command"],
        "motor_action_executed": execution["motor_action_executed"],
        "execution_result": execution["execution_result"],
        "outcome_observed": outcome["outcome_observed"],
        "outcome_match": outcome["outcome_match"],
        "movement_observed": outcome["movement_observed"],
        "reach_observed": outcome["reach_observed"],
        "audit_recorded": outcome["audit_recorded"],
    }


def _derive_feedback_trace(source: dict[str, Any]) -> dict[str, Any]:
    result = source.get("execution_result")
    config = RESULT_TO_FEEDBACK.get(result)
    created = source.get("outcome_observed") is True and source.get("outcome_match") is True and config is not None
    return {
        "feedback_trace_created": created,
        "feedback_scope": "same_session_sandbox_only" if created else None,
        "source_final_action": source.get("final_action") if created else source.get("final_action"),
        "source_execution_result": result if created else None,
        "feedback_label": config["feedback_label"] if created else None,
        "confidence_delta": config["confidence_delta"] if created else 0.0,
        "response_axis": config["response_axis"] if created else None,
        "trace_only": True,
        "applied_persistently": False,
        "candidate_reordering_created": False,
        "new_action_created": False,
        "blocked_reason": None if created else "outcome_not_available_for_feedback",
        "audit_recorded": True,
    }


def _derive_settling_trace(feedback: dict[str, Any]) -> dict[str, Any]:
    created = feedback.get("feedback_trace_created") is True
    return {
        "settling_trace_created": created,
        "settling_scope": "same_session_sandbox_only" if created else None,
        "settling_mode": RESULT_TO_FEEDBACK.get(feedback.get("source_execution_result"), {}).get("settling_mode")
        if created else None,
        "response_axis": feedback.get("response_axis") if created else None,
        "signal_before_settling": 0.24 if created else None,
        "signal_after_settling": 0.20 if created else None,
        "baseline_signal": 0.20 if created else None,
        "settled_to_baseline": True if created else False,
        "persistent_state_written": False,
        "memory_write_performed": False,
        "predictor_mutation_performed": False,
        "blocked_reason": None if created else "feedback_not_available_for_settling",
        "audit_recorded": True,
    }


def _derive_rollback_trace(feedback: dict[str, Any], settling: dict[str, Any]) -> dict[str, Any]:
    created = feedback.get("feedback_trace_created") is True or settling.get("settling_trace_created") is True
    return {
        "rollback_available": True,
        "rollback_scope": "same_session_sandbox_only",
        "session_end_restores_baseline": True,
        "dirty_state_after_rollback": False,
        "feedback_trace_removed_from_runtime_state": created,
        "settling_trace_removed_from_runtime_state": created,
        "persistent_update_performed": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_command_execution_loop_not_validated")
    if source.get("source_record_type") != "sandbox_body_motor_command_execution_loop_minimal":
        errors.append("source_command_execution_loop_record_type_not_expected")
    if source.get("body_id") != "qingyin_minimal_grid_body_v0":
        errors.append("source_command_execution_loop_body_id_not_expected")
    if source.get("body_scope") != "sandbox_only":
        errors.append("source_command_execution_loop_body_scope_not_expected")
    if source.get("final_action") is not None and source.get("final_action") not in ("step_forward", "reach_front"):
        errors.append("source_command_execution_loop_final_action_invalid")
    if source.get("audit_recorded") is not True:
        errors.append("source_command_execution_loop_audit_not_recorded")


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    def add(name: str, mutator) -> None:
        record = deepcopy(valid_record)
        mutator(record)
        record["invalid_case"] = name
        cases.append(record)

    add("wrong_record_type", lambda r: r.__setitem__("record_type", "body_motor_feedback"))
    add("source_not_validated", lambda r: r["source_command_execution_loop"].__setitem__("source_validated", False))
    add("source_wrong_action", lambda r: r["source_command_execution_loop"].__setitem__("final_action", "jump"))
    add("source_outcome_not_observed", lambda r: r["source_command_execution_loop"].__setitem__("outcome_observed", False))
    add("feedback_not_created", lambda r: r["feedback_trace"].__setitem__("feedback_trace_created", False))
    add("wrong_feedback_scope", lambda r: r["feedback_trace"].__setitem__("feedback_scope", "cross_session"))
    add("wrong_feedback_label", lambda r: r["feedback_trace"].__setitem__("feedback_label", "wrong"))
    add("wrong_confidence_delta", lambda r: r["feedback_trace"].__setitem__("confidence_delta", 0.99))
    add("wrong_response_axis", lambda r: r["feedback_trace"].__setitem__("response_axis", "cortisol_like"))
    add("feedback_persistent", lambda r: r["feedback_trace"].__setitem__("applied_persistently", True))
    add("feedback_reordering", lambda r: r["feedback_trace"].__setitem__("candidate_reordering_created", True))
    add("feedback_new_action", lambda r: r["feedback_trace"].__setitem__("new_action_created", True))
    add("settling_not_created", lambda r: r["settling_trace"].__setitem__("settling_trace_created", False))
    add("wrong_settling_scope", lambda r: r["settling_trace"].__setitem__("settling_scope", "persistent"))
    add("wrong_settling_mode", lambda r: r["settling_trace"].__setitem__("settling_mode", "safety_reset"))
    add("wrong_signal_after", lambda r: r["settling_trace"].__setitem__("signal_after_settling", 0.22))
    add("not_settled_to_baseline", lambda r: r["settling_trace"].__setitem__("settled_to_baseline", False))
    add("settling_persistent_state", lambda r: r["settling_trace"].__setitem__("persistent_state_written", True))
    add("settling_memory_write", lambda r: r["settling_trace"].__setitem__("memory_write_performed", True))
    add("settling_predictor_mutation", lambda r: r["settling_trace"].__setitem__("predictor_mutation_performed", True))
    add("rollback_unavailable", lambda r: r["rollback_trace"].__setitem__("rollback_available", False))
    add("rollback_dirty", lambda r: r["rollback_trace"].__setitem__("dirty_state_after_rollback", True))
    add("rollback_memory_write", lambda r: r["rollback_trace"].__setitem__("memory_write_performed", True))
    add("blocked_new_action", lambda r: r["blocked_flags"].__setitem__("new_selected_action_created", True))
    add("blocked_new_command", lambda r: r["blocked_flags"].__setitem__("new_direct_command_created", True))
    add("blocked_persistent_feedback", lambda r: r["blocked_flags"].__setitem__("persistent_feedback_created", True))
    add("blocked_memory_write", lambda r: r["blocked_flags"].__setitem__("memory_write_performed", True))
    add("blocked_retention_write", lambda r: r["blocked_flags"].__setitem__("retention_write_performed", True))
    add("blocked_predictor_mutation", lambda r: r["blocked_flags"].__setitem__("predictor_mutation_performed", True))
    add("blocked_production_behavior", lambda r: r["blocked_flags"].__setitem__("production_behavior_changed", True))
    add("blocked_semantic_vision", lambda r: r["blocked_flags"].__setitem__("semantic_vision", True))
    add("blocked_subjective_claim", lambda r: r["blocked_flags"].__setitem__("subjective_emotion_claim_allowed", True))
    add("blocked_proof_claim", lambda r: r["blocked_flags"].__setitem__("proof_of_learning_claimed", True))
    add("empty_human_summary", lambda r: r["human_summary"].__setitem__("plain_result", ""))
    return cases


def _summary(results: list[dict[str, Any]]) -> dict[str, int]:
    valid_results = [result for result in results if result["valid"]]
    return {
        "feedback_settling_result_count": len(results),
        "valid_feedback_settling_count": len(valid_results),
        "invalid_feedback_settling_count": len(results) - len(valid_results),
        "source_loop_checked_count": _count_valid(valid_results, "source_loop_checked"),
        "feedback_trace_created_count": _count_valid(valid_results, "feedback_trace_created"),
        "feedback_blocked_count": _count_valid(valid_results, "feedback_blocked"),
        "settling_trace_created_count": _count_valid(valid_results, "settling_trace_created"),
        "settling_blocked_count": _count_valid(valid_results, "settling_blocked"),
        "rollback_available_count": _count_valid(valid_results, "rollback_available"),
        "rollback_restores_baseline_count": _count_valid(valid_results, "rollback_restores_baseline"),
        "step_forward_feedback_count": _count_valid(valid_results, "step_forward_feedback"),
        "reach_front_feedback_count": _count_valid(valid_results, "reach_front_feedback"),
        "wall_feedback_blocked_count": _count_valid(valid_results, "wall_feedback_blocked"),
        "same_session_only_count": _count_valid(valid_results, "same_session_only"),
        "new_action_blocked_count": _count_valid(valid_results, "new_action_blocked"),
        "candidate_reordering_blocked_count": _count_valid(valid_results, "candidate_reordering_blocked"),
        "persistent_feedback_blocked_count": _count_valid(valid_results, "persistent_feedback_blocked"),
        "memory_write_blocked_count": _count_valid(valid_results, "memory_write_blocked"),
        "retention_blocked_count": _count_valid(valid_results, "retention_blocked"),
        "predictor_mutation_blocked_count": _count_valid(valid_results, "predictor_mutation_blocked"),
        "persistent_state_blocked_count": _count_valid(valid_results, "persistent_state_blocked"),
        "production_behavior_blocked_count": _count_valid(valid_results, "production_behavior_blocked"),
        "semantic_vision_blocked_count": _count_valid(valid_results, "semantic_vision_blocked"),
        "subjective_claim_blocked_count": _count_valid(valid_results, "subjective_claim_blocked"),
        "proof_claim_blocked_count": _count_valid(valid_results, "proof_claim_blocked"),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["feedback_settling_result_count"] == 37
        and summary["valid_feedback_settling_count"] == 3
        and summary["invalid_feedback_settling_count"] == 34
        and summary["source_loop_checked_count"] == 3
        and summary["feedback_trace_created_count"] == 2
        and summary["feedback_blocked_count"] == 1
        and summary["settling_trace_created_count"] == 2
        and summary["settling_blocked_count"] == 1
        and summary["rollback_available_count"] == 3
        and summary["rollback_restores_baseline_count"] == 3
        and summary["step_forward_feedback_count"] == 1
        and summary["reach_front_feedback_count"] == 1
        and summary["wall_feedback_blocked_count"] == 1
        and summary["same_session_only_count"] == 3
        and summary["new_action_blocked_count"] == 3
        and summary["candidate_reordering_blocked_count"] == 3
        and summary["persistent_feedback_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["retention_blocked_count"] == 3
        and summary["predictor_mutation_blocked_count"] == 3
        and summary["persistent_state_blocked_count"] == 3
        and summary["production_behavior_blocked_count"] == 3
        and summary["semantic_vision_blocked_count"] == 3
        and summary["subjective_claim_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
    )


def _dict(value: Any, errors: list[str], error_code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(error_code)
        return {}
    return value


def _count_valid(results: list[dict[str, Any]], field: str) -> int:
    return sum(1 for result in results if result.get(field) is True)
