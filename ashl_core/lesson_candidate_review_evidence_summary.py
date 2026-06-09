"""Reviewer-facing evidence summaries for pending_review lesson_candidate records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .failure_reason_from_outcome_pair import run_failure_reason_from_outcome_pair_check
from .lesson_candidate_from_failure_reason import (
    validate_lesson_candidate_record,
)
from .lesson_candidate_review_gate import (
    run_lesson_candidate_review_gate_check,
    validate_lesson_candidate_review_gate_result,
)
from .outcome_pair_from_action_trial_trace import run_outcome_pair_from_action_trial_trace_check


COMMAND = "run-lesson-candidate-review-evidence-summary-check"
FLOW = "lesson_candidate_review_evidence_summary_v0"

REQUIRED_FIELDS = {
    "evidence_summary_id",
    "source_lesson_candidate_id",
    "source_review_gate_result_id",
    "source_failure_reason_id",
    "source_pair_id",
    "action_intent_id",
    "review_status",
    "evidence_sections",
    "boundary_summary",
    "missing_evidence",
    "source_trace",
    "safety_flags",
}

REQUIRED_EVIDENCE_SECTIONS = {
    "action_intent_summary",
    "outcome_pair_summary",
    "failure_reason_summary",
    "lesson_candidate_summary",
    "review_gate_summary",
}

REQUIRED_REVIEW_STATUS_FIELDS = {
    "pending_review",
    "eligible_for_human_review",
    "approved",
    "rejected",
    "reviewed_by_human",
}

REQUIRED_BOUNDARY_FIELDS = {
    "approval_decision_created",
    "lesson_approved",
    "lesson_rejected",
    "lesson_applied",
    "behavior_preview_created",
    "action_selection_influence",
    "memory_write",
    "predictor_modified",
    "persistent_rule_write",
}

REQUIRED_SAFETY_FLAGS = {
    "trace_only",
    "review_support_only",
    "blocked_from_review_decision",
    "blocked_from_lesson_approval",
    "blocked_from_lesson_rejection",
    "blocked_from_lesson_application",
    "blocked_from_action_selection",
    "blocked_from_action_behavior_change",
    "blocked_from_memory_write",
    "blocked_from_predictor_mutation",
    "blocked_from_persistent_rule_write",
}

FALSE_BOUNDARY_FLAGS = {
    "approval_decision_created",
    "lesson_approved",
    "lesson_rejected",
    "lesson_applied",
    "behavior_preview_created",
    "action_selection_influence",
    "memory_write",
    "predictor_modified",
    "persistent_rule_write",
}


def build_lesson_candidate_review_evidence_summary(
    lesson_candidate: dict[str, Any],
    review_gate_result: dict[str, Any],
    *,
    failure_reason: dict[str, Any] | None = None,
    outcome_pair: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build review-support-only evidence for a lesson candidate.

    This is not a review decision. It never approves, rejects, previews, applies,
    persists, writes memory, mutates predictors, or changes action selection.
    """

    candidate_validation = validate_lesson_candidate_record(lesson_candidate)
    gate_validation = validate_lesson_candidate_review_gate_result(review_gate_result)
    pending_review = (
        candidate_validation["valid"]
        and gate_validation["valid"]
        and review_gate_result.get("gate_status") == "pending_review"
        and review_gate_result.get("eligible_for_human_review") is True
    )
    sections = _build_evidence_sections(lesson_candidate, review_gate_result, failure_reason, outcome_pair)
    missing_evidence = _missing_evidence(sections)
    if not pending_review:
        missing_evidence.append("blocked_review_gate")

    return {
        "evidence_summary_id": f"lesson_evidence_summary:{lesson_candidate.get('lesson_candidate_id') or 'missing'}",
        "source_lesson_candidate_id": lesson_candidate.get("lesson_candidate_id"),
        "source_review_gate_result_id": review_gate_result.get("review_gate_result_id"),
        "source_failure_reason_id": lesson_candidate.get("source_failure_reason_id"),
        "source_pair_id": lesson_candidate.get("source_pair_id"),
        "action_intent_id": lesson_candidate.get("action_intent_id"),
        "review_status": {
            "pending_review": pending_review,
            "eligible_for_human_review": pending_review,
            "approved": False,
            "rejected": False,
            "reviewed_by_human": False,
        },
        "evidence_sections": sections,
        "boundary_summary": _build_boundary_summary(),
        "missing_evidence": _dedupe(missing_evidence),
        "source_trace": _build_source_trace(),
        "safety_flags": _build_safety_flags(),
    }


def validate_lesson_candidate_review_evidence_summary(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    review_status = _validate_review_status(record.get("review_status"), errors)
    sections = _validate_evidence_sections(record.get("evidence_sections"), record, errors)
    boundary = _validate_boundary_summary(record.get("boundary_summary"), errors)
    safety_flags = _validate_safety_flags(record.get("safety_flags"), errors)
    _validate_source_trace(record.get("source_trace"), errors)
    missing_evidence = record.get("missing_evidence")
    if not isinstance(missing_evidence, list):
        errors.append("missing_evidence_not_list")
        missing_evidence = []
    if missing_evidence:
        errors.append("missing_evidence_present")

    return {
        "evidence_summary_id": record.get("evidence_summary_id"),
        "source_lesson_candidate_id": record.get("source_lesson_candidate_id"),
        "source_review_gate_result_id": record.get("source_review_gate_result_id"),
        "source_failure_reason_id": record.get("source_failure_reason_id"),
        "source_pair_id": record.get("source_pair_id"),
        "action_intent_id": record.get("action_intent_id"),
        "valid": not errors,
        "error_codes": errors,
        "pending_review": review_status.get("pending_review") is True,
        "eligible_for_human_review": review_status.get("eligible_for_human_review") is True,
        "approved": review_status.get("approved") is True,
        "rejected": review_status.get("rejected") is True,
        "reviewed_by_human": review_status.get("reviewed_by_human") is True,
        "present_sections": sorted(
            section for section in REQUIRED_EVIDENCE_SECTIONS if sections.get(section, {}).get("present") is True
        ),
        "approval_decision_created": boundary.get("approval_decision_created") is True,
        "lesson_approved": boundary.get("lesson_approved") is True,
        "lesson_rejected": boundary.get("lesson_rejected") is True,
        "lesson_applied": boundary.get("lesson_applied") is True,
        "behavior_preview_created": boundary.get("behavior_preview_created") is True,
        "action_selection_influence": boundary.get("action_selection_influence") is True,
        "memory_write": boundary.get("memory_write") is True,
        "predictor_modified": boundary.get("predictor_modified") is True,
        "persistent_rule_write": boundary.get("persistent_rule_write") is True,
        "trace_only": safety_flags.get("trace_only") is True,
        "review_support_only": safety_flags.get("review_support_only") is True,
    }


def run_lesson_candidate_review_evidence_summary_check() -> dict[str, Any]:
    gate_result = run_lesson_candidate_review_gate_check()
    failure_result = run_failure_reason_from_outcome_pair_check()
    outcome_result = run_outcome_pair_from_action_trial_trace_check()

    failure_reasons = {
        record.get("failure_reason_id"): record for record in failure_result.get("failure_reason_records", [])
    }
    outcome_pairs = {record.get("pair_id"): record for record in outcome_result.get("generated_pairs", [])}

    lesson_candidates = gate_result["lesson_candidate_records"]
    review_gate_results = gate_result["review_gate_results"]
    evidence_summaries = [
        build_lesson_candidate_review_evidence_summary(
            lesson_candidate,
            review_gate,
            failure_reason=failure_reasons.get(lesson_candidate.get("source_failure_reason_id")),
            outcome_pair=outcome_pairs.get(lesson_candidate.get("source_pair_id")),
        )
        for lesson_candidate, review_gate in zip(lesson_candidates, review_gate_results)
    ]
    valid_summary = next(summary for summary in evidence_summaries if summary["review_status"]["pending_review"])
    evidence_summaries.extend(_build_invalid_demo_summaries(valid_summary))
    validations = [validate_lesson_candidate_review_evidence_summary(record) for record in evidence_summaries]
    summary = _build_summary(gate_result, evidence_summaries, validations)

    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "lesson_candidate_records": lesson_candidates,
        "review_gate_results": review_gate_results,
        "evidence_summaries": evidence_summaries,
        "evidence_summary_validations": validations,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check builds reviewer-facing evidence summaries for pending_review lesson_candidate records.",
            "Evidence summaries are review-support-only and do not create review decisions.",
            "No approval, rejection, behavior preview, lesson application, action selection influence, memory write, predictor mutation, or persistent write is added.",
        ],
    }


def _build_evidence_sections(
    lesson_candidate: dict[str, Any],
    review_gate_result: dict[str, Any],
    failure_reason: dict[str, Any] | None,
    outcome_pair: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    action_intent = outcome_pair.get("action_intent") if isinstance(outcome_pair, dict) else None
    expected = outcome_pair.get("expected_outcome") if isinstance(outcome_pair, dict) else None
    actual = outcome_pair.get("actual_outcome") if isinstance(outcome_pair, dict) else None
    proposed_correction = lesson_candidate.get("proposed_correction") or {}
    applicability = lesson_candidate.get("applicability") or {}
    return {
        "action_intent_summary": {
            "present": isinstance(action_intent, dict) and bool(lesson_candidate.get("action_intent_id")),
            "action_intent_id": lesson_candidate.get("action_intent_id"),
            "action_type": action_intent.get("action_type") if isinstance(action_intent, dict) else None,
        },
        "outcome_pair_summary": {
            "present": isinstance(outcome_pair, dict),
            "source_pair_id": lesson_candidate.get("source_pair_id"),
            "mismatch": outcome_pair.get("mismatch") if isinstance(outcome_pair, dict) else None,
            "expected_outcome_known": expected.get("known") if isinstance(expected, dict) else None,
            "actual_outcome_known": actual.get("known") if isinstance(actual, dict) else None,
        },
        "failure_reason_summary": {
            "present": isinstance(failure_reason, dict),
            "failure_reason_id": lesson_candidate.get("source_failure_reason_id"),
            "category": failure_reason.get("category") if isinstance(failure_reason, dict) else None,
            "known": failure_reason.get("known") if isinstance(failure_reason, dict) else None,
        },
        "lesson_candidate_summary": {
            "present": validate_lesson_candidate_record(lesson_candidate)["valid"],
            "candidate_type": lesson_candidate.get("candidate_type"),
            "correction_type": proposed_correction.get("correction_type"),
            "requires_human_review": applicability.get("requires_human_review"),
        },
        "review_gate_summary": {
            "present": validate_lesson_candidate_review_gate_result(review_gate_result)["valid"],
            "gate_status": review_gate_result.get("gate_status"),
            "eligible_for_human_review": review_gate_result.get("eligible_for_human_review"),
            "blocked_reasons": list(review_gate_result.get("blocked_reasons", [])),
        },
    }


def _build_invalid_demo_summaries(valid_summary: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for section in sorted(REQUIRED_EVIDENCE_SECTIONS):
        record = _copy_case(valid_summary, f"missing_{section}")
        record["evidence_sections"].pop(section)
        record["missing_evidence"] = [section]
        cases.append(record)

    review_status_cases = {
        "pending_review_false": ("pending_review", False),
        "eligible_for_human_review_false": ("eligible_for_human_review", False),
        "approved_true": ("approved", True),
        "rejected_true": ("rejected", True),
        "reviewed_by_human_true": ("reviewed_by_human", True),
    }
    for case_name, (field, value) in review_status_cases.items():
        record = _copy_case(valid_summary, case_name)
        record["review_status"][field] = value
        cases.append(record)

    for field in sorted(FALSE_BOUNDARY_FLAGS):
        record = _copy_case(valid_summary, f"{field}_true")
        record["boundary_summary"][field] = True
        cases.append(record)

    safety_cases = {
        "trace_only_false": "trace_only",
        "review_support_only_false": "review_support_only",
        "blocked_from_review_decision_false": "blocked_from_review_decision",
        "blocked_from_lesson_approval_false": "blocked_from_lesson_approval",
        "blocked_from_lesson_rejection_false": "blocked_from_lesson_rejection",
        "blocked_from_lesson_application_false": "blocked_from_lesson_application",
    }
    for case_name, field in safety_cases.items():
        record = _copy_case(valid_summary, case_name)
        record["safety_flags"][field] = False
        cases.append(record)
    return cases


def _copy_case(record: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(record)
    copied["case_name"] = case_name
    copied["evidence_summary_id"] = f"{record['evidence_summary_id']}:{case_name}"
    return copied


def _validate_review_status(review_status: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(review_status, dict):
        errors.append("review_status_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_REVIEW_STATUS_FIELDS):
        if field not in review_status:
            errors.append(f"review_status_missing_field:{field}")
    if review_status.get("pending_review") is not True:
        errors.append("pending_review_not_true")
    if review_status.get("eligible_for_human_review") is not True:
        errors.append("eligible_for_human_review_not_true")
    if review_status.get("approved") is not False:
        errors.append("approved_enabled")
    if review_status.get("rejected") is not False:
        errors.append("rejected_enabled")
    if review_status.get("reviewed_by_human") is not False:
        errors.append("reviewed_by_human_enabled")
    return review_status


def _validate_evidence_sections(
    evidence_sections: Any, record: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    if not isinstance(evidence_sections, dict):
        errors.append("evidence_sections_missing_or_not_dict")
        return {}
    for section in sorted(REQUIRED_EVIDENCE_SECTIONS):
        if section not in evidence_sections:
            errors.append(f"missing_evidence_section:{section}")
            continue
        section_value = evidence_sections.get(section)
        if not isinstance(section_value, dict):
            errors.append(f"evidence_section_not_dict:{section}")
            continue
        if section_value.get("present") is not True:
            errors.append(f"evidence_section_not_present:{section}")
    _validate_linkage(evidence_sections, record, errors)
    return evidence_sections


def _validate_linkage(sections: dict[str, Any], record: dict[str, Any], errors: list[str]) -> None:
    action = sections.get("action_intent_summary") or {}
    pair = sections.get("outcome_pair_summary") or {}
    failure = sections.get("failure_reason_summary") or {}
    if isinstance(action, dict) and action.get("action_intent_id") != record.get("action_intent_id"):
        errors.append("action_intent_id_mismatch")
    if isinstance(pair, dict) and pair.get("source_pair_id") != record.get("source_pair_id"):
        errors.append("source_pair_id_mismatch")
    if isinstance(failure, dict) and failure.get("failure_reason_id") != record.get("source_failure_reason_id"):
        errors.append("source_failure_reason_id_mismatch")


def _validate_boundary_summary(boundary: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(boundary, dict):
        errors.append("boundary_summary_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_BOUNDARY_FIELDS):
        if field not in boundary:
            errors.append(f"boundary_summary_missing_field:{field}")
    for field in sorted(FALSE_BOUNDARY_FLAGS):
        if boundary.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")
    return boundary


def _validate_safety_flags(safety_flags: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(safety_flags, dict):
        errors.append("safety_flags_missing_or_not_dict")
        return {}
    for field in sorted(REQUIRED_SAFETY_FLAGS):
        if field not in safety_flags:
            errors.append(f"missing_safety_flag:{field}")
    required_true_flags = {
        "trace_only": "trace_only_not_true",
        "review_support_only": "review_support_only_not_true",
        "blocked_from_review_decision": "review_decision_not_blocked",
        "blocked_from_lesson_approval": "lesson_approval_not_blocked",
        "blocked_from_lesson_rejection": "lesson_rejection_not_blocked",
        "blocked_from_lesson_application": "lesson_application_not_blocked",
        "blocked_from_action_selection": "action_selection_not_blocked",
        "blocked_from_action_behavior_change": "action_behavior_change_not_blocked",
        "blocked_from_memory_write": "memory_write_not_blocked",
        "blocked_from_predictor_mutation": "predictor_mutation_not_blocked",
        "blocked_from_persistent_rule_write": "persistent_rule_write_not_blocked",
    }
    for flag, error_code in required_true_flags.items():
        if safety_flags.get(flag) is not True:
            errors.append(error_code)
    return safety_flags


def _validate_source_trace(source_trace: Any, errors: list[str]) -> None:
    if not isinstance(source_trace, dict):
        errors.append("source_trace_missing_or_not_dict")
        return
    expected = {
        "source": "lesson_candidate_review_evidence_summary",
        "lesson_candidate_source": "lesson_candidate_from_failure_reason",
        "review_gate_source": "lesson_candidate_review_gate",
        "failure_reason_source": "failure_reason_from_outcome_pair",
        "outcome_pair_source": "outcome_pair_from_action_trial_trace",
        "outcome_pair_schema": "expected_actual_outcome_pair_schema",
    }
    for field, value in expected.items():
        if source_trace.get(field) != value:
            errors.append(f"invalid_source_trace:{field}")


def _missing_evidence(sections: dict[str, dict[str, Any]]) -> list[str]:
    return sorted(
        section
        for section in REQUIRED_EVIDENCE_SECTIONS
        if not isinstance(sections.get(section), dict) or sections[section].get("present") is not True
    )


def _build_boundary_summary() -> dict[str, bool]:
    return {field: False for field in sorted(REQUIRED_BOUNDARY_FIELDS)}


def _build_source_trace() -> dict[str, str]:
    return {
        "source": "lesson_candidate_review_evidence_summary",
        "lesson_candidate_source": "lesson_candidate_from_failure_reason",
        "review_gate_source": "lesson_candidate_review_gate",
        "failure_reason_source": "failure_reason_from_outcome_pair",
        "outcome_pair_source": "outcome_pair_from_action_trial_trace",
        "outcome_pair_schema": "expected_actual_outcome_pair_schema",
    }


def _build_safety_flags() -> dict[str, bool]:
    return {
        "trace_only": True,
        "review_support_only": True,
        "blocked_from_review_decision": True,
        "blocked_from_lesson_approval": True,
        "blocked_from_lesson_rejection": True,
        "blocked_from_lesson_application": True,
        "blocked_from_action_selection": True,
        "blocked_from_action_behavior_change": True,
        "blocked_from_memory_write": True,
        "blocked_from_predictor_mutation": True,
        "blocked_from_persistent_rule_write": True,
    }


def _build_summary(
    gate_result: dict[str, Any],
    evidence_summaries: list[dict[str, Any]],
    validations: list[dict[str, Any]],
) -> dict[str, int]:
    valid_summaries = [result for result in validations if result["valid"]]
    return {
        "lesson_candidate_record_count": gate_result["summary"]["lesson_candidate_record_count"],
        "valid_lesson_candidate_count": gate_result["summary"]["valid_lesson_candidate_count"],
        "review_gate_result_count": gate_result["summary"]["review_gate_result_count"],
        "pending_review_count": gate_result["summary"]["pending_review_count"],
        "blocked_gate_count": gate_result["summary"]["blocked_count"],
        "evidence_summary_count": len(evidence_summaries),
        "valid_evidence_summary_count": len(valid_summaries),
        "invalid_evidence_summary_count": sum(1 for result in validations if not result["valid"]),
        "blocked_summary_count": sum(1 for result in validations if not result["valid"]),
        "missing_action_intent_summary_blocked_count": _count_error(
            validations, "missing_evidence_section:action_intent_summary"
        ),
        "missing_outcome_pair_summary_blocked_count": _count_error(
            validations, "missing_evidence_section:outcome_pair_summary"
        ),
        "missing_failure_reason_summary_blocked_count": _count_error(
            validations, "missing_evidence_section:failure_reason_summary"
        ),
        "missing_lesson_candidate_summary_blocked_count": _count_error(
            validations, "missing_evidence_section:lesson_candidate_summary"
        ),
        "missing_review_gate_summary_blocked_count": _count_error(
            validations, "missing_evidence_section:review_gate_summary"
        ),
        "approval_decision_created_blocked_count": _count_error(validations, "approval_decision_created_enabled"),
        "lesson_approved_blocked_count": _count_error(validations, "lesson_approved_enabled"),
        "lesson_rejected_blocked_count": _count_error(validations, "lesson_rejected_enabled"),
        "lesson_applied_blocked_count": _count_error(validations, "lesson_applied_enabled"),
        "behavior_preview_created_blocked_count": _count_error(validations, "behavior_preview_created_enabled"),
        "action_selection_influence_count": _count_valid_flag(valid_summaries, "action_selection_influence"),
        "memory_write_count": _count_valid_flag(valid_summaries, "memory_write"),
        "predictor_modified_count": _count_valid_flag(valid_summaries, "predictor_modified"),
        "persistent_rule_write_count": _count_valid_flag(valid_summaries, "persistent_rule_write"),
    }


def _all_checks_passed(summary: dict[str, int]) -> bool:
    return (
        summary["lesson_candidate_record_count"] == 15
        and summary["valid_lesson_candidate_count"] == 2
        and summary["review_gate_result_count"] == 15
        and summary["pending_review_count"] >= 1
        and summary["blocked_gate_count"] >= 1
        and summary["valid_evidence_summary_count"] >= 1
        and summary["invalid_evidence_summary_count"] >= 1
        and summary["blocked_summary_count"] >= 1
        and summary["missing_action_intent_summary_blocked_count"] >= 1
        and summary["missing_outcome_pair_summary_blocked_count"] >= 1
        and summary["missing_failure_reason_summary_blocked_count"] >= 1
        and summary["missing_lesson_candidate_summary_blocked_count"] >= 1
        and summary["missing_review_gate_summary_blocked_count"] >= 1
        and summary["approval_decision_created_blocked_count"] >= 1
        and summary["lesson_approved_blocked_count"] >= 1
        and summary["lesson_rejected_blocked_count"] >= 1
        and summary["lesson_applied_blocked_count"] >= 1
        and summary["behavior_preview_created_blocked_count"] >= 1
        and summary["action_selection_influence_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["persistent_rule_write_count"] == 0
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "lesson_candidate_review_evidence_summary_enabled": True,
        "trace_check_only": True,
        "review_support_only": True,
        "uses_lesson_candidate_review_gate": True,
        "uses_lesson_candidate_from_failure_reason": True,
        "uses_failure_reason_from_outcome_pair": True,
        "uses_outcome_pair_from_action_trial_trace": True,
        "uses_expected_actual_outcome_pair_schema": True,
        "new_cli_added": True,
        "human_review_decision_schema_added": False,
        "approval_decision_created": False,
        "lesson_candidate_approval_added": False,
        "lesson_candidate_rejection_added": False,
        "needs_revision_decision_added": False,
        "stale_decision_added": False,
        "reviewed_by_human_added": False,
        "behavior_preview_created": False,
        "lesson_application_runtime_added": False,
        "runtime_action_selection_added": False,
        "action_selection_modified": False,
        "new_action_behavior_added": False,
        "persistent_learning_added": False,
        "persistent_candidate_creation_added": False,
        "persistent_rule_write_added": False,
        "memory_write_added": False,
        "predictor_mutation_added": False,
        "perception_to_action_bridge_added": False,
        "focus_to_action_bridge_added": False,
        "active_focus_added": False,
        "focus_applied_added": False,
        "attention_control_added": False,
        "endocrine_runtime_added": False,
        "endocrine_controlled_action_added": False,
        "autonomy_added": False,
        "semantic_vision_claimed": False,
        "consciousness_claimed": False,
        "subjective_claims_added": False,
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "memory_write_count": summary["memory_write_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "persistent_rule_write_count": summary["persistent_rule_write_count"],
    }


def _count_error(validations: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validations if error_code in result["error_codes"])


def _count_valid_flag(validations: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in validations if result.get(flag) is True)


def _dedupe(values: list[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped
