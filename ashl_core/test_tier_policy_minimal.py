"""Workflow-only test tier policy for future Phase0 packages."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-test-tier-policy-minimal-check"
FLOW = "test_tier_policy_minimal_v0"
REQUIRED_FULL_REGRESSION_REASONS = (
    "selected_action_boundary_change",
    "final_action_boundary_change",
    "sandbox_execution_boundary_change",
    "memory_write_boundary_change",
    "retention_write_boundary_change",
    "predictor_mutation_boundary_change",
    "production_boundary_change",
    "release_or_progress_log_before_pause",
    "user_explicitly_requests_full_regression",
)
TRUE_FIELDS = (
    "targeted_tests_required",
    "smoke_required",
    "git_diff_check_required",
    "git_status_required",
    "full_unittest_discover_conditional",
    "full_unittest_skip_requires_reason",
    "policy_is_workflow_only",
    "audit_recorded",
)
FALSE_FIELDS = (
    "full_unittest_discover_default",
    "boundary_index_change_required_by_policy_only",
    "selected_action_created",
    "final_action_created_by_policy",
    "direct_command_created",
    "production_behavior_changed",
    "memory_write_performed",
    "retention_write_performed",
    "predictor_mutation_performed",
    "proof_of_learning_claim_allowed",
)


def build_test_tier_policy_record(
    full_unittest_discover_skipped: bool = False,
    full_unittest_skip_reason: str = "",
) -> dict[str, Any]:
    return {
        "record_type": "test_tier_policy",
        "record_version": "v0",
        "policy_status": "active_test_tier_policy",
        "default_package_test_tier": "targeted",
        "targeted_tests_required": True,
        "smoke_required": True,
        "git_diff_check_required": True,
        "git_status_required": True,
        "full_unittest_discover_default": False,
        "full_unittest_discover_conditional": True,
        "full_unittest_required_when": list(REQUIRED_FULL_REGRESSION_REASONS),
        "full_unittest_skip_requires_reason": True,
        "full_unittest_discover_skipped": full_unittest_discover_skipped,
        "full_unittest_skip_reason": full_unittest_skip_reason,
        "full_unittest_runtime_note": (
            "Full unittest discover is heavy and was observed around 3517 tests / about 205 seconds."
        ),
        "future_report_format": {
            "targeted_tests": [
                "py -3 -m unittest tests/test_<package>.py",
                "py -3 run_all_smoke_tests.py",
                "git diff --check",
                "git status --short",
            ],
            "full_regression": "py -3 -m unittest discover: PASS / skipped with reason",
        },
        "policy_is_workflow_only": True,
        "boundary_index_change_required_by_policy_only": False,
        "selected_action_created": False,
        "final_action_created_by_policy": False,
        "direct_command_created": False,
        "production_behavior_changed": False,
        "memory_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "proof_of_learning_claim_allowed": False,
        "audit_recorded": True,
    }


def validate_test_tier_policy_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "test_tier_policy",
        "record_version": "v0",
        "policy_status": "active_test_tier_policy",
        "default_package_test_tier": "targeted",
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if record.get("full_unittest_required_when") != list(REQUIRED_FULL_REGRESSION_REASONS):
        errors.append("full_unittest_required_when_not_expected")
    if record.get("full_unittest_discover_skipped") is True and not record.get(
        "full_unittest_skip_reason"
    ):
        errors.append("full_unittest_skipped_without_reason")
    return {
        "valid": not errors,
        "error_codes": errors,
        "test_policy_checked": (
            record.get("default_package_test_tier") == "targeted"
            and record.get("targeted_tests_required") is True
            and record.get("smoke_required") is True
        ),
        "full_regression_policy_checked": (
            record.get("full_unittest_discover_default") is False
            and record.get("full_unittest_discover_conditional") is True
            and record.get("full_unittest_skip_requires_reason") is True
        ),
        "policy_boundary_blocked": record.get("boundary_index_change_required_by_policy_only") is False,
        "runtime_boundary_blocked": (
            record.get("selected_action_created") is False
            and record.get("final_action_created_by_policy") is False
            and record.get("direct_command_created") is False
        ),
    }


def run_test_tier_policy_minimal_check() -> dict[str, Any]:
    valid_policy = build_test_tier_policy_record()
    valid_result = validate_test_tier_policy_record(valid_policy)
    invalid_policies = _invalid_policies(valid_policy)
    invalid_results = [validate_test_tier_policy_record(item) for item in invalid_policies]
    summary = {
        "valid_test_policy_count": 1 if valid_result["valid"] else 0,
        "invalid_test_policy_count": sum(1 for result in invalid_results if not result["valid"]),
        "test_policy_checked_count": 1 if valid_result["test_policy_checked"] else 0,
        "full_regression_policy_checked_count": (
            1 if valid_result["full_regression_policy_checked"] else 0
        ),
        "policy_boundary_blocked_count": 1 if valid_result["policy_boundary_blocked"] else 0,
        "runtime_boundary_blocked_count": 1 if valid_result["runtime_boundary_blocked"] else 0,
    }
    summary["all_test_tier_policy_checks_passed"] = (
        valid_result["valid"]
        and summary["invalid_test_policy_count"] == len(invalid_policies)
        and summary["valid_test_policy_count"] == 1
        and summary["test_policy_checked_count"] == 1
        and summary["full_regression_policy_checked_count"] == 1
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_test_tier_policy_checks_passed"] else "failed",
        "valid_policy": valid_policy,
        "valid_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
    }


def _invalid_policies(valid_policy: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("full_unittest_discover_default", True),
        ("full_unittest_discover_conditional", False),
        ("full_unittest_skip_requires_reason", False),
        ("boundary_index_change_required_by_policy_only", True),
        ("policy_is_workflow_only", False),
        ("selected_action_created", True),
        ("final_action_created_by_policy", True),
        ("direct_command_created", True),
        ("production_behavior_changed", True),
        ("memory_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("proof_of_learning_claim_allowed", True),
    ):
        bad = deepcopy(valid_policy)
        bad[field] = value
        invalids.append(bad)
    bad = deepcopy(valid_policy)
    bad["full_unittest_discover_skipped"] = True
    bad["full_unittest_skip_reason"] = ""
    invalids.append(bad)
    bad = deepcopy(valid_policy)
    bad["full_unittest_required_when"] = ["every_package"]
    invalids.append(bad)
    return invalids
