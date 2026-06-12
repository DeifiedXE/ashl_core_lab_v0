"""Record explicit Level 1 sandbox application approval without applying a lesson."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .reviewed_lesson_sandbox_application_readiness_minimal import (
    build_reviewed_lesson_sandbox_application_readiness,
    validate_reviewed_lesson_sandbox_application_readiness,
)


COMMAND = "run-level1-explicit-lesson-application-approval-minimal-check"
FLOW = "level1_explicit_lesson_application_approval_minimal_v0"
APPROVAL_ID = "level1_explicit_lesson_application_approval_demo_001"
APPROVAL_MODE = "explicit_human_application_approval_only"
READINESS_STATUS = "not_ready_missing_explicit_human_application_approval"
APPROVED = "approved_for_future_level1_sandbox_application_package"
REJECTED = "rejected_for_application"
NEEDS_MORE = "needs_more_evidence_before_application"
ALLOWED_DECISIONS = {APPROVED, REJECTED, NEEDS_MORE}

REQUIRED_TOP_LEVEL = {
    "approval_id",
    "approval_mode",
    "source_readiness",
    "approval_scope",
    "human_application_approval",
    "approval_result",
    "allowed_next_layer",
    "human_summary",
    "blocked_flags",
}
REQUIRED_HUMAN_SUMMARY = {
    "what_was_approved",
    "approval_scope",
    "what_is_still_blocked",
    "plain_result",
}
REQUIRED_BLOCKED_FLAGS = {
    "lesson_applied",
    "sandbox_lesson_applied",
    "runtime_lesson_applied",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_modified",
    "runtime_behavior_changed",
    "production_action_selection",
    "runtime_action_selection",
    "selected_action_created",
    "final_action_created",
    "direct_action_command",
    "real_navigation_changed",
    "ui_behavior_changed",
    "persistent_policy_written",
    "general_behavior_changed",
    "proof_of_learning_claim",
}
SCOPE_FALSE_FIELDS = {
    "production_scope",
    "runtime_global_scope",
    "persistent_policy_scope",
    "memory_write_scope",
    "retention_write_scope",
    "predictor_mutation_scope",
}
RESULT_FALSE_FIELDS = {
    "lesson_applied",
    "sandbox_lesson_applied",
    "runtime_lesson_applied",
    "memory_write",
    "retention_write",
    "predictor_modified",
    "runtime_behavior_changed",
}
NEXT_LAYER_FIELDS = {
    "may_enter_level1_sandbox_lesson_application_package",
    "may_apply_lesson_in_this_package",
    "may_apply_runtime_lesson",
    "may_write_memory",
    "may_write_retention",
    "may_mutate_predictor",
    "may_change_runtime_behavior",
    "may_create_final_action",
}


def build_level1_explicit_lesson_application_approval(
    readiness_record: dict[str, Any] | None = None,
    approval_decision: str = NEEDS_MORE,
    approval_text: str | None = None,
    approval_source: str = "none",
) -> dict[str, Any]:
    if readiness_record is None:
        readiness_record = build_reviewed_lesson_sandbox_application_readiness()

    readiness_validation = validate_reviewed_lesson_sandbox_application_readiness(readiness_record)
    readiness_source = readiness_record.get("readiness_result", {})
    readiness_scope = readiness_record.get("application_scope", {})
    source_evidence = readiness_record.get("source_evidence", {})

    explicit_user_statement_present = (
        approval_decision == APPROVED
        and approval_source == "explicit_user_statement"
        and isinstance(approval_text, str)
        and bool(approval_text.strip())
    )
    approved = approval_decision == APPROVED and explicit_user_statement_present
    rejected = approval_decision == REJECTED
    needs_more = approval_decision == NEEDS_MORE
    valid_readiness = readiness_validation.get("valid") is True

    return {
        "approval_id": _approval_id(approval_decision),
        "approval_mode": APPROVAL_MODE,
        "source_readiness": {
            "source_readiness_id": readiness_record.get(
                "readiness_id",
                "reviewed_lesson_sandbox_application_readiness_demo_001",
            ),
            "readiness_status": readiness_source.get("readiness_status", READINESS_STATUS),
            "target_scope": readiness_scope.get("target_scope", "phase0_level1_sandbox_only"),
            "lesson_effect_evidence_trace_created": (
                valid_readiness
                and source_evidence.get("lesson_effect_evidence_trace_created") is True
            ),
            "ready_for_application_before_approval": (
                readiness_source.get("ready_for_application") is True
            ),
            "allowed_to_apply_lesson_before_approval": (
                readiness_source.get("allowed_to_apply_lesson") is True
            ),
        },
        "approval_scope": {
            "approved_target_scope": "phase0_level1_sandbox_only",
            "target_level_id": "phase0_level1_first_contact_danger",
            "target_action_context": "check_before_retry_when_front_symbol_d",
            "sandbox_only": True,
            "production_scope": False,
            "runtime_global_scope": False,
            "persistent_policy_scope": False,
            "memory_write_scope": False,
            "retention_write_scope": False,
            "predictor_mutation_scope": False,
        },
        "human_application_approval": {
            "approval_decision": approval_decision,
            "approver": "human_mentor",
            "approval_source": approval_source,
            "approval_text": approval_text or "",
            "approver_role": "project_owner" if explicit_user_statement_present else "none",
            "approval_actor": "user" if explicit_user_statement_present else "none",
            "approval_reason": _approval_reason(approval_decision),
            "approval_is_explicit": approved,
            "approval_is_for_future_package_only": approved,
            "approval_applies_lesson_now": False,
            "codex_self_approval_allowed": False,
            "ai_self_approval_allowed": False,
            "demo_fixture_is_real_approval": False,
            "implicit_approval_allowed": False,
            "approval_inferred_from_completed_tests": False,
            "approval_inferred_from_readiness": False,
            "approval_inferred_from_marker_text": False,
            "test_user_statement_fixture": explicit_user_statement_present,
        },
        "approval_result": {
            "explicit_human_application_approval_present": approved,
            "explicit_user_statement_present": explicit_user_statement_present,
            "approval_source_valid": explicit_user_statement_present,
            "approval_actor_valid": explicit_user_statement_present,
            "demo_fixture_rejected_as_real_approval": True,
            "codex_self_approval_rejected": True,
            "ai_self_approval_rejected": True,
            "implicit_approval_rejected": True,
            "approved_for_future_level1_sandbox_application_package": approved,
            "rejected_for_application": rejected,
            "needs_more_evidence_before_application": needs_more,
            "lesson_applied": False,
            "sandbox_lesson_applied": False,
            "runtime_lesson_applied": False,
            "memory_write": False,
            "retention_write": False,
            "predictor_modified": False,
            "runtime_behavior_changed": False,
        },
        "allowed_next_layer": {
            "may_enter_level1_sandbox_lesson_application_package": approved,
            "may_apply_lesson_in_this_package": False,
            "may_apply_runtime_lesson": False,
            "may_write_memory": False,
            "may_write_retention": False,
            "may_mutate_predictor": False,
            "may_change_runtime_behavior": False,
            "may_create_final_action": False,
        },
        "human_summary": {
            "what_was_approved": _summary_what_was_approved(approval_decision),
            "approval_scope": "Approval is limited to the Phase0 Level 1 sandbox scope.",
            "what_is_still_blocked": (
                "This package does not apply the lesson, write memory, write retention, "
                "mutate predictors, or change runtime behavior."
            ),
            "plain_result": _plain_result(approval_decision),
        },
        "blocked_flags": {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)},
    }


def validate_level1_explicit_lesson_application_approval(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_top = REQUIRED_TOP_LEVEL - set(record)
    for field in sorted(missing_top):
        errors.append(f"missing_top_level:{field}")
    if record.get("approval_mode") != APPROVAL_MODE:
        errors.append("approval_mode_not_explicit_human_application_approval_only")

    source = _section(record, "source_readiness", errors)
    if source.get("readiness_status") != READINESS_STATUS:
        errors.append("source_readiness_status_not_missing_explicit_human_application_approval")
    if source.get("target_scope") != "phase0_level1_sandbox_only":
        errors.append("source_target_scope_not_phase0_level1_sandbox_only")
    _require_true(source, "lesson_effect_evidence_trace_created", errors)
    _require_false(source, "ready_for_application_before_approval", errors)
    _require_false(source, "allowed_to_apply_lesson_before_approval", errors)

    scope = _section(record, "approval_scope", errors)
    if scope.get("approved_target_scope") != "phase0_level1_sandbox_only":
        errors.append("approved_target_scope_not_phase0_level1_sandbox_only")
    if scope.get("target_level_id") != "phase0_level1_first_contact_danger":
        errors.append("target_level_id_not_phase0_level1_first_contact_danger")
    _require_true(scope, "sandbox_only", errors)
    for field in sorted(SCOPE_FALSE_FIELDS):
        _require_false(scope, field, errors)

    approval = _section(record, "human_application_approval", errors)
    decision = approval.get("approval_decision")
    if decision not in ALLOWED_DECISIONS:
        errors.append("unknown_approval_decision")
    _require_non_empty(approval, "approver", errors)
    _require_non_empty(approval, "approval_reason", errors)
    if approval.get("approval_is_explicit") is not (decision == APPROVED):
        errors.append("approval_is_explicit_mismatch")
    if decision == APPROVED:
        _require_true(approval, "approval_is_for_future_package_only", errors)
        if approval.get("approval_source") != "explicit_user_statement":
            errors.append("approval_source_not_explicit_user_statement")
        _require_non_empty(approval, "approval_text", errors)
        if approval.get("approval_actor") != "user":
            errors.append("approval_actor_not_user")
        if approval.get("approver_role") != "project_owner":
            errors.append("approver_role_not_project_owner")
    _require_false(approval, "approval_applies_lesson_now", errors)
    for field in (
        "codex_self_approval_allowed",
        "ai_self_approval_allowed",
        "demo_fixture_is_real_approval",
        "implicit_approval_allowed",
        "approval_inferred_from_completed_tests",
        "approval_inferred_from_readiness",
        "approval_inferred_from_marker_text",
    ):
        _require_false(approval, field, errors)
    if approval.get("approval_text") == "蝯血?":
        errors.append("marker_text_is_not_application_approval")

    result = _section(record, "approval_result", errors)
    next_layer = _section(record, "allowed_next_layer", errors)
    _validate_decision_result(decision, approval, result, next_layer, errors)

    human_summary = _section(record, "human_summary", errors)
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        _require_non_empty(human_summary, field, errors)

    blocked_flags = _section(record, "blocked_flags", errors)
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "approval_id": record.get("approval_id"),
        "valid": not errors,
        "error_codes": errors,
        "approval_decision": decision,
        "approved_for_future_package": decision == APPROVED,
        "rejected_for_application": decision == REJECTED,
        "needs_more_evidence_before_application": decision == NEEDS_MORE,
        "explicit_human_application_approval_present": (
            result.get("explicit_human_application_approval_present") is True
        ),
        "may_enter_level1_sandbox_lesson_application_package": (
            next_layer.get("may_enter_level1_sandbox_lesson_application_package") is True
        ),
        "approval_scope_sandbox_only": scope.get("sandbox_only") is True,
        "approval_future_package_only": (
            approval.get("approval_is_for_future_package_only") is True
        ),
        "explicit_user_statement_present": result.get("explicit_user_statement_present") is True,
        "approval_source_valid": result.get("approval_source_valid") is True,
        "approval_actor_valid": result.get("approval_actor_valid") is True,
        "demo_fixture_rejected_as_real_approval": (
            result.get("demo_fixture_rejected_as_real_approval") is True
        ),
        "codex_self_approval_rejected": result.get("codex_self_approval_rejected") is True,
        "ai_self_approval_rejected": result.get("ai_self_approval_rejected") is True,
        "implicit_approval_rejected": result.get("implicit_approval_rejected") is True,
        "lesson_application_blocked": result.get("lesson_applied") is False,
        "sandbox_lesson_application_blocked": result.get("sandbox_lesson_applied") is False,
        "runtime_lesson_application_blocked": result.get("runtime_lesson_applied") is False,
        "memory_write_blocked": result.get("memory_write") is False,
        "retention_write_blocked": result.get("retention_write") is False,
        "predictor_mutation_blocked": result.get("predictor_modified") is False,
        "runtime_behavior_change_blocked": result.get("runtime_behavior_changed") is False,
        "final_action_blocked": next_layer.get("may_create_final_action") is False,
        "proof_of_learning_claim_blocked": (
            blocked_flags.get("proof_of_learning_claim") is False
        ),
    }


def run_level1_explicit_lesson_application_approval_minimal_check() -> dict[str, Any]:
    valid_records = [
        build_level1_explicit_lesson_application_approval(
            approval_decision=APPROVED,
            approval_source="explicit_user_statement",
            approval_text=(
                "I explicitly approve a future Phase0 Level 1 sandbox-only lesson "
                "application package."
            ),
        ),
        build_level1_explicit_lesson_application_approval(approval_decision=REJECTED),
        build_level1_explicit_lesson_application_approval(approval_decision=NEEDS_MORE),
    ]
    records = valid_records + _build_invalid_records(valid_records[0], valid_records[1], valid_records[2])
    validation_results = [
        validate_level1_explicit_lesson_application_approval(record) for record in records
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_level1_explicit_lesson_application_approval_minimal_checks_passed"] else "failed",
        "explicit_approval_results": records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "approval_only": True,
            "readiness_reused": True,
            "lesson_application_added": False,
            "sandbox_lesson_application_added": False,
            "runtime_lesson_application_added": False,
            "memory_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "runtime_behavior_change_added": False,
            "final_action_created": False,
            "direct_action_command_created": False,
            "proof_of_learning_claimed": False,
        },
        "notes": [
            "Human approval may authorize a future sandbox application package, but approval is not application.",
            "Boundary Index remains 2026-06-09-b60.",
        ],
    }


def _validate_decision_result(
    decision: str | None,
    approval: dict[str, Any],
    result: dict[str, Any],
    next_layer: dict[str, Any],
    errors: list[str],
) -> None:
    explicit_user_statement_present = (
        decision == APPROVED
        and approval.get("approval_source") == "explicit_user_statement"
        and isinstance(approval.get("approval_text"), str)
        and bool(approval.get("approval_text", "").strip())
        and approval.get("approval_actor") == "user"
        and approval.get("approver_role") == "project_owner"
        and approval.get("codex_self_approval_allowed") is False
        and approval.get("ai_self_approval_allowed") is False
        and approval.get("demo_fixture_is_real_approval") is False
        and approval.get("implicit_approval_allowed") is False
        and approval.get("approval_inferred_from_completed_tests") is False
        and approval.get("approval_inferred_from_readiness") is False
        and approval.get("approval_inferred_from_marker_text") is False
        and approval.get("approval_text") != "蝯血?"
    )
    approved = decision == APPROVED and explicit_user_statement_present
    rejected = decision == REJECTED
    needs_more = decision == NEEDS_MORE
    expected_result = {
        "explicit_human_application_approval_present": approved,
        "explicit_user_statement_present": explicit_user_statement_present,
        "approval_source_valid": explicit_user_statement_present,
        "approval_actor_valid": explicit_user_statement_present,
        "demo_fixture_rejected_as_real_approval": True,
        "codex_self_approval_rejected": True,
        "ai_self_approval_rejected": True,
        "implicit_approval_rejected": True,
        "approved_for_future_level1_sandbox_application_package": approved,
        "rejected_for_application": rejected,
        "needs_more_evidence_before_application": needs_more,
    }
    for field, expected in expected_result.items():
        if result.get(field) is not expected:
            errors.append(f"{field}_decision_mismatch")
    for field in sorted(RESULT_FALSE_FIELDS):
        _require_false(result, field, errors)

    expected_next = {
        "may_enter_level1_sandbox_lesson_application_package": approved,
        "may_apply_lesson_in_this_package": False,
        "may_apply_runtime_lesson": False,
        "may_write_memory": False,
        "may_write_retention": False,
        "may_mutate_predictor": False,
        "may_change_runtime_behavior": False,
        "may_create_final_action": False,
    }
    for field, expected in expected_next.items():
        if next_layer.get(field) is not expected:
            errors.append(f"{field}_decision_mismatch")


def _build_invalid_records(
    approved_record: dict[str, Any],
    rejected_record: dict[str, Any],
    needs_more_record: dict[str, Any],
) -> list[dict[str, Any]]:
    invalid: list[dict[str, Any]] = []
    invalid.append(_mutated(approved_record, ["approval_mode"], "bad_mode"))
    invalid.append(_mutated(approved_record, ["source_readiness", "readiness_status"], "ready"))
    invalid.append(_mutated(approved_record, ["source_readiness", "ready_for_application_before_approval"], True))
    invalid.append(_mutated(approved_record, ["source_readiness", "allowed_to_apply_lesson_before_approval"], True))
    invalid.append(_mutated(approved_record, ["approval_scope", "approved_target_scope"], "runtime_global"))
    invalid.append(_mutated(approved_record, ["approval_scope", "sandbox_only"], False))
    for field in sorted(SCOPE_FALSE_FIELDS):
        invalid.append(_mutated(approved_record, ["approval_scope", field], True))
    invalid.append(_mutated(approved_record, ["human_application_approval", "approval_decision"], "apply_now"))
    invalid.append(_mutated(approved_record, ["human_application_approval", "approval_source"], "test_fixture"))
    invalid.append(_mutated(approved_record, ["human_application_approval", "approval_text"], ""))
    invalid.append(_mutated(approved_record, ["human_application_approval", "approval_actor"], "codex"))
    invalid.append(_mutated(approved_record, ["human_application_approval", "approver_role"], "assistant"))
    invalid.append(_mutated(approved_record, ["human_application_approval", "approval_is_explicit"], False))
    invalid.append(_mutated(approved_record, ["human_application_approval", "approval_is_for_future_package_only"], False))
    invalid.append(_mutated(approved_record, ["human_application_approval", "approval_applies_lesson_now"], True))
    invalid.append(_mutated(approved_record, ["human_application_approval", "codex_self_approval_allowed"], True))
    invalid.append(_mutated(approved_record, ["human_application_approval", "ai_self_approval_allowed"], True))
    invalid.append(_mutated(approved_record, ["human_application_approval", "demo_fixture_is_real_approval"], True))
    invalid.append(_mutated(approved_record, ["human_application_approval", "implicit_approval_allowed"], True))
    invalid.append(_mutated(approved_record, ["human_application_approval", "approval_inferred_from_completed_tests"], True))
    invalid.append(_mutated(approved_record, ["human_application_approval", "approval_inferred_from_readiness"], True))
    invalid.append(_mutated(approved_record, ["human_application_approval", "approval_inferred_from_marker_text"], True))
    invalid.append(_mutated(approved_record, ["human_application_approval", "approval_text"], "蝯血?"))
    invalid.append(
        _mutated(
            approved_record,
            ["allowed_next_layer", "may_enter_level1_sandbox_lesson_application_package"],
            False,
        )
    )
    for field in (
        "may_apply_lesson_in_this_package",
        "may_write_memory",
        "may_write_retention",
        "may_mutate_predictor",
        "may_change_runtime_behavior",
    ):
        invalid.append(_mutated(approved_record, ["allowed_next_layer", field], True))
    invalid.append(
        _mutated(
            rejected_record,
            ["allowed_next_layer", "may_enter_level1_sandbox_lesson_application_package"],
            True,
        )
    )
    invalid.append(
        _mutated(
            needs_more_record,
            ["allowed_next_layer", "may_enter_level1_sandbox_lesson_application_package"],
            True,
        )
    )
    invalid.append(_mutated(approved_record, ["human_application_approval", "approver"], ""))
    invalid.append(_mutated(approved_record, ["human_application_approval", "approval_reason"], ""))
    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        invalid.append(_mutated(approved_record, ["human_summary", field], ""))
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid.append(_mutated(approved_record, ["blocked_flags", field], True))
    return invalid


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [item for item in validation_results if item["valid"]]
    summary = {
        "explicit_approval_result_count": len(validation_results),
        "valid_explicit_approval_result_count": len(valid),
        "invalid_explicit_approval_result_count": len(validation_results) - len(valid),
    }
    for key in (
        "approved_for_future_package",
        "rejected_for_application",
        "needs_more_evidence_before_application",
        "explicit_human_application_approval_present",
        "explicit_user_statement_present",
        "approval_source_valid",
        "approval_actor_valid",
        "demo_fixture_rejected_as_real_approval",
        "codex_self_approval_rejected",
        "ai_self_approval_rejected",
        "implicit_approval_rejected",
        "may_enter_level1_sandbox_lesson_application_package",
        "approval_scope_sandbox_only",
        "approval_future_package_only",
        "lesson_application_blocked",
        "sandbox_lesson_application_blocked",
        "runtime_lesson_application_blocked",
        "memory_write_blocked",
        "retention_write_blocked",
        "predictor_mutation_blocked",
        "runtime_behavior_change_blocked",
        "final_action_blocked",
        "proof_of_learning_claim_blocked",
    ):
        summary[f"{key}_count"] = sum(1 for item in valid if item.get(key) is True)

    summary["all_level1_explicit_lesson_application_approval_minimal_checks_passed"] = (
        summary["valid_explicit_approval_result_count"] == 3
        and summary["invalid_explicit_approval_result_count"] >= 1
        and summary["approved_for_future_package_count"] == 1
        and summary["rejected_for_application_count"] == 1
        and summary["needs_more_evidence_before_application_count"] == 1
        and summary["explicit_human_application_approval_present_count"] == 1
        and summary["explicit_user_statement_present_count"] == 1
        and summary["approval_source_valid_count"] == 1
        and summary["approval_actor_valid_count"] == 1
        and summary["demo_fixture_rejected_as_real_approval_count"] == 3
        and summary["codex_self_approval_rejected_count"] == 3
        and summary["ai_self_approval_rejected_count"] == 3
        and summary["implicit_approval_rejected_count"] == 3
        and summary["may_enter_level1_sandbox_lesson_application_package_count"] == 1
        and summary["lesson_application_blocked_count"] == 3
        and summary["memory_write_blocked_count"] == 3
        and summary["runtime_behavior_change_blocked_count"] == 3
    )
    return summary


def _approval_id(decision: str) -> str:
    suffix = {
        APPROVED: "approved",
        REJECTED: "rejected",
        NEEDS_MORE: "needs_more_evidence",
    }.get(decision, "unknown")
    return f"{APPROVAL_ID}:{suffix}"


def _approval_reason(decision: str) -> str:
    if decision == REJECTED:
        return "The candidate should not proceed to a future Level 1 sandbox application package."
    if decision == NEEDS_MORE:
        return "More evidence is required before any future Level 1 sandbox application package."
    return (
        "The evidence path and boundaries are ready to attempt a future Level 1 "
        "sandbox-only lesson application package."
    )


def _summary_what_was_approved(decision: str) -> str:
    if decision == REJECTED:
        return "Human review rejected application for this candidate."
    if decision == NEEDS_MORE:
        return "Human review requested more evidence before application."
    return "Human approval was recorded for a future Level 1 sandbox-only lesson application package."


def _plain_result(decision: str) -> str:
    if decision == REJECTED:
        return "The reviewed lesson cannot proceed to a sandbox application package."
    if decision == NEEDS_MORE:
        return "The reviewed lesson needs more evidence before any sandbox application package."
    return "Explicit approval now exists for a future sandbox application package, but no lesson has been applied."


def _section(record: dict[str, Any], name: str, errors: list[str]) -> dict[str, Any]:
    value = record.get(name)
    if not isinstance(value, dict):
        errors.append(f"{name}_not_dict")
        return {}
    return value


def _require_true(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) is not True:
        errors.append(f"{field}_not_true")


def _require_false(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if section.get(field) not in {False, 0}:
        errors.append(f"{field}_not_false")


def _require_non_empty(section: dict[str, Any], field: str, errors: list[str]) -> None:
    if not isinstance(section.get(field), str) or not section.get(field).strip():
        errors.append(f"{field}_empty")


def _mutated(record: dict[str, Any], path: list[str], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: dict[str, Any] = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(run_level1_explicit_lesson_application_approval_minimal_check(), ensure_ascii=False, indent=2))
