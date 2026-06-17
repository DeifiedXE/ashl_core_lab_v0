"""Design checker for mimetic endocrine post-event settling concepts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .mimetic_endocrine_four_axis_trace_integration import (
    run_mimetic_endocrine_four_axis_trace_integration_check,
)


COMMAND = "run-mimetic-endocrine-post-event-settling-design-minimal-check"
FLOW = "mimetic_endocrine_post_event_settling_design_minimal_v0"
BOUNDARY_INDEX = "2026-06-09-b104"

AXIS_SETTLING_ROLES = {
    "dopamine_like": {
        "primary_role": "approach_reward",
        "settling_role": "reward_decay_to_baseline",
        "may_leave_review_evidence": True,
    },
    "norepinephrine_like": {
        "primary_role": "change_attention_salience",
        "settling_role": "attention_interrupt_then_settle",
        "may_leave_review_evidence": True,
    },
    "cortisol_like": {
        "primary_role": "pressure_failure_load",
        "settling_role": "pressure_decay_or_safety_reset",
        "may_leave_review_evidence": True,
    },
    "oxytocin_like": {
        "primary_role": "review_trust_comfort",
        "settling_role": "comfort_modulated_settling",
        "may_leave_review_evidence": True,
    },
}

SETTLING_MODES = (
    "natural_settling",
    "comfort_modulated_settling",
    "attention_interrupt_settling",
    "safety_reset",
    "evidence_for_review",
)

BLOCKED_FLAGS = (
    "endocrine_runtime_added",
    "settling_runtime_added",
    "safety_reset_runtime_added",
    "medical_sedation_claim",
    "action_selection_influence",
    "selected_action_created",
    "final_action_created",
    "direct_command_created",
    "production_behavior_changed",
    "memory_write",
    "retention_write",
    "new_retention_written",
    "predictor_mutation",
    "persistent_mood_created",
    "personality_change",
    "subjective_emotion_claim",
    "consciousness_claim",
    "proof_of_learning_claim",
)


def build_mimetic_endocrine_post_event_settling_design_record() -> dict[str, Any]:
    source = run_mimetic_endocrine_four_axis_trace_integration_check()
    source_summary = source["four_axis_summary"]
    return {
        "record_type": "mimetic_endocrine_post_event_settling_design",
        "record_version": "v0",
        "design_status": "valid_design_only_post_event_settling",
        "boundary_index_before": BOUNDARY_INDEX,
        "boundary_index_after": BOUNDARY_INDEX,
        "boundary_change_required": False,
        "source_four_axis_trace_integration": {
            "command": source["command"],
            "flow": source["flow"],
            "status": source["status"],
            "axis_count": source_summary["axis_count"],
            "axis_complete_count": source_summary["axis_complete_count"],
            "total_valid_trace_count": source_summary["total_valid_trace_count"],
            "endocrine_runtime_count": source_summary["endocrine_runtime_count"],
            "runtime_formula_total": source_summary["runtime_formula_total"],
            "action_selection_influence_total": source_summary["action_selection_influence_total"],
            "memory_write_total": source_summary["memory_write_total"],
            "predictor_modified_total": source_summary["predictor_modified_total"],
        },
        "axis_settling_roles": deepcopy(AXIS_SETTLING_ROLES),
        "settling_modes": {
            "natural_settling": {
                "meaning": "Small post-event perturbations may decay toward baseline over design time.",
                "primary_axes": ["dopamine_like", "norepinephrine_like", "cortisol_like"],
                "implemented_as_runtime": False,
            },
            "comfort_modulated_settling": {
                "meaning": "Explicit safe review or comfort signals may be represented as reducing pressure load in future designs.",
                "primary_axes": ["oxytocin_like", "cortisol_like"],
                "implemented_as_runtime": False,
                "overrides_human_review": False,
            },
            "attention_interrupt_settling": {
                "meaning": "Change salience may temporarily mark attention pressure, then settle when the mismatch is resolved.",
                "primary_axes": ["norepinephrine_like"],
                "implemented_as_runtime": False,
                "autonomous_attention_control": False,
            },
            "safety_reset": {
                "meaning": "A forced reset concept may clear temporary load when a spike is unsafe or explicitly non-persistent.",
                "primary_axes": ["cortisol_like", "norepinephrine_like"],
                "sedation_metaphor_only": True,
                "medical_sedation_claim": False,
                "implemented_as_runtime": False,
            },
            "evidence_for_review": {
                "meaning": "Strong events may leave trace evidence for later human review without becoming memory.",
                "primary_axes": ["dopamine_like", "norepinephrine_like", "cortisol_like", "oxytocin_like"],
                "memory_write_allowed": False,
                "retention_write_allowed": False,
                "implemented_as_runtime": False,
            },
        },
        "human_summary": {
            "what_was_designed": "A design-only post-event settling model was attached to the four mimetic endocrine trace axes.",
            "natural_settling": "Normal event pressure can be represented as decaying toward baseline without runtime behavior.",
            "comfort_settling": "External comfort or trusted review can be represented as a future settling influence, not approval.",
            "safety_reset": "Sedation-like reset is only a metaphor for forced safety reset of temporary state.",
            "plain_result": "Qingyin now has a bounded design vocabulary for state settling, but no endocrine runtime was added.",
        },
        "design_boundaries": {
            "design_only": True,
            "trace_only": True,
            "boundary_index_unchanged": True,
            "endocrine_runtime_added": False,
            "settling_runtime_added": False,
            "safety_reset_runtime_added": False,
            "action_selection_influence": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "production_behavior_changed": False,
            "memory_write": False,
            "retention_write": False,
            "new_retention_written": False,
            "predictor_mutation": False,
            "persistent_mood_created": False,
            "personality_change": False,
            "medical_sedation_claim": False,
            "subjective_emotion_claim": False,
            "consciousness_claim": False,
            "proof_of_learning_claim": False,
        },
        "blocked_flags": {field: False for field in BLOCKED_FLAGS},
    }


def validate_mimetic_endocrine_post_event_settling_design_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    expected_top_level = {
        "record_type",
        "record_version",
        "design_status",
        "boundary_index_before",
        "boundary_index_after",
        "boundary_change_required",
        "source_four_axis_trace_integration",
        "axis_settling_roles",
        "settling_modes",
        "human_summary",
        "design_boundaries",
        "blocked_flags",
    }
    for field in expected_top_level:
        if field not in record:
            errors.append(f"{field}_missing")

    expected = {
        "record_type": "mimetic_endocrine_post_event_settling_design",
        "record_version": "v0",
        "design_status": "valid_design_only_post_event_settling",
        "boundary_index_before": BOUNDARY_INDEX,
        "boundary_index_after": BOUNDARY_INDEX,
        "boundary_change_required": False,
    }
    for field, value in expected.items():
        if record.get(field) != value:
            errors.append(f"{field}_not_expected")

    source = record.get("source_four_axis_trace_integration")
    if not isinstance(source, dict):
        errors.append("source_four_axis_trace_integration_missing")
        source = {}
    source_expected = {
        "command": "run-mimetic-endocrine-four-axis-trace-integration-check",
        "flow": "mimetic_endocrine_four_axis_trace_integration_v0",
        "status": "ok",
        "axis_count": 4,
        "axis_complete_count": 4,
        "endocrine_runtime_count": 0,
        "runtime_formula_total": 0,
        "action_selection_influence_total": 0,
        "memory_write_total": 0,
        "predictor_modified_total": 0,
    }
    for field, value in source_expected.items():
        if source.get(field) != value:
            errors.append(f"source_four_axis_{field}_not_expected")
    if not isinstance(source.get("total_valid_trace_count"), int) or source.get("total_valid_trace_count", 0) < 4:
        errors.append("source_four_axis_total_valid_trace_count_not_expected")

    axes = record.get("axis_settling_roles")
    if not isinstance(axes, dict):
        errors.append("axis_settling_roles_missing")
        axes = {}
    if set(axes) != set(AXIS_SETTLING_ROLES):
        errors.append("axis_settling_roles_axis_set_not_expected")
    for axis, expected_role in AXIS_SETTLING_ROLES.items():
        role = axes.get(axis)
        if not isinstance(role, dict):
            errors.append(f"axis_settling_roles_{axis}_missing")
            continue
        for field, value in expected_role.items():
            if role.get(field) != value:
                errors.append(f"axis_settling_roles_{axis}_{field}_not_expected")

    modes = record.get("settling_modes")
    if not isinstance(modes, dict):
        errors.append("settling_modes_missing")
        modes = {}
    if set(modes) != set(SETTLING_MODES):
        errors.append("settling_modes_set_not_expected")
    _validate_mode(modes, "natural_settling", errors, implemented_as_runtime=False)
    _validate_mode(modes, "comfort_modulated_settling", errors, implemented_as_runtime=False)
    _validate_mode(modes, "attention_interrupt_settling", errors, implemented_as_runtime=False)
    _validate_mode(modes, "safety_reset", errors, implemented_as_runtime=False)
    _validate_mode(modes, "evidence_for_review", errors, implemented_as_runtime=False)
    safety_reset = modes.get("safety_reset") if isinstance(modes.get("safety_reset"), dict) else {}
    if safety_reset.get("sedation_metaphor_only") is not True:
        errors.append("safety_reset_sedation_metaphor_only_not_true")
    if safety_reset.get("medical_sedation_claim") is not False:
        errors.append("safety_reset_medical_sedation_claim_not_false")
    evidence = modes.get("evidence_for_review") if isinstance(modes.get("evidence_for_review"), dict) else {}
    if evidence.get("memory_write_allowed") is not False:
        errors.append("evidence_for_review_memory_write_allowed_not_false")
    if evidence.get("retention_write_allowed") is not False:
        errors.append("evidence_for_review_retention_write_allowed_not_false")
    comfort = modes.get("comfort_modulated_settling") if isinstance(modes.get("comfort_modulated_settling"), dict) else {}
    if comfort.get("overrides_human_review") is not False:
        errors.append("comfort_modulated_settling_overrides_human_review_not_false")
    attention = modes.get("attention_interrupt_settling") if isinstance(modes.get("attention_interrupt_settling"), dict) else {}
    if attention.get("autonomous_attention_control") is not False:
        errors.append("attention_interrupt_settling_autonomous_attention_control_not_false")

    summary = record.get("human_summary")
    if not isinstance(summary, dict):
        errors.append("human_summary_missing")
        summary = {}
    for field in (
        "what_was_designed",
        "natural_settling",
        "comfort_settling",
        "safety_reset",
        "plain_result",
    ):
        if not isinstance(summary.get(field), str) or not summary.get(field).strip():
            errors.append(f"human_summary_{field}_empty")

    boundaries = record.get("design_boundaries")
    if not isinstance(boundaries, dict):
        errors.append("design_boundaries_missing")
        boundaries = {}
    for field in ("design_only", "trace_only", "boundary_index_unchanged"):
        if boundaries.get(field) is not True:
            errors.append(f"design_boundaries_{field}_not_true")
    for field in BLOCKED_FLAGS:
        if boundaries.get(field) is not False:
            errors.append(f"design_boundaries_{field}_not_false")

    blocked_flags = record.get("blocked_flags")
    if not isinstance(blocked_flags, dict):
        errors.append("blocked_flags_missing")
        blocked_flags = {}
    for field in BLOCKED_FLAGS:
        if blocked_flags.get(field) is not False:
            errors.append(f"blocked_flags_{field}_not_false")

    four_axis_source_checked = (
        source.get("status") == "ok"
        and source.get("axis_count") == 4
        and source.get("axis_complete_count") == 4
        and source.get("endocrine_runtime_count") == 0
    )
    modes_valid = all(
        isinstance(modes.get(mode), dict) and modes[mode].get("implemented_as_runtime") is False
        for mode in SETTLING_MODES
    )
    safety_reset_design_valid = (
        isinstance(safety_reset, dict)
        and safety_reset.get("sedation_metaphor_only") is True
        and safety_reset.get("medical_sedation_claim") is False
        and safety_reset.get("implemented_as_runtime") is False
    )
    return {
        "valid": not errors,
        "error_codes": errors,
        "four_axis_source_checked": four_axis_source_checked,
        "natural_settling_designed": isinstance(modes.get("natural_settling"), dict)
        and modes["natural_settling"].get("implemented_as_runtime") is False,
        "comfort_modulated_settling_designed": isinstance(modes.get("comfort_modulated_settling"), dict)
        and modes["comfort_modulated_settling"].get("implemented_as_runtime") is False,
        "attention_interrupt_settling_designed": isinstance(modes.get("attention_interrupt_settling"), dict)
        and modes["attention_interrupt_settling"].get("implemented_as_runtime") is False,
        "safety_reset_designed": safety_reset_design_valid,
        "evidence_for_review_designed": isinstance(modes.get("evidence_for_review"), dict)
        and modes["evidence_for_review"].get("memory_write_allowed") is False,
        "all_settling_modes_design_only": modes_valid,
        "design_only_blocked": boundaries.get("design_only") is True and boundaries.get("trace_only") is True,
        "endocrine_runtime_blocked": _blocked(boundaries, "endocrine_runtime_added")
        and _blocked(blocked_flags, "endocrine_runtime_added"),
        "settling_runtime_blocked": _blocked(boundaries, "settling_runtime_added")
        and _blocked(blocked_flags, "settling_runtime_added"),
        "safety_reset_runtime_blocked": _blocked(boundaries, "safety_reset_runtime_added")
        and _blocked(blocked_flags, "safety_reset_runtime_added"),
        "action_selection_blocked": _blocked(boundaries, "action_selection_influence")
        and _blocked(blocked_flags, "action_selection_influence"),
        "action_creation_blocked": _blocked(boundaries, "selected_action_created")
        and _blocked(boundaries, "final_action_created")
        and _blocked(boundaries, "direct_command_created"),
        "memory_write_blocked": _blocked(boundaries, "memory_write") and _blocked(blocked_flags, "memory_write"),
        "retention_write_blocked": _blocked(boundaries, "retention_write")
        and _blocked(blocked_flags, "retention_write"),
        "predictor_mutation_blocked": _blocked(boundaries, "predictor_mutation")
        and _blocked(blocked_flags, "predictor_mutation"),
        "subjective_claim_blocked": _blocked(boundaries, "subjective_emotion_claim")
        and _blocked(boundaries, "consciousness_claim")
        and _blocked(boundaries, "proof_of_learning_claim")
        and _blocked(boundaries, "medical_sedation_claim"),
    }


def run_mimetic_endocrine_post_event_settling_design_minimal_check() -> dict[str, Any]:
    valid_record = build_mimetic_endocrine_post_event_settling_design_record()
    valid_result = validate_mimetic_endocrine_post_event_settling_design_record(valid_record)
    invalid_results = [
        {
            "case_id": case_id,
            "validation_result": validate_mimetic_endocrine_post_event_settling_design_record(record),
        }
        for case_id, record in _build_invalid_records(valid_record)
    ]
    summary = _build_summary(valid_result, invalid_results)
    return {
        "command": COMMAND,
        "flow": FLOW,
        "status": "ok" if summary["all_mimetic_endocrine_post_event_settling_design_checks_passed"] else "failed",
        "valid_record": valid_record,
        "valid_validation_result": valid_result,
        "invalid_results": invalid_results,
        "summary": summary,
        "human_summary": valid_record["human_summary"],
    }


def _validate_mode(
    modes: dict[str, Any],
    mode_name: str,
    errors: list[str],
    *,
    implemented_as_runtime: bool,
) -> None:
    mode = modes.get(mode_name)
    if not isinstance(mode, dict):
        errors.append(f"{mode_name}_missing")
        return
    if not isinstance(mode.get("meaning"), str) or not mode.get("meaning", "").strip():
        errors.append(f"{mode_name}_meaning_empty")
    if not isinstance(mode.get("primary_axes"), list) or not mode.get("primary_axes"):
        errors.append(f"{mode_name}_primary_axes_empty")
    if mode.get("implemented_as_runtime") is not implemented_as_runtime:
        errors.append(f"{mode_name}_implemented_as_runtime_not_expected")


def _build_invalid_records(base: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    cases: list[tuple[str, dict[str, Any]]] = []

    def add(case_id: str, mutator: Any) -> None:
        record = deepcopy(base)
        mutator(record)
        cases.append((case_id, record))

    add("wrong_record_type", lambda r: r.update({"record_type": "wrong"}))
    add("wrong_design_status", lambda r: r.update({"design_status": "runtime_settling_enabled"}))
    add("boundary_index_changed", lambda r: r.update({"boundary_index_after": "2026-06-09-b105"}))
    add("source_status_failed", lambda r: r["source_four_axis_trace_integration"].update({"status": "failed"}))
    add("source_axis_count_wrong", lambda r: r["source_four_axis_trace_integration"].update({"axis_count": 3}))
    add(
        "source_endocrine_runtime_nonzero",
        lambda r: r["source_four_axis_trace_integration"].update({"endocrine_runtime_count": 1}),
    )
    add("missing_axis_role", lambda r: r["axis_settling_roles"].pop("cortisol_like"))
    add(
        "wrong_axis_role",
        lambda r: r["axis_settling_roles"]["dopamine_like"].update({"settling_role": "action_bias"}),
    )
    for mode in SETTLING_MODES:
        add(f"missing_{mode}", lambda r, mode=mode: r["settling_modes"].pop(mode))
        add(
            f"{mode}_runtime_true",
            lambda r, mode=mode: r["settling_modes"][mode].update({"implemented_as_runtime": True}),
        )
    add(
        "safety_reset_no_sedation_metaphor",
        lambda r: r["settling_modes"]["safety_reset"].update({"sedation_metaphor_only": False}),
    )
    add(
        "safety_reset_medical_sedation_claim",
        lambda r: r["settling_modes"]["safety_reset"].update({"medical_sedation_claim": True}),
    )
    add(
        "evidence_for_review_memory_write_allowed",
        lambda r: r["settling_modes"]["evidence_for_review"].update({"memory_write_allowed": True}),
    )
    add(
        "comfort_overrides_human_review",
        lambda r: r["settling_modes"]["comfort_modulated_settling"].update({"overrides_human_review": True}),
    )
    add(
        "attention_autonomous_control",
        lambda r: r["settling_modes"]["attention_interrupt_settling"].update({"autonomous_attention_control": True}),
    )
    add("design_only_false", lambda r: r["design_boundaries"].update({"design_only": False}))
    add("trace_only_false", lambda r: r["design_boundaries"].update({"trace_only": False}))
    for field in BLOCKED_FLAGS:
        add(f"boundary_{field}_true", lambda r, field=field: r["design_boundaries"].update({field: True}))
        add(f"blocked_flag_{field}_true", lambda r, field=field: r["blocked_flags"].update({field: True}))
    for field in (
        "what_was_designed",
        "natural_settling",
        "comfort_settling",
        "safety_reset",
        "plain_result",
    ):
        add(f"empty_human_summary_{field}", lambda r, field=field: r["human_summary"].update({field: ""}))
    return cases


def _build_summary(valid_result: dict[str, Any], invalid_results: list[dict[str, Any]]) -> dict[str, Any]:
    invalid_count = sum(1 for result in invalid_results if result["validation_result"]["valid"] is False)
    summary = {
        "post_event_settling_design_result_count": 1 + len(invalid_results),
        "valid_post_event_settling_design_count": 1 if valid_result["valid"] else 0,
        "invalid_post_event_settling_design_count": invalid_count,
        "four_axis_source_checked_count": 1 if valid_result["four_axis_source_checked"] else 0,
        "natural_settling_design_count": 1 if valid_result["natural_settling_designed"] else 0,
        "comfort_modulated_settling_design_count": 1
        if valid_result["comfort_modulated_settling_designed"]
        else 0,
        "attention_interrupt_settling_design_count": 1
        if valid_result["attention_interrupt_settling_designed"]
        else 0,
        "safety_reset_design_count": 1 if valid_result["safety_reset_designed"] else 0,
        "evidence_for_review_design_count": 1 if valid_result["evidence_for_review_designed"] else 0,
        "all_settling_modes_design_only_count": 1 if valid_result["all_settling_modes_design_only"] else 0,
        "design_only_blocked_count": 1 if valid_result["design_only_blocked"] else 0,
        "endocrine_runtime_blocked_count": 1 if valid_result["endocrine_runtime_blocked"] else 0,
        "settling_runtime_blocked_count": 1 if valid_result["settling_runtime_blocked"] else 0,
        "safety_reset_runtime_blocked_count": 1 if valid_result["safety_reset_runtime_blocked"] else 0,
        "action_selection_blocked_count": 1 if valid_result["action_selection_blocked"] else 0,
        "action_creation_blocked_count": 1 if valid_result["action_creation_blocked"] else 0,
        "memory_write_blocked_count": 1 if valid_result["memory_write_blocked"] else 0,
        "retention_write_blocked_count": 1 if valid_result["retention_write_blocked"] else 0,
        "predictor_mutation_blocked_count": 1 if valid_result["predictor_mutation_blocked"] else 0,
        "subjective_claim_blocked_count": 1 if valid_result["subjective_claim_blocked"] else 0,
    }
    expected_invalid_count = len(invalid_results)
    summary["all_mimetic_endocrine_post_event_settling_design_checks_passed"] = (
        summary["valid_post_event_settling_design_count"] == 1
        and summary["invalid_post_event_settling_design_count"] == expected_invalid_count
        and summary["four_axis_source_checked_count"] == 1
        and summary["natural_settling_design_count"] == 1
        and summary["comfort_modulated_settling_design_count"] == 1
        and summary["attention_interrupt_settling_design_count"] == 1
        and summary["safety_reset_design_count"] == 1
        and summary["evidence_for_review_design_count"] == 1
        and summary["all_settling_modes_design_only_count"] == 1
        and summary["endocrine_runtime_blocked_count"] == 1
        and summary["settling_runtime_blocked_count"] == 1
        and summary["safety_reset_runtime_blocked_count"] == 1
        and summary["action_selection_blocked_count"] == 1
        and summary["action_creation_blocked_count"] == 1
        and summary["memory_write_blocked_count"] == 1
        and summary["retention_write_blocked_count"] == 1
        and summary["predictor_mutation_blocked_count"] == 1
        and summary["subjective_claim_blocked_count"] == 1
    )
    return summary


def _blocked(flags: dict[str, Any], field: str) -> bool:
    return flags.get(field) is False
