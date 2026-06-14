"""Bounded memory runtime influence in a deterministic controlled runner."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS
from .memory_admission_minimal import LESSON_NAME
from .memory_influence_preview_minimal import (
    DISCOURAGED_FUTURE_TENDENCY,
    PREFERRED_FUTURE_TENDENCY,
    build_memory_influence_preview_record,
    validate_memory_influence_preview_record,
)
from .memory_runtime_influence_approval_boundary_minimal import (
    APPROVED_DECISION,
    BOUNDARY_INDEX_VERSION_AFTER as SOURCE_BOUNDARY_INDEX_VERSION,
    build_memory_runtime_influence_approval_record,
    validate_memory_runtime_influence_approval_record,
)
from .memory_write_and_read_minimal import (
    build_controlled_memory_read_record,
    validate_controlled_memory_read_record,
)


COMMAND = "run-memory-runtime-influence-minimal-check"
FLOW = "memory_runtime_influence_minimal_v0"
PACKAGE_ID = "PKG-Phase0-MemoryRuntimeInfluence-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = SOURCE_BOUNDARY_INDEX_VERSION
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b81"
RUNTIME_INFLUENCE_STATUS = "bounded_tendency_shift_applied_and_rolled_back"
RUNTIME_INFLUENCE_SCOPE = "deterministic_controlled_runner_only"
RUNTIME_INFLUENCE_TYPE = "bounded_tendency_score_shift"
MEMORY_OFF_BASELINE = {
    DISCOURAGED_FUTURE_TENDENCY: 0.50,
    PREFERRED_FUTURE_TENDENCY: 0.50,
}
MEMORY_ON_INFLUENCED = {
    DISCOURAGED_FUTURE_TENDENCY: 0.45,
    PREFERRED_FUTURE_TENDENCY: 0.60,
}
MAX_ABSOLUTE_DELTA = 0.10
FALSE_RUNTIME_FIELDS = (
    "dirty_state_after_rollback",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "production_behavior_changed",
    "predictor_read_enabled",
    "predictor_influence_enabled",
    "predictor_mutation_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "proof_of_learning_claim_allowed",
    "autonomous_learning_claim_allowed",
    "autonomous_action_claim_allowed",
)
TRUE_RUNTIME_FIELDS = (
    "runtime_tendency_changed",
    "rollback_to_baseline_performed",
    "rollback_restored_baseline",
    "future_action_selection_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "future_production_promotion_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "repo_audit_acknowledged",
    "audit_recorded",
    "rollback_available",
)


def _deterministic_controlled_runner(memory_enabled: bool) -> dict[str, float]:
    return deepcopy(MEMORY_ON_INFLUENCED if memory_enabled else MEMORY_OFF_BASELINE)


def build_memory_runtime_influence_record(
    controlled_memory_read: dict[str, Any] | None = None,
    memory_influence_preview: dict[str, Any] | None = None,
    memory_runtime_influence_approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_read = deepcopy(controlled_memory_read) if controlled_memory_read is not None else (
        build_controlled_memory_read_record()
    )
    if not validate_controlled_memory_read_record(source_read)["valid"]:
        raise ValueError("invalid_controlled_memory_read_source")

    source_preview = deepcopy(memory_influence_preview) if memory_influence_preview is not None else (
        build_memory_influence_preview_record(source_read)
    )
    if not validate_memory_influence_preview_record(source_preview)["valid"]:
        raise ValueError("invalid_memory_influence_preview_source")

    source_approval = (
        deepcopy(memory_runtime_influence_approval)
        if memory_runtime_influence_approval is not None
        else build_memory_runtime_influence_approval_record(source_preview)
    )
    approval_result = validate_memory_runtime_influence_approval_record(source_approval)
    if not approval_result["valid"]:
        raise ValueError("invalid_memory_runtime_influence_approval_source")
    if source_approval.get("approval_decision") != APPROVED_DECISION:
        raise ValueError("blocked_memory_runtime_influence_approval_decision")
    if source_approval.get("future_memory_runtime_influence_package_may_proceed") is not True:
        raise ValueError("memory_runtime_influence_approval_not_permitted")

    memory_off = _deterministic_controlled_runner(memory_enabled=False)
    memory_on = _deterministic_controlled_runner(memory_enabled=True)
    memory_off_after_rollback = _deterministic_controlled_runner(memory_enabled=False)
    deltas = {
        action: round(memory_on[action] - memory_off[action], 2)
        for action in memory_off
    }
    max_delta = max(abs(delta) for delta in deltas.values())
    return {
        "record_type": "memory_runtime_influence",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "runtime_influence_status": RUNTIME_INFLUENCE_STATUS,
        "runtime_influence_scope": RUNTIME_INFLUENCE_SCOPE,
        "runtime_influence_type": RUNTIME_INFLUENCE_TYPE,
        "source_memory_record_type": "minimal_reviewed_lesson_memory_record",
        "source_preview_record_type": source_preview.get("record_type"),
        "source_approval_record_type": source_approval.get("record_type"),
        "source_lesson_name": source_preview.get("source_lesson_name") or LESSON_NAME,
        "memory_off_baseline": memory_off,
        "memory_on_influenced": memory_on,
        "memory_off_after_rollback": memory_off_after_rollback,
        "score_deltas": deltas,
        "preferred_tendency": source_preview.get("preferred_future_tendency"),
        "discouraged_tendency": source_preview.get("discouraged_future_tendency"),
        "max_absolute_delta": max_delta,
        "runtime_tendency_changed": memory_on != memory_off,
        "rollback_to_baseline_performed": True,
        "rollback_restored_baseline": memory_off_after_rollback == memory_off,
        "dirty_state_after_rollback": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "production_behavior_changed": False,
        "predictor_read_enabled": False,
        "predictor_influence_enabled": False,
        "predictor_mutation_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "proof_of_learning_claim_allowed": False,
        "current_allowed_use": "bounded_controlled_runtime_tendency_evidence_only",
        "future_action_selection_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "repo_audit_acknowledged": True,
        "qingyin_current_status": QINGYIN_STATUS,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_controlled_memory_read": source_read,
        "source_memory_influence_preview": source_preview,
        "source_memory_runtime_influence_approval": source_approval,
    }


def validate_memory_runtime_influence_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "memory_runtime_influence",
        "record_version": "v0",
        "runtime_influence_status": RUNTIME_INFLUENCE_STATUS,
        "runtime_influence_scope": RUNTIME_INFLUENCE_SCOPE,
        "runtime_influence_type": RUNTIME_INFLUENCE_TYPE,
        "source_memory_record_type": "minimal_reviewed_lesson_memory_record",
        "source_preview_record_type": "memory_influence_preview",
        "source_approval_record_type": "memory_runtime_influence_approval",
        "source_lesson_name": LESSON_NAME,
        "preferred_tendency": PREFERRED_FUTURE_TENDENCY,
        "discouraged_tendency": DISCOURAGED_FUTURE_TENDENCY,
        "current_allowed_use": "bounded_controlled_runtime_tendency_evidence_only",
        "qingyin_current_status": QINGYIN_STATUS,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")

    source_read = record.get("source_controlled_memory_read")
    if not isinstance(source_read, dict):
        errors.append("source_controlled_memory_read_missing")
    elif not validate_controlled_memory_read_record(source_read)["valid"]:
        errors.append("source_controlled_memory_read_invalid")

    source_preview = record.get("source_memory_influence_preview")
    if not isinstance(source_preview, dict):
        errors.append("source_memory_influence_preview_missing")
    elif not validate_memory_influence_preview_record(source_preview)["valid"]:
        errors.append("source_memory_influence_preview_invalid")

    source_approval = record.get("source_memory_runtime_influence_approval")
    if not isinstance(source_approval, dict):
        errors.append("source_memory_runtime_influence_approval_missing")
    else:
        approval_result = validate_memory_runtime_influence_approval_record(source_approval)
        if not approval_result["valid"]:
            errors.append("source_memory_runtime_influence_approval_invalid")
        if source_approval.get("approval_decision") != APPROVED_DECISION:
            errors.append("source_memory_runtime_influence_approval_not_approved")
        if source_approval.get("future_memory_runtime_influence_package_may_proceed") is not True:
            errors.append("source_memory_runtime_influence_approval_may_proceed_not_true")

    memory_off = record.get("memory_off_baseline")
    memory_on = record.get("memory_on_influenced")
    memory_rollback = record.get("memory_off_after_rollback")
    if memory_off != MEMORY_OFF_BASELINE:
        errors.append("memory_off_baseline_not_expected")
    if memory_on != MEMORY_ON_INFLUENCED:
        errors.append("memory_on_influenced_not_expected")
    if memory_rollback != MEMORY_OFF_BASELINE:
        errors.append("memory_off_after_rollback_not_expected")

    score_deltas = record.get("score_deltas")
    expected_deltas = {
        DISCOURAGED_FUTURE_TENDENCY: -0.05,
        PREFERRED_FUTURE_TENDENCY: 0.10,
    }
    if score_deltas != expected_deltas:
        errors.append("score_deltas_not_expected")
    if record.get("max_absolute_delta") != MAX_ABSOLUTE_DELTA:
        errors.append("max_absolute_delta_not_expected")
    if isinstance(record.get("max_absolute_delta"), (int, float)) and record["max_absolute_delta"] > MAX_ABSOLUTE_DELTA:
        errors.append("max_absolute_delta_too_high")

    for field in FALSE_RUNTIME_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in TRUE_RUNTIME_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")

    return {
        "valid": not errors,
        "error_codes": errors,
        "approval_checked": isinstance(source_approval, dict)
        and validate_memory_runtime_influence_approval_record(source_approval)["valid"]
        and source_approval.get("approval_decision") == APPROVED_DECISION,
        "controlled_memory_read_checked": isinstance(source_read, dict)
        and validate_controlled_memory_read_record(source_read)["valid"],
        "preview_checked": isinstance(source_preview, dict)
        and validate_memory_influence_preview_record(source_preview)["valid"],
        "memory_off_baseline_checked": memory_off == MEMORY_OFF_BASELINE,
        "memory_on_influence_checked": memory_on == MEMORY_ON_INFLUENCED,
        "rollback_checked": record.get("rollback_to_baseline_performed") is True
        and record.get("rollback_restored_baseline") is True
        and memory_rollback == MEMORY_OFF_BASELINE,
        "max_delta_checked": record.get("max_absolute_delta") == MAX_ABSOLUTE_DELTA,
        "runtime_tendency_changed": record.get("runtime_tendency_changed") is True,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "retained_jsonl_write_blocked": record.get("retained_jsonl_write_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_memory_runtime_influence_minimal_check() -> dict[str, Any]:
    valid_record = build_memory_runtime_influence_record()
    invalid_records = _invalid_records(valid_record)
    validations = [validate_memory_runtime_influence_record(record) for record in [valid_record] + invalid_records]
    valid_results = [result for result in validations if result["valid"]]
    summary = {
        "valid_runtime_influence_count": len(valid_results),
        "invalid_runtime_influence_count": len(validations) - len(valid_results),
        "approval_checked_count": sum(1 for result in valid_results if result["approval_checked"]),
        "controlled_memory_read_checked_count": sum(
            1 for result in valid_results if result["controlled_memory_read_checked"]
        ),
        "preview_checked_count": sum(1 for result in valid_results if result["preview_checked"]),
        "memory_off_baseline_checked_count": sum(1 for result in valid_results if result["memory_off_baseline_checked"]),
        "memory_on_influence_checked_count": sum(1 for result in valid_results if result["memory_on_influence_checked"]),
        "rollback_checked_count": sum(1 for result in valid_results if result["rollback_checked"]),
        "max_delta_checked_count": sum(1 for result in valid_results if result["max_delta_checked"]),
        "runtime_tendency_changed_count": sum(1 for result in valid_results if result["runtime_tendency_changed"]),
        "selected_action_blocked_count": sum(1 for result in valid_results if result["selected_action_blocked"]),
        "final_action_blocked_count": sum(1 for result in valid_results if result["final_action_blocked"]),
        "predictor_mutation_blocked_count": sum(1 for result in valid_results if result["predictor_mutation_blocked"]),
        "retained_jsonl_write_blocked_count": sum(
            1 for result in valid_results if result["retained_jsonl_write_blocked"]
        ),
        "production_behavior_blocked_count": sum(1 for result in valid_results if result["production_behavior_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid_results if result["proof_claim_blocked"]),
    }
    summary["all_memory_runtime_influence_minimal_checks_passed"] = _all_checks_passed(summary)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_memory_runtime_influence_minimal_checks_passed"] else "failed",
        "valid_record": valid_record,
        "invalid_records": invalid_records,
        "validation_results": validations,
        "summary": summary,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "Opens the minimal bounded memory runtime influence boundary for one approved memory record "
                "inside a deterministic controlled runner, while predictor mutation, action selection, "
                "production promotion, retained JSONL write, and proof-of-learning remain blocked."
            ),
        },
        "safe_claim": (
            "ASHL Core can apply a bounded memory-influenced runtime tendency shift inside a deterministic "
            "controlled runner and roll it back to baseline, while predictor mutation, action selection, "
            "production promotion, retained JSONL write, retention write, and proof-of-learning remain blocked."
        ),
    }


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary.get("valid_runtime_influence_count") == 1
        and summary.get("invalid_runtime_influence_count", 0) >= 1
        and summary.get("approval_checked_count") == 1
        and summary.get("controlled_memory_read_checked_count") == 1
        and summary.get("preview_checked_count") == 1
        and summary.get("memory_off_baseline_checked_count") == 1
        and summary.get("memory_on_influence_checked_count") == 1
        and summary.get("rollback_checked_count") == 1
        and summary.get("max_delta_checked_count") == 1
        and summary.get("runtime_tendency_changed_count") == 1
        and summary.get("selected_action_blocked_count") == 1
        and summary.get("final_action_blocked_count") == 1
        and summary.get("predictor_mutation_blocked_count") == 1
        and summary.get("retained_jsonl_write_blocked_count") == 1
        and summary.get("production_behavior_blocked_count") == 1
        and summary.get("proof_claim_blocked_count") == 1
    )


def _invalid_records(valid_record: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def changed(field: str, value: Any) -> None:
        record = deepcopy(valid_record)
        record[field] = value
        invalids.append(record)

    changed("runtime_influence_scope", "production_runtime")
    changed("max_absolute_delta", 0.11)
    changed("rollback_to_baseline_performed", False)
    changed("rollback_restored_baseline", False)
    changed("dirty_state_after_rollback", True)
    changed("selected_action_created", True)
    changed("final_action_created", True)
    changed("direct_command_created", True)
    changed("production_behavior_changed", True)
    changed("predictor_read_enabled", True)
    changed("predictor_influence_enabled", True)
    changed("predictor_mutation_performed", True)
    changed("retained_jsonl_write_performed", True)
    changed("retention_write_performed", True)
    changed("proof_of_learning_claim_allowed", True)
    changed("autonomous_learning_claim_allowed", True)
    changed("autonomous_action_claim_allowed", True)
    changed("memory_on_influenced", {DISCOURAGED_FUTURE_TENDENCY: 0.40, PREFERRED_FUTURE_TENDENCY: 0.60})
    changed("memory_off_after_rollback", {DISCOURAGED_FUTURE_TENDENCY: 0.45, PREFERRED_FUTURE_TENDENCY: 0.60})

    missing_approval = deepcopy(valid_record)
    missing_approval.pop("source_memory_runtime_influence_approval", None)
    invalids.append(missing_approval)

    blocked_approval = deepcopy(valid_record)
    blocked_approval["source_memory_runtime_influence_approval"] = build_memory_runtime_influence_approval_record(
        approval_decision="rejected_for_runtime_influence"
    )
    invalids.append(blocked_approval)

    missing_read = deepcopy(valid_record)
    missing_read.pop("source_controlled_memory_read", None)
    invalids.append(missing_read)

    missing_preview = deepcopy(valid_record)
    missing_preview.pop("source_memory_influence_preview", None)
    invalids.append(missing_preview)

    codex_approval = deepcopy(valid_record)
    codex_approval["source_memory_runtime_influence_approval"]["approval_actor"] = "codex"
    invalids.append(codex_approval)

    return invalids


if __name__ == "__main__":
    import json

    print(json.dumps(run_memory_runtime_influence_minimal_check(), indent=2, sort_keys=True))
