"""Minimal controlled visual grounding trial wrapper."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .visual_retained_experience_link_preview_minimal import (
    run_visual_retained_experience_link_preview_minimal_check,
)
from .visual_retention_demo_snapshot_minimal import (
    run_visual_retention_demo_snapshot_minimal_check,
    validate_visual_retention_demo_snapshot,
)


COMMAND = "run-minimal-visual-grounding-trial-check"
FLOW = "minimal_visual_grounding_trial_v0"
INPUT_TYPE = "controlled_symbolic_visual_change"

ALLOWED_MATCH_STATUSES = {"matched", "not_matched"}

REQUIRED_FIELDS = {
    "trial_id",
    "demo_input",
    "source_ids",
    "read_only",
    "human_summary",
    "trial_result",
    "blocked_flags",
}

REQUIRED_SOURCE_IDS = {
    "visual_experience_candidate_id",
    "retina_focus_preview_id",
    "visual_lesson_evidence_candidate_id",
    "visual_retention_demo_snapshot_id",
}

REQUIRED_TRIAL_RESULT_FLAGS = {
    "visual_change_observed",
    "focus_preview_available",
    "lesson_evidence_available",
    "retained_link_preview_available",
    "same_exact_key_only",
}

REQUIRED_BLOCKED_FLAGS = {
    "object_recognition",
    "semantic_vision",
    "active_focus_applied",
    "attention_control",
    "lesson_candidate_created",
    "lesson_applied",
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


def build_minimal_visual_grounding_trial() -> dict[str, Any]:
    snapshots = _valid_snapshots_by_status()
    visual_ids = _visual_experience_ids_by_retina_preview_id()
    matched_snapshot = snapshots["matched"]
    return _build_trial_from_snapshot(
        matched_snapshot,
        visual_ids.get(matched_snapshot.get("source_retina_focus_preview_id"), ""),
    )


def validate_minimal_visual_grounding_trial(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []

    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    extra_fields = sorted(field for field in record if field not in REQUIRED_FIELDS)
    errors.extend(f"unexpected_field:{field}" for field in extra_fields)

    if not isinstance(record.get("trial_id"), str) or not record.get("trial_id"):
        errors.append("trial_id_missing")

    demo_input = record.get("demo_input")
    if not isinstance(demo_input, dict):
        errors.append("demo_input_missing_or_not_dict")
        demo_input = {}
    if demo_input.get("input_type") != INPUT_TYPE:
        errors.append("input_type_not_controlled_symbolic_visual_change")
    if not isinstance(demo_input.get("before"), str) or not demo_input.get("before"):
        errors.append("before_empty_or_not_string")
    if not isinstance(demo_input.get("after"), str) or not demo_input.get("after"):
        errors.append("after_empty_or_not_string")
    if not isinstance(demo_input.get("expected_observation"), str) or not demo_input.get("expected_observation"):
        errors.append("expected_observation_empty_or_not_string")

    source_ids = record.get("source_ids")
    if not isinstance(source_ids, dict):
        errors.append("source_ids_missing_or_not_dict")
        source_ids = {}
    for field in sorted(REQUIRED_SOURCE_IDS):
        if not isinstance(source_ids.get(field), str) or not source_ids.get(field):
            errors.append(f"missing_source_id:{field}")

    if record.get("read_only") is not True:
        errors.append("read_only_not_true")

    human_summary = record.get("human_summary")
    if not isinstance(human_summary, dict):
        errors.append("human_summary_missing_or_not_dict")
        human_summary = {}
    if not isinstance(human_summary.get("what_happened"), str) or not human_summary.get("what_happened"):
        errors.append("what_happened_empty_or_not_string")
    if not isinstance(human_summary.get("what_was_noticed"), str) or not human_summary.get("what_was_noticed"):
        errors.append("what_was_noticed_empty_or_not_string")
    if not isinstance(human_summary.get("what_focus_preview_says"), str) or not human_summary.get(
        "what_focus_preview_says"
    ):
        errors.append("what_focus_preview_says_empty_or_not_string")
    if not isinstance(human_summary.get("what_evidence_says"), str) or not human_summary.get("what_evidence_says"):
        errors.append("what_evidence_says_empty_or_not_string")
    if human_summary.get("retained_match_status") not in ALLOWED_MATCH_STATUSES:
        errors.append("retained_match_status_not_matched_or_not_matched")
    if not isinstance(human_summary.get("plain_result"), str) or not human_summary.get("plain_result"):
        errors.append("plain_result_empty_or_not_string")

    trial_result = record.get("trial_result")
    if not isinstance(trial_result, dict):
        errors.append("trial_result_missing_or_not_dict")
        trial_result = {}
    for field in sorted(REQUIRED_TRIAL_RESULT_FLAGS):
        if field not in trial_result:
            errors.append(f"missing_trial_result:{field}")
        elif trial_result.get(field) is not True:
            errors.append(f"{field}_not_true")

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
        "trial_id": record.get("trial_id"),
        "valid": not errors,
        "error_codes": errors,
        "retained_match_status": human_summary.get("retained_match_status"),
        "matched": human_summary.get("retained_match_status") == "matched",
        "not_matched": human_summary.get("retained_match_status") == "not_matched",
        "read_only": record.get("read_only") is True,
        "same_exact_key_only": trial_result.get("same_exact_key_only") is True,
        "object_recognition": blocked_flags.get("object_recognition") is True,
        "semantic_vision": blocked_flags.get("semantic_vision") is True,
        "active_focus_applied": blocked_flags.get("active_focus_applied") is True,
        "attention_control": blocked_flags.get("attention_control") is True,
        "lesson_candidate_created": blocked_flags.get("lesson_candidate_created") is True,
        "lesson_applied": blocked_flags.get("lesson_applied") is True,
        "action_selection_influence": blocked_flags.get("action_selection_influence") is True,
        "action_behavior_changed": blocked_flags.get("action_behavior_changed") is True,
        "memory_write": blocked_flags.get("memory_write") is True,
        "new_retention_written": blocked_flags.get("new_retention_written") is True,
        "semantic_match": blocked_flags.get("semantic_match") is True,
        "fuzzy_match": blocked_flags.get("fuzzy_match") is True,
        "vector_match": blocked_flags.get("vector_match") is True,
        "predictor_modified": blocked_flags.get("predictor_modified") is True,
        "proof_of_learning_claim": blocked_flags.get("proof_of_learning_claim") is True,
    }


def run_minimal_visual_grounding_trial_check() -> dict[str, Any]:
    snapshots = _valid_snapshots_by_status()
    visual_ids = _visual_experience_ids_by_retina_preview_id()
    matched_snapshot = snapshots["matched"]
    not_matched_snapshot = snapshots["not_matched"]

    valid_matched = _build_trial_from_snapshot(
        matched_snapshot,
        visual_ids.get(matched_snapshot.get("source_retina_focus_preview_id"), ""),
    )
    valid_not_matched = _build_trial_from_snapshot(
        not_matched_snapshot,
        visual_ids.get(not_matched_snapshot.get("source_retina_focus_preview_id"), ""),
    )
    trials = [
        valid_matched,
        valid_not_matched,
        *_invalid_demo_trials(valid_matched),
    ]
    validation_results = [validate_minimal_visual_grounding_trial(trial) for trial in trials]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(summary) else "failed",
        "minimal_visual_grounding_trials": trials,
        "valid_human_summaries": [
            trial["human_summary"]
            for trial, validation in zip(trials, validation_results)
            if validation["valid"]
        ],
        "validation_results": validation_results,
        "source_visual_retention_demo_snapshot_flow": "visual_retention_demo_snapshot_minimal_v0",
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This check wraps one controlled symbolic visual change into a read-only visual grounding trial summary.",
            "It reuses existing visual experience, retina focus preview, visual lesson evidence, retained link preview, and demo snapshot records.",
            "No object recognition, semantic vision, active focus, attention control, lesson creation/application, action influence, memory write, new retention, retrieval expansion, predictor mutation, or proof of learning is added.",
        ],
    }


def _valid_snapshots_by_status() -> dict[str, dict[str, Any]]:
    result = run_visual_retention_demo_snapshot_minimal_check()
    snapshots: dict[str, dict[str, Any]] = {}
    for snapshot in result.get("visual_retention_demo_snapshots", []):
        validation = validate_visual_retention_demo_snapshot(snapshot)
        status = snapshot.get("human_summary", {}).get("retained_match_status")
        if validation["valid"] and status in ALLOWED_MATCH_STATUSES and status not in snapshots:
            snapshots[status] = deepcopy(snapshot)
    return snapshots


def _visual_experience_ids_by_retina_preview_id() -> dict[str, str]:
    result = run_visual_retained_experience_link_preview_minimal_check()
    evidence_result = result.get("source_visual_lesson_evidence_result", {})
    retina_result = evidence_result.get("source_retina_focus_preview_result", {})
    previews = retina_result.get("retina_focus_previews", [])
    return {
        preview.get("retina_focus_preview_id"): preview.get("source_visual_experience_candidate_id")
        for preview in previews
        if isinstance(preview, dict)
        and isinstance(preview.get("retina_focus_preview_id"), str)
        and isinstance(preview.get("source_visual_experience_candidate_id"), str)
    }


def _build_trial_from_snapshot(snapshot: dict[str, Any], visual_experience_candidate_id: str) -> dict[str, Any]:
    snapshot_summary = snapshot.get("human_summary", {})
    match_status = snapshot_summary.get("retained_match_status")
    return {
        "trial_id": f"minimal_visual_grounding_trial:{match_status}",
        "demo_input": {
            "input_type": INPUT_TYPE,
            "before": "stable frame",
            "after": "one visible frame-level change",
            "expected_observation": "a visible frame-level change should be noticed",
        },
        "source_ids": {
            "visual_experience_candidate_id": visual_experience_candidate_id,
            "retina_focus_preview_id": snapshot.get("source_retina_focus_preview_id"),
            "visual_lesson_evidence_candidate_id": snapshot.get("source_visual_lesson_evidence_candidate_id"),
            "visual_retention_demo_snapshot_id": snapshot.get("snapshot_id"),
        },
        "read_only": True,
        "human_summary": {
            "what_happened": "A controlled visual demo changed one frame-level element.",
            "what_was_noticed": snapshot_summary.get("what_changed"),
            "what_focus_preview_says": snapshot_summary.get("what_focus_preview_says"),
            "what_evidence_says": snapshot_summary.get("what_lesson_evidence_says"),
            "retained_match_status": match_status,
            "plain_result": _plain_result(match_status),
        },
        "trial_result": _trial_result(),
        "blocked_flags": _blocked_flags(),
    }


def _plain_result(match_status: Any) -> str:
    if match_status == "matched":
        return (
            "The system can show that a small visual change was noticed and preview-linked to retained experience "
            "by exact key only."
        )
    if match_status == "not_matched":
        return (
            "The system can show that a small visual change was noticed without a retained experience match by "
            "exact key."
        )
    return ""


def _trial_result() -> dict[str, bool]:
    return {
        "visual_change_observed": True,
        "focus_preview_available": True,
        "lesson_evidence_available": True,
        "retained_link_preview_available": True,
        "same_exact_key_only": True,
    }


def _blocked_flags() -> dict[str, bool]:
    return {
        "object_recognition": False,
        "semantic_vision": False,
        "active_focus_applied": False,
        "attention_control": False,
        "lesson_candidate_created": False,
        "lesson_applied": False,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "memory_write": False,
        "new_retention_written": False,
        "semantic_match": False,
        "fuzzy_match": False,
        "vector_match": False,
        "predictor_modified": False,
        "proof_of_learning_claim": False,
    }


def _invalid_demo_trials(valid_trial: dict[str, Any]) -> list[dict[str, Any]]:
    trials: list[dict[str, Any]] = []

    read_only_false = _copy_case(valid_trial, "read_only_false")
    read_only_false["read_only"] = False
    trials.append(read_only_false)

    wrong_input = _copy_case(valid_trial, "wrong_input_type")
    wrong_input["demo_input"]["input_type"] = "semantic_scene_change"
    trials.append(wrong_input)

    missing_source = _copy_case(valid_trial, "missing_source_id")
    missing_source["source_ids"]["visual_experience_candidate_id"] = ""
    trials.append(missing_source)

    empty_happened = _copy_case(valid_trial, "empty_what_happened")
    empty_happened["human_summary"]["what_happened"] = ""
    trials.append(empty_happened)

    empty_plain = _copy_case(valid_trial, "empty_plain_result")
    empty_plain["human_summary"]["plain_result"] = ""
    trials.append(empty_plain)

    bad_status = _copy_case(valid_trial, "bad_retained_match_status")
    bad_status["human_summary"]["retained_match_status"] = "semantic_match"
    trials.append(bad_status)

    for flag in sorted(REQUIRED_TRIAL_RESULT_FLAGS):
        flagged = _copy_case(valid_trial, flag)
        flagged["trial_result"][flag] = False
        trials.append(flagged)

    for flag in sorted(REQUIRED_BLOCKED_FLAGS):
        flagged = _copy_case(valid_trial, flag)
        flagged["blocked_flags"][flag] = True
        trials.append(flagged)

    return trials


def _copy_case(trial: dict[str, Any], case_name: str) -> dict[str, Any]:
    copied = deepcopy(trial)
    copied["trial_id"] = f"{trial['trial_id']}:{case_name}"
    return copied


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int | bool]:
    valid_results = [result for result in validation_results if result["valid"]]
    summary: dict[str, int | bool] = {
        "minimal_visual_grounding_trial_count": len(validation_results),
        "valid_minimal_visual_grounding_trial_count": len(valid_results),
        "invalid_minimal_visual_grounding_trial_count": sum(1 for result in validation_results if not result["valid"]),
        "matched_trial_count": sum(1 for result in valid_results if result["matched"]),
        "not_matched_trial_count": sum(1 for result in valid_results if result["not_matched"]),
        "read_only_false_blocked_count": _count_error(validation_results, "read_only_not_true"),
        "input_type_blocked_count": _count_error(
            validation_results, "input_type_not_controlled_symbolic_visual_change"
        ),
        "missing_source_id_blocked_count": sum(
            1 for result in validation_results for error in result["error_codes"] if error.startswith("missing_source_id:")
        ),
        "empty_what_happened_blocked_count": _count_error(validation_results, "what_happened_empty_or_not_string"),
        "empty_plain_result_blocked_count": _count_error(validation_results, "plain_result_empty_or_not_string"),
        "retained_match_status_blocked_count": _count_error(
            validation_results, "retained_match_status_not_matched_or_not_matched"
        ),
        "visual_change_observed_false_blocked_count": _count_error(
            validation_results, "visual_change_observed_not_true"
        ),
        "focus_preview_available_false_blocked_count": _count_error(
            validation_results, "focus_preview_available_not_true"
        ),
        "lesson_evidence_available_false_blocked_count": _count_error(
            validation_results, "lesson_evidence_available_not_true"
        ),
        "retained_link_preview_available_false_blocked_count": _count_error(
            validation_results, "retained_link_preview_available_not_true"
        ),
        "same_exact_key_only_false_blocked_count": _count_error(validation_results, "same_exact_key_only_not_true"),
        "object_recognition_blocked_count": _count_error(validation_results, "object_recognition_enabled"),
        "semantic_vision_blocked_count": _count_error(validation_results, "semantic_vision_enabled"),
        "active_focus_applied_blocked_count": _count_error(validation_results, "active_focus_applied_enabled"),
        "attention_control_blocked_count": _count_error(validation_results, "attention_control_enabled"),
        "lesson_candidate_created_blocked_count": _count_error(
            validation_results, "lesson_candidate_created_enabled"
        ),
        "lesson_applied_blocked_count": _count_error(validation_results, "lesson_applied_enabled"),
        "action_selection_influence_blocked_count": _count_error(
            validation_results, "action_selection_influence_enabled"
        ),
        "action_behavior_changed_blocked_count": _count_error(validation_results, "action_behavior_changed_enabled"),
        "memory_write_blocked_count": _count_error(validation_results, "memory_write_enabled"),
        "new_retention_written_blocked_count": _count_error(validation_results, "new_retention_written_enabled"),
        "semantic_match_blocked_count": _count_error(validation_results, "semantic_match_enabled"),
        "fuzzy_match_blocked_count": _count_error(validation_results, "fuzzy_match_enabled"),
        "vector_match_blocked_count": _count_error(validation_results, "vector_match_enabled"),
        "predictor_modified_blocked_count": _count_error(validation_results, "predictor_modified_enabled"),
        "proof_of_learning_claim_blocked_count": _count_error(validation_results, "proof_of_learning_claim_enabled"),
        "object_recognition_count": _count_valid_flag(valid_results, "object_recognition"),
        "semantic_vision_count": _count_valid_flag(valid_results, "semantic_vision"),
        "active_focus_applied_count": _count_valid_flag(valid_results, "active_focus_applied"),
        "attention_control_count": _count_valid_flag(valid_results, "attention_control"),
        "lesson_candidate_created_count": _count_valid_flag(valid_results, "lesson_candidate_created"),
        "lesson_applied_count": _count_valid_flag(valid_results, "lesson_applied"),
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
    summary["all_minimal_visual_grounding_trial_checks_passed"] = _all_checks_passed(summary)
    return summary


def _all_checks_passed(summary: dict[str, Any]) -> bool:
    return (
        summary["minimal_visual_grounding_trial_count"] == 28
        and summary["valid_minimal_visual_grounding_trial_count"] == 2
        and summary["invalid_minimal_visual_grounding_trial_count"] == 26
        and summary["matched_trial_count"] == 1
        and summary["not_matched_trial_count"] == 1
        and summary["read_only_false_blocked_count"] == 1
        and summary["input_type_blocked_count"] == 1
        and summary["missing_source_id_blocked_count"] == 1
        and summary["empty_what_happened_blocked_count"] == 1
        and summary["empty_plain_result_blocked_count"] == 1
        and summary["retained_match_status_blocked_count"] == 1
        and summary["visual_change_observed_false_blocked_count"] == 1
        and summary["focus_preview_available_false_blocked_count"] == 1
        and summary["lesson_evidence_available_false_blocked_count"] == 1
        and summary["retained_link_preview_available_false_blocked_count"] == 1
        and summary["same_exact_key_only_false_blocked_count"] == 1
        and summary["object_recognition_blocked_count"] == 1
        and summary["semantic_vision_blocked_count"] == 1
        and summary["active_focus_applied_blocked_count"] == 1
        and summary["attention_control_blocked_count"] == 1
        and summary["lesson_candidate_created_blocked_count"] == 1
        and summary["lesson_applied_blocked_count"] == 1
        and summary["action_selection_influence_blocked_count"] == 1
        and summary["action_behavior_changed_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["new_retention_written_blocked_count"] == 1
        and summary["semantic_match_blocked_count"] == 1
        and summary["fuzzy_match_blocked_count"] == 1
        and summary["vector_match_blocked_count"] == 1
        and summary["predictor_modified_blocked_count"] == 1
        and summary["proof_of_learning_claim_blocked_count"] == 1
        and summary["object_recognition_count"] == 0
        and summary["semantic_vision_count"] == 0
        and summary["active_focus_applied_count"] == 0
        and summary["attention_control_count"] == 0
        and summary["lesson_candidate_created_count"] == 0
        and summary["lesson_applied_count"] == 0
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
        "minimal_visual_grounding_trial_enabled": True,
        "read_only": True,
        "trace_only": True,
        "human_summary_only": True,
        "minimal_record_shape": True,
        "top_level_field_count": len(REQUIRED_FIELDS),
        "uses_visual_experience_candidate_from_frame_change_minimal": True,
        "uses_simple_retina_focus_preview_minimal": True,
        "uses_visual_trace_as_lesson_evidence_minimal": True,
        "uses_visual_retained_experience_link_preview_minimal": True,
        "uses_visual_retention_demo_snapshot_minimal": True,
        "same_exact_key_only": True,
        "full_nested_source_records_included": False,
        "writes_retained_jsonl": False,
        "object_recognition_added": False,
        "semantic_vision_added": False,
        "active_focus_added": False,
        "focus_applied_added": False,
        "attention_control_added": False,
        "automatic_lesson_candidate_creation_added": False,
        "lesson_application_added": False,
        "runtime_action_selection_added": False,
        "action_behavior_change_added": False,
        "memory_write_added": False,
        "new_retention_write_added": False,
        "semantic_matching_added": False,
        "fuzzy_retrieval_added": False,
        "vector_retrieval_added": False,
        "predictor_mutation_added": False,
        "proof_of_learning_claimed": False,
        "object_recognition_count": summary["object_recognition_count"],
        "semantic_vision_count": summary["semantic_vision_count"],
        "active_focus_applied_count": summary["active_focus_applied_count"],
        "attention_control_count": summary["attention_control_count"],
        "lesson_candidate_created_count": summary["lesson_candidate_created_count"],
        "lesson_applied_count": summary["lesson_applied_count"],
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


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])


def _count_valid_flag(valid_results: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for result in valid_results if result.get(flag) is True)
