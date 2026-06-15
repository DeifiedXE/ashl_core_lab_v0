"""Sandbox-only use of approved memory-influenced tendency for candidate ordering."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS
from .memory_influenced_sandbox_rerun_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as MINEFIELD_RERUN_BOUNDARY,
    build_memory_influenced_sandbox_rerun_record,
    validate_memory_influenced_sandbox_rerun_record,
)
from .memory_influenced_toy_repair_rerun_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as TOY_REPAIR_RERUN_BOUNDARY,
    build_memory_influenced_toy_repair_rerun_record,
    validate_memory_influenced_toy_repair_rerun_record,
)
from .memory_runtime_influence_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as MEMORY_RUNTIME_BOUNDARY,
    build_memory_runtime_influence_record,
    validate_memory_runtime_influence_record,
)


COMMAND = "run-sandbox-behavior-use-minimal-check"
FLOW = "sandbox_behavior_use_minimal_v0"
PACKAGE_ID = "PKG-Phase0-SandboxBehaviorUse-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b84"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b85"
APPROVAL_STATUS = "approved_for_sandbox_candidate_ordering_only"
APPROVAL_SCOPE = "memory_influenced_tendency_to_sandbox_candidate_ordering"
ALLOWED_BEHAVIOR = "rank_sandbox_candidate_actions"
ORDERING_STATUS = "completed_sandbox_only_candidate_ordering"
SANDBOX_SCOPE = "phase0_level3_sandbox_only"
ORDERING_REASON = "memory_on_increases_check_before_retry_and_decreases_retry_same_action_without_check"
CANDIDATES_BEFORE = [
    "retry_same_action_without_check",
    "check_before_retry",
    "fallback_stop_and_report",
]
CANDIDATES_AFTER = [
    "check_before_retry",
    "fallback_stop_and_report",
    "retry_same_action_without_check",
]
SOURCE_EVIDENCE = ["minefield_rerun_b82", "toy_repair_rerun_b84"]
FALSE_APPROVAL_FIELDS = (
    "selected_action_allowed",
    "final_action_allowed",
    "production_behavior_allowed",
    "predictor_mutation_allowed",
    "retention_allowed",
    "proof_of_learning_claim_allowed",
)
FALSE_ORDERING_FIELDS = (
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
TRUE_ORDERING_FIELDS = (
    "ordering_is_sandbox_only",
    "ordering_is_advisory",
    "future_selected_action_requires_separate_boundary",
    "future_final_action_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "future_production_promotion_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "audit_recorded",
    "rollback_available",
)


def build_sandbox_behavior_use_approval_record() -> dict[str, Any]:
    return {
        "record_type": "sandbox_behavior_use_approval",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "approval_status": APPROVAL_STATUS,
        "approval_scope": APPROVAL_SCOPE,
        "source_boundary_index": BOUNDARY_INDEX_VERSION_BEFORE,
        "allowed_behavior": ALLOWED_BEHAVIOR,
        "selected_action_allowed": False,
        "final_action_allowed": False,
        "production_behavior_allowed": False,
        "predictor_mutation_allowed": False,
        "retention_allowed": False,
        "proof_of_learning_claim_allowed": False,
    }


def validate_sandbox_behavior_use_approval_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_behavior_use_approval",
        "record_version": "v0",
        "approval_status": APPROVAL_STATUS,
        "approval_scope": APPROVAL_SCOPE,
        "source_boundary_index": BOUNDARY_INDEX_VERSION_BEFORE,
        "allowed_behavior": ALLOWED_BEHAVIOR,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")
    for field in FALSE_APPROVAL_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "selected_action_blocked": record.get("selected_action_allowed") is False,
        "final_action_blocked": record.get("final_action_allowed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_allowed") is False,
        "production_behavior_blocked": record.get("production_behavior_allowed") is False,
        "retention_blocked": record.get("retention_allowed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_sandbox_candidate_ordering_record(
    approval_record: dict[str, Any] | None = None,
    memory_runtime_influence: dict[str, Any] | None = None,
    minefield_rerun: dict[str, Any] | None = None,
    toy_repair_rerun: dict[str, Any] | None = None,
) -> dict[str, Any]:
    approval = deepcopy(approval_record) if approval_record is not None else build_sandbox_behavior_use_approval_record()
    if not validate_sandbox_behavior_use_approval_record(approval)["valid"]:
        raise ValueError("invalid_sandbox_behavior_use_approval")

    source_memory = deepcopy(memory_runtime_influence) if memory_runtime_influence is not None else (
        build_memory_runtime_influence_record()
    )
    if not validate_memory_runtime_influence_record(source_memory)["valid"]:
        raise ValueError("invalid_memory_runtime_influence_source")

    source_minefield = deepcopy(minefield_rerun) if minefield_rerun is not None else (
        build_memory_influenced_sandbox_rerun_record(source_memory)
    )
    if not validate_memory_influenced_sandbox_rerun_record(source_minefield)["valid"]:
        raise ValueError("invalid_minefield_rerun_source")

    source_toy_repair = deepcopy(toy_repair_rerun) if toy_repair_rerun is not None else (
        build_memory_influenced_toy_repair_rerun_record(source_memory)
    )
    if not validate_memory_influenced_toy_repair_rerun_record(source_toy_repair)["valid"]:
        raise ValueError("invalid_toy_repair_rerun_source")

    return {
        "record_type": "sandbox_candidate_action_ordering",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "ordering_status": ORDERING_STATUS,
        "sandbox_scope": SANDBOX_SCOPE,
        "source_approval_record_type": approval.get("record_type"),
        "source_memory_influence": "bounded_runtime_tendency_influence_b81",
        "source_cross_sandbox_evidence": list(SOURCE_EVIDENCE),
        "candidate_actions_before_ordering": list(CANDIDATES_BEFORE),
        "candidate_actions_after_ordering": list(CANDIDATES_AFTER),
        "ordering_reason": ORDERING_REASON,
        "ordering_is_sandbox_only": True,
        "ordering_is_advisory": True,
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
        "future_selected_action_requires_separate_boundary": True,
        "future_final_action_requires_separate_boundary": True,
        "future_predictor_influence_requires_separate_boundary": True,
        "future_production_promotion_requires_separate_boundary": True,
        "future_retention_requires_separate_boundary": True,
        "qingyin_current_status": QINGYIN_STATUS,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_approval_record": approval,
        "source_memory_runtime_influence_record": source_memory,
        "source_minefield_rerun_record": source_minefield,
        "source_toy_repair_rerun_record": source_toy_repair,
    }


def validate_sandbox_candidate_ordering_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "sandbox_candidate_action_ordering",
        "record_version": "v0",
        "ordering_status": ORDERING_STATUS,
        "sandbox_scope": SANDBOX_SCOPE,
        "source_approval_record_type": "sandbox_behavior_use_approval",
        "source_memory_influence": "bounded_runtime_tendency_influence_b81",
        "ordering_reason": ORDERING_REASON,
        "qingyin_current_status": QINGYIN_STATUS,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    if record.get("source_cross_sandbox_evidence") != SOURCE_EVIDENCE:
        errors.append("source_cross_sandbox_evidence_not_expected")
    if record.get("candidate_actions_before_ordering") != CANDIDATES_BEFORE:
        errors.append("candidate_actions_before_ordering_not_expected")
    after = record.get("candidate_actions_after_ordering", [])
    if after != CANDIDATES_AFTER:
        errors.append("candidate_actions_after_ordering_not_expected")
    if not _ranked_before(after, "check_before_retry", "retry_same_action_without_check"):
        errors.append("check_before_retry_not_ranked_above_retry_same_action_without_check")

    approval = record.get("source_approval_record")
    if not isinstance(approval, dict):
        errors.append("source_approval_record_missing")
    elif not validate_sandbox_behavior_use_approval_record(approval)["valid"]:
        errors.append("source_approval_record_invalid")
    memory = record.get("source_memory_runtime_influence_record")
    if not isinstance(memory, dict):
        errors.append("source_memory_runtime_influence_record_missing")
    elif not validate_memory_runtime_influence_record(memory)["valid"]:
        errors.append("source_memory_runtime_influence_record_invalid")
    minefield = record.get("source_minefield_rerun_record")
    if not isinstance(minefield, dict):
        errors.append("source_minefield_rerun_record_missing")
    elif not validate_memory_influenced_sandbox_rerun_record(minefield)["valid"]:
        errors.append("source_minefield_rerun_record_invalid")
    toy_repair = record.get("source_toy_repair_rerun_record")
    if not isinstance(toy_repair, dict):
        errors.append("source_toy_repair_rerun_record_missing")
    elif not validate_memory_influenced_toy_repair_rerun_record(toy_repair)["valid"]:
        errors.append("source_toy_repair_rerun_record_invalid")

    if (
        isinstance(memory, dict)
        and memory.get("record_type") == "memory_runtime_influence"
        and MEMORY_RUNTIME_BOUNDARY != "2026-06-09-b81"
    ):
        errors.append("b81_memory_runtime_source_missing")
    if (
        isinstance(minefield, dict)
        and minefield.get("record_type") == "memory_influenced_sandbox_rerun"
        and MINEFIELD_RERUN_BOUNDARY != "2026-06-09-b82"
    ):
        errors.append("b82_minefield_rerun_source_missing")
    if (
        isinstance(toy_repair, dict)
        and toy_repair.get("record_type") == "memory_influenced_toy_repair_rerun"
        and TOY_REPAIR_RERUN_BOUNDARY != "2026-06-09-b84"
    ):
        errors.append("b84_toy_repair_rerun_source_missing")

    for field in FALSE_ORDERING_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in TRUE_ORDERING_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "candidate_ordering_checked": _ranked_before(after, "check_before_retry", "retry_same_action_without_check"),
        "approval_checked": isinstance(approval, dict) and validate_sandbox_behavior_use_approval_record(approval)["valid"],
        "memory_runtime_source_checked": isinstance(memory, dict) and validate_memory_runtime_influence_record(memory)["valid"],
        "minefield_evidence_checked": isinstance(minefield, dict)
        and validate_memory_influenced_sandbox_rerun_record(minefield)["valid"],
        "toy_repair_evidence_checked": isinstance(toy_repair, dict)
        and validate_memory_influenced_toy_repair_rerun_record(toy_repair)["valid"],
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_sandbox_behavior_use_minimal_check() -> dict[str, Any]:
    approval = build_sandbox_behavior_use_approval_record()
    ordering = build_sandbox_candidate_ordering_record(approval)
    invalid_approvals = _invalid_approvals(approval)
    invalid_orderings = _invalid_orderings(ordering)
    approval_results = [
        validate_sandbox_behavior_use_approval_record(item)
        for item in [approval] + invalid_approvals
    ]
    ordering_results = [
        validate_sandbox_candidate_ordering_record(item)
        for item in [ordering] + invalid_orderings
    ]
    valid_approval_results = [result for result in approval_results if result["valid"]]
    valid_ordering_results = [result for result in ordering_results if result["valid"]]
    summary = {
        "valid_approval_count": len(valid_approval_results),
        "invalid_approval_count": len(approval_results) - len(valid_approval_results),
        "valid_ordering_count": len(valid_ordering_results),
        "invalid_ordering_count": len(ordering_results) - len(valid_ordering_results),
        "candidate_ordering_checked_count": sum(
            1 for result in valid_ordering_results if result["candidate_ordering_checked"]
        ),
        "approval_checked_count": sum(1 for result in valid_ordering_results if result["approval_checked"]),
        "memory_runtime_source_checked_count": sum(
            1 for result in valid_ordering_results if result["memory_runtime_source_checked"]
        ),
        "cross_sandbox_evidence_checked_count": sum(
            1
            for result in valid_ordering_results
            if result["minefield_evidence_checked"] and result["toy_repair_evidence_checked"]
        ),
        "selected_action_blocked_count": sum(1 for result in valid_ordering_results if result["selected_action_blocked"]),
        "final_action_blocked_count": sum(1 for result in valid_ordering_results if result["final_action_blocked"]),
        "predictor_mutation_blocked_count": sum(
            1 for result in valid_ordering_results if result["predictor_mutation_blocked"]
        ),
        "production_behavior_blocked_count": sum(
            1 for result in valid_ordering_results if result["production_behavior_blocked"]
        ),
        "retention_blocked_count": sum(1 for result in valid_ordering_results if result["retention_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid_ordering_results if result["proof_claim_blocked"]),
    }
    summary["all_sandbox_behavior_use_minimal_checks_passed"] = _all_checks_passed(summary)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_sandbox_behavior_use_minimal_checks_passed"] else "failed",
        "valid_approval": approval,
        "valid_ordering": ordering,
        "invalid_approvals": invalid_approvals,
        "invalid_orderings": invalid_orderings,
        "validation_results": {
            "approvals": approval_results,
            "orderings": ordering_results,
        },
        "summary": summary,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package permits approved memory-influenced tendency to affect sandbox-only candidate "
                "action ordering. It does not create selected_action, final_action, direct command, predictor "
                "mutation, production behavior, retained JSONL write, retention write, or proof-of-learning."
            ),
        },
        "safe_claim": (
            "ASHL Core can use approved memory-influenced tendency to rank sandbox-only candidate actions, "
            "placing check_before_retry above retry_same_action_without_check under memory_on, while selected_action, "
            "final_action, direct command, predictor mutation, production behavior, retained JSONL write, retention "
            "write, and proof-of-learning remain blocked."
        ),
    }


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary.get("valid_approval_count") == 1
        and summary.get("invalid_approval_count", 0) >= 1
        and summary.get("valid_ordering_count") == 1
        and summary.get("invalid_ordering_count", 0) >= 1
        and summary.get("candidate_ordering_checked_count") == 1
        and summary.get("approval_checked_count") == 1
        and summary.get("memory_runtime_source_checked_count") == 1
        and summary.get("cross_sandbox_evidence_checked_count") == 1
        and summary.get("selected_action_blocked_count") == 1
        and summary.get("final_action_blocked_count") == 1
        and summary.get("predictor_mutation_blocked_count") == 1
        and summary.get("production_behavior_blocked_count") == 1
        and summary.get("retention_blocked_count") == 1
        and summary.get("proof_claim_blocked_count") == 1
    )


def _ranked_before(actions: list[Any], first: str, second: str) -> bool:
    return first in actions and second in actions and actions.index(first) < actions.index(second)


def _invalid_approvals(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("approval_status", "approved_for_selected_action"),
        ("allowed_behavior", "create_selected_action"),
        ("selected_action_allowed", True),
        ("final_action_allowed", True),
        ("production_behavior_allowed", True),
        ("predictor_mutation_allowed", True),
        ("retention_allowed", True),
        ("proof_of_learning_claim_allowed", True),
    ):
        record = deepcopy(valid)
        record[field] = value
        invalids.append(record)
    return invalids


def _invalid_orderings(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def changed(field: str, value: Any) -> None:
        record = deepcopy(valid)
        record[field] = value
        invalids.append(record)

    missing_approval = deepcopy(valid)
    missing_approval.pop("source_approval_record", None)
    invalids.append(missing_approval)
    missing_memory = deepcopy(valid)
    missing_memory.pop("source_memory_runtime_influence_record", None)
    invalids.append(missing_memory)
    missing_minefield = deepcopy(valid)
    missing_minefield.pop("source_minefield_rerun_record", None)
    invalids.append(missing_minefield)
    missing_toy_repair = deepcopy(valid)
    missing_toy_repair.pop("source_toy_repair_rerun_record", None)
    invalids.append(missing_toy_repair)
    changed("source_cross_sandbox_evidence", ["minefield_rerun_b82"])
    changed(
        "candidate_actions_after_ordering",
        ["retry_same_action_without_check", "check_before_retry", "fallback_stop_and_report"],
    )
    changed("ordering_is_sandbox_only", False)
    changed("ordering_is_advisory", False)
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
    changed("future_selected_action_requires_separate_boundary", False)
    changed("audit_recorded", False)
    changed("rollback_available", False)
    return invalids


if __name__ == "__main__":
    import json

    print(json.dumps(run_sandbox_behavior_use_minimal_check(), indent=2, sort_keys=True))
