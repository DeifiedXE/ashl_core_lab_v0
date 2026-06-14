"""Design-only contract for a future memory admission package."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS, REPEATED_KEY
from .memory_readiness_design_for_approved_bucket_lesson_minimal import (
    BOUNDARY_VERSION,
    build_memory_readiness_design_for_approved_bucket_lesson,
    validate_memory_readiness_design_for_approved_bucket_lesson,
)


COMMAND = "run-memory-admission-package-design-minimal-check"
FLOW = "memory_admission_package_design_minimal_v0"
PACKAGE_ID = "PKG-Phase0-Memory-Admission-Package-Design-Minimal-v0"
REQUIRED_FUTURE_INPUTS = (
    "approved_human_interpreted_bucket_derived_lesson_candidate",
    "memory_readiness_design_record",
    "explicit_human_memory_admission_approval",
    "target_memory_layer_selection_record",
    "retention_and_rollback_rule_record",
    "cross_session_influence_rebuild_rule_record",
    "runtime_influence_boundary_record",
    "predictor_influence_boundary_record",
    "audit_and_revocation_path_record",
)
DISALLOWED_CURRENT_TARGET_LAYERS = (
    "core_memory",
    "long_term_memory",
    "archive_memory",
    "runtime_policy",
    "predictor_parameter",
    "production_rule",
)
FALSE_PERMISSION_FIELDS = (
    "memory_admission_allowed_now",
    "memory_write_allowed",
    "retained_jsonl_write_allowed",
    "retention_write_allowed",
    "runtime_influence_allowed",
    "predictor_influence_allowed",
    "predictor_mutation_allowed",
    "production_behavior_change_allowed",
    "selected_action_allowed",
    "final_action_allowed",
    "proof_of_learning_claim_allowed",
)


def build_memory_admission_package_design(
    memory_readiness_design: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        deepcopy(memory_readiness_design)
        if memory_readiness_design is not None
        else build_memory_readiness_design_for_approved_bucket_lesson()
    )
    source_validation = validate_memory_readiness_design_for_approved_bucket_lesson(source)
    if not source_validation["valid"]:
        raise ValueError("invalid_memory_readiness_design_source")
    if source.get("source_review_decision") != "approved_for_future_memory_readiness_design_only":
        raise ValueError("source_review_decision_not_approved")
    return {
        "record_type": "memory_admission_package_design",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "source_record_type": source.get("record_type"),
        "source_lesson_name": source.get("lesson_name"),
        "source_repeated_key": source.get("repeated_key"),
        "source_memory_readiness_status": source.get("readiness_design_status"),
        "source_review_decision": source.get("source_review_decision"),
        "design_status": "future_memory_admission_package_design_recorded",
        "package_design_only": True,
        "memory_admission_performed": False,
        "memory_write_performed": False,
        "future_package_purpose": (
            "evaluate_whether_approved_bucket_derived_lesson_can_be_admitted_as_reviewed_lesson_memory_candidate"
        ),
        "allowed_future_target_forms": ["reviewed_lesson_memory_candidate"],
        "disallowed_current_target_layers": list(DISALLOWED_CURRENT_TARGET_LAYERS),
        "required_future_inputs": list(REQUIRED_FUTURE_INPUTS),
        "required_future_approval": {
            "approval_source": "explicit_user_statement",
            "approval_actor": "user",
            "approver_role": "project_owner",
            "approval_text_required": True,
            "approval_purpose": "future_memory_admission_only",
            "approval_does_not_authorize_runtime_influence": True,
            "approval_does_not_authorize_predictor_mutation": True,
            "approval_does_not_authorize_production_behavior": True,
        },
        "target_layer_design": {
            "target_layer_must_be_explicit": True,
            "default_target_layer": None,
            "long_term_memory_allowed_now": False,
            "core_memory_allowed": False,
            "archive_memory_allowed_now": False,
            "working_memory_allowed_for_design_preview_only": True,
            "reviewed_lesson_memory_candidate_allowed_for_future_package": True,
        },
        "retention_and_rollback_design": {
            "retained_jsonl_write_allowed_now": False,
            "future_retention_rule_required": True,
            "rollback_rule_required": True,
            "rollback_outcome_options_required": [
                "delete_record",
                "invalidate_record",
                "keep_record_as_audit_only",
            ],
            "rollback_must_define_whether_record_is_deleted_invalidated_or_kept_as_audit": True,
            "rollback_must_block_auto_influence_rebuild": True,
        },
        "cross_session_influence_design": {
            "cross_session_influence_allowed_now": False,
            "future_rebuild_rule_required": True,
            "auto_rebuild_after_rollback_allowed": False,
            "session_start_auto_influence_allowed": False,
        },
        "runtime_influence_design": {
            "runtime_influence_allowed_now": False,
            "future_runtime_influence_requires_separate_boundary_package": True,
            "sandbox_influence_design_only_allowed": True,
        },
        "predictor_design": {
            "predictor_influence_allowed_now": False,
            "predictor_mutation_allowed_now": False,
            "future_predictor_influence_requires_separate_boundary_package": True,
        },
        "audit_and_revocation_design": {
            "audit_record_required": True,
            "revocation_path_required": True,
            "human_readable_summary_required": True,
            "source_evidence_chain_required": True,
        },
        "repo_audit_acknowledged": True,
        "qingyin_current_status": QINGYIN_STATUS,
        "qingyin_self_authored_lesson_text": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "memory_admission_allowed_now": False,
        "memory_write_allowed": False,
        "retained_jsonl_write_allowed": False,
        "retention_write_allowed": False,
        "runtime_influence_allowed": False,
        "predictor_influence_allowed": False,
        "predictor_mutation_allowed": False,
        "production_behavior_change_allowed": False,
        "selected_action_allowed": False,
        "final_action_allowed": False,
        "proof_of_learning_claim_allowed": False,
        "source_memory_readiness_design": source,
    }


def validate_memory_admission_package_design(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "memory_admission_package_design":
        errors.append("record_type_not_memory_admission_package_design")
    if record.get("record_version") != "v0":
        errors.append("record_version_not_v0")
    if record.get("source_record_type") != "memory_readiness_design_for_approved_bucket_lesson":
        errors.append("source_record_type_not_memory_readiness_design")
    source_record = record.get("source_memory_readiness_design")
    if not isinstance(source_record, dict):
        errors.append("source_memory_readiness_design_missing")
    elif not validate_memory_readiness_design_for_approved_bucket_lesson(source_record)["valid"]:
        errors.append("source_memory_readiness_design_invalid")
    if record.get("source_review_decision") != "approved_for_future_memory_readiness_design_only":
        errors.append("source_review_decision_not_approved")
    if record.get("source_repeated_key") != REPEATED_KEY:
        errors.append("source_repeated_key_not_expected")
    if record.get("source_memory_readiness_status") != "memory_readiness_design_recorded":
        errors.append("source_memory_readiness_status_not_recorded")
    if record.get("design_status") != "future_memory_admission_package_design_recorded":
        errors.append("design_status_not_recorded")
    if record.get("package_design_only") is not True:
        errors.append("package_design_only_not_true")
    if record.get("memory_admission_performed") is not False:
        errors.append("memory_admission_performed_not_false")
    if record.get("memory_write_performed") is not False:
        errors.append("memory_write_performed_not_false")
    if not isinstance(record.get("future_package_purpose"), str) or not record.get("future_package_purpose"):
        errors.append("future_package_purpose_empty")
    if record.get("allowed_future_target_forms") != ["reviewed_lesson_memory_candidate"]:
        errors.append("allowed_future_target_forms_not_expected")
    if not set(DISALLOWED_CURRENT_TARGET_LAYERS).issubset(
        set(record.get("disallowed_current_target_layers", []))
    ):
        errors.append("disallowed_current_target_layers_incomplete")
    required_inputs = record.get("required_future_inputs")
    if not isinstance(required_inputs, list):
        errors.append("required_future_inputs_not_list")
        required_inputs = []
    missing_inputs = sorted(set(REQUIRED_FUTURE_INPUTS) - set(required_inputs))
    errors.extend(f"missing_required_future_input:{item}" for item in missing_inputs)
    _validate_future_approval(record.get("required_future_approval"), errors)
    _validate_target_layer(record.get("target_layer_design"), errors)
    _validate_retention_and_rollback(record.get("retention_and_rollback_design"), errors)
    _validate_cross_session(record.get("cross_session_influence_design"), errors)
    _validate_runtime(record.get("runtime_influence_design"), errors)
    _validate_predictor(record.get("predictor_design"), errors)
    _validate_audit(record.get("audit_and_revocation_design"), errors)
    if record.get("repo_audit_acknowledged") is not True:
        errors.append("repo_audit_acknowledged_not_true")
    if record.get("qingyin_current_status") != QINGYIN_STATUS:
        errors.append("qingyin_current_status_not_phase0_trace_checker_system")
    if record.get("qingyin_self_authored_lesson_text") is not False:
        errors.append("qingyin_self_authored_lesson_text_not_false")
    if record.get("autonomous_learning_claim_allowed") is not False:
        errors.append("autonomous_learning_claim_allowed_not_false")
    if record.get("autonomous_action_claim_allowed") is not False:
        errors.append("autonomous_action_claim_allowed_not_false")
    for field in FALSE_PERMISSION_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "source_readiness_checked": record.get("source_record_type")
        == "memory_readiness_design_for_approved_bucket_lesson",
        "future_approval_required": _dict_get(record, "required_future_approval", "approval_text_required") is True,
        "target_layer_selection_required": _dict_get(record, "target_layer_design", "target_layer_must_be_explicit")
        is True,
        "rollback_rule_required": _dict_get(record, "retention_and_rollback_design", "rollback_rule_required")
        is True,
        "cross_session_rebuild_rule_required": _dict_get(
            record, "cross_session_influence_design", "future_rebuild_rule_required"
        )
        is True,
        "runtime_boundary_required": _dict_get(
            record, "runtime_influence_design", "future_runtime_influence_requires_separate_boundary_package"
        )
        is True,
        "predictor_boundary_required": _dict_get(
            record, "predictor_design", "future_predictor_influence_requires_separate_boundary_package"
        )
        is True,
        "memory_admission_blocked": record.get("memory_admission_allowed_now") is False,
        "memory_write_blocked": record.get("memory_write_allowed") is False,
        "retained_jsonl_write_blocked": record.get("retained_jsonl_write_allowed") is False,
        "runtime_influence_blocked": record.get("runtime_influence_allowed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_allowed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_memory_admission_package_design_minimal_check() -> dict[str, Any]:
    valid = build_memory_admission_package_design()
    invalid = _invalid_records(valid)
    validations = [validate_memory_admission_package_design(record) for record in [valid] + invalid]
    valid_results = [result for result in validations if result["valid"]]
    summary = {
        "valid_memory_admission_design_count": len(valid_results),
        "invalid_memory_admission_design_count": len(validations) - len(valid_results),
        "source_readiness_checked_count": sum(1 for result in valid_results if result["source_readiness_checked"]),
        "future_approval_required_count": sum(1 for result in valid_results if result["future_approval_required"]),
        "target_layer_selection_required_count": sum(
            1 for result in valid_results if result["target_layer_selection_required"]
        ),
        "rollback_rule_required_count": sum(1 for result in valid_results if result["rollback_rule_required"]),
        "cross_session_rebuild_rule_required_count": sum(
            1 for result in valid_results if result["cross_session_rebuild_rule_required"]
        ),
        "runtime_boundary_required_count": sum(1 for result in valid_results if result["runtime_boundary_required"]),
        "predictor_boundary_required_count": sum(
            1 for result in valid_results if result["predictor_boundary_required"]
        ),
        "memory_admission_blocked_count": sum(1 for result in valid_results if result["memory_admission_blocked"]),
        "memory_write_blocked_count": sum(1 for result in valid_results if result["memory_write_blocked"]),
        "retained_jsonl_write_blocked_count": sum(
            1 for result in valid_results if result["retained_jsonl_write_blocked"]
        ),
        "runtime_influence_blocked_count": sum(1 for result in valid_results if result["runtime_influence_blocked"]),
        "predictor_mutation_blocked_count": sum(
            1 for result in valid_results if result["predictor_mutation_blocked"]
        ),
        "proof_claim_blocked_count": sum(1 for result in valid_results if result["proof_claim_blocked"]),
    }
    summary["all_memory_admission_package_design_checks_passed"] = _all_checks_passed(summary)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_memory_admission_package_design_checks_passed"] else "failed",
        "valid_record": valid,
        "invalid_records": invalid,
        "validation_results": validations,
        "summary": summary,
        "boundary": {
            "boundary_change_required": False,
            "boundary_index_update_required": False,
            "boundary_index_version_before": BOUNDARY_VERSION,
            "boundary_index_version_after": BOUNDARY_VERSION,
            "rationale": (
                "This package records design-only package constraints without changing memory admission "
                "permission, memory write permission, retained JSONL behavior, runtime influence, "
                "predictor influence, retention, or action-selection boundaries."
            ),
        },
        "safe_claim": (
            "ASHL Core can record a design-only future memory admission package contract for one approved "
            "human-interpreted, bucket-derived lesson candidate, while keeping memory admission, memory write, "
            "retained JSONL write, runtime influence, predictor mutation, action selection, production promotion, "
            "and proof-of-learning blocked."
        ),
    }


def _validate_future_approval(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("required_future_approval_missing")
        value = {}
    expected = {
        "approval_source": "explicit_user_statement",
        "approval_actor": "user",
        "approver_role": "project_owner",
        "approval_text_required": True,
        "approval_purpose": "future_memory_admission_only",
        "approval_does_not_authorize_runtime_influence": True,
        "approval_does_not_authorize_predictor_mutation": True,
        "approval_does_not_authorize_production_behavior": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            errors.append(f"required_future_approval_{field}_not_expected")


def _validate_target_layer(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("target_layer_design_missing")
        value = {}
    checks = {
        "target_layer_must_be_explicit": True,
        "long_term_memory_allowed_now": False,
        "core_memory_allowed": False,
        "archive_memory_allowed_now": False,
        "working_memory_allowed_for_design_preview_only": True,
        "reviewed_lesson_memory_candidate_allowed_for_future_package": True,
    }
    if value.get("default_target_layer") is not None:
        errors.append("default_target_layer_not_none")
    for field, expected in checks.items():
        if value.get(field) != expected:
            errors.append(f"target_layer_design_{field}_not_expected")


def _validate_retention_and_rollback(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("retention_and_rollback_design_missing")
        value = {}
    checks = {
        "retained_jsonl_write_allowed_now": False,
        "future_retention_rule_required": True,
        "rollback_rule_required": True,
        "rollback_must_define_whether_record_is_deleted_invalidated_or_kept_as_audit": True,
        "rollback_must_block_auto_influence_rebuild": True,
    }
    options = value.get("rollback_outcome_options_required")
    if not isinstance(options, list) or not {"delete_record", "invalidate_record", "keep_record_as_audit_only"}.issubset(
        set(options)
    ):
        errors.append("rollback_outcome_options_required_incomplete")
    for field, expected in checks.items():
        if value.get(field) != expected:
            errors.append(f"retention_and_rollback_design_{field}_not_expected")


def _validate_cross_session(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("cross_session_influence_design_missing")
        value = {}
    checks = {
        "cross_session_influence_allowed_now": False,
        "future_rebuild_rule_required": True,
        "auto_rebuild_after_rollback_allowed": False,
        "session_start_auto_influence_allowed": False,
    }
    for field, expected in checks.items():
        if value.get(field) != expected:
            errors.append(f"cross_session_influence_design_{field}_not_expected")


def _validate_runtime(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("runtime_influence_design_missing")
        value = {}
    checks = {
        "runtime_influence_allowed_now": False,
        "future_runtime_influence_requires_separate_boundary_package": True,
        "sandbox_influence_design_only_allowed": True,
    }
    for field, expected in checks.items():
        if value.get(field) != expected:
            errors.append(f"runtime_influence_design_{field}_not_expected")


def _validate_predictor(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("predictor_design_missing")
        value = {}
    checks = {
        "predictor_influence_allowed_now": False,
        "predictor_mutation_allowed_now": False,
        "future_predictor_influence_requires_separate_boundary_package": True,
    }
    for field, expected in checks.items():
        if value.get(field) != expected:
            errors.append(f"predictor_design_{field}_not_expected")


def _validate_audit(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("audit_and_revocation_design_missing")
        value = {}
    for field in (
        "audit_record_required",
        "revocation_path_required",
        "human_readable_summary_required",
        "source_evidence_chain_required",
    ):
        if value.get(field) is not True:
            errors.append(f"audit_and_revocation_design_{field}_not_true")


def _invalid_records(valid: dict[str, Any]) -> list[dict[str, Any]]:
    records = [
        _without(valid, "source_memory_readiness_design"),
        _mutated(valid, ["source_review_decision"], "rejected"),
        _mutated(valid, ["package_design_only"], False),
        _mutated(valid, ["memory_admission_performed"], True),
        _mutated(valid, ["memory_write_performed"], True),
        _mutated(valid, ["required_future_approval", "approval_text_required"], False),
        _mutated(valid, ["target_layer_design", "target_layer_must_be_explicit"], False),
        _mutated(valid, ["target_layer_design", "default_target_layer"], "long_term_memory"),
        _mutated(valid, ["target_layer_design", "long_term_memory_allowed_now"], True),
        _mutated(valid, ["target_layer_design", "core_memory_allowed"], True),
        _mutated(valid, ["retention_and_rollback_design", "retained_jsonl_write_allowed_now"], True),
        _mutated(valid, ["retention_and_rollback_design", "rollback_rule_required"], False),
        _mutated(valid, ["retention_and_rollback_design", "rollback_must_block_auto_influence_rebuild"], False),
        _mutated(valid, ["cross_session_influence_design", "cross_session_influence_allowed_now"], True),
        _mutated(valid, ["cross_session_influence_design", "session_start_auto_influence_allowed"], True),
        _mutated(valid, ["runtime_influence_design", "runtime_influence_allowed_now"], True),
        _mutated(valid, ["runtime_influence_design", "future_runtime_influence_requires_separate_boundary_package"], False),
        _mutated(valid, ["predictor_design", "predictor_influence_allowed_now"], True),
        _mutated(valid, ["predictor_design", "predictor_mutation_allowed_now"], True),
        _mutated(valid, ["predictor_design", "future_predictor_influence_requires_separate_boundary_package"], False),
        _mutated(valid, ["audit_and_revocation_design", "revocation_path_required"], False),
        _mutated(valid, ["required_future_inputs"], list(REQUIRED_FUTURE_INPUTS[:-1])),
        _mutated(valid, ["repo_audit_acknowledged"], False),
        _mutated(valid, ["qingyin_self_authored_lesson_text"], True),
        _mutated(valid, ["autonomous_learning_claim_allowed"], True),
        _mutated(valid, ["autonomous_action_claim_allowed"], True),
    ]
    for field in FALSE_PERMISSION_FIELDS:
        records.append(_mutated(valid, [field], True))
    return records


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["valid_memory_admission_design_count"] == 1
        and summary["invalid_memory_admission_design_count"] >= 1
        and summary["source_readiness_checked_count"] == 1
        and summary["future_approval_required_count"] == 1
        and summary["target_layer_selection_required_count"] == 1
        and summary["rollback_rule_required_count"] == 1
        and summary["cross_session_rebuild_rule_required_count"] == 1
        and summary["runtime_boundary_required_count"] == 1
        and summary["predictor_boundary_required_count"] == 1
        and summary["memory_admission_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["retained_jsonl_write_blocked_count"] == 1
        and summary["runtime_influence_blocked_count"] == 1
        and summary["predictor_mutation_blocked_count"] == 1
        and summary["proof_claim_blocked_count"] == 1
    )


def _dict_get(record: dict[str, Any], key: str, subkey: str) -> Any:
    value = record.get(key)
    return value.get(subkey) if isinstance(value, dict) else None


def _without(record: dict[str, Any], key: str) -> dict[str, Any]:
    clone = deepcopy(record)
    clone.pop(key, None)
    return clone


def _mutated(record: dict[str, Any], path: list[Any], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: Any = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(run_memory_admission_package_design_minimal_check(), indent=2))
