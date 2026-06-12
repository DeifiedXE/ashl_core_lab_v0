"""Check reviewed lesson sandbox application readiness without applying lessons."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .generic_lesson_evidence_pipeline_completion_bridge_minimal import (
    build_generic_lesson_evidence_pipeline_completion_bridge,
    validate_generic_lesson_evidence_pipeline_completion_bridge,
)


COMMAND = "run-reviewed-lesson-sandbox-application-readiness-minimal-check"
FLOW = "reviewed_lesson_sandbox_application_readiness_minimal_v0"
READINESS_ID = "reviewed_lesson_sandbox_application_readiness_demo_001"
READINESS_MODE = "sandbox_application_readiness_only"
READINESS_STATUS = "not_ready_missing_explicit_human_application_approval"
READY_AFTER_APPROVAL_STATUS = "ready_for_level1_sandbox_application_after_explicit_user_approval"
BOUNDARY_DOC = Path("docs/reviewed_lesson_application_boundary_reconciliation_v0.md")

REQUIRED_TOP_LEVEL = {
    "readiness_id",
    "readiness_mode",
    "source_evidence",
    "application_scope",
    "satisfied_requirements",
    "missing_requirements",
    "readiness_result",
    "human_summary",
    "blocked_flags",
}
REQUIRED_HUMAN_SUMMARY = {
    "what_was_checked",
    "what_is_ready",
    "what_is_missing",
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
SATISFIED_REQUIREMENTS = {
    "valid_generic_lesson_review_decision",
    "decision_accepted_for_preview",
    "valid_reviewed_lesson_trace_preview",
    "valid_reviewed_lesson_dry_run_correction",
    "valid_dry_run_correction_into_trial_trace",
    "valid_before_after_trial_contrast",
    "valid_lesson_effect_evidence_trace",
    "application_scope_defined",
    "rollback_path_defined",
    "audit_trace_required",
    "mentor_override_preserved",
    "memory_write_boundary_checked",
    "retention_write_boundary_checked",
    "predictor_mutation_boundary_checked",
    "runtime_behavior_boundary_checked",
}


def build_reviewed_lesson_sandbox_application_readiness(
    evidence_pipeline_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if evidence_pipeline_result is None:
        evidence_pipeline_result = build_generic_lesson_evidence_pipeline_completion_bridge()

    evidence_validation = validate_generic_lesson_evidence_pipeline_completion_bridge(evidence_pipeline_result)
    evidence_result = evidence_pipeline_result.get("lesson_effect_evidence_bridge_result", {})
    source_id = evidence_pipeline_result.get(
        "evidence_pipeline_bridge_id",
        "generic_lesson_evidence_pipeline_completion_bridge_demo_001",
    )
    if isinstance(source_id, str) and ":" in source_id:
        source_id = source_id.split(":", 1)[0]
    evidence_ready = (
        evidence_validation.get("valid") is True
        and evidence_result.get("lesson_effect_evidence_trace_created") is True
        and evidence_result.get("evidence_only") is True
    )

    return {
        "readiness_id": READINESS_ID,
        "readiness_mode": READINESS_MODE,
        "source_evidence": {
            "source_type": "generic_lesson_effect_evidence_trace",
            "source_bridge_id": source_id,
            "lesson_effect_evidence_trace_created": evidence_ready,
            "evidence_only": evidence_ready,
            "lesson_applied": False,
            "memory_write": False,
            "retention_write": False,
            "predictor_modified": False,
            "runtime_behavior_changed": False,
        },
        "application_scope": {
            "target_scope": "phase0_level1_sandbox_only",
            "target_level_id": "phase0_level1_first_contact_danger",
            "target_action_context": "check_before_retry_when_front_symbol_d",
            "production_scope": False,
            "runtime_global_scope": False,
            "persistent_policy_scope": False,
        },
        "satisfied_requirements": {field: True for field in sorted(SATISFIED_REQUIREMENTS)},
        "missing_requirements": {
            "explicit_human_application_approval": True,
            "sandbox_application_package_exists": False,
        },
        "readiness_result": {
            "readiness_status": READINESS_STATUS,
            "ready_for_application": False,
            "ready_for_sandbox_application_package": False,
            "allowed_to_apply_lesson": False,
            "allowed_to_write_memory": False,
            "allowed_to_write_retention": False,
            "allowed_to_mutate_predictor": False,
            "allowed_to_change_runtime_behavior": False,
            "allowed_to_create_final_action": False,
        },
        "human_summary": {
            "what_was_checked": (
                "The reviewed lesson evidence trace was checked against the sandbox application boundary."
            ),
            "what_is_ready": (
                "The evidence path, sandbox scope, rollback/audit requirements, mentor override, "
                "and mutation/write boundaries are represented."
            ),
            "what_is_missing": "Explicit human application approval is still missing.",
            "plain_result": (
                "The reviewed lesson is not ready to be applied; it can only proceed after a separate "
                "explicit application approval."
            ),
        },
        "blocked_flags": {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)},
    }


def validate_reviewed_lesson_sandbox_application_readiness(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_top = REQUIRED_TOP_LEVEL - set(record)
    for field in sorted(missing_top):
        errors.append(f"missing_top_level:{field}")
    if record.get("readiness_mode") != READINESS_MODE:
        errors.append("readiness_mode_not_sandbox_application_readiness_only")

    source = _section(record, "source_evidence", errors)
    for field in (
        "lesson_effect_evidence_trace_created",
        "evidence_only",
    ):
        _require_true(source, field, errors)
    for field in (
        "lesson_applied",
        "memory_write",
        "retention_write",
        "predictor_modified",
        "runtime_behavior_changed",
    ):
        _require_false(source, field, errors)

    scope = _section(record, "application_scope", errors)
    if scope.get("target_scope") != "phase0_level1_sandbox_only":
        errors.append("target_scope_not_phase0_level1_sandbox_only")
    if scope.get("target_level_id") != "phase0_level1_first_contact_danger":
        errors.append("target_level_id_not_phase0_level1_first_contact_danger")
    for field in ("production_scope", "runtime_global_scope", "persistent_policy_scope"):
        _require_false(scope, field, errors)

    satisfied = _section(record, "satisfied_requirements", errors)
    for field in sorted(SATISFIED_REQUIREMENTS):
        _require_true(satisfied, field, errors)

    missing = _section(record, "missing_requirements", errors)
    result = _section(record, "readiness_result", errors)
    status = result.get("readiness_status")
    if status == READINESS_STATUS:
        _require_true(missing, "explicit_human_application_approval", errors)
        _require_false(missing, "sandbox_application_package_exists", errors)
        for field in (
            "ready_for_application",
            "ready_for_sandbox_application_package",
            "allowed_to_apply_lesson",
        ):
            _require_false(result, field, errors)
    elif status == READY_AFTER_APPROVAL_STATUS:
        _require_false(missing, "explicit_human_application_approval", errors)
        _require_true(missing, "sandbox_application_package_exists", errors)
        for field in (
            "ready_for_application",
            "ready_for_sandbox_application_package",
            "allowed_to_apply_lesson",
        ):
            _require_true(result, field, errors)
    else:
        errors.append("readiness_status_not_recognized")

    for field in (
        "allowed_to_write_memory",
        "allowed_to_write_retention",
        "allowed_to_mutate_predictor",
        "allowed_to_change_runtime_behavior",
        "allowed_to_create_final_action",
    ):
        _require_false(result, field, errors)

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
        "readiness_id": record.get("readiness_id"),
        "valid": not errors,
        "error_codes": errors,
        "evidence_trace_ready": source.get("lesson_effect_evidence_trace_created") is True,
        "application_scope_defined": satisfied.get("application_scope_defined") is True,
        "rollback_path_defined": satisfied.get("rollback_path_defined") is True,
        "audit_trace_required": satisfied.get("audit_trace_required") is True,
        "mentor_override_preserved": satisfied.get("mentor_override_preserved") is True,
        "missing_explicit_human_application_approval": (
            missing.get("explicit_human_application_approval") is True
        ),
        "not_ready_status": result.get("readiness_status") == READINESS_STATUS,
        "ready_for_application_blocked": result.get("ready_for_application") is False,
        "sandbox_application_package_ready_blocked": (
            result.get("ready_for_sandbox_application_package") is False
        ),
        "lesson_application_blocked": result.get("allowed_to_apply_lesson") is False,
        "memory_write_blocked": result.get("allowed_to_write_memory") is False,
        "retention_write_blocked": result.get("allowed_to_write_retention") is False,
        "predictor_mutation_blocked": result.get("allowed_to_mutate_predictor") is False,
        "runtime_behavior_change_blocked": (
            result.get("allowed_to_change_runtime_behavior") is False
        ),
        "final_action_blocked": result.get("allowed_to_create_final_action") is False,
        "proof_of_learning_claim_blocked": (
            blocked_flags.get("proof_of_learning_claim") is False
        ),
    }


def run_reviewed_lesson_sandbox_application_readiness_minimal_check() -> dict[str, Any]:
    valid_record = build_reviewed_lesson_sandbox_application_readiness()
    records = [valid_record] + _build_invalid_records(valid_record)
    validation_results = [
        validate_reviewed_lesson_sandbox_application_readiness(record) for record in records
    ]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_reviewed_lesson_sandbox_application_readiness_minimal_checks_passed"] else "failed",
        "sandbox_application_readiness_results": records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": {
            "readiness_only": True,
            "boundary_doc_reused": BOUNDARY_DOC.exists(),
            "lesson_application_added": False,
            "sandbox_lesson_application_added": False,
            "runtime_lesson_application_added": False,
            "explicit_application_approval_added": False,
            "memory_write_added": False,
            "retention_write_added": False,
            "predictor_mutation_added": False,
            "runtime_behavior_change_added": False,
            "final_action_created": False,
            "proof_of_learning_claimed": False,
        },
        "notes": [
            "Readiness is not application.",
            "Explicit human application approval remains missing.",
            "Boundary Index remains 2026-06-09-b60.",
        ],
    }


def _build_invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalid: list[dict[str, Any]] = []

    invalid.append(_mutated(valid_record, ["readiness_mode"], "bad_mode"))
    for field in ("lesson_effect_evidence_trace_created", "evidence_only"):
        invalid.append(_mutated(valid_record, ["source_evidence", field], False))
    for field in (
        "lesson_applied",
        "memory_write",
        "retention_write",
        "predictor_modified",
        "runtime_behavior_changed",
    ):
        invalid.append(_mutated(valid_record, ["source_evidence", field], True))

    invalid.append(_mutated(valid_record, ["application_scope", "target_scope"], "production_scope"))
    for field in ("production_scope", "runtime_global_scope", "persistent_policy_scope"):
        invalid.append(_mutated(valid_record, ["application_scope", field], True))

    for field in sorted(SATISFIED_REQUIREMENTS):
        invalid.append(_mutated(valid_record, ["satisfied_requirements", field], False))

    invalid.append(_mutated(valid_record, ["missing_requirements", "explicit_human_application_approval"], False))
    invalid.append(_mutated(valid_record, ["missing_requirements", "sandbox_application_package_exists"], True))

    for field in (
        "ready_for_application",
        "ready_for_sandbox_application_package",
        "allowed_to_apply_lesson",
        "allowed_to_write_memory",
        "allowed_to_write_retention",
        "allowed_to_mutate_predictor",
        "allowed_to_change_runtime_behavior",
        "allowed_to_create_final_action",
    ):
        invalid.append(_mutated(valid_record, ["readiness_result", field], True))

    for field in sorted(REQUIRED_HUMAN_SUMMARY):
        invalid.append(_mutated(valid_record, ["human_summary", field], ""))

    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        invalid.append(_mutated(valid_record, ["blocked_flags", field], True))

    return invalid


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [item for item in validation_results if item["valid"]]
    summary = {
        "sandbox_application_readiness_result_count": len(validation_results),
        "valid_sandbox_application_readiness_count": len(valid),
        "invalid_sandbox_application_readiness_count": len(validation_results) - len(valid),
    }
    for key in (
        "evidence_trace_ready",
        "application_scope_defined",
        "rollback_path_defined",
        "audit_trace_required",
        "mentor_override_preserved",
        "missing_explicit_human_application_approval",
        "not_ready_status",
        "ready_for_application_blocked",
        "sandbox_application_package_ready_blocked",
        "lesson_application_blocked",
        "memory_write_blocked",
        "retention_write_blocked",
        "predictor_mutation_blocked",
        "runtime_behavior_change_blocked",
        "final_action_blocked",
        "proof_of_learning_claim_blocked",
    ):
        summary[f"{key}_count"] = sum(1 for item in valid if item.get(key) is True)

    summary["all_reviewed_lesson_sandbox_application_readiness_minimal_checks_passed"] = (
        summary["valid_sandbox_application_readiness_count"] == 1
        and summary["invalid_sandbox_application_readiness_count"] >= 1
        and summary["evidence_trace_ready_count"] == 1
        and summary["application_scope_defined_count"] == 1
        and summary["rollback_path_defined_count"] == 1
        and summary["audit_trace_required_count"] == 1
        and summary["mentor_override_preserved_count"] == 1
        and summary["missing_explicit_human_application_approval_count"] == 1
        and summary["not_ready_status_count"] == 1
        and summary["ready_for_application_blocked_count"] == 1
        and summary["lesson_application_blocked_count"] == 1
    )
    return summary


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

    print(json.dumps(run_reviewed_lesson_sandbox_application_readiness_minimal_check(), ensure_ascii=False, indent=2))
