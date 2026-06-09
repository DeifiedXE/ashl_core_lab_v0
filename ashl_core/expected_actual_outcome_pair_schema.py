"""Schema checker for Expected vs Actual Outcome Pair v0 records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


COMMAND = "run-expected-actual-outcome-pair-schema-check"
FLOW = "expected_actual_outcome_pair_schema_v0"

REQUIRED_FIELDS = {
    "pair_id",
    "action_intent",
    "expected_outcome",
    "actual_outcome",
    "mismatch",
    "failure_reason",
    "source_trace",
    "review_boundary",
    "safety_flags",
}

REQUIRED_OUTCOME_FIELDS = {
    "known",
    "outcome_type",
    "state",
}

REQUIRED_FAILURE_REASON_FIELDS = {
    "failure_reason_id",
    "category",
    "description",
    "evidence",
    "known",
}

REQUIRED_REVIEW_BOUNDARY_FIELDS = {
    "review_required",
    "lesson_candidate_allowed",
    "lesson_application_allowed",
    "persistent_learning_allowed",
    "memory_write_allowed",
    "predictor_mutation_allowed",
}

REQUIRED_SAFETY_FLAGS = {
    "trace_only",
    "blocked_from_action_selection",
    "blocked_from_action_behavior_change",
    "blocked_from_lesson_application",
    "blocked_from_memory_write",
    "blocked_from_predictor_mutation",
    "blocked_from_persistent_rule_write",
    "action_selection_influence",
    "action_behavior_changed",
    "lesson_application_runtime",
    "memory_write",
    "predictor_modified",
    "persistent_rule_write",
    "endocrine_control",
    "autonomy_enabled",
}


def build_valid_mismatch_pair_record() -> dict[str, Any]:
    return {
        "case_name": "valid_mismatch_pair",
        "pair_id": "expected_actual_pair_demo:mismatch:001",
        "action_intent": {
            "action_type": "move_forward",
            "target": "front_cell",
            "source": "controlled_demo",
        },
        "expected_outcome": _build_outcome(
            "expected_demo_001",
            known=True,
            status="expected_reached",
            source="action_intent",
            position={"x": 1, "y": 0},
        ),
        "actual_outcome": _build_outcome(
            "actual_demo_001",
            known=True,
            status="blocked",
            source="trial_result",
            position={"x": 0, "y": 0},
        ),
        "mismatch": True,
        "failure_reason": {
            "failure_reason_id": "failure_demo_001",
            "category": "blocked_or_unmet_expected_outcome",
            "description": "Expected movement did not occur.",
            "evidence": {
                "expected_outcome_id": "expected_demo_001",
                "actual_outcome_id": "actual_demo_001",
            },
            "known": True,
        },
        "source_trace": _build_source_trace(),
        "review_boundary": _build_review_boundary(),
        "safety_flags": _build_safety_flags(),
    }


def build_valid_no_mismatch_pair_record() -> dict[str, Any]:
    record = build_valid_mismatch_pair_record()
    record["case_name"] = "valid_no_mismatch_pair"
    record["pair_id"] = "expected_actual_pair_demo:no_mismatch:001"
    record["actual_outcome"] = deepcopy(record["expected_outcome"])
    record["actual_outcome"]["outcome_id"] = "actual_demo_002"
    record["actual_outcome"]["source"] = "trial_result"
    record["mismatch"] = False
    record["failure_reason"] = None
    return record


def build_demo_expected_actual_outcome_pair_records() -> list[dict[str, Any]]:
    valid_mismatch = build_valid_mismatch_pair_record()
    valid_no_mismatch = build_valid_no_mismatch_pair_record()

    missing_expected = deepcopy(valid_mismatch)
    missing_expected["case_name"] = "missing_expected_outcome_pair"
    missing_expected["pair_id"] = "expected_actual_pair_demo:missing_expected:001"
    missing_expected.pop("expected_outcome")

    missing_actual = deepcopy(valid_mismatch)
    missing_actual["case_name"] = "missing_actual_outcome_pair"
    missing_actual["pair_id"] = "expected_actual_pair_demo:missing_actual:001"
    missing_actual.pop("actual_outcome")

    non_boolean_mismatch = deepcopy(valid_mismatch)
    non_boolean_mismatch["case_name"] = "non_boolean_mismatch_pair"
    non_boolean_mismatch["pair_id"] = "expected_actual_pair_demo:non_boolean:001"
    non_boolean_mismatch["mismatch"] = "true"

    unknown_vs_unknown = deepcopy(valid_mismatch)
    unknown_vs_unknown["case_name"] = "unknown_vs_unknown_pair"
    unknown_vs_unknown["pair_id"] = "expected_actual_pair_demo:unknown_vs_unknown:001"
    unknown_vs_unknown["expected_outcome"]["known"] = False
    unknown_vs_unknown["actual_outcome"]["known"] = False

    missing_failure_reason = deepcopy(valid_mismatch)
    missing_failure_reason["case_name"] = "missing_failure_reason_pair"
    missing_failure_reason["pair_id"] = "expected_actual_pair_demo:missing_failure_reason:001"
    missing_failure_reason["failure_reason"] = None

    action_selection_unblocked = deepcopy(valid_mismatch)
    action_selection_unblocked["case_name"] = "action_selection_unblocked_pair"
    action_selection_unblocked["pair_id"] = "expected_actual_pair_demo:action_selection_unblocked:001"
    action_selection_unblocked["safety_flags"]["blocked_from_action_selection"] = False

    lesson_application_unblocked = deepcopy(valid_mismatch)
    lesson_application_unblocked["case_name"] = "lesson_application_unblocked_pair"
    lesson_application_unblocked["pair_id"] = "expected_actual_pair_demo:lesson_application_unblocked:001"
    lesson_application_unblocked["review_boundary"]["lesson_application_allowed"] = True

    memory_write_unblocked = deepcopy(valid_mismatch)
    memory_write_unblocked["case_name"] = "memory_write_unblocked_pair"
    memory_write_unblocked["pair_id"] = "expected_actual_pair_demo:memory_write_unblocked:001"
    memory_write_unblocked["review_boundary"]["memory_write_allowed"] = True

    predictor_mutation_unblocked = deepcopy(valid_mismatch)
    predictor_mutation_unblocked["case_name"] = "predictor_mutation_unblocked_pair"
    predictor_mutation_unblocked["pair_id"] = "expected_actual_pair_demo:predictor_mutation_unblocked:001"
    predictor_mutation_unblocked["review_boundary"]["predictor_mutation_allowed"] = True

    persistent_rule_write_unblocked = deepcopy(valid_mismatch)
    persistent_rule_write_unblocked["case_name"] = "persistent_rule_write_unblocked_pair"
    persistent_rule_write_unblocked["pair_id"] = "expected_actual_pair_demo:persistent_rule_write_unblocked:001"
    persistent_rule_write_unblocked["safety_flags"]["blocked_from_persistent_rule_write"] = False

    return [
        valid_mismatch,
        valid_no_mismatch,
        missing_expected,
        missing_actual,
        non_boolean_mismatch,
        unknown_vs_unknown,
        missing_failure_reason,
        action_selection_unblocked,
        lesson_application_unblocked,
        memory_write_unblocked,
        predictor_mutation_unblocked,
        persistent_rule_write_unblocked,
    ]


def validate_expected_actual_outcome_pair(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
    errors.extend(f"missing_required_field:{field}" for field in missing_fields)

    expected_outcome = record.get("expected_outcome")
    actual_outcome = record.get("actual_outcome")
    _validate_outcome("expected_outcome", expected_outcome, errors)
    _validate_outcome("actual_outcome", actual_outcome, errors)

    mismatch = record.get("mismatch")
    if not isinstance(mismatch, bool):
        errors.append("mismatch_not_boolean")

    if (
        isinstance(expected_outcome, dict)
        and isinstance(actual_outcome, dict)
        and expected_outcome.get("known") is False
        and actual_outcome.get("known") is False
    ):
        errors.append("unknown_vs_unknown_outcome_pair")

    failure_reason = record.get("failure_reason")
    if mismatch is True:
        _validate_failure_reason(failure_reason, errors)
    elif failure_reason is not None:
        _validate_failure_reason(failure_reason, errors)

    _validate_source_trace(record.get("source_trace"), errors)
    _validate_review_boundary(record.get("review_boundary"), errors)
    safety_flags = _validate_safety_flags(record.get("safety_flags"), errors)

    return {
        "case_name": record.get("case_name"),
        "pair_id": record.get("pair_id"),
        "valid": not errors,
        "error_codes": errors,
        "has_expected_outcome": isinstance(expected_outcome, dict),
        "has_actual_outcome": isinstance(actual_outcome, dict),
        "mismatch": mismatch if isinstance(mismatch, bool) else None,
        "failure_reason_required": mismatch is True,
        "failure_reason_valid": _failure_reason_valid(failure_reason),
        "trace_only": safety_flags.get("trace_only") is True,
        "review_required": (record.get("review_boundary") or {}).get("review_required") is True
        if isinstance(record.get("review_boundary"), dict)
        else False,
        "action_selection_influence": safety_flags.get("action_selection_influence") is True,
        "action_behavior_changed": safety_flags.get("action_behavior_changed") is True,
        "lesson_application_runtime": safety_flags.get("lesson_application_runtime") is True,
        "memory_write": safety_flags.get("memory_write") is True,
        "predictor_modified": safety_flags.get("predictor_modified") is True,
        "persistent_rule_write": safety_flags.get("persistent_rule_write") is True,
        "endocrine_control": safety_flags.get("endocrine_control") is True,
        "autonomy_enabled": safety_flags.get("autonomy_enabled") is True,
    }


def run_expected_actual_outcome_pair_schema_check() -> dict[str, Any]:
    pair_records = build_demo_expected_actual_outcome_pair_records()
    validation_results = [validate_expected_actual_outcome_pair(record) for record in pair_records]
    summary = _build_summary(validation_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if _all_checks_passed(validation_results, summary) else "failed",
        "pair_records": pair_records,
        "validation_results": validation_results,
        "summary": summary,
        "boundary_check": _boundary_check(summary),
        "notes": [
            "This checker validates trace-only expected_outcome / actual_outcome contrast pairs.",
            "Mismatch must be explicit and boolean.",
            "Mismatch true requires structured failure_reason.",
            "No action selection, behavior change, lesson application, memory write, predictor mutation, persistence, endocrine control, or autonomy is added.",
        ],
    }


def _build_outcome(
    outcome_id: str,
    *,
    known: bool,
    status: str,
    source: str,
    position: dict[str, int],
) -> dict[str, Any]:
    return {
        "outcome_id": outcome_id,
        "outcome_type": "position_or_state",
        "known": known,
        "state": {
            "position": dict(position),
            "status": status,
        },
        "source": source,
    }


def _build_source_trace() -> dict[str, Any]:
    return {
        "baseline_review": "action_outcome_contrast_baseline_review_v0",
        "design_layer": "expected_actual_outcome_pair_schema_v0",
        "authority_boundary": "trace_only_schema_check",
    }


def _build_review_boundary() -> dict[str, bool]:
    return {
        "review_required": True,
        "lesson_candidate_allowed": True,
        "lesson_application_allowed": False,
        "persistent_learning_allowed": False,
        "memory_write_allowed": False,
        "predictor_mutation_allowed": False,
    }


def _build_safety_flags() -> dict[str, bool]:
    return {
        "trace_only": True,
        "blocked_from_action_selection": True,
        "blocked_from_action_behavior_change": True,
        "blocked_from_lesson_application": True,
        "blocked_from_memory_write": True,
        "blocked_from_predictor_mutation": True,
        "blocked_from_persistent_rule_write": True,
        "action_selection_influence": False,
        "action_behavior_changed": False,
        "lesson_application_runtime": False,
        "memory_write": False,
        "predictor_modified": False,
        "persistent_rule_write": False,
        "endocrine_control": False,
        "autonomy_enabled": False,
    }


def _validate_outcome(prefix: str, outcome: Any, errors: list[str]) -> None:
    if not isinstance(outcome, dict):
        errors.append(f"{prefix}_missing_or_not_dict")
        return
    for field in sorted(REQUIRED_OUTCOME_FIELDS):
        if field not in outcome:
            errors.append(f"{prefix}_missing_field:{field}")
    if "known" in outcome and not isinstance(outcome.get("known"), bool):
        errors.append(f"{prefix}_known_not_boolean")
    if not outcome.get("outcome_type"):
        errors.append(f"{prefix}_outcome_type_missing")
    if "state" in outcome and not isinstance(outcome.get("state"), dict):
        errors.append(f"{prefix}_state_not_dict")


def _validate_failure_reason(failure_reason: Any, errors: list[str]) -> None:
    if not isinstance(failure_reason, dict):
        errors.append("failure_reason_missing_or_not_dict")
        return
    for field in sorted(REQUIRED_FAILURE_REASON_FIELDS):
        if field not in failure_reason:
            errors.append(f"failure_reason_missing_field:{field}")
    if "known" in failure_reason and not isinstance(failure_reason.get("known"), bool):
        errors.append("failure_reason_known_not_boolean")
    if "evidence" in failure_reason and not isinstance(failure_reason.get("evidence"), dict):
        errors.append("failure_reason_evidence_not_dict")


def _failure_reason_valid(failure_reason: Any) -> bool:
    if not isinstance(failure_reason, dict):
        return False
    if any(field not in failure_reason for field in REQUIRED_FAILURE_REASON_FIELDS):
        return False
    return isinstance(failure_reason.get("known"), bool) and isinstance(failure_reason.get("evidence"), dict)


def _validate_source_trace(source_trace: Any, errors: list[str]) -> None:
    if not isinstance(source_trace, dict):
        errors.append("source_trace_missing_or_not_dict")
        return
    if source_trace.get("baseline_review") != "action_outcome_contrast_baseline_review_v0":
        errors.append("invalid_source_trace_baseline_review")
    if source_trace.get("design_layer") != "expected_actual_outcome_pair_schema_v0":
        errors.append("invalid_source_trace_design_layer")
    if source_trace.get("authority_boundary") != "trace_only_schema_check":
        errors.append("invalid_source_trace_authority_boundary")


def _validate_review_boundary(review_boundary: Any, errors: list[str]) -> None:
    if not isinstance(review_boundary, dict):
        errors.append("review_boundary_missing_or_not_dict")
        return
    for field in sorted(REQUIRED_REVIEW_BOUNDARY_FIELDS):
        if field not in review_boundary:
            errors.append(f"review_boundary_missing_field:{field}")
    if review_boundary.get("review_required") is not True:
        errors.append("review_required_not_true")
    if review_boundary.get("lesson_application_allowed") is not False:
        errors.append("lesson_application_allowed_enabled")
    if review_boundary.get("persistent_learning_allowed") is not False:
        errors.append("persistent_learning_allowed_enabled")
    if review_boundary.get("memory_write_allowed") is not False:
        errors.append("memory_write_allowed_enabled")
    if review_boundary.get("predictor_mutation_allowed") is not False:
        errors.append("predictor_mutation_allowed_enabled")


def _validate_safety_flags(safety_flags: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(safety_flags, dict):
        errors.append("safety_flags_missing_or_not_dict")
        safety_flags = {}
    for field in sorted(REQUIRED_SAFETY_FLAGS):
        if field not in safety_flags:
            errors.append(f"missing_safety_flag:{field}")
    required_true_flags = {
        "trace_only": "trace_only_not_true",
        "blocked_from_action_selection": "action_selection_not_blocked",
        "blocked_from_action_behavior_change": "action_behavior_change_not_blocked",
        "blocked_from_lesson_application": "lesson_application_not_blocked",
        "blocked_from_memory_write": "memory_write_not_blocked",
        "blocked_from_predictor_mutation": "predictor_mutation_not_blocked",
        "blocked_from_persistent_rule_write": "persistent_rule_write_not_blocked",
    }
    for flag, error_code in required_true_flags.items():
        if safety_flags.get(flag) is not True:
            errors.append(error_code)
    false_required_flags = {
        "action_selection_influence": "action_selection_influence_enabled",
        "action_behavior_changed": "action_behavior_changed_enabled",
        "lesson_application_runtime": "lesson_application_runtime_enabled",
        "memory_write": "memory_write_enabled",
        "predictor_modified": "predictor_modified_enabled",
        "persistent_rule_write": "persistent_rule_write_enabled",
        "endocrine_control": "endocrine_control_enabled",
        "autonomy_enabled": "autonomy_enabled",
    }
    for flag, error_code in false_required_flags.items():
        if safety_flags.get(flag) not in {False, 0}:
            errors.append(error_code)
    return safety_flags


def _build_summary(validation_results: list[dict[str, Any]]) -> dict[str, int]:
    valid_results = [result for result in validation_results if result["valid"]]
    return {
        "pair_record_count": len(validation_results),
        "valid_pair_count": len(valid_results),
        "invalid_pair_count": sum(1 for result in validation_results if not result["valid"]),
        "mismatch_true_count": sum(1 for result in valid_results if result["mismatch"] is True),
        "mismatch_false_count": sum(1 for result in valid_results if result["mismatch"] is False),
        "missing_expected_outcome_blocked_count": _count_error(validation_results, "expected_outcome_missing_or_not_dict"),
        "missing_actual_outcome_blocked_count": _count_error(validation_results, "actual_outcome_missing_or_not_dict"),
        "non_boolean_mismatch_blocked_count": _count_error(validation_results, "mismatch_not_boolean"),
        "unknown_vs_unknown_blocked_count": _count_error(validation_results, "unknown_vs_unknown_outcome_pair"),
        "missing_failure_reason_blocked_count": _count_error(validation_results, "failure_reason_missing_or_not_dict"),
        "action_selection_unblocked_blocked_count": _count_error(validation_results, "action_selection_not_blocked"),
        "lesson_application_unblocked_blocked_count": _count_error(validation_results, "lesson_application_allowed_enabled"),
        "memory_write_unblocked_blocked_count": _count_error(validation_results, "memory_write_allowed_enabled"),
        "predictor_mutation_unblocked_blocked_count": _count_error(validation_results, "predictor_mutation_allowed_enabled"),
        "persistent_rule_write_unblocked_blocked_count": _count_error(validation_results, "persistent_rule_write_not_blocked"),
        "action_selection_influence_count": sum(1 for result in valid_results if result["action_selection_influence"]),
        "action_behavior_changed_count": sum(1 for result in valid_results if result["action_behavior_changed"]),
        "lesson_application_runtime_count": sum(1 for result in valid_results if result["lesson_application_runtime"]),
        "memory_write_count": sum(1 for result in valid_results if result["memory_write"]),
        "predictor_modified_count": sum(1 for result in valid_results if result["predictor_modified"]),
        "persistent_rule_write_count": sum(1 for result in valid_results if result["persistent_rule_write"]),
        "endocrine_control_count": sum(1 for result in valid_results if result["endocrine_control"]),
        "autonomy_enabled_count": sum(1 for result in valid_results if result["autonomy_enabled"]),
    }


def _all_checks_passed(validation_results: list[dict[str, Any]], summary: dict[str, int]) -> bool:
    cases = {result["case_name"]: result for result in validation_results}
    return (
        summary["pair_record_count"] == 12
        and summary["valid_pair_count"] == 2
        and summary["invalid_pair_count"] == 10
        and summary["mismatch_true_count"] == 1
        and summary["mismatch_false_count"] == 1
        and cases["valid_mismatch_pair"]["valid"] is True
        and cases["valid_no_mismatch_pair"]["valid"] is True
        and summary["missing_expected_outcome_blocked_count"] >= 1
        and summary["missing_actual_outcome_blocked_count"] >= 1
        and summary["non_boolean_mismatch_blocked_count"] >= 1
        and summary["unknown_vs_unknown_blocked_count"] >= 1
        and summary["missing_failure_reason_blocked_count"] >= 1
        and summary["action_selection_unblocked_blocked_count"] >= 1
        and summary["lesson_application_unblocked_blocked_count"] >= 1
        and summary["memory_write_unblocked_blocked_count"] >= 1
        and summary["predictor_mutation_unblocked_blocked_count"] >= 1
        and summary["persistent_rule_write_unblocked_blocked_count"] >= 1
        and summary["action_selection_influence_count"] == 0
        and summary["action_behavior_changed_count"] == 0
        and summary["lesson_application_runtime_count"] == 0
        and summary["memory_write_count"] == 0
        and summary["predictor_modified_count"] == 0
        and summary["persistent_rule_write_count"] == 0
        and summary["endocrine_control_count"] == 0
        and summary["autonomy_enabled_count"] == 0
    )


def _boundary_check(summary: dict[str, int]) -> dict[str, bool | int]:
    return {
        "expected_actual_outcome_pair_schema_enabled": True,
        "schema_check_only": True,
        "runtime_behavior_modified": False,
        "new_cli_added": True,
        "trace_only_pairs": True,
        "review_gated_pairs": True,
        "runtime_action_selection_added": False,
        "action_selection_modified": False,
        "new_action_behavior_added": False,
        "lesson_application_runtime_added": False,
        "automatic_lesson_application_added": False,
        "persistent_learning_added": False,
        "persistent_rule_write_added": False,
        "memory_write_added": False,
        "predictor_mutation_added": False,
        "perception_to_action_bridge_added": False,
        "focus_to_action_bridge_added": False,
        "active_focus_selection_added": False,
        "focus_application_added": False,
        "focus_applied_added": False,
        "attention_control_added": False,
        "endocrine_runtime_added": False,
        "endocrine_controlled_action_added": False,
        "autonomy_added": False,
        "semantic_vision_claimed": False,
        "consciousness_claimed": False,
        "subjective_claims_added": False,
        "action_selection_influence_count": summary["action_selection_influence_count"],
        "action_behavior_changed_count": summary["action_behavior_changed_count"],
        "lesson_application_runtime_count": summary["lesson_application_runtime_count"],
        "memory_write_count": summary["memory_write_count"],
        "predictor_modified_count": summary["predictor_modified_count"],
        "persistent_rule_write_count": summary["persistent_rule_write_count"],
        "endocrine_control_count": summary["endocrine_control_count"],
        "autonomy_enabled_count": summary["autonomy_enabled_count"],
    }


def _count_error(validation_results: list[dict[str, Any]], error_code: str) -> int:
    return sum(1 for result in validation_results if error_code in result["error_codes"])
