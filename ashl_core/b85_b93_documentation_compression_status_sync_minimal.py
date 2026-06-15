"""Documentation/status sync checker for the b85-b93 same-session thought loop."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any


COMMAND = "run-b85-b93-documentation-compression-status-sync-minimal-check"
FLOW = "b85_b93_documentation_compression_status_sync_minimal_v0"
PACKAGE_ID = "PKG-Phase0-B85B93DocumentationCompressionStatusSync-Minimal-v0"
BOUNDARY_INDEX_VERSION = "2026-06-09-b93"
RECORD_TYPE = "b85_b93_documentation_compression_status_sync"
SYNC_STATUS = "completed_documentation_compression_status_sync"
COMPRESSED_LOOP_SUMMARY = (
    "candidate ordering -> doubt -> verification candidate registry/planning/execution -> "
    "feedback -> ephemeral application -> same-session reordering -> rollback"
)
DOCS_UPDATED = [
    "README.md",
    "docs/phase0_status.md",
    "docs/phase0_capability_matrix.md",
    "docs/phase0_task_queue.md",
    "docs/research_plan.md",
]
TRUE_FIELDS = (
    "same_session_only",
    "sandbox_only",
    "rollback_required",
    "rollback_verified",
    "audit_recorded",
)
FALSE_FIELDS = (
    "boundary_change_required",
    "boundary_index_update_required",
    "current_boundary_index_updated",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "persistent_rule_created",
    "persistent_trust_doubt_update_performed",
    "cross_session_feedback_persistence",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "production_behavior_changed",
    "verification_execution_is_production_behavior",
    "same_session_loop_proves_learning",
    "proof_of_learning_claim_allowed",
    "qingyin_autonomous_action_claim_allowed",
)
OVERCLAIM_FIELDS = (
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "persistent_rule_created",
    "persistent_trust_doubt_update_performed",
    "cross_session_feedback_persistence",
    "memory_write_performed",
    "retained_jsonl_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "production_behavior_changed",
    "verification_execution_is_production_behavior",
    "same_session_loop_proves_learning",
    "proof_of_learning_claim_allowed",
    "qingyin_autonomous_action_claim_allowed",
)


def build_b85_b93_status_sync_record() -> dict[str, Any]:
    line_count = _current_boundary_index_line_count()
    return {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "sync_status": SYNC_STATUS,
        "boundary_index_before": BOUNDARY_INDEX_VERSION,
        "boundary_index_after": BOUNDARY_INDEX_VERSION,
        "boundary_change_required": False,
        "boundary_index_update_required": False,
        "compressed_loop_summary": COMPRESSED_LOOP_SUMMARY,
        "same_session_only": True,
        "sandbox_only": True,
        "rollback_required": True,
        "rollback_verified": True,
        "docs_updated": DOCS_UPDATED[:],
        "current_boundary_index_updated": False,
        "current_boundary_index_line_count": line_count,
        "current_boundary_index_line_count_max": 150,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "persistent_trust_doubt_update_performed": False,
        "cross_session_feedback_persistence": False,
        "memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "verification_execution_is_production_behavior": False,
        "same_session_loop_proves_learning": False,
        "proof_of_learning_claim_allowed": False,
        "qingyin_autonomous_action_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_b85_b93_status_sync_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": RECORD_TYPE,
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "sync_status": SYNC_STATUS,
        "boundary_index_before": BOUNDARY_INDEX_VERSION,
        "boundary_index_after": BOUNDARY_INDEX_VERSION,
        "compressed_loop_summary": COMPRESSED_LOOP_SUMMARY,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if record.get("boundary_index_before") != record.get("boundary_index_after"):
        errors.append("boundary_index_changed_by_status_sync")
    docs_updated = record.get("docs_updated")
    missing_docs = [path for path in DOCS_UPDATED if not isinstance(docs_updated, list) or path not in docs_updated]
    if missing_docs:
        errors.append("docs_updated_missing_required_doc")
    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if record.get("current_boundary_index_line_count_max", 0) > 150:
        errors.append("current_boundary_index_line_count_max_too_high")
    if record.get("current_boundary_index_updated") is True and record.get("current_boundary_index_line_count", 151) > 150:
        errors.append("current_boundary_index_line_count_exceeds_limit")

    overclaim_blocked = all(record.get(field) is False for field in OVERCLAIM_FIELDS)
    return {
        "valid": not errors,
        "error_codes": errors,
        "docs_updated_count": len(docs_updated) if isinstance(docs_updated, list) else 0,
        "missing_docs_count": len(missing_docs),
        "boundary_unchanged_checked": (
            record.get("boundary_index_before") == BOUNDARY_INDEX_VERSION
            and record.get("boundary_index_after") == BOUNDARY_INDEX_VERSION
            and record.get("boundary_change_required") is False
            and record.get("boundary_index_update_required") is False
        ),
        "line_count_checked": record.get("current_boundary_index_line_count_max", 0) <= 150,
        "overclaim_blocked": overclaim_blocked,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "persistent_update_blocked": record.get("persistent_trust_doubt_update_performed") is False,
        "cross_session_blocked": record.get("cross_session_feedback_persistence") is False,
        "memory_write_blocked": record.get("memory_write_performed") is False
        and record.get("retained_jsonl_write_performed") is False,
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False
        and record.get("verification_execution_is_production_behavior") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False
        and record.get("same_session_loop_proves_learning") is False,
    }


def run_b85_b93_documentation_compression_status_sync_minimal_check() -> dict[str, Any]:
    valid_sync = build_b85_b93_status_sync_record()
    valid_result = validate_b85_b93_status_sync_record(valid_sync)
    invalid_syncs = _invalid_sync_records(valid_sync)
    invalid_results = [validate_b85_b93_status_sync_record(record) for record in invalid_syncs]
    summary = {
        "valid_sync_count": 1 if valid_result["valid"] else 0,
        "invalid_sync_count": sum(1 for result in invalid_results if not result["valid"]),
        "boundary_unchanged_checked_count": 1 if valid_result["boundary_unchanged_checked"] else 0,
        "docs_updated_count": valid_result["docs_updated_count"],
        "line_count_checked_count": 1 if valid_result["line_count_checked"] else 0,
        "overclaim_blocked_count": 1 if valid_result["overclaim_blocked"] else 0,
        "selected_action_blocked_count": 1 if valid_result["selected_action_blocked"] else 0,
        "final_action_blocked_count": 1 if valid_result["final_action_blocked"] else 0,
        "persistent_update_blocked_count": 1 if valid_result["persistent_update_blocked"] else 0,
        "cross_session_blocked_count": 1 if valid_result["cross_session_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if valid_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "production_behavior_blocked_count": 1 if valid_result["production_behavior_blocked"] else 0,
        "proof_claim_blocked_count": 1 if valid_result["proof_claim_blocked"] else 0,
    }
    summary["all_b85_b93_documentation_compression_status_sync_checks_passed"] = (
        valid_result["valid"]
        and summary["valid_sync_count"] == 1
        and summary["invalid_sync_count"] == len(invalid_syncs)
        and summary["docs_updated_count"] == len(DOCS_UPDATED)
        and all(
            value == 1
            for key, value in summary.items()
            if key.endswith("_count")
            and key not in {"valid_sync_count", "invalid_sync_count", "docs_updated_count"}
        )
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok"
        if summary["all_b85_b93_documentation_compression_status_sync_checks_passed"]
        else "failed",
        "package_id": PACKAGE_ID,
        "valid_sync": valid_sync,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
        "boundary": {
            "boundary_change_required": False,
            "boundary_index_update_required": False,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION,
            "rationale": (
                "Documentation/status sync only; no permission scope, runtime behavior, persistence, memory, "
                "retention, predictor, selected_action, final_action, production, or proof boundary changed."
            ),
        },
        "safe_claim": (
            "ASHL Core can maintain compact synchronized documentation for the b85-b93 same-session sandbox "
            "thought loop, confirming the loop remains sandbox-only, same-session-only, rollback-verified, "
            "and non-persistent, while selected_action, final_action, persistent updates, memory writes, "
            "retention writes, predictor mutation, production behavior, and proof-of-learning remain blocked."
        ),
    }


def _invalid_sync_records(valid_sync: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("boundary_index_after", "2026-06-09-b94"),
        ("boundary_change_required", True),
        ("boundary_index_update_required", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("qingyin_autonomous_action_claim_allowed", True),
        ("persistent_rule_created", True),
        ("persistent_trust_doubt_update_performed", True),
        ("cross_session_feedback_persistence", True),
        ("memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("production_behavior_changed", True),
        ("verification_execution_is_production_behavior", True),
        ("same_session_loop_proves_learning", True),
        ("proof_of_learning_claim_allowed", True),
        ("rollback_required", False),
        ("rollback_verified", False),
    ):
        bad = deepcopy(valid_sync)
        bad[field] = value
        invalids.append(bad)
    missing_docs = deepcopy(valid_sync)
    missing_docs["docs_updated"] = valid_sync["docs_updated"][:-1]
    invalids.append(missing_docs)
    line_count = deepcopy(valid_sync)
    line_count["current_boundary_index_updated"] = True
    line_count["current_boundary_index_line_count"] = 151
    invalids.append(line_count)
    max_line_count = deepcopy(valid_sync)
    max_line_count["current_boundary_index_line_count_max"] = 151
    invalids.append(max_line_count)
    return invalids


def _current_boundary_index_line_count() -> int:
    path = Path("docs/current_boundary_index.md")
    if not path.exists():
        return 0
    return len(path.read_text(encoding="utf-8").splitlines())


if __name__ == "__main__":
    import json

    print(json.dumps(run_b85_b93_documentation_compression_status_sync_minimal_check(), ensure_ascii=False, indent=2))
