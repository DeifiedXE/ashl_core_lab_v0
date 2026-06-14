"""Human interpretation and review of bucket-derived lesson candidate signals."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .bucket_derived_lesson_candidate_signal_minimal import (
    BOUNDARY_VERSION,
    build_bucket_derived_lesson_candidate_signal,
    validate_bucket_derived_lesson_candidate_signal,
)


COMMAND = "run-bucket-signal-human-interpretation-review-minimal-check"
FLOW = "bucket_signal_human_interpretation_review_minimal_v0"
PACKAGE_ID = "PKG-Phase0-Bucket-Signal-Human-Interpretation-Review-Audit-Reconciliation-Minimal-v0"
REPEATED_KEY = "retry_same_risky_action_without_check"
QINGYIN_STATUS = "phase0_trace_checker_system"
INTERPRETED_LESSON_TEXT = (
    "When an intended action is risky, failed, or likely to repeat the same mistake, do not retry "
    "the same action immediately. Check the relevant state or cause first, then choose a safer "
    "alternative, fallback, or stop and report."
)
PLAIN_LANGUAGE_SUMMARY = (
    "Human interpretation: repeated risky retry should be paused for a state or cause check before "
    "retrying, choosing an alternative, falling back, or reporting."
)
REVIEW_DECISIONS = (
    "approved_for_future_memory_readiness_design_only",
    "rejected",
    "needs_more_evidence",
    "needs_rewrite",
)
FALSE_PERMISSION_FIELDS = (
    "memory_write_allowed",
    "retained_jsonl_write_allowed",
    "runtime_influence_allowed",
    "predictor_influence_allowed",
    "production_behavior_change_allowed",
    "selected_action_allowed",
    "final_action_allowed",
    "proof_of_learning_claim_allowed",
)
REVIEW_FALSE_PERMISSION_FIELDS = (
    "memory_write_allowed",
    "retained_jsonl_write_allowed",
    "runtime_influence_allowed",
    "predictor_influence_allowed",
    "production_behavior_change_allowed",
    "selected_action_allowed",
    "final_action_allowed",
    "proof_of_learning_claim_allowed",
)
AUDIT_FIELDS = {
    "repo_audit_acknowledged": True,
    "qingyin_current_status": QINGYIN_STATUS,
    "qingyin_autonomous_learning_claim_allowed": False,
    "qingyin_autonomous_action_claim_allowed": False,
    "qingyin_self_proposed_text_available": False,
    "runtime_memory_influenced_behavior_count": 0,
}


def build_human_interpreted_lesson_candidate_from_bucket_signal(
    bucket_signal: dict[str, Any] | None = None,
) -> dict[str, Any]:
    signal = deepcopy(bucket_signal) if bucket_signal is not None else build_bucket_derived_lesson_candidate_signal()
    signal_validation = validate_bucket_derived_lesson_candidate_signal(signal)
    if not signal_validation["valid"]:
        raise ValueError("invalid_bucket_signal")
    if signal.get("candidate_signal_status") != "pending_human_interpretation":
        raise ValueError("bucket_signal_not_pending_human_interpretation")
    if signal.get("signal_source_type") != "qingyin_bucket_derived_system_detected":
        raise ValueError("bucket_signal_authorship_not_qingyin_bucket_derived_system_detected")
    if signal.get("repeated_key") != REPEATED_KEY:
        raise ValueError("bucket_signal_repeated_key_not_expected")
    if signal.get("occurrence_count", 0) < signal.get("minimum_signal_threshold", 999):
        raise ValueError("bucket_signal_below_threshold")
    if signal.get("generated_lesson_text") is not None or signal.get("suggested_human_interpretation") is not None:
        raise ValueError("bucket_signal_already_has_text")
    if signal.get("human_interpretation_required") is not True:
        raise ValueError("bucket_signal_human_interpretation_not_required")
    return {
        "record_type": "human_interpreted_lesson_candidate_from_bucket_signal",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "source_signal_type": signal.get("record_type"),
        "source_signal_status": signal.get("candidate_signal_status"),
        "source_signal_authorship": signal.get("signal_source_type"),
        "source_repeated_key": signal.get("repeated_key"),
        "source_occurrence_count": signal.get("occurrence_count"),
        "source_minimum_signal_threshold": signal.get("minimum_signal_threshold"),
        "interpretation_status": "human_interpreted_pending_review",
        "interpretation_author_type": "human_or_human_gpt_assisted",
        "qingyin_generated_text": False,
        "qingyin_self_proposed_text": False,
        "candidate_text_generated_by_qingyin": False,
        "interpreted_lesson_text": INTERPRETED_LESSON_TEXT,
        "plain_language_summary": PLAIN_LANGUAGE_SUMMARY,
        **AUDIT_FIELDS,
        "human_review_required": True,
        "memory_write_allowed": False,
        "retained_jsonl_write_allowed": False,
        "retention_write_allowed": False,
        "runtime_influence_allowed": False,
        "predictor_influence_allowed": False,
        "production_behavior_change_allowed": False,
        "selected_action_allowed": False,
        "final_action_allowed": False,
        "proof_of_learning_claim_allowed": False,
        "task_queue_status_is_approval": False,
        "passing_tests_are_approval": False,
        "codex_generated_status_is_approval": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_bucket_signal": signal,
    }


def validate_human_interpreted_lesson_candidate(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "human_interpreted_lesson_candidate_from_bucket_signal":
        errors.append("record_type_not_human_interpreted_lesson_candidate_from_bucket_signal")
    if record.get("record_version") != "v0":
        errors.append("record_version_not_v0")
    if record.get("source_signal_type") != "bucket_derived_lesson_candidate_signal":
        errors.append("source_signal_type_not_bucket_derived_lesson_candidate_signal")
    if record.get("source_signal_status") != "pending_human_interpretation":
        errors.append("source_signal_status_not_pending_human_interpretation")
    if record.get("source_signal_authorship") != "qingyin_bucket_derived_system_detected":
        errors.append("source_signal_authorship_not_qingyin_bucket_derived_system_detected")
    if not isinstance(record.get("source_repeated_key"), str) or not record.get("source_repeated_key"):
        errors.append("source_repeated_key_empty")
    if record.get("source_repeated_key") != REPEATED_KEY:
        errors.append("source_repeated_key_not_expected")
    occurrence = record.get("source_occurrence_count")
    threshold = record.get("source_minimum_signal_threshold")
    if not isinstance(occurrence, int) or not isinstance(threshold, int) or occurrence < threshold:
        errors.append("source_occurrence_count_below_threshold")
    if record.get("interpretation_status") != "human_interpreted_pending_review":
        errors.append("interpretation_status_not_pending_review")
    if record.get("interpretation_author_type") != "human_or_human_gpt_assisted":
        errors.append("interpretation_author_type_not_human_or_human_gpt_assisted")
    for field in ("qingyin_generated_text", "qingyin_self_proposed_text", "candidate_text_generated_by_qingyin"):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    for field in ("interpreted_lesson_text", "plain_language_summary"):
        if not isinstance(record.get(field), str) or not record.get(field).strip():
            errors.append(f"{field}_empty")
    _validate_audit_fields(record, errors)
    if record.get("human_review_required") is not True:
        errors.append("human_review_required_not_true")
    for field in FALSE_PERMISSION_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if record.get("retention_write_allowed") is not False:
        errors.append("retention_write_allowed_not_false")
    for field in ("task_queue_status_is_approval", "passing_tests_are_approval", "codex_generated_status_is_approval"):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if record.get("audit_recorded") is not True:
        errors.append("audit_recorded_not_true")
    if record.get("rollback_available") is not True:
        errors.append("rollback_available_not_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "qingyin_self_authorship_blocked": (
            record.get("qingyin_generated_text") is False
            and record.get("qingyin_self_proposed_text") is False
            and record.get("candidate_text_generated_by_qingyin") is False
        ),
        "repo_audit_acknowledged": record.get("repo_audit_acknowledged") is True,
        "human_review_required": record.get("human_review_required") is True,
        "memory_write_blocked": record.get("memory_write_allowed") is False,
        "runtime_influence_blocked": record.get("runtime_influence_allowed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def build_human_interpretation_review_decision(
    interpreted_candidate: dict[str, Any] | None = None,
    review_decision: str = "approved_for_future_memory_readiness_design_only",
) -> dict[str, Any]:
    candidate = (
        deepcopy(interpreted_candidate)
        if interpreted_candidate is not None
        else build_human_interpreted_lesson_candidate_from_bucket_signal()
    )
    candidate_validation = validate_human_interpreted_lesson_candidate(candidate)
    if not candidate_validation["valid"]:
        raise ValueError("invalid_human_interpreted_candidate")
    if review_decision not in REVIEW_DECISIONS:
        raise ValueError("unknown_review_decision")
    approved_design = review_decision == "approved_for_future_memory_readiness_design_only"
    return {
        "record_type": "human_interpretation_review_decision",
        "record_version": "v0",
        "package_id": PACKAGE_ID,
        "target_record_type": candidate.get("record_type"),
        "target_repeated_key": candidate.get("source_repeated_key"),
        "review_status": "reviewed",
        "review_decision": review_decision,
        "allowed_review_decisions": list(REVIEW_DECISIONS),
        "reviewer_actor": "human",
        "reviewer_role": "project_owner",
        "review_text": _review_text(review_decision),
        "not_application_approval": True,
        "not_memory_write_approval": True,
        "not_runtime_influence_approval": True,
        "not_predictor_approval": True,
        "not_proof_of_learning": True,
        "memory_readiness_design_allowed": approved_design,
        "memory_write_allowed": False,
        "retained_jsonl_write_allowed": False,
        "retention_write_allowed": False,
        "runtime_influence_allowed": False,
        "predictor_influence_allowed": False,
        "production_behavior_change_allowed": False,
        "selected_action_allowed": False,
        "final_action_allowed": False,
        "proof_of_learning_claim_allowed": False,
        "task_queue_status_is_approval": False,
        "passing_tests_are_approval": False,
        "codex_generated_status_is_approval": False,
        "audit_recorded": True,
        "rollback_available": True,
        "source_interpreted_candidate": candidate,
    }


def validate_human_interpretation_review_decision(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if record.get("record_type") != "human_interpretation_review_decision":
        errors.append("record_type_not_human_interpretation_review_decision")
    if record.get("record_version") != "v0":
        errors.append("record_version_not_v0")
    if record.get("target_record_type") != "human_interpreted_lesson_candidate_from_bucket_signal":
        errors.append("target_record_type_not_human_interpreted_lesson_candidate")
    if record.get("target_repeated_key") != REPEATED_KEY:
        errors.append("target_repeated_key_not_expected")
    if record.get("review_status") != "reviewed":
        errors.append("review_status_not_reviewed")
    decision = record.get("review_decision")
    allowed = record.get("allowed_review_decisions")
    if allowed != list(REVIEW_DECISIONS):
        errors.append("allowed_review_decisions_not_expected")
    if decision not in REVIEW_DECISIONS:
        errors.append("unknown_review_decision")
    if record.get("reviewer_actor") != "human":
        errors.append("reviewer_actor_not_human")
    if record.get("reviewer_role") != "project_owner":
        errors.append("reviewer_role_not_project_owner")
    if not isinstance(record.get("review_text"), str) or not record.get("review_text").strip():
        errors.append("review_text_empty")
    for field in (
        "not_application_approval",
        "not_memory_write_approval",
        "not_runtime_influence_approval",
        "not_predictor_approval",
        "not_proof_of_learning",
    ):
        if record.get(field) is not True:
            errors.append(f"{field}_not_true")
    if decision == "approved_for_future_memory_readiness_design_only":
        if record.get("memory_readiness_design_allowed") is not True:
            errors.append("approved_decision_did_not_allow_memory_readiness_design")
    elif decision in REVIEW_DECISIONS:
        if record.get("memory_readiness_design_allowed") is not False:
            errors.append("non_approved_decision_allowed_memory_readiness_design")
    for field in REVIEW_FALSE_PERMISSION_FIELDS:
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if record.get("retention_write_allowed") is not False:
        errors.append("retention_write_allowed_not_false")
    for field in ("task_queue_status_is_approval", "passing_tests_are_approval", "codex_generated_status_is_approval"):
        if record.get(field) is not False:
            errors.append(f"{field}_not_false")
    if record.get("audit_recorded") is not True:
        errors.append("audit_recorded_not_true")
    if record.get("rollback_available") is not True:
        errors.append("rollback_available_not_true")
    return {
        "valid": not errors,
        "error_codes": errors,
        "review_decision": decision,
        "memory_readiness_design_allowed": record.get("memory_readiness_design_allowed") is True,
        "memory_write_blocked": record.get("memory_write_allowed") is False,
        "runtime_influence_blocked": record.get("runtime_influence_allowed") is False,
        "proof_claim_blocked": record.get("proof_of_learning_claim_allowed") is False,
    }


def run_bucket_signal_human_interpretation_review_minimal_check() -> dict[str, Any]:
    valid_candidate = build_human_interpreted_lesson_candidate_from_bucket_signal()
    valid_decisions = [
        build_human_interpretation_review_decision(valid_candidate, decision)
        for decision in REVIEW_DECISIONS
    ]
    candidates = [valid_candidate] + _invalid_candidates(valid_candidate)
    decisions = valid_decisions + _invalid_decisions(valid_decisions[0])
    candidate_validations = [validate_human_interpreted_lesson_candidate(candidate) for candidate in candidates]
    decision_validations = [validate_human_interpretation_review_decision(decision) for decision in decisions]
    valid_candidate_results = [result for result in candidate_validations if result["valid"]]
    valid_decision_results = [result for result in decision_validations if result["valid"]]
    summary = {
        "valid_interpreted_candidate_count": len(valid_candidate_results),
        "invalid_interpreted_candidate_count": len(candidate_validations) - len(valid_candidate_results),
        "valid_review_decision_count": len(valid_decision_results),
        "invalid_review_decision_count": len(decision_validations) - len(valid_decision_results),
        "repo_audit_acknowledged_count": sum(1 for result in valid_candidate_results if result["repo_audit_acknowledged"]),
        "qingyin_self_authorship_blocked_count": sum(
            1 for result in valid_candidate_results if result["qingyin_self_authorship_blocked"]
        ),
        "human_review_required_count": sum(1 for result in valid_candidate_results if result["human_review_required"]),
        "memory_write_blocked_count": sum(
            1 for result in valid_candidate_results if result["memory_write_blocked"]
        )
        + sum(1 for result in valid_decision_results if result["memory_write_blocked"]),
        "runtime_influence_blocked_count": sum(
            1 for result in valid_candidate_results if result["runtime_influence_blocked"]
        )
        + sum(1 for result in valid_decision_results if result["runtime_influence_blocked"]),
        "proof_claim_blocked_count": sum(1 for result in valid_candidate_results if result["proof_claim_blocked"])
        + sum(1 for result in valid_decision_results if result["proof_claim_blocked"]),
        "approved_for_future_memory_readiness_design_only_count": sum(
            1
            for result in valid_decision_results
            if result["review_decision"] == "approved_for_future_memory_readiness_design_only"
        ),
        "rejected_count": sum(1 for result in valid_decision_results if result["review_decision"] == "rejected"),
        "needs_more_evidence_count": sum(
            1 for result in valid_decision_results if result["review_decision"] == "needs_more_evidence"
        ),
        "needs_rewrite_count": sum(
            1 for result in valid_decision_results if result["review_decision"] == "needs_rewrite"
        ),
    }
    summary["all_bucket_signal_human_interpretation_review_checks_passed"] = _all_checks_passed(summary)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_bucket_signal_human_interpretation_review_checks_passed"] else "failed",
        "valid_interpreted_candidate": valid_candidate,
        "valid_review_decisions": valid_decisions,
        "candidate_validation_results": candidate_validations,
        "review_decision_validation_results": decision_validations,
        "summary": summary,
        "boundary": {
            "boundary_change_required": False,
            "boundary_index_update_required": False,
            "boundary_index_version_before": BOUNDARY_VERSION,
            "boundary_index_version_after": BOUNDARY_VERSION,
            "rationale": (
                "This package records human interpretation and human review of an existing structured signal "
                "inside current trace/checker constraints. It does not write memory, write retained JSONL, "
                "change runtime behavior, mutate predictors, select actions, promote production behavior, "
                "or claim proof of learning."
            ),
        },
        "safe_claim": (
            "ASHL Core can take a bucket-derived structured lesson candidate signal, record a human or "
            "human/GPT-assisted interpretation as a reviewable lesson candidate, and record a human review "
            "decision for future memory readiness design only, while keeping memory write, retained JSONL "
            "write, runtime influence, predictor mutation, action selection, production promotion, and "
            "proof-of-learning blocked."
        ),
        "audit_claim": (
            "Qingyin is currently a boundary-constrained Phase0 trace/checker system, not an autonomous "
            "learning or autonomous acting individual."
        ),
    }


def _validate_audit_fields(record: dict[str, Any], errors: list[str]) -> None:
    for field, expected in AUDIT_FIELDS.items():
        if record.get(field) != expected:
            errors.append(f"{field}_not_expected")


def _review_text(decision: str) -> str:
    if decision == "approved_for_future_memory_readiness_design_only":
        return (
            "Human reviewer accepts this as a human-interpreted lesson candidate derived from a bucket "
            "signal, for future memory readiness design only."
        )
    if decision == "rejected":
        return "Human reviewer rejects this interpreted candidate."
    if decision == "needs_more_evidence":
        return "Human reviewer requires more evidence before this interpreted candidate can continue."
    return "Human reviewer requires the interpreted candidate to be rewritten before it can continue."


def _invalid_candidates(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalid = [
        _mutated(valid, ["qingyin_generated_text"], True),
        _mutated(valid, ["qingyin_self_proposed_text"], True),
        _mutated(valid, ["candidate_text_generated_by_qingyin"], True),
        _mutated(valid, ["repo_audit_acknowledged"], False),
        _mutated(valid, ["qingyin_current_status"], "autonomous_learner"),
        _mutated(valid, ["qingyin_autonomous_learning_claim_allowed"], True),
        _mutated(valid, ["qingyin_autonomous_action_claim_allowed"], True),
        _mutated(valid, ["runtime_memory_influenced_behavior_count"], 1),
        _mutated(valid, ["human_review_required"], False),
        _mutated(valid, ["source_occurrence_count"], 2),
        _mutated(valid, ["interpreted_lesson_text"], ""),
        _mutated(valid, ["plain_language_summary"], ""),
        _mutated(valid, ["source_repeated_key"], "other_key"),
        _mutated(valid, ["task_queue_status_is_approval"], True),
        _mutated(valid, ["passing_tests_are_approval"], True),
        _mutated(valid, ["codex_generated_status_is_approval"], True),
        _mutated(valid, ["retention_write_allowed"], True),
        _mutated(valid, ["audit_recorded"], False),
        _mutated(valid, ["rollback_available"], False),
    ]
    for field in FALSE_PERMISSION_FIELDS:
        invalid.append(_mutated(valid, [field], True))
    return invalid


def _invalid_decisions(valid: dict[str, Any]) -> list[dict[str, Any]]:
    invalid = [
        _mutated(valid, ["review_decision"], "applied"),
        _mutated(valid, ["reviewer_actor"], "codex"),
        _mutated(valid, ["reviewer_role"], "assistant"),
        _mutated(valid, ["review_text"], ""),
        _mutated(valid, ["not_application_approval"], False),
        _mutated(valid, ["not_memory_write_approval"], False),
        _mutated(valid, ["not_runtime_influence_approval"], False),
        _mutated(valid, ["not_predictor_approval"], False),
        _mutated(valid, ["not_proof_of_learning"], False),
        _mutated(valid, ["memory_readiness_design_allowed"], False),
        _mutated(valid, ["task_queue_status_is_approval"], True),
        _mutated(valid, ["passing_tests_are_approval"], True),
        _mutated(valid, ["codex_generated_status_is_approval"], True),
        _mutated(valid, ["retention_write_allowed"], True),
        _mutated(valid, ["audit_recorded"], False),
        _mutated(valid, ["rollback_available"], False),
    ]
    rejected = build_human_interpretation_review_decision(
        valid["source_interpreted_candidate"], "rejected"
    )
    rejected["memory_readiness_design_allowed"] = True
    invalid.append(rejected)
    for field in REVIEW_FALSE_PERMISSION_FIELDS:
        invalid.append(_mutated(valid, [field], True))
    return invalid


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["valid_interpreted_candidate_count"] == 1
        and summary["invalid_interpreted_candidate_count"] >= 1
        and summary["valid_review_decision_count"] == 4
        and summary["invalid_review_decision_count"] >= 1
        and summary["repo_audit_acknowledged_count"] == 1
        and summary["qingyin_self_authorship_blocked_count"] == 1
        and summary["human_review_required_count"] == 1
        and summary["memory_write_blocked_count"] == 5
        and summary["runtime_influence_blocked_count"] == 5
        and summary["proof_claim_blocked_count"] == 5
        and summary["approved_for_future_memory_readiness_design_only_count"] == 1
        and summary["rejected_count"] == 1
        and summary["needs_more_evidence_count"] == 1
        and summary["needs_rewrite_count"] == 1
    )


def _mutated(record: dict[str, Any], path: list[Any], value: Any) -> dict[str, Any]:
    clone = deepcopy(record)
    cursor: Any = clone
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return clone


if __name__ == "__main__":
    import json

    print(json.dumps(run_bucket_signal_human_interpretation_review_minimal_check(), indent=2))
