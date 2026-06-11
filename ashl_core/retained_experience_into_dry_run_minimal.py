"""Trace-only dry-run context from retained exact-key lookup previews."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .dry_run_correction_into_trial_trace import run_dry_run_correction_into_trial_trace_check
from .retained_experience_exact_key_lookup_minimal import (
    run_retained_experience_exact_key_lookup_minimal_check,
    validate_retained_exact_key_lookup_preview,
)
from .reviewed_lesson_dry_run_correction_minimal import (
    run_reviewed_lesson_dry_run_correction_minimal_check,
)


COMMAND = "run-retained-experience-into-dry-run-minimal-check"
FLOW = "retained_experience_into_dry_run_minimal_v0"

REQUIRED_FIELDS = {
    "dry_run_context_id",
    "source_lookup_preview_id",
    "source_trial_intent_id",
    "context_status",
    "trace_only",
    "human_summary",
    "blocked_flags",
}

REQUIRED_BLOCKED_FLAGS = {
    "lesson_applied",
    "runtime_action_selection",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "new_retention_written",
    "semantic_match",
    "fuzzy_match",
    "vector_match",
    "predictor_modified",
    "proof_of_learning_claim",
}

DEFAULT_TRIAL_INTENT = {
    "trial_intent_id": "trial_intent_demo_001",
    "intent_summary": "Preview whether retained exact-key context can be shown in dry-run.",
}


def build_retained_experience_dry_run_context(
    lookup_preview: dict[str, Any],
    trial_intent: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    lookup_validation = validate_retained_exact_key_lookup_preview(lookup_preview)
    if not lookup_validation["valid"] or lookup_validation["read_only"] is not True:
        return None

    trial = trial_intent if isinstance(trial_intent, dict) else DEFAULT_TRIAL_INTENT
    trial_intent_id = trial.get("trial_intent_id") if isinstance(trial.get("trial_intent_id"), str) else ""
    match_result = lookup_preview.get("match_result", {})
    matched = match_result.get("matched") is True
    matched_count = match_result.get("matched_count") if isinstance(match_result.get("matched_count"), int) else 0
    return {
        "dry_run_context_id": _dry_run_context_id(lookup_preview, trial_intent_id),
        "source_lookup_preview_id": lookup_preview.get("lookup_preview_id"),
        "source_trial_intent_id": trial_intent_id,
        "context_status": {
            "retained_context_available": matched,
            "matched_retained_record_count": matched_count,
            "usable_for_dry_run": True,
            "usable_for_runtime_action": False,
        },
        "trace_only": True,
        "human_summary": {
            "lookup_result": _lookup_result_text(matched),
            "dry_run_use": _dry_run_use_text(matched),
            "plain_result": _plain_result(matched),
        },
        "blocked_flags": _blocked_flags(),
    }


def validate_retained_experience_dry_run_context(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not isinstance(record.get("source_lookup_preview_id"), str) or not record.get("source_lookup_preview_id"):
        errors.append("source_lookup_preview_id_missing")

    context_status = record.get("context_status")
    if not isinstance(context_status, dict):
        errors.append("context_status_missing_or_not_dict")
        context_status = {}
    if not isinstance(context_status.get("retained_context_available"), bool):
        errors.append("retained_context_available_not_boolean")
    matched_count = context_status.get("matched_retained_record_count")
    if not isinstance(matched_count, int) or matched_count < 0:
        errors.append("matched_retained_record_count_not_non_negative_integer")
    if context_status.get("usable_for_dry_run") is not True:
        errors.append("usable_for_dry_run_not_true")
    if context_status.get("usable_for_runtime_action") is not False:
        errors.append("usable_for_runtime_action_not_false")

    if record.get("trace_only") is not True:
        errors.append("trace_only_not_true")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    for field in ("lookup_result", "dry_run_use", "plain_result"):
        if not isinstance(human_summary.get(field), str) or not human_summary.get(field):
            errors.append(f"{field}_empty_or_not_string")

    blocked_flags = record.get("blocked_flags")
    if not isinstance(blocked_flags, dict):
        errors.append("blocked_flags_missing_or_not_dict")
        blocked_flags = {}
    for field in sorted(REQUIRED_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "dry_run_context_id": record.get("dry_run_context_id"),
        "valid": not errors,
        "error_codes": errors,
        "matched_context": context_status.get("retained_context_available") is True,
        "not_matched_context": context_status.get("retained_context_available") is False,
        "trace_only": record.get("trace_only") is True,
        "usable_for_dry_run": context_status.get("usable_for_dry_run") is True,
        "usable_for_runtime_action": context_status.get("usable_for_runtime_action") is True,
        **_blocked_flag_values(blocked_flags),
    }


def run_retained_experience_into_dry_run_minimal_check() -> dict[str, Any]:
    lookup_result = run_retained_experience_exact_key_lookup_minimal_check()
    reviewed_dry_run_result = run_reviewed_lesson_dry_run_correction_minimal_check()
    trial_trace_dry_run_result = run_dry_run_correction_into_trial_trace_check()
    matched_lookup = _first_valid_lookup(lookup_result, matched=True)
    not_matched_lookup = _first_valid_lookup(lookup_result, matched=False)
    valid_matched = build_retained_experience_dry_run_context(matched_lookup, DEFAULT_TRIAL_INTENT)
    valid_not_matched = build_retained_experience_dry_run_context(not_matched_lookup, DEFAULT_TRIAL_INTENT)
    contexts = [
        valid_matched,
        valid_not_matched,
        *_invalid_demo_contexts(valid_matched),
    ]
    validation_results = [validate_retained_experience_dry_run_context(context) for context in contexts]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "retained_experience_dry_run_contexts": contexts,
        "valid_human_summaries": [
            context["human_summary"]
            for context, validation in zip(contexts, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "source_lookup_summary": lookup_result.get("summary", {}),
        "source_lookup_flow": lookup_result.get("flow"),
        "source_dry_run_reference": {
            "reviewed_lesson_dry_run_correction_flow": reviewed_dry_run_result.get("flow"),
            "dry_run_correction_into_trial_trace_flow": trial_trace_dry_run_result.get("flow"),
            "retained_context_injected_into_existing_dry_run_flows": False,
        },
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker converts valid retained exact-key lookup previews into trace-only dry-run context.",
            "Dry-run context may show retained context availability but cannot apply lessons, select actions, change behavior, write memory, write retention, retrieve semantically, mutate predictors, or claim proof of learning.",
        ],
    }


def _first_valid_lookup(result: dict[str, Any], matched: bool) -> dict[str, Any]:
    for lookup, validation in zip(
        result.get("retained_exact_key_lookup_previews", []),
        result.get("validation_results", []),
    ):
        if validation.get("valid") and lookup.get("match_result", {}).get("matched") is matched:
            return deepcopy(lookup)
    return {}


def _dry_run_context_id(lookup_preview: dict[str, Any], trial_intent_id: str) -> str:
    source_id = str(lookup_preview.get("lookup_preview_id", "unknown")).replace(":", "_")
    trial_id = trial_intent_id or "no_trial_intent"
    return f"retained_experience_dry_run_context:{source_id}:{trial_id}"


def _lookup_result_text(matched: bool) -> str:
    if matched:
        return "A retained experience with the same exact key was found."
    return "No retained experience with the same exact key was found."


def _dry_run_use_text(matched: bool) -> str:
    if matched:
        return "The retained experience can be shown as context inside dry-run preview."
    return "The dry-run preview can show that no retained context is available for this exact key."


def _plain_result(matched: bool) -> str:
    if matched:
        return "The system can consider retained context in dry-run only; it does not change real behavior."
    return "The system can continue dry-run without retained context; it does not change real behavior."


def _blocked_flags() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _invalid_demo_contexts(valid_context: dict[str, Any]) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []

    trace_only_false = _copy_case(valid_context, "trace_only_false")
    trace_only_false["trace_only"] = False
    contexts.append(trace_only_false)

    dry_run_false = _copy_case(valid_context, "usable_for_dry_run_false")
    dry_run_false["context_status"]["usable_for_dry_run"] = False
    contexts.append(dry_run_false)

    runtime_action_true = _copy_case(valid_context, "usable_for_runtime_action_true")
    runtime_action_true["context_status"]["usable_for_runtime_action"] = True
    contexts.append(runtime_action_true)

    missing_source = _copy_case(valid_context, "missing_source_lookup_preview")
    missing_source["source_lookup_preview_id"] = ""
    contexts.append(missing_source)

    empty_lookup = _copy_case(valid_context, "empty_lookup_result")
    empty_lookup["human_summary"]["lookup_result"] = ""
    contexts.append(empty_lookup)

    empty_plain = _copy_case(valid_context, "empty_plain_result")
    empty_plain["human_summary"]["plain_result"] = ""
    contexts.append(empty_plain)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_context, flag)
        flagged["blocked_flags"][flag] = True
        contexts.append(flagged)

    return contexts


def _copy_case(context: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(context)
    copied["dry_run_context_id"] = f"{context['dry_run_context_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "retained_dry_run_context_count": len(validation_results),
        "valid_retained_dry_run_context_count": len(valid_results),
        "invalid_retained_dry_run_context_count": sum(1 for result in validation_results if not result["valid"]),
        "matched_context_count": sum(1 for result in valid_results if result["matched_context"]),
        "not_matched_context_count": sum(1 for result in valid_results if result["not_matched_context"]),
        "trace_only_false_blocked_count": _count_error(validation_results, "trace_only_not_true"),
        "usable_for_dry_run_false_blocked_count": _count_error(
            validation_results, "usable_for_dry_run_not_true"
        ),
        "usable_for_runtime_action_blocked_count": _count_error(
            validation_results, "usable_for_runtime_action_not_false"
        ),
        "missing_source_lookup_preview_blocked_count": _count_error(
            validation_results, "source_lookup_preview_id_missing"
        ),
        "empty_lookup_result_blocked_count": _count_error(
            validation_results, "lookup_result_empty_or_not_string"
        ),
        "empty_plain_result_blocked_count": _count_error(
            validation_results, "plain_result_empty_or_not_string"
        ),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "runtime_action_selection_blocked_count": _count_error(
            validation_results, "runtime_action_selection_enabled"
        ),
        "action_selection_influence_blocked_count": _count_error(
            validation_results, "action_selection_influence_enabled"
        ),
        "action_behavior_changed_blocked_count": _count_error(
            validation_results, "action_behavior_changed_enabled"
        ),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(
            validation_results, "new_retention_written_enabled"
        ),
        "semantic_match_blocked_count": _count_error(validation_results, "semantic_match_enabled"),
        "fuzzy_match_blocked_count": _count_error(validation_results, "fuzzy_match_enabled"),
        "vector_match_blocked_count": _count_error(validation_results, "vector_match_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(
            validation_results, "proof_of_learning_claim_enabled"
        ),
        "lesson_applied_count": _count_valid_flag(valid_results, "lesson_applied"),
        "runtime_action_selection_count": _count_valid_flag(valid_results, "runtime_action_selection"),
        "action_selection_influence_count": _count_valid_flag(valid_results, "action_selection_influence"),
        "action_behavior_changed_count": _count_valid_flag(valid_results, "action_behavior_changed"),
        "memory_write_count": _count_valid_flag(valid_results, "memory_write"),
        "new_retention_written_count": _count_valid_flag(valid_results, "new_retention_written"),
        "semantic_match_count": _count_valid_flag(valid_results, "semantic_match"),
        "fuzzy_match_count": _count_valid_flag(valid_results, "fuzzy_match"),
        "vector_match_count": _count_valid_flag(valid_results, "vector_match"),
        "predictor_modified_count": _count_valid_flag(valid_results, "predictor_modified"),
        "proof_of_learning_claim_count": _count_valid_flag(valid_results, "proof_of_learning_claim"),
    }
    summary["all_retained_experience_into_dry_run_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["retained_dry_run_context_count"] == 19
        and summary["valid_retained_dry_run_context_count"] == 2
        and summary["invalid_retained_dry_run_context_count"] == 17
        and summary["matched_context_count"] == 1
        and summary["not_matched_context_count"] == 1
        and summary["trace_only_false_blocked_count"] == 1
        and summary["usable_for_dry_run_false_blocked_count"] == 1
        and summary["usable_for_runtime_action_blocked_count"] == 1
        and summary["missing_source_lookup_preview_blocked_count"] == 1
        and summary["empty_lookup_result_blocked_count"] == 1
        and summary["empty_plain_result_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["runtime_action_selection_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["new_retention_written_blocked_count"] == 1
        and summary["semantic_match_blocked_count"] == 1
        and summary["fuzzy_match_blocked_count"] == 1
        and summary["vector_match_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["lesson_applied_count"] == 0
        and summary["runtime_action_selection_count"] == 0
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["new_retention_written_count"] == 0
        and summary["semantic_match_count"] == 0
        and summary["fuzzy_match_count"] == 0
        and summary["vector_match_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int]:
    return {
        "retained_experience_into_dry_run_minimal_enabled": True,
        "trace_only": True,
        "dry_run_preview_only": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "uses_retained_experience_exact_key_lookup_minimal": True,
        "references_reviewed_lesson_dry_run_correction_minimal": True,
        "references_dry_run_correction_into_trial_trace": True,
        "retained_context_injected_into_existing_dry_run_flows": False,
        "retained_context_can_enter_dry_run_context": True,
        "usable_for_runtime_action": False,
        "lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "memory_write_added": False,
        "new_retention_write_added": False,
        "semantic_retrieval_added": False,
        "fuzzy_retrieval_added": False,
        "vector_retrieval_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "lesson_applied_count": summary["lesson_applied_count"],
        "runtime_action_selection_count": summary["runtime_action_selection_count"],
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "memory_write_count": summary["memory_write_count"],
        "new_retention_written_count": summary["new_retention_written_count"],
        "semantic_match_count": summary["semantic_match_count"],
        "fuzzy_match_count": summary["fuzzy_match_count"],
        "vector_match_count": summary["vector_match_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "proof_of_learning_claim_count": summary["proof_of_learning_claim_count"],
    }


def _blocked_flag_values(blocked_flags: dict[str, Any]) -> dict[str, bool]:
    return {field: blocked_flags.get(field) is True for field in sorted(REQUIRED_BLOCKED_FLAGS)}


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
