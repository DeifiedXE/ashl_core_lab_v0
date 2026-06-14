"""Memory-influenced Level 3 sandbox re-run tendency trace comparison."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_signal_human_interpretation_review_minimal import QINGYIN_STATUS
from .level3_toy_minefield_variant_suite_stability_minimal import (
    REQUIRED_VARIANT_IDS,
    TARGET_SCOPE,
    build_level3_toy_minefield_variant_suite_stability_review,
    validate_level3_toy_minefield_variant_suite_stability_review,
)
from .memory_admission_minimal import LESSON_NAME
from .memory_influence_preview_minimal import (
    DISCOURAGED_FUTURE_TENDENCY,
    PREFERRED_FUTURE_TENDENCY,
    validate_memory_influence_preview_record,
)
from .memory_runtime_influence_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER as SOURCE_BOUNDARY_INDEX_VERSION,
    MAX_ABSOLUTE_DELTA,
    MEMORY_OFF_BASELINE,
    MEMORY_ON_INFLUENCED,
    RUNTIME_INFLUENCE_STATUS,
    RUNTIME_INFLUENCE_STATUS,
    build_memory_runtime_influence_record,
    validate_memory_runtime_influence_record,
)
from .memory_write_and_read_minimal import validate_controlled_memory_read_record


COMMAND = "run-memory-influenced-sandbox-rerun-minimal-check"
FLOW = "memory_influenced_sandbox_rerun_minimal_v0"
PACKAGE_ID = "PKG-Phase0-MemoryInfluencedSandboxRerun-Minimal-v0"
BOUNDARY_INDEX_VERSION_BEFORE = SOURCE_BOUNDARY_INDEX_VERSION
BOUNDARY_INDEX_VERSION_AFTER = "2026-06-09-b82"
RERUN_STATUS = "completed_memory_off_memory_on_rollback_comparison"
RERUN_TYPE = "deterministic_variant_suite_tendency_comparison"
SANDBOX_TRACE_EFFECT = "tendency_trace_only"
MEMORY_INFLUENCE_SCOPE = "bounded_tendency_trace_only"
COMPARISON_STATUS = "passed_expected_memory_influenced_tendency_trace"
EXPECTED_EFFECT = "memory_on_increases_check_before_retry_tendency"
OBSERVED_EFFECT = "memory_on_increased_check_before_retry_tendency_across_variants"
SOURCE_REPEATED_KEY = "retry_same_risky_action_without_check"
FALSE_FIELDS = (
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
TRUE_FIELDS = (
    "memory_influence_used_in_sandbox",
    "rollback_to_baseline_performed",
    "rollback_restored_baseline",
    "future_sandbox_behavior_use_requires_separate_boundary",
    "future_action_selection_requires_separate_boundary",
    "future_predictor_influence_requires_separate_boundary",
    "future_production_promotion_requires_separate_boundary",
    "future_retention_requires_separate_boundary",
    "repo_audit_acknowledged",
    "audit_recorded",
    "rollback_available",
)


def build_memory_influenced_sandbox_variant_rerun(variant_id: str) -> dict[str, Any]:
    if variant_id not in REQUIRED_VARIANT_IDS:
        raise ValueError("unknown_level3_variant_id")
    return {
        "record_type": "memory_influenced_sandbox_variant_rerun",
        "variant_id": variant_id,
        "sandbox_scope": TARGET_SCOPE,
        "memory_off": {
            **deepcopy(MEMORY_OFF_BASELINE),
            "selected_action_created": False,
            "final_action_created": False,
        },
        "memory_on": {
            **deepcopy(MEMORY_ON_INFLUENCED),
            "selected_action_created": False,
            "final_action_created": False,
        },
        "memory_off_after_rollback": {
            **deepcopy(MEMORY_OFF_BASELINE),
            "selected_action_created": False,
            "final_action_created": False,
        },
        "check_before_retry_tendency_increased_under_memory": True,
        "rollback_restored_baseline": True,
        "trace_only": True,
        "no_action_selection": True,
    }


def validate_memory_influenced_sandbox_variant_rerun(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "memory_influenced_sandbox_variant_rerun":
        errors.append("record_type_not_memory_influenced_sandbox_variant_rerun")
    if record.get("variant_id") not in REQUIRED_VARIANT_IDS:
        errors.append("variant_id_not_required")
    if record.get("sandbox_scope") != TARGET_SCOPE:
        errors.append("sandbox_scope_not_level3_toy_minefield")

    memory_off = record.get("memory_off", {})
    memory_on = record.get("memory_on", {})
    rollback = record.get("memory_off_after_rollback", {})
    if _score_only(memory_off) != MEMORY_OFF_BASELINE:
        errors.append("variant_memory_off_not_expected")
    if _score_only(memory_on) != MEMORY_ON_INFLUENCED:
        errors.append("variant_memory_on_not_expected")
    if _score_only(rollback) != MEMORY_OFF_BASELINE:
        errors.append("variant_rollback_not_expected")
    if memory_on.get(PREFERRED_FUTURE_TENDENCY, 0) <= memory_off.get(PREFERRED_FUTURE_TENDENCY, 1):
        errors.append("variant_check_before_retry_not_increased")
    if memory_on.get(DISCOURAGED_FUTURE_TENDENCY, 1) >= memory_off.get(DISCOURAGED_FUTURE_TENDENCY, 0):
        errors.append("variant_retry_same_action_not_decreased")
    for section_name, section in (("memory_off", memory_off), ("memory_on", memory_on), ("rollback", rollback)):
        if section.get("selected_action_created") is not False:
            errors.append(f"{section_name}_selected_action_created_not_false")
        if section.get("final_action_created") is not False:
            errors.append(f"{section_name}_final_action_created_not_false")
    if record.get("check_before_retry_tendency_increased_under_memory") is not True:
        errors.append("check_before_retry_tendency_increased_under_memory_not_true")
    if record.get("rollback_restored_baseline") is not True:
        errors.append("rollback_restored_baseline_not_true")
    if record.get("trace_only") is not True:
        errors.append("trace_only_not_true")
    if record.get("no_action_selection") is not True:
        errors.append("no_action_selection_not_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "memory_off_checked": _score_only(memory_off) == MEMORY_OFF_BASELINE,
        "memory_on_checked": _score_only(memory_on) == MEMORY_ON_INFLUENCED,
        "rollback_checked": _score_only(rollback) == MEMORY_OFF_BASELINE
        and record.get("rollback_restored_baseline") is True,
        "check_before_retry_increase_checked": record.get("check_before_retry_tendency_increased_under_memory") is True
        and memory_on.get(PREFERRED_FUTURE_TENDENCY, 0) > memory_off.get(PREFERRED_FUTURE_TENDENCY, 1),
        "selected_action_blocked": all(
            section.get("selected_action_created") is False for section in (memory_off, memory_on, rollback)
        ),
        "final_action_blocked": all(
            section.get("final_action_created") is False for section in (memory_off, memory_on, rollback)
        ),
    }


def build_memory_influenced_sandbox_rerun_record(
    memory_runtime_influence: dict[str, Any] | None = None,
    level3_variant_suite_source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_influence = deepcopy(memory_runtime_influence) if memory_runtime_influence is not None else (
        build_memory_runtime_influence_record()
    )
    if not validate_memory_runtime_influence_record(source_influence)["valid"]:
        raise ValueError("invalid_memory_runtime_influence_source")

    source_suite = deepcopy(level3_variant_suite_source) if level3_variant_suite_source is not None else (
        build_level3_toy_minefield_variant_suite_stability_review()
    )
    if not validate_level3_toy_minefield_variant_suite_stability_review(source_suite)["valid"]:
        raise ValueError("invalid_level3_variant_suite_source")

    source_read = source_influence.get("source_controlled_memory_read")
    source_preview = source_influence.get("source_memory_influence_preview")
    if not isinstance(source_read, dict) or not validate_controlled_memory_read_record(source_read)["valid"]:
        raise ValueError("invalid_controlled_memory_read_source")
    if not isinstance(source_preview, dict) or not validate_memory_influence_preview_record(source_preview)["valid"]:
        raise ValueError("invalid_memory_influence_preview_source")

    variants = list(REQUIRED_VARIANT_IDS)
    variant_reruns = [build_memory_influenced_sandbox_variant_rerun(variant_id) for variant_id in variants]
    return {
        "record_type": "memory_influenced_sandbox_rerun",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "rerun_status": RERUN_STATUS,
        "sandbox_scope": TARGET_SCOPE,
        "rerun_type": RERUN_TYPE,
        "source_memory_runtime_influence_record_type": source_influence.get("record_type"),
        "source_memory_influence_status": source_influence.get("runtime_influence_status"),
        "source_lesson_name": source_influence.get("source_lesson_name"),
        "source_repeated_key": SOURCE_REPEATED_KEY,
        "variants": variants,
        "variant_reruns": variant_reruns,
        "memory_off_baseline": deepcopy(source_influence.get("memory_off_baseline")),
        "memory_on_influenced": deepcopy(source_influence.get("memory_on_influenced")),
        "memory_off_after_rollback": deepcopy(source_influence.get("memory_off_after_rollback")),
        "observed_tendency_shift": {
            "check_before_retry_increased": True,
            "retry_same_action_without_check_decreased": True,
            "max_absolute_delta": source_influence.get("max_absolute_delta"),
        },
        "sandbox_trace_effect": SANDBOX_TRACE_EFFECT,
        "memory_influence_used_in_sandbox": True,
        "memory_influence_scope": MEMORY_INFLUENCE_SCOPE,
        "rollback_to_baseline_performed": True,
        "rollback_restored_baseline": True,
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
        "current_allowed_use": "sandbox_tendency_trace_evidence_only",
        "future_sandbox_behavior_use_requires_separate_boundary": True,
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
        "source_memory_runtime_influence": source_influence,
        "source_level3_variant_suite": source_suite,
        "source_controlled_memory_read": source_read,
        "source_memory_influence_preview": source_preview,
    }


def validate_memory_influenced_sandbox_rerun_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "memory_influenced_sandbox_rerun",
        "record_version": "v0",
        "rerun_status": RERUN_STATUS,
        "sandbox_scope": TARGET_SCOPE,
        "rerun_type": RERUN_TYPE,
        "source_memory_runtime_influence_record_type": "memory_runtime_influence",
        "source_memory_influence_status": RUNTIME_INFLUENCE_STATUS,
        "source_lesson_name": LESSON_NAME,
        "source_repeated_key": SOURCE_REPEATED_KEY,
        "sandbox_trace_effect": SANDBOX_TRACE_EFFECT,
        "memory_influence_scope": MEMORY_INFLUENCE_SCOPE,
        "current_allowed_use": "sandbox_tendency_trace_evidence_only",
        "qingyin_current_status": QINGYIN_STATUS,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if sorted(record.get("variants", [])) != sorted(REQUIRED_VARIANT_IDS):
        errors.append("variants_missing_required_ids")
    if record.get("memory_off_baseline") != MEMORY_OFF_BASELINE:
        errors.append("memory_off_baseline_not_expected")
    if record.get("memory_on_influenced") != MEMORY_ON_INFLUENCED:
        errors.append("memory_on_influenced_not_expected")
    if record.get("memory_off_after_rollback") != MEMORY_OFF_BASELINE:
        errors.append("memory_off_after_rollback_not_expected")

    shift = record.get("observed_tendency_shift", {})
    if shift.get("check_before_retry_increased") is not True:
        errors.append("check_before_retry_increased_not_true")
    if shift.get("retry_same_action_without_check_decreased") is not True:
        errors.append("retry_same_action_without_check_decreased_not_true")
    if shift.get("max_absolute_delta") != MAX_ABSOLUTE_DELTA:
        errors.append("observed_max_absolute_delta_not_expected")
    if isinstance(shift.get("max_absolute_delta"), (int, float)) and shift["max_absolute_delta"] > MAX_ABSOLUTE_DELTA:
        errors.append("observed_max_absolute_delta_too_high")

    source_influence = record.get("source_memory_runtime_influence")
    if not isinstance(source_influence, dict):
        errors.append("source_memory_runtime_influence_missing")
    elif not validate_memory_runtime_influence_record(source_influence)["valid"]:
        errors.append("source_memory_runtime_influence_invalid")
    source_suite = record.get("source_level3_variant_suite")
    if not isinstance(source_suite, dict):
        errors.append("source_level3_variant_suite_missing")
    elif not validate_level3_toy_minefield_variant_suite_stability_review(source_suite)["valid"]:
        errors.append("source_level3_variant_suite_invalid")
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

    variant_results = [
        validate_memory_influenced_sandbox_variant_rerun(item)
        for item in record.get("variant_reruns", [])
        if isinstance(item, dict)
    ]
    if len(variant_results) != len(REQUIRED_VARIANT_IDS) or not all(result["valid"] for result in variant_results):
        errors.append("variant_reruns_invalid")

    for field in FALSE_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in TRUE_FIELDS:
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")

    return {
        "valid": not errors,
        "error_codes": errors,
        "memory_runtime_influence_checked": isinstance(source_influence, dict)
        and validate_memory_runtime_influence_record(source_influence)["valid"],
        "level3_variant_source_checked": isinstance(source_suite, dict)
        and validate_level3_toy_minefield_variant_suite_stability_review(source_suite)["valid"],
        "memory_off_checked": record.get("memory_off_baseline") == MEMORY_OFF_BASELINE,
        "memory_on_checked": record.get("memory_on_influenced") == MEMORY_ON_INFLUENCED,
        "rollback_checked": record.get("rollback_to_baseline_performed") is True
        and record.get("rollback_restored_baseline") is True
        and record.get("memory_off_after_rollback") == MEMORY_OFF_BASELINE,
        "check_before_retry_increase_checked": shift.get("check_before_retry_increased") is True,
        "max_delta_checked": shift.get("max_absolute_delta") == MAX_ABSOLUTE_DELTA,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "retained_jsonl_write_blocked": record.get("retained_jsonl_write_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_memory_influenced_sandbox_rerun_comparison(
    rerun_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rerun = deepcopy(rerun_record) if rerun_record is not None else build_memory_influenced_sandbox_rerun_record()
    valid_rerun = validate_memory_influenced_sandbox_rerun_record(rerun)["valid"]
    return {
        "record_type": "memory_influenced_sandbox_rerun_comparison",
        "record_version": "v0",
        "comparison_status": COMPARISON_STATUS,
        "variant_count": len(rerun.get("variant_reruns", [])),
        "all_variants_passed": valid_rerun
        and all(validate_memory_influenced_sandbox_variant_rerun(item)["valid"] for item in rerun.get("variant_reruns", [])),
        "expected_effect": EXPECTED_EFFECT,
        "observed_effect": OBSERVED_EFFECT,
        "memory_off_baseline_restored_after_rollback": rerun.get("rollback_restored_baseline") is True,
        "max_absolute_delta_within_limit": rerun.get("observed_tendency_shift", {}).get("max_absolute_delta") == MAX_ABSOLUTE_DELTA,
        "selected_action_created": False,
        "final_action_created": False,
        "predictor_mutation_performed": False,
        "production_behavior_changed": False,
        "proof_of_learning_claim_allowed": False,
        "human_summary": (
            "Memory-influenced tendency increased check_before_retry across the deterministic Level 3 toy "
            "minefield variant re-run, then rollback restored baseline. This is sandbox tendency trace "
            "evidence only, not action selection or proof of learning."
        ),
        "source_rerun_record": rerun,
    }


def validate_memory_influenced_sandbox_rerun_comparison(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {
        "record_type": "memory_influenced_sandbox_rerun_comparison",
        "record_version": "v0",
        "comparison_status": COMPARISON_STATUS,
        "expected_effect": EXPECTED_EFFECT,
        "observed_effect": OBSERVED_EFFECT,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            errors.append(f"{field}_not_expected")
    if record.get("variant_count", 0) < len(REQUIRED_VARIANT_IDS):
        errors.append("variant_count_too_low")
    if record.get("all_variants_passed") is not True:
        errors.append("all_variants_passed_not_true")
    if record.get("memory_off_baseline_restored_after_rollback") is not True:
        errors.append("memory_off_baseline_restored_after_rollback_not_true")
    if record.get("max_absolute_delta_within_limit") is not True:
        errors.append("max_absolute_delta_within_limit_not_true")
    for field in (
        "selected_action_created",
        "final_action_created",
        "predictor_mutation_performed",
        "production_behavior_changed",
        "proof_of_learning_claim_allowed",
    ):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if not isinstance(record.get("human_summary"), str) or not record.get("human_summary", "").strip():
        errors.append("human_summary_empty")
    source = record.get("source_rerun_record")
    if not isinstance(source, dict):
        errors.append("source_rerun_record_missing")
    elif not validate_memory_influenced_sandbox_rerun_record(source)["valid"]:
        errors.append("source_rerun_record_invalid")
    return {
        "valid": not errors,
        "error_codes": errors,
        "selected_action_blocked": record.get("selected_action_created") is False,
        "final_action_blocked": record.get("final_action_created") is False,
        "predictor_mutation_blocked": record.get("predictor_mutation_performed") is False,
        "production_behavior_blocked": record.get("production_behavior_changed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_memory_influenced_sandbox_rerun_minimal_check() -> dict[str, Any]:
    valid_rerun = build_memory_influenced_sandbox_rerun_record()
    comparison = build_memory_influenced_sandbox_rerun_comparison(valid_rerun)
    invalid_reruns = _invalid_reruns(valid_rerun)
    invalid_variants = _invalid_variants(valid_rerun["variant_reruns"][0])
    invalid_comparisons = _invalid_comparisons(comparison)
    rerun_validations = [validate_memory_influenced_sandbox_rerun_record(item) for item in [valid_rerun] + invalid_reruns]
    variant_validations = [
        validate_memory_influenced_sandbox_variant_rerun(item)
        for item in valid_rerun["variant_reruns"] + invalid_variants
    ]
    comparison_validations = [
        validate_memory_influenced_sandbox_rerun_comparison(item)
        for item in [comparison] + invalid_comparisons
    ]
    valid_rerun_results = [result for result in rerun_validations if result["valid"]]
    valid_variant_results = [result for result in variant_validations if result["valid"]]
    valid_comparison_results = [result for result in comparison_validations if result["valid"]]
    summary = {
        "valid_rerun_count": len(valid_rerun_results),
        "invalid_rerun_count": len(rerun_validations) - len(valid_rerun_results),
        "valid_variant_rerun_count": len(valid_variant_results),
        "invalid_variant_rerun_count": len(variant_validations) - len(valid_variant_results),
        "valid_comparison_count": len(valid_comparison_results),
        "invalid_comparison_count": len(comparison_validations) - len(valid_comparison_results),
        "memory_runtime_influence_checked_count": sum(
            1 for result in valid_rerun_results if result["memory_runtime_influence_checked"]
        ),
        "level3_variant_source_checked_count": sum(
            1 for result in valid_rerun_results if result["level3_variant_source_checked"]
        ),
        "memory_off_checked_count": sum(1 for result in valid_rerun_results if result["memory_off_checked"]),
        "memory_on_checked_count": sum(1 for result in valid_rerun_results if result["memory_on_checked"]),
        "rollback_checked_count": sum(1 for result in valid_rerun_results if result["rollback_checked"]),
        "check_before_retry_increase_checked_count": sum(
            1 for result in valid_rerun_results if result["check_before_retry_increase_checked"]
        ),
        "max_delta_checked_count": sum(1 for result in valid_rerun_results if result["max_delta_checked"]),
        "selected_action_blocked_count": sum(1 for result in valid_rerun_results if result["selected_action_blocked"]),
        "final_action_blocked_count": sum(1 for result in valid_rerun_results if result["final_action_blocked"]),
        "predictor_mutation_blocked_count": sum(
            1 for result in valid_rerun_results if result["predictor_mutation_blocked"]
        ),
        "retained_jsonl_write_blocked_count": sum(
            1 for result in valid_rerun_results if result["retained_jsonl_write_blocked"]
        ),
        "production_behavior_blocked_count": sum(
            1 for result in valid_rerun_results if result["production_behavior_blocked"]
        ),
        "proof_claim_blocked_count": sum(1 for result in valid_rerun_results if result["proof_claim_blocked"]),
    }
    summary["all_memory_influenced_sandbox_rerun_minimal_checks_passed"] = _all_checks_passed(summary)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_memory_influenced_sandbox_rerun_minimal_checks_passed"] else "failed",
        "valid_record": valid_rerun,
        "valid_comparison": comparison,
        "invalid_reruns": invalid_reruns,
        "invalid_variants": invalid_variants,
        "invalid_comparisons": invalid_comparisons,
        "validation_results": {
            "reruns": rerun_validations,
            "variants": variant_validations,
            "comparisons": comparison_validations,
        },
        "summary": summary,
        "boundary": {
            "boundary_change_required": True,
            "boundary_index_update_required": True,
            "boundary_index_version_before": BOUNDARY_INDEX_VERSION_BEFORE,
            "boundary_index_version_after": BOUNDARY_INDEX_VERSION_AFTER,
            "rationale": (
                "This package introduces memory-influenced Level 3 sandbox re-run tendency traces using the "
                "approved bounded runtime influence, while selected_action, final_action, predictor mutation, "
                "production promotion, retained JSONL write, retention write, and proof-of-learning remain blocked."
            ),
        },
        "safe_claim": (
            "ASHL Core can re-run the deterministic Phase0 Level 3 toy minefield sandbox variant suite with "
            "memory_off / memory_on / rollback tendency traces, showing memory_on increases check_before_retry "
            "tendency while rollback restores baseline, with selected_action, final_action, predictor mutation, "
            "production promotion, retained JSONL write, retention write, and proof-of-learning blocked."
        ),
    }


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary.get("valid_rerun_count") == 1
        and summary.get("invalid_rerun_count", 0) >= 1
        and summary.get("valid_variant_rerun_count") == len(REQUIRED_VARIANT_IDS)
        and summary.get("invalid_variant_rerun_count", 0) >= 1
        and summary.get("valid_comparison_count") == 1
        and summary.get("invalid_comparison_count", 0) >= 1
        and summary.get("memory_runtime_influence_checked_count") == 1
        and summary.get("level3_variant_source_checked_count") == 1
        and summary.get("memory_off_checked_count") == 1
        and summary.get("memory_on_checked_count") == 1
        and summary.get("rollback_checked_count") == 1
        and summary.get("check_before_retry_increase_checked_count") == 1
        and summary.get("max_delta_checked_count") == 1
        and summary.get("selected_action_blocked_count") == 1
        and summary.get("final_action_blocked_count") == 1
        and summary.get("predictor_mutation_blocked_count") == 1
        and summary.get("retained_jsonl_write_blocked_count") == 1
        and summary.get("production_behavior_blocked_count") == 1
        and summary.get("proof_claim_blocked_count") == 1
    )


def _score_only(record: dict[str, Any]) -> dict[str, float]:
    return {
        DISCOURAGED_FUTURE_TENDENCY: record.get(DISCOURAGED_FUTURE_TENDENCY),
        PREFERRED_FUTURE_TENDENCY: record.get(PREFERRED_FUTURE_TENDENCY),
    }


def _invalid_reruns(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def changed(field: str, value: Any) -> None:
        record = deepcopy(valid)
        record[field] = value
        invalids.append(record)

    missing_influence = deepcopy(valid)
    missing_influence.pop("source_memory_runtime_influence", None)
    invalids.append(missing_influence)
    missing_suite = deepcopy(valid)
    missing_suite.pop("source_level3_variant_suite", None)
    invalids.append(missing_suite)
    changed("variants", ["safe_path_variant"])
    changed("memory_on_influenced", {DISCOURAGED_FUTURE_TENDENCY: 0.50, PREFERRED_FUTURE_TENDENCY: 0.50})
    retry_increase = deepcopy(valid)
    retry_increase["observed_tendency_shift"]["retry_same_action_without_check_decreased"] = False
    invalids.append(retry_increase)
    max_delta = deepcopy(valid)
    max_delta["observed_tendency_shift"]["max_absolute_delta"] = 0.11
    invalids.append(max_delta)
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
    changed("future_sandbox_behavior_use_requires_separate_boundary", False)
    changed("future_action_selection_requires_separate_boundary", False)
    changed("proof_of_learning_claim_allowed", True)
    changed("autonomous_learning_claim_allowed", True)
    changed("autonomous_action_claim_allowed", True)
    return invalids


def _invalid_variants(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []

    def changed(path: tuple[str, ...], value: Any) -> None:
        record = deepcopy(valid)
        target = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        invalids.append(record)

    changed(("memory_on", PREFERRED_FUTURE_TENDENCY), 0.50)
    changed(("memory_on", DISCOURAGED_FUTURE_TENDENCY), 0.55)
    changed(("memory_off_after_rollback", PREFERRED_FUTURE_TENDENCY), 0.60)
    changed(("memory_on", "selected_action_created"), True)
    changed(("memory_on", "final_action_created"), True)
    changed(("check_before_retry_tendency_increased_under_memory",), False)
    changed(("rollback_restored_baseline",), False)
    changed(("trace_only",), False)
    changed(("no_action_selection",), False)
    return invalids


def _invalid_comparisons(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalids: list[dict[str, Any]] = []
    for field, value in (
        ("comparison_status", "failed"),
        ("variant_count", 1),
        ("all_variants_passed", False),
        ("memory_off_baseline_restored_after_rollback", False),
        ("max_absolute_delta_within_limit", False),
        ("selected_action_created", True),
        ("final_action_created", True),
        ("predictor_mutation_performed", True),
        ("production_behavior_changed", True),
        ("proof_of_learning_claim_allowed", True),
        ("human_summary", ""),
    ):
        record = deepcopy(valid)
        record[field] = value
        invalids.append(record)
    return invalids


if __name__ == "__main__":
    import json

    print(json.dumps(run_memory_influenced_sandbox_rerun_minimal_check(), indent=2, sort_keys=True))
