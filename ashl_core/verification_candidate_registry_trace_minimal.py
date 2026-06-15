"""Trace-only registry for bounded verification candidates."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .doubt_action_trace_minimal import build_doubt_action_trace, validate_doubt_action_trace
from .doubt_gated_sandbox_candidate_ordering_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as DOUBT_GATED_ORDERING_BOUNDARY,
    build_doubt_gated_candidate_ordering_record,
    validate_doubt_gated_candidate_ordering_record,
)


COMMAND = "run-verification-candidate-registry-trace-minimal-check"
FLOW = "verification_candidate_registry_trace_minimal_v0"
PACKAGE_ID = "PKG-Phase0-VerificationCandidateRegistryTrace-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = "2026-06-09-b87"
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b88"
REQUIRED_CANDIDATE_IDS = [
    "observe_or_alternative_probe",
    "inspect_device",
    "check_before_retry",
    "retry_limited",
    "fallback_stop_and_report",
]
COMMON_FORBIDDEN_IF = [
    "requires_real_world_tool",
    "requires_production_action",
    "requires_final_action",
    "requires_memory_write",
]


def build_verification_candidate(candidate_id: str = "observe_or_alternative_probe") -> dict[str, Any]:
    specs = {
        "observe_or_alternative_probe": {
            "candidate_type": "low_risk_probe",
            "risk_level": "low",
            "stop_condition": "local_context_observed_or_budget_used",
            "expected_probe_outcome": "local_context_observed_or_alternative_checked",
            "allowed_sandbox_scope": ["phase0_level3_sandbox_only"],
        },
        "inspect_device": {
            "candidate_type": "low_risk_probe",
            "risk_level": "low",
            "stop_condition": "inspection_result_recorded_or_budget_used",
            "expected_probe_outcome": "fault_or_context_information_observed",
            "allowed_sandbox_scope": ["phase0_level3_sandbox_only", "phase0_level3_toy_repair_sandbox_only"],
        },
        "check_before_retry": {
            "candidate_type": "safety_check",
            "risk_level": "low",
            "stop_condition": "risk_or_blocker_checked_or_budget_used",
            "expected_probe_outcome": "risk_or_blocker_checked_before_retry",
            "allowed_sandbox_scope": ["phase0_level3_sandbox_only"],
        },
        "retry_limited": {
            "candidate_type": "bounded_retry_probe",
            "risk_level": "medium",
            "stop_condition": "one_retry_attempt_or_failure_observed",
            "expected_probe_outcome": "retry_result_observed_within_budget",
            "allowed_sandbox_scope": ["phase0_level3_sandbox_only"],
            "forbidden_if_extra": ["high_risk_action"],
        },
        "fallback_stop_and_report": {
            "candidate_type": "conservative_fallback",
            "risk_level": "low",
            "stop_condition": "unsafe_or_uncertain_context_reported_or_budget_used",
            "expected_probe_outcome": "unsafe_or_uncertain_context_reported",
            "allowed_sandbox_scope": ["phase0_level3_sandbox_only"],
        },
    }
    if candidate_id not in specs:
        return {
            "record_type": "verification_candidate",
            "record_version": "v0",
            "candidate_id": candidate_id,
            "candidate_type": "free_form_candidate",
            "risk_level": "high",
            "reversible": False,
            "max_attempts": 1,
            "stop_condition": "",
            "expected_probe_outcome": "",
            "forbidden_if": [],
            "allowed_sandbox_scope": [],
            "execution_allowed": False,
            "trace_only": True,
            "llm_used": False,
        }
    spec = specs[candidate_id]
    forbidden_if = list(COMMON_FORBIDDEN_IF) + list(spec.get("forbidden_if_extra", []))
    return {
        "record_type": "verification_candidate",
        "record_version": "v0",
        "candidate_id": candidate_id,
        "candidate_type": spec["candidate_type"],
        "risk_level": spec["risk_level"],
        "reversible": True,
        "max_attempts": 1,
        "stop_condition": spec["stop_condition"],
        "expected_probe_outcome": spec["expected_probe_outcome"],
        "forbidden_if": forbidden_if,
        "allowed_sandbox_scope": list(spec["allowed_sandbox_scope"]),
        "execution_allowed": False,
        "trace_only": True,
        "llm_used": False,
    }


def validate_verification_candidate(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "verification_candidate":
        errors.append("record_type_not_verification_candidate")
    candidate_id = record.get("candidate_id")
    if not isinstance(candidate_id, str) or not candidate_id:
        errors.append("candidate_id_missing")
    if candidate_id not in REQUIRED_CANDIDATE_IDS:
        errors.append("candidate_not_registered")
    if record.get("candidate_type") == "free_form_candidate":
        errors.append("free_form_candidate_not_allowed")
    if record.get("risk_level") not in {"low", "medium"}:
        errors.append("risk_level_not_allowed")
    if record.get("risk_level") == "low" and record.get("reversible") is False:
        errors.append("low_risk_irreversible_without_justification")
    if not isinstance(record.get("reversible"), bool):
        errors.append("reversible_not_bool")
    if not isinstance(record.get("max_attempts"), int) or record.get("max_attempts", -1) < 0:
        errors.append("max_attempts_invalid")
    if candidate_id == "retry_limited" and record.get("max_attempts") != 1:
        errors.append("retry_limited_max_attempts_not_one")
    if not isinstance(record.get("stop_condition"), str) or not record.get("stop_condition"):
        errors.append("stop_condition_missing")
    if not isinstance(record.get("expected_probe_outcome"), str) or not record.get("expected_probe_outcome"):
        errors.append("expected_probe_outcome_missing")
    if not isinstance(record.get("allowed_sandbox_scope"), list) or not record.get("allowed_sandbox_scope"):
        errors.append("allowed_sandbox_scope_missing")
    if record.get("execution_allowed") is not False:
        errors.append("execution_allowed_not_false")
    if record.get("trace_only") is not True:
        errors.append("trace_only_not_true")
    if record.get("llm_used") is not False:
        errors.append("llm_used_not_false")
    if "high_risk_action" in record.get("forbidden_if", []) and candidate_id != "retry_limited":
        errors.append("high_risk_candidate_allowed")
    return {
        "valid": not errors,
        "error_codes": errors,
        "execution_blocked": record.get("execution_allowed") is False,
        "trace_only_checked": record.get("trace_only") is True,
        "llm_blocked": record.get("llm_used") is False,
        "registered_candidate_checked": candidate_id in REQUIRED_CANDIDATE_IDS,
    }


def build_verification_candidate_registry() -> dict[str, Any]:
    candidates = [build_verification_candidate(candidate_id) for candidate_id in REQUIRED_CANDIDATE_IDS]
    return {
        "record_type": "verification_candidate_registry",
        "record_version": "v0",
        "registry_status": "valid_verification_candidate_registry",
        "candidate_count": len(candidates),
        "candidate_ids": list(REQUIRED_CANDIDATE_IDS),
        "candidates": candidates,
        "all_candidates_trace_only": True,
        "all_candidates_have_stop_condition": True,
        "all_candidates_have_risk_level": True,
        "all_candidates_have_allowed_scope": True,
        "all_candidates_execution_blocked": True,
        "free_form_candidates_allowed": False,
        "llm_generated_candidates_allowed": False,
        "audit_recorded": True,
    }


def validate_verification_candidate_registry(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    candidates = record.get("candidates", [])
    candidate_ids = record.get("candidate_ids", [])
    candidate_results = [validate_verification_candidate(c) for c in candidates if isinstance(c, dict)]
    if record.get("record_type") != "verification_candidate_registry":
        errors.append("record_type_not_registry")
    if record.get("candidate_count", 0) < len(REQUIRED_CANDIDATE_IDS):
        errors.append("candidate_count_too_low")
    for candidate_id in REQUIRED_CANDIDATE_IDS:
        if candidate_id not in candidate_ids:
            errors.append(f"{candidate_id}_missing")
    expected_flags = (
        "all_candidates_trace_only",
        "all_candidates_have_stop_condition",
        "all_candidates_have_risk_level",
        "all_candidates_have_allowed_scope",
        "all_candidates_execution_blocked",
        "audit_recorded",
    )
    for field in expected_flags:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    if record.get("free_form_candidates_allowed") is not False:
        errors.append("free_form_candidates_allowed_not_false")
    if record.get("llm_generated_candidates_allowed") is not False:
        errors.append("llm_generated_candidates_allowed_not_false")
    if len(candidate_results) != len(candidates) or not all(result["valid"] for result in candidate_results):
        errors.append("candidate_validation_failed")
    return {
        "valid": not errors,
        "error_codes": errors,
        "registered_candidate_checked": all(candidate_id in candidate_ids for candidate_id in REQUIRED_CANDIDATE_IDS),
        "free_form_candidate_blocked": record.get("free_form_candidates_allowed") is False,
        "execution_blocked": record.get("all_candidates_execution_blocked") is True,
    }


def build_verification_candidate_trace(
    selected_verification_candidate_id: str = "observe_or_alternative_probe",
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_trace = build_doubt_action_trace()
    if not validate_doubt_action_trace(source_trace)["valid"]:
        raise ValueError("invalid_doubt_action_trace_source")
    source_registry = deepcopy(registry) if registry is not None else build_verification_candidate_registry()
    if not validate_verification_candidate_registry(source_registry)["valid"]:
        raise ValueError("invalid_verification_candidate_registry")
    candidate = _candidate_by_id(source_registry, selected_verification_candidate_id)
    if candidate is None:
        candidate = build_verification_candidate(selected_verification_candidate_id)
    return {
        "record_type": "verification_candidate_trace",
        "record_version": "v0",
        "trace_status": "valid_registered_verification_candidate_trace",
        "source_doubt_action_trace": "doubt_action_trace_b86",
        "source_doubt_gated_ordering": "doubt_gated_ordering_b87",
        "source_registry_record_type": "verification_candidate_registry",
        "trigger": "expected_actual_mismatch",
        "expected_outcome": source_trace["expected_outcome"],
        "actual_outcome": source_trace["actual_outcome"],
        "selected_verification_candidate_id": selected_verification_candidate_id,
        "candidate_found_in_registry": _candidate_by_id(source_registry, selected_verification_candidate_id) is not None,
        "candidate_risk_level": candidate.get("risk_level"),
        "candidate_reversible": candidate.get("reversible"),
        "candidate_max_attempts": candidate.get("max_attempts"),
        "candidate_stop_condition": candidate.get("stop_condition"),
        "candidate_expected_probe_outcome": candidate.get("expected_probe_outcome"),
        "verification_action_executed": False,
        "ordering_reference_only": True,
        "trace_only": True,
        "llm_used": False,
        "selected_action_created": False,
        "final_action_created": False,
        "direct_command_created": False,
        "persistent_rule_created": False,
        "long_term_memory_write_performed": False,
        "retained_jsonl_write_performed": False,
        "retention_write_performed": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "autonomous_learning_claim_allowed": False,
        "autonomous_action_claim_allowed": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_registry": source_registry,
    }


def validate_verification_candidate_trace(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    registry = record.get("source_registry", {})
    selected = record.get("selected_verification_candidate_id")
    candidate = _candidate_by_id(registry, selected) if isinstance(registry, dict) else None
    if record.get("record_type") != "verification_candidate_trace":
        errors.append("record_type_not_trace")
    if record.get("candidate_found_in_registry") is not True or candidate is None:
        errors.append("candidate_not_found_in_registry")
    if record.get("candidate_risk_level") not in {"low", "medium"}:
        errors.append("candidate_risk_level_not_allowed")
    if not record.get("candidate_stop_condition"):
        errors.append("candidate_stop_condition_missing")
    if not record.get("candidate_expected_probe_outcome"):
        errors.append("candidate_expected_probe_outcome_missing")
    if record.get("verification_action_executed") is not False:
        errors.append("verification_action_executed_not_false")
    for field in (
        "ordering_reference_only",
        "trace_only",
        "audit_recorded",
        "rollback_available",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    for field in (
        "llm_used",
        "selected_action_created",
        "final_action_created",
        "direct_command_created",
        "persistent_rule_created",
        "long_term_memory_write_performed",
        "retained_jsonl_write_performed",
        "retention_write_performed",
        "predictor_mutation_performed",
        "production_behavior_changed",
        "proof_of_learning_claim_allowed",
        "autonomous_learning_claim_allowed",
        "autonomous_action_claim_allowed",
    ):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    return {
        "valid": not errors,
        "error_codes": errors,
        "registered_candidate_checked": candidate is not None,
        "execution_blocked": record.get("verification_action_executed") is False,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "persistent_rule_blocked": record.get("persistent_rule_created") is False,
        "memory_write_blocked": (
            record.get("long_term_memory_write_performed") is False
            and record.get("retained_jsonl_write_performed") is False
        ),
        "retention_blocked": record.get("retention_write_performed") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def validate_doubt_gated_ordering_uses_registered_candidate(
    ordering_record: dict[str, Any] | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ordering = deepcopy(ordering_record) if ordering_record is not None else build_doubt_gated_candidate_ordering_record()
    source_registry = deepcopy(registry) if registry is not None else build_verification_candidate_registry()
    errors: list[str] = []
    if not validate_doubt_gated_candidate_ordering_record(ordering)["valid"]:
        errors.append("doubt_gated_ordering_invalid")
    if not validate_verification_candidate_registry(source_registry)["valid"]:
        errors.append("registry_invalid")
    registry_ids = set(source_registry.get("candidate_ids", []))
    verification_candidates = [
        action
        for action in ordering.get("candidate_actions_after_ordering", [])
        if action not in {"retry_same_action_without_check", "fallback_stop_and_report"}
    ]
    unregistered = [candidate for candidate in verification_candidates if candidate not in registry_ids]
    if unregistered:
        errors.append("unregistered_candidate_referenced")
    if ordering.get("verification_action_executed") is not False:
        errors.append("verification_action_executed_not_false")
    if DOUBT_GATED_ORDERING_BOUNDARY != "2026-06-09-b87":
        errors.append("b87_doubt_gated_ordering_source_missing")
    return {
        "valid": not errors,
        "error_codes": errors,
        "b87_ordering_reference_checked": not errors,
        "unregistered_candidate_blocked": bool(unregistered),
        "referenced_candidates": verification_candidates,
        "unregistered_candidates": unregistered,
    }


def run_verification_candidate_registry_trace_minimal_check() -> dict[str, Any]:
    candidates = [build_verification_candidate(candidate_id) for candidate_id in REQUIRED_CANDIDATE_IDS]
    candidate_results = [validate_verification_candidate(candidate) for candidate in candidates]
    registry = build_verification_candidate_registry()
    registry_result = validate_verification_candidate_registry(registry)
    trace = build_verification_candidate_trace("observe_or_alternative_probe", registry)
    trace_result = validate_verification_candidate_trace(trace)
    ordering_result = validate_doubt_gated_ordering_uses_registered_candidate(registry=registry)
    invalid_candidates = _invalid_candidates(candidates)
    invalid_candidate_results = [validate_verification_candidate(candidate) for candidate in invalid_candidates]
    invalid_registries = _invalid_registries(registry)
    invalid_registry_results = [validate_verification_candidate_registry(item) for item in invalid_registries]
    invalid_traces = _invalid_traces(trace)
    invalid_trace_results = [validate_verification_candidate_trace(item) for item in invalid_traces]
    invalid_ordering = build_doubt_gated_candidate_ordering_record()
    invalid_ordering["candidate_actions_after_ordering"] = ["free_form_probe", "retry_same_action_without_check"]
    invalid_ordering_result = validate_doubt_gated_ordering_uses_registered_candidate(invalid_ordering, registry)
    summary = {
        "valid_candidate_count": sum(1 for result in candidate_results if result["valid"]),
        "invalid_candidate_count": sum(1 for result in invalid_candidate_results if not result["valid"]),
        "valid_registry_count": 1 if registry_result["valid"] else 0,
        "invalid_registry_count": sum(1 for result in invalid_registry_results if not result["valid"]),
        "valid_trace_count": 1 if trace_result["valid"] else 0,
        "invalid_trace_count": sum(1 for result in invalid_trace_results if not result["valid"]),
        "registered_candidate_checked_count": 1 if trace_result["registered_candidate_checked"] else 0,
        "b87_ordering_reference_checked_count": 1 if ordering_result["valid"] else 0,
        "unregistered_candidate_blocked_count": 1 if invalid_ordering_result["unregistered_candidate_blocked"] else 0,
        "free_form_candidate_blocked_count": 1 if any("free_form_candidate_not_allowed" in r["error_codes"] for r in invalid_candidate_results) else 0,
        "execution_blocked_count": 1 if trace_result["execution_blocked"] else 0,
        "selected_action_blocked_count": 1 if trace_result["selected_action_blocked"] else 0,
        "final_action_blocked_count": 1 if trace_result["final_action_blocked"] else 0,
        "persistent_rule_blocked_count": 1 if trace_result["persistent_rule_blocked"] else 0,
        "memory_write_blocked_count": 1 if trace_result["memory_write_blocked"] else 0,
        "retention_blocked_count": 1 if trace_result["retention_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if trace_result["predictor_mutation_blocked"] else 0,
        "proof_claim_blocked_count": 1 if trace_result["proof_claim_blocked"] else 0,
    }
    summary["all_verification_candidate_registry_trace_checks_passed"] = (
        summary["valid_candidate_count"] == len(REQUIRED_CANDIDATE_IDS)
        and summary["invalid_candidate_count"] == len(invalid_candidates)
        and summary["valid_registry_count"] == 1
        and summary["invalid_registry_count"] == len(invalid_registries)
        and summary["valid_trace_count"] == 1
        and summary["invalid_trace_count"] == len(invalid_traces)
        and all(value == 1 for key, value in summary.items() if key.endswith("_count") and key not in {"valid_candidate_count", "invalid_candidate_count", "invalid_registry_count", "invalid_trace_count"})
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_verification_candidate_registry_trace_checks_passed"] else "failed",
        "package_id": PACKAGE_ID,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package introduces a validation boundary for named low-risk verification candidates."
            ),
        },
        "valid_candidates": candidates,
        "valid_registry": registry,
        "valid_trace": trace,
        "b87_ordering_reference_result": ordering_result,
        "summary": summary,
    }


def _candidate_by_id(registry: dict[str, Any], candidate_id: str) -> dict[str, Any] | None:
    for candidate in registry.get("candidates", []):
        if isinstance(candidate, dict) and candidate.get("candidate_id") == candidate_id:
            return candidate
    return None


def _invalid_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base = candidates[0]
    retry = next(candidate for candidate in candidates if candidate["candidate_id"] == "retry_limited")
    invalids = []
    for field, value in (
        ("risk_level", None),
        ("stop_condition", ""),
        ("expected_probe_outcome", ""),
        ("allowed_sandbox_scope", []),
        ("candidate_id", "free_form_probe"),
        ("candidate_type", "free_form_candidate"),
        ("llm_used", True),
        ("execution_allowed", True),
        ("trace_only", False),
        ("reversible", False),
    ):
        bad = deepcopy(base)
        bad[field] = value
        invalids.append(bad)
    bad_retry = deepcopy(retry)
    bad_retry["max_attempts"] = 2
    invalids.append(bad_retry)
    high_risk = deepcopy(base)
    high_risk["risk_level"] = "high"
    invalids.append(high_risk)
    return invalids


def _invalid_registries(registry: dict[str, Any]) -> list[dict[str, Any]]:
    invalids = []
    for field, value in (
        ("candidate_count", 4),
        ("all_candidates_trace_only", False),
        ("all_candidates_have_stop_condition", False),
        ("all_candidates_have_risk_level", False),
        ("all_candidates_have_allowed_scope", False),
        ("all_candidates_execution_blocked", False),
        ("free_form_candidates_allowed", True),
        ("llm_generated_candidates_allowed", True),
    ):
        bad = deepcopy(registry)
        bad[field] = value
        invalids.append(bad)
    missing = deepcopy(registry)
    missing["candidate_ids"] = ["observe_or_alternative_probe"]
    invalids.append(missing)
    return invalids


def _invalid_traces(trace: dict[str, Any]) -> list[dict[str, Any]]:
    invalids = []
    for field, value in (
        ("selected_verification_candidate_id", "free_form_probe"),
        ("candidate_found_in_registry", False),
        ("verification_action_executed", True),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("direct_command_created", True),
        ("persistent_rule_created", True),
        ("long_term_memory_write_performed", True),
        ("retained_jsonl_write_performed", True),
        ("retention_write_performed", True),
        ("predictor_mutation_performed", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("autonomous_learning_claim_allowed", True),
        ("autonomous_action_claim_allowed", True),
        ("llm_used", True),
    ):
        bad = deepcopy(trace)
        bad[field] = value
        invalids.append(bad)
    return invalids
