"""Create sandbox-only direct_command from arbitration command boundary."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER as SOURCE_BOUNDARY_INDEX,
    build_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_record,
    run_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_record,
)


COMMAND = "run-sandbox-candidate-ordering-arbitration-direct-command-minimal-check"
FLOW = "sandbox_candidate_ordering_arbitration_direct_command_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxCandidateOrderingArbitrationDirectCommand-Minimal-v0"
BOUNDARY_INDEX_BEFORE = "2026-06-09-b144"
BOUNDARY_INDEX_AFTER = "2026-06-09-b145"

REQUIRED_TOP_LEVEL_FIELDS = {
    "direct_command_record_id",
    "record_type",
    "record_version",
    "package_id",
    "boundary_index_before",
    "boundary_index_after",
    "boundary_change_required",
    "source_direct_command_approval_boundary",
    "sandbox_direct_command",
    "rollback_preview",
    "human_summary",
    "blocked_flags",
}

BLOCKED_FLAGS = {
    "sandbox_action_executed",
    "sandbox_execution_result_created",
    "runtime_behavior_changed",
    "purpose_created_from_affordance",
    "purpose_created_from_feedback",
    "purpose_created_from_tendency",
    "purpose_changed_by_affordance",
    "purpose_changed_by_feedback",
    "purpose_changed_by_tendency",
    "raw_weighted_sum_used",
    "affordance_used_as_desire",
    "feedback_cross_purpose_applied",
    "tendency_overrode_purpose",
    "tendency_overrode_affordance_gate",
    "feedback_persisted",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_modified",
    "direct_endocrine_feed",
    "direct_tendency_feed",
    "production_behavior_changed",
    "proof_of_learning_claim",
}


def build_sandbox_candidate_ordering_arbitration_direct_command_record(
    direct_command_approval_boundary_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(direct_command_approval_boundary_record)
        if direct_command_approval_boundary_record is not None
        else build_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_record()
    )
    source_validation = validate_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_record(source)
    if not source_validation["valid"]:
        raise ValueError("direct_command_approval_boundary_record must validate before direct_command creation")

    source_summary = _source_summary(source)
    scenario = source_summary["scenario_id"]
    command_text = source_summary["candidate_for_future_direct_command"]
    final_action = source_summary["source_final_action"]
    return {
        "direct_command_record_id": f"sandbox_candidate_ordering_arbitration_direct_command_{scenario}_demo_001",
        "record_type": "sandbox_candidate_ordering_arbitration_direct_command_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
        "source_direct_command_approval_boundary": source_summary,
        "sandbox_direct_command": {
            "direct_command_created": True,
            "direct_command": command_text,
            "direct_command_source": "sandbox_candidate_ordering_arbitration_direct_command_approval_boundary",
            "direct_command_scope": "sandbox_only",
            "direct_command_reason": "arbitration_final_action_direct_command_boundary",
            "scenario_id": scenario,
            "approved_purpose": source_summary["approved_purpose"],
            "candidate_family": source_summary["candidate_family"],
            "source_final_action": final_action,
            "source_selected_action": source_summary["source_selected_action"],
            "arbitration_rules_preserved": source_summary["source_arbitration_rules_preserved"],
            "sandbox_action_executed": False,
            "execution_result_created": False,
            "execution_allowed_in_this_package": False,
            "future_execution_requires_separate_boundary": True,
            "future_memory_write_requires_separate_boundary": True,
            "future_retention_requires_separate_boundary": True,
            "future_predictor_influence_requires_separate_boundary": True,
            "future_production_promotion_requires_separate_boundary": True,
            "rollback_available": True,
            "audit_recorded": True,
        },
        "rollback_preview": {
            "rollback_available": True,
            "direct_command_removed_on_rollback": True,
            "dirty_state_after_rollback": False,
            "persistent_update_performed": False,
        },
        "human_summary": {
            "what_was_created": f"Arbitration final_action {final_action} created sandbox-only direct_command {command_text}.",
            "what_changed": "An arbitration sandbox final_action became a sandbox-only direct_command record.",
            "what_is_blocked": "Execution, persistence, predictor access or mutation, direct feedback feeds, production behavior, and proof claims remain blocked.",
            "plain_result": "Arbitration can now prepare a sandbox direct command, but it still cannot execute it.",
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_sandbox_candidate_ordering_arbitration_direct_command_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing = sorted(field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing)
    extra = sorted(field for field in record if field not in REQUIRED_TOP_LEVEL_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra)

    expected = {
        "record_type": "sandbox_candidate_ordering_arbitration_direct_command_minimal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "boundary_index_before": BOUNDARY_INDEX_BEFORE,
        "boundary_index_after": BOUNDARY_INDEX_AFTER,
        "boundary_change_required": True,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = _as_dict(record.get("source_direct_command_approval_boundary"), errors, "source_direct_command_approval_boundary")
    command = _as_dict(record.get("sandbox_direct_command"), errors, "sandbox_direct_command")
    rollback = _as_dict(record.get("rollback_preview"), errors, "rollback_preview")
    human = _as_dict(record.get("human_summary"), errors, "human_summary")
    blocked = _as_dict(record.get("blocked_flags"), errors, "blocked_flags")

    _validate_source(source, errors)
    _validate_direct_command(command, source, errors)
    _validate_rollback(rollback, errors)
    _validate_human_summary(human, errors)
    _validate_blocked_flags(blocked, errors)

    return {
        "valid": not errors,
        "error_codes": errors,
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "direct_command": command.get("direct_command"),
        "direct_command_created": command.get("direct_command_created") is True,
        "sandbox_only_direct_command": command.get("direct_command_scope") == "sandbox_only",
        "arbitration_rules_preserved": command.get("arbitration_rules_preserved") is True,
        "execution_blocked": command.get("sandbox_action_executed") is False
        and command.get("execution_result_created") is False
        and command.get("execution_allowed_in_this_package") is False
        and blocked.get("sandbox_action_executed") is False
        and blocked.get("sandbox_execution_result_created") is False,
        "memory_write_blocked": blocked.get("memory_write") is False
        and blocked.get("retention_write") is False
        and blocked.get("new_retention_written") is False,
        "predictor_use_blocked": blocked.get("predictor_read_enabled") is False
        and blocked.get("predictor_influence_enabled") is False
        and blocked.get("predictor_modified") is False,
        "direct_feed_blocked": blocked.get("direct_endocrine_feed") is False
        and blocked.get("direct_tendency_feed") is False,
        "proof_claim_blocked": blocked.get("proof_of_learning_claim") is False,
        "rollback_available": command.get("rollback_available") is True
        and rollback.get("rollback_available") is True
        and rollback.get("dirty_state_after_rollback") is False,
    }


def run_sandbox_candidate_ordering_arbitration_direct_command_minimal_check() -> dict[str, Any]:
    source_records = run_sandbox_candidate_ordering_arbitration_direct_command_approval_boundary_minimal_check()[
        "valid_records"
    ]
    valid_records = [
        build_sandbox_candidate_ordering_arbitration_direct_command_record(source) for source in source_records
    ]
    records = [*valid_records, *_invalid_records(valid_records[0], valid_records[1], valid_records[2])]
    validation_results = [validate_sandbox_candidate_ordering_arbitration_direct_command_record(record) for record in records]
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
            "boundary_reason": "Creates sandbox-only direct_command records from arbitration direct-command approval boundary.",
        },
        "valid_records": valid_records,
        "validation_results": validation_results,
        "summary": summary,
        "human_summary": {
            "what_was_built": "Arbitration sandbox direct_command creation was added.",
            "what_changed": "Arbitration final_actions can become sandbox-only direct_command records.",
            "what_is_blocked": "Execution, persistence, predictor use or mutation, direct feedback feeds, production behavior, and proof claims remain blocked.",
            "plain_result": "The arbitration path can now prepare sandbox direct commands, but it still cannot execute them.",
        },
        "valid_result_count": len(valid_results),
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    boundary = source["direct_command_approval_boundary"]
    source_final = source["source_sandbox_final_action"]
    return {
        "source_direct_command_approval_boundary_id": source["direct_command_approval_boundary_id"],
        "source_validated": True,
        "source_boundary_index": source["boundary_index_after"],
        "scenario_id": source_final["scenario_id"],
        "approved_purpose": source_final["approved_purpose"],
        "candidate_family": source_final["candidate_family"],
        "source_final_action": source_final["final_action"],
        "source_selected_action": source_final["source_selected_action"],
        "candidate_for_future_direct_command": boundary["candidate_for_future_direct_command"],
        "future_direct_command_allowed": boundary["future_direct_command_allowed"],
        "direct_command_scope": boundary["direct_command_scope"],
        "source_direct_command_created_in_source_package": boundary["direct_command_created_in_this_package"],
        "source_sandbox_execution_created": boundary["sandbox_execution_created"],
        "source_execution_allowed_in_source_package": boundary["execution_allowed_in_this_package"],
        "future_execution_requires_separate_boundary": boundary["future_execution_requires_separate_boundary"],
        "source_rollback_available": boundary["rollback_available"],
        "source_audit_recorded": boundary["audit_recorded"],
        "source_arbitration_rules_preserved": source_final["source_arbitration_rules_preserved"],
    }


def _validate_source(source: dict[str, Any], errors: list[str]) -> None:
    if source.get("source_validated") is not True:
        errors.append("source_validated_not_true")
    if source.get("source_boundary_index") != SOURCE_BOUNDARY_INDEX:
        errors.append("source_boundary_index_not_expected")
    if source.get("future_direct_command_allowed") is not True:
        errors.append("source_future_direct_command_allowed_not_true")
    if source.get("direct_command_scope") != "sandbox_only":
        errors.append("source_direct_command_scope_not_sandbox_only")
    if source.get("candidate_for_future_direct_command") != f"sandbox.arbitration.{source.get('source_final_action')}":
        errors.append("source_direct_command_not_from_final_action")
    if source.get("source_arbitration_rules_preserved") is not True:
        errors.append("source_arbitration_rules_preserved_not_true")
    for field in (
        "source_direct_command_created_in_source_package",
        "source_sandbox_execution_created",
        "source_execution_allowed_in_source_package",
    ):
        if source.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in (
        "future_execution_requires_separate_boundary",
        "source_rollback_available",
        "source_audit_recorded",
    ):
        if source.get(field) is not True:
            errors.append(f"{field}_not_true")


def _validate_direct_command(command: dict[str, Any], source: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "direct_command_created": True,
        "direct_command": source.get("candidate_for_future_direct_command"),
        "direct_command_source": "sandbox_candidate_ordering_arbitration_direct_command_approval_boundary",
        "direct_command_scope": "sandbox_only",
        "direct_command_reason": "arbitration_final_action_direct_command_boundary",
        "scenario_id": source.get("scenario_id"),
        "approved_purpose": source.get("approved_purpose"),
        "candidate_family": source.get("candidate_family"),
        "source_final_action": source.get("source_final_action"),
        "source_selected_action": source.get("source_selected_action"),
        "arbitration_rules_preserved": True,
        "sandbox_action_executed": False,
        "execution_result_created": False,
        "execution_allowed_in_this_package": False,
        "future_execution_requires_separate_boundary": True,
        "future_memory_write_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "rollback_available": True,
        "audit_recorded": True,
    }
    for field, value in expected.items():
        if command.get(field) != value:
            errors.append(f"sandbox_direct_command_{field}_not_expected")


def _validate_rollback(rollback: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "rollback_available": True,
        "direct_command_removed_on_rollback": True,
        "dirty_state_after_rollback": False,
        "persistent_update_performed": False,
    }
    for field, value in expected.items():
        if rollback.get(field) != value:
            errors.append(f"rollback_preview_{field}_not_expected")


def _validate_human_summary(human: dict[str, Any], errors: list[str]) -> None:
    for field in ("what_was_created", "what_changed", "what_is_blocked", "plain_result"):
        if not _non_empty_string(human.get(field)):
            errors.append(f"human_summary_{field}_empty")


def _validate_blocked_flags(blocked: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(flag for flag in BLOCKED_FLAGS if flag not in blocked)
    errors.extend(f"missing_blocked_flag:{flag}" for flag in missing)
    extra = sorted(flag for flag in blocked if flag not in BLOCKED_FLAGS)
    errors.extend(f"unexpected_blocked_flag:{flag}" for flag in extra)
    for flag in BLOCKED_FLAGS:
        if blocked.get(flag) is not False:
            errors.append(f"blocked_flags_{flag}_not_false")


def _invalid_records(first: dict[str, Any], second: dict[str, Any], third: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def mutate(source: dict[str, Any], label: str, path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(source)
        target: dict[str, Any] = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        record["direct_command_record_id"] = f"{record['direct_command_record_id']}_invalid_{label}"
        invalids.append(record)

    mutate(first, "bad_record_type", ("record_type",), "sandbox_arbitration_direct_command")
    mutate(first, "wrong_boundary_after", ("boundary_index_after",), BOUNDARY_INDEX_BEFORE)
    mutate(first, "source_not_validated", ("source_direct_command_approval_boundary", "source_validated"), False)
    mutate(first, "source_future_not_allowed", ("source_direct_command_approval_boundary", "future_direct_command_allowed"), False)
    mutate(first, "source_direct_command", ("source_direct_command_approval_boundary", "source_direct_command_created_in_source_package"), True)
    mutate(first, "source_rules_not_preserved", ("source_direct_command_approval_boundary", "source_arbitration_rules_preserved"), False)
    mutate(first, "direct_command_not_created", ("sandbox_direct_command", "direct_command_created"), False)
    mutate(first, "wrong_direct_command", ("sandbox_direct_command", "direct_command"), "sandbox.arbitration.wait")
    mutate(first, "wrong_scope", ("sandbox_direct_command", "direct_command_scope"), "production")
    mutate(first, "wrong_source", ("sandbox_direct_command", "direct_command_source"), "unapproved_boundary")
    mutate(first, "rules_not_preserved", ("sandbox_direct_command", "arbitration_rules_preserved"), False)
    mutate(first, "execution", ("sandbox_direct_command", "sandbox_action_executed"), True)
    mutate(first, "execution_result", ("sandbox_direct_command", "execution_result_created"), True)
    mutate(first, "execution_allowed", ("sandbox_direct_command", "execution_allowed_in_this_package"), True)
    mutate(first, "future_execution_boundary_missing", ("sandbox_direct_command", "future_execution_requires_separate_boundary"), False)
    mutate(first, "rollback_dirty", ("rollback_preview", "dirty_state_after_rollback"), True)
    mutate(first, "rollback_not_available", ("rollback_preview", "rollback_available"), False)
    mutate(second, "memory_write", ("blocked_flags", "memory_write"), True)
    mutate(second, "retention_write", ("blocked_flags", "retention_write"), True)
    mutate(second, "predictor_read", ("blocked_flags", "predictor_read_enabled"), True)
    mutate(second, "predictor_influence", ("blocked_flags", "predictor_influence_enabled"), True)
    mutate(second, "predictor_modified", ("blocked_flags", "predictor_modified"), True)
    mutate(second, "runtime_behavior", ("blocked_flags", "runtime_behavior_changed"), True)
    mutate(second, "direct_feed", ("blocked_flags", "direct_tendency_feed"), True)
    mutate(third, "proof_claim", ("blocked_flags", "proof_of_learning_claim"), True)
    mutate(third, "raw_sum", ("blocked_flags", "raw_weighted_sum_used"), True)
    mutate(third, "purpose_changed", ("blocked_flags", "purpose_changed_by_tendency"), True)
    mutate(third, "feedback_cross_purpose", ("blocked_flags", "feedback_cross_purpose_applied"), True)
    mutate(third, "empty_summary", ("human_summary", "plain_result"), "")
    return invalids


def _summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid = [result for result in validation_results if result["valid"]]
    return {
        "direct_command_result_count": len(validation_results),
        "valid_direct_command_count": len(valid),
        "invalid_direct_command_count": len(validation_results) - len(valid),
        "direct_command_created_count": sum(1 for result in valid if result["direct_command_created"]),
        "reach_front_item_direct_command_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.reach_front_item"
        ),
        "wait_or_observe_direct_command_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.wait_or_observe"
        ),
        "observe_or_alternative_probe_direct_command_count": sum(
            1 for result in valid if result["direct_command"] == "sandbox.arbitration.observe_or_alternative_probe"
        ),
        "sandbox_only_direct_command_count": sum(1 for result in valid if result["sandbox_only_direct_command"]),
        "arbitration_rules_preserved_count": sum(1 for result in valid if result["arbitration_rules_preserved"]),
        "execution_blocked_count": sum(1 for result in valid if result["execution_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid if result["memory_write_blocked"]),
        "predictor_use_blocked_count": sum(1 for result in valid if result["predictor_use_blocked"]),
        "direct_feed_blocked_count": sum(1 for result in valid if result["direct_feed_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid if result["proof_claim_blocked"]),
        "rollback_available_count": sum(1 for result in valid if result["rollback_available"]),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["direct_command_result_count"] == 32
        and summary["valid_direct_command_count"] == 3
        and summary["invalid_direct_command_count"] == 29
        and summary["direct_command_created_count"] == 3
        and summary["reach_front_item_direct_command_count"] == 1
        and summary["wait_or_observe_direct_command_count"] == 1
        and summary["observe_or_alternative_probe_direct_command_count"] == 1
        and summary["sandbox_only_direct_command_count"] == 3
        and summary["arbitration_rules_preserved_count"] == 3
        and summary["execution_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["predictor_use_blocked_count"] == 3
        and summary["direct_feed_blocked_count"] == 3
        and summary["proof_claim_blocked_count"] == 3
        and summary["rollback_available_count"] == 3
    )


def _as_dict(value: Any, errors: list[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{field}_missing_or_not_dict")
        return {}
    return value


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
