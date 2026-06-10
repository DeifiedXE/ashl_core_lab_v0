"""Minimal mentor-gated durable retention for session experience records."""

from __future__ import annotations

import json
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

from .session_experience_record_schema_minimal import (
    run_session_experience_record_schema_minimal_check,
    validate_session_experience_record,
)


COMMAND = "run-mentor-gated-experience-retention-minimal-check"
FLOW = "mentor_gated_experience_retention_minimal_v0"
APPROVAL_PHRASE = "留"
RETENTION_TARGET = "append_only_jsonl"
DEFAULT_RETENTION_PATH = Path("data/retention/mentor_retained_experiences_v0.jsonl")

REQUIRED_DECISION_FIELDS = {
    "retention_decision_id",
    "source_experience_record_id",
    "mentor_text",
    "approved_for_retention",
    "retention_target",
    "trace_only",
    "blocked_flags",
}

REQUIRED_DECISION_BLOCKED_FLAGS = {
    "automatic_retention",
    "action_selection_influence",
    "action_behavior_changed",
    "predictor_modified",
    "proof_of_learning_claim",
}

REQUIRED_RETAINED_FIELDS = {
    "retained_record_id",
    "source_experience_record_id",
    "exact_key",
    "experience_type",
    "retention_status",
    "retained_by",
    "retention_reason",
    "source_snapshot",
    "blocked_flags",
}

REQUIRED_RETAINED_BLOCKED_FLAGS = {
    "action_selection_influence",
    "action_behavior_changed",
    "predictor_modified",
    "proof_of_learning_claim",
}


def build_mentor_retention_decision(
    experience_record: dict[str, Any],
    mentor_text: str,
) -> dict[str, Any]:
    source_id = experience_record.get("experience_record_id")
    approved = mentor_text == APPROVAL_PHRASE
    return {
        "retention_decision_id": f"mentor_retention_decision:{_ascii_safe(source_id)}",
        "source_experience_record_id": source_id,
        "mentor_text": mentor_text,
        "approved_for_retention": approved,
        "retention_target": RETENTION_TARGET,
        "trace_only": False,
        "blocked_flags": _decision_blocked_flags(),
    }


def validate_mentor_retention_decision(decision: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_DECISION_FIELDS if field not in decision)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in decision if field not in REQUIRED_DECISION_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not decision.get("source_experience_record_id"):
        errors.append("missing_source_linkage:source_experience_record_id")
    if not isinstance(decision.get("mentor_text"), str):
        errors.append("mentor_text_not_string")
    if not isinstance(decision.get("approved_for_retention"), bool):
        errors.append("approved_for_retention_not_boolean")
    if decision.get("retention_target") != RETENTION_TARGET:
        errors.append("retention_target_not_append_only_jsonl")
    if decision.get("trace_only") is not False:
        errors.append("trace_only_not_false_for_retention_decision")

    mentor_text = decision.get("mentor_text")
    approved = decision.get("approved_for_retention")
    if mentor_text == APPROVAL_PHRASE and approved is not True:
        errors.append("approval_phrase_not_approved")
    if mentor_text != APPROVAL_PHRASE and approved is not False:
        errors.append("non_approval_phrase_approved")
    if mentor_text != APPROVAL_PHRASE:
        errors.append("mentor_text_not_approval_phrase")

    blocked_flags = decision.get("blocked_flags")
    if not isinstance(blocked_flags, dict):
        errors.append("blocked_flags_missing_or_not_dict")
        blocked_flags = {}
    for field in sorted(REQUIRED_DECISION_BLOCKED_FLAGS):
        if field not in blocked_flags:
            errors.append(f"missing_blocked_flag:{field}")
        elif blocked_flags.get(field) not in {False, 0}:
            errors.append(f"{field}_enabled")

    return {
        "retention_decision_id": decision.get("retention_decision_id"),
        "source_experience_record_id": decision.get("source_experience_record_id"),
        "valid": not errors,
        "error_codes": errors,
        "mentor_text": decision.get("mentor_text"),
        "approved_for_retention": decision.get("approved_for_retention") is True,
        "retention_target": decision.get("retention_target"),
        "trace_only": decision.get("trace_only") is False,
        "automatic_retention": blocked_flags.get("automatic_retention") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def append_retained_experience_jsonl(
    experience_record: dict[str, Any],
    decision: dict[str, Any],
    path: str | Path,
) -> dict[str, Any]:
    record_copy = deepcopy(experience_record)
    decision_copy = deepcopy(decision)
    path = Path(path)

    record_validation = validate_session_experience_record(record_copy)
    decision_validation = validate_mentor_retention_decision(decision_copy)
    errors: list[str] = []
    if not record_validation["valid"]:
        errors.append("invalid_session_experience_record")
    if record_copy.get("retention_status") != "not_retained":
        errors.append("source_retention_status_not_not_retained")
    if not decision_validation["valid"]:
        errors.append("invalid_retention_decision")
    if decision_copy.get("approved_for_retention") is not True:
        errors.append("decision_not_approved_for_retention")
    if decision_copy.get("source_experience_record_id") != record_copy.get("experience_record_id"):
        errors.append("source_experience_record_id_mismatch")

    if errors:
        return {
            "appended": False,
            "path": str(path),
            "retained_record": None,
            "error_codes": errors,
        }

    retained_record = _build_retained_record(record_copy)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(retained_record, ensure_ascii=False, sort_keys=True))
        handle.write("\n")

    loaded = load_retained_experience_jsonl(path)
    return {
        "appended": True,
        "append_only": True,
        "path": str(path),
        "retained_record": retained_record,
        "loaded_record_count": len(loaded),
        "loaded_records_include_appended": retained_record in loaded,
        "error_codes": [],
    }


def load_retained_experience_jsonl(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def run_mentor_gated_experience_retention_minimal_check() -> dict[str, Any]:
    source_record = _valid_session_experience_record()
    approved_decision = build_mentor_retention_decision(source_record, APPROVAL_PHRASE)
    decisions = [approved_decision] + _invalid_demo_decisions(approved_decision)
    decision_validations = [validate_mentor_retention_decision(decision) for decision in decisions]

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "nested" / "mentor_retained_experiences_v0.jsonl"
        append_result = append_retained_experience_jsonl(source_record, approved_decision, path)
        loaded_records = load_retained_experience_jsonl(path)

        blocked_decision = build_mentor_retention_decision(source_record, "不要")
        not_approved_append_result = append_retained_experience_jsonl(source_record, blocked_decision, path)

        mismatch_decision = deepcopy(approved_decision)
        mismatch_decision["source_experience_record_id"] = "other_session_experience"
        source_mismatch_append_result = append_retained_experience_jsonl(source_record, mismatch_decision, path)

    retained_record = append_result.get("retained_record")
    summary = _build_summary(
        decision_validations,
        append_result,
        loaded_records,
        not_approved_append_result,
        source_mismatch_append_result,
        retained_record,
    )
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "source_session_experience_record": source_record,
        "retention_decisions": decisions,
        "decision_validation_results": decision_validations,
        "append_result": append_result,
        "loaded_records": loaded_records,
        "not_approved_append_result": not_approved_append_result,
        "source_mismatch_append_result": source_mismatch_append_result,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker opens the first mentor-gated append-only JSONL retention path.",
            "Only exact mentor_text == '留' approves retention in v0.",
            "The CLI check uses a temporary file and does not write the default project retention file.",
            "Retained records do not influence action selection, change behavior, mutate predictors, or claim proof of learning.",
        ],
    }


def _valid_session_experience_record() -> dict[str, Any]:
    result = run_session_experience_record_schema_minimal_check()
    return deepcopy(
        next(
            record
            for record, validation in zip(
                result["session_experience_records"],
                result["validation_results"],
            )
            if validation["valid"]
        )
    )


def _invalid_demo_decisions(valid_decision: dict[str, Any]) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []

    blocked_text = _copy_decision_case(valid_decision, "mentor_text_blocked")
    blocked_text["mentor_text"] = "不要"
    blocked_text["approved_for_retention"] = False
    decisions.append(blocked_text)

    for flag in [
        "automatic_retention",
        "action_selection_influence",
        "action_behavior_changed",
        "predictor_modified",
        "proof_of_learning_claim",
    ]:
        flagged = _copy_decision_case(valid_decision, flag)
        flagged["blocked_flags"][flag] = True
        decisions.append(flagged)

    return decisions


def _build_summary(
    decision_validations: list[dict[str, Any]],
    append_result: dict[str, Any],
    loaded_records: list[dict[str, Any]],
    not_approved_append_result: dict[str, Any],
    source_mismatch_append_result: dict[str, Any],
    retained_record: dict[str, Any] | None,
) -> dict[str, int | bool]:
    valid_decisions = [result for result in decision_validations if result["valid"]]
    retained_records = [retained_record] if retained_record else []
    summary: dict[str, int | bool] = {
        "retention_decision_count": len(decision_validations),
        "approved_retention_decision_count": sum(
            1 for result in valid_decisions if result["approved_for_retention"]
        ),
        "blocked_retention_decision_count": sum(
            1 for result in decision_validations if not result["valid"]
        ),
        "jsonl_append_count": 1 if append_result.get("appended") is True else 0,
        "jsonl_load_back_count": 1 if append_result.get("loaded_records_include_appended") is True else 0,
        "retained_record_count": len(loaded_records),
        "mentor_text_blocked_count": _count_error(
            decision_validations, "mentor_text_not_approval_phrase"
        ),
        "automatic_retention_blocked_count": _count_error(
            decision_validations, "automatic_retention_enabled"
        ),
        "action_selection_influence_blocked_count": _count_error(
            decision_validations, "action_selection_influence_enabled"
        ),
        "action_behavior_changed_blocked_count": _count_error(
            decision_validations, "action_behavior_changed_enabled"
        ),
        "predictor_modified_blocked_count": _count_error(
            decision_validations, "predictor_modified_enabled"
        ),
        "proof_of_learning_claim_blocked_count": _count_error(
            decision_validations, "proof_of_learning_claim_enabled"
        ),
        "not_approved_append_blocked_count": _count_append_error(
            not_approved_append_result, "decision_not_approved_for_retention"
        ),
        "source_mismatch_append_blocked_count": _count_append_error(
            source_mismatch_append_result, "source_experience_record_id_mismatch"
        ),
        "retained_action_selection_influence_count": _count_retained_flag(
            retained_records, "action_selection_influence"
        ),
        "retained_action_behavior_changed_count": _count_retained_flag(
            retained_records, "action_behavior_changed"
        ),
        "retained_predictor_modified_count": _count_retained_flag(
            retained_records, "predictor_modified"
        ),
        "retained_proof_of_learning_claim_count": _count_retained_flag(
            retained_records, "proof_of_learning_claim"
        ),
    }
    summary["all_mentor_gated_experience_retention_minimal_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["retention_decision_count"] == 7
        and summary["approved_retention_decision_count"] == 1
        and summary["blocked_retention_decision_count"] == 6
        and summary["jsonl_append_count"] == 1
        and summary["jsonl_load_back_count"] == 1
        and summary["retained_record_count"] == 1
        and summary["mentor_text_blocked_count"] == 1
        and summary["automatic_retention_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["not_approved_append_blocked_count"] == 1
        and summary["source_mismatch_append_blocked_count"] == 1
        and summary["retained_action_selection_influence_count"] == 0
        and summary["retained_action_behavior_changed_count"] == 0
        and summary["retained_predictor_modified_count"] == 0
        and summary["retained_proof_of_learning_claim_count"] == 0
    )


def _boundary_check(summary: dict[str, Any]) -> dict[str, bool | int | str]:
    return {
        "mentor_gated_experience_retention_minimal_enabled": True,
        "first_true_retention_boundary": True,
        "append_only_jsonl": True,
        "durable_read_back_supported": True,
        "mentor_text_exact_lau_only": True,
        "approval_phrase": APPROVAL_PHRASE,
        "default_retention_path": str(DEFAULT_RETENTION_PATH),
        "production_write_cli_added": False,
        "automatic_retention_added": False,
        "four_layer_memory_added": False,
        "semantic_similarity_added": False,
        "fuzzy_matching_added": False,
        "vector_retrieval_added": False,
        "lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "rollback_manual_only": True,
        "destructive_auto_delete_added": False,
        "retained_action_selection_influence_count": summary["retained_action_selection_influence_count"],
        "retained_action_behavior_changed_count": summary["retained_action_behavior_changed_count"],
        "retained_predictor_modified_count": summary["retained_predictor_modified_count"],
        "retained_proof_of_learning_claim_count": summary["retained_proof_of_learning_claim_count"],
    }


def _build_retained_record(experience_record: dict[str, Any]) -> dict[str, Any]:
    source_id = experience_record.get("experience_record_id")
    return {
        "retained_record_id": f"retained_experience:{_ascii_safe(source_id)}",
        "source_experience_record_id": source_id,
        "exact_key": experience_record.get("exact_key"),
        "experience_type": experience_record.get("experience_type"),
        "retention_status": "retained",
        "retained_by": "mentor",
        "retention_reason": f"mentor_text:{APPROVAL_PHRASE}",
        "source_snapshot": {
            "source_evidence_trace_id": experience_record.get("source_evidence_trace_id"),
            "source_bucket_candidate_id": experience_record.get("source_bucket_candidate_id"),
            "original_retention_status": experience_record.get("retention_status"),
        },
        "blocked_flags": _retained_blocked_flags(),
    }


def _decision_blocked_flags() -> dict[str, bool]:
    return {
        "automatic_retention": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "predictor_modified": False,
        "proof_of_learning_claim": False,
    }


def _retained_blocked_flags() -> dict[str, bool]:
    return {
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "predictor_modified": False,
        "proof_of_learning_claim": False,
    }


def _copy_decision_case(decision: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(decision)
    copied["retention_decision_id"] = f"{decision['retention_decision_id']}:{case_name}"
    return copied


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_append_error(result: dict[str, Any], error_code: str) -> int:
    return 1 if error_code in result.get("error_codes", []) else 0


def _count_retained_flag(records: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for record in records if record.get("blocked_flags", {}).get(flag) is True)


def _ascii_safe(value: Any) -> str:
    text = "null" if value is None else str(value)
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in text)
