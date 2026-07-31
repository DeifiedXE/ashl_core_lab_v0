"""Package 129 adapter into the canonical Package 112 scorer."""

from __future__ import annotations

from typing import Any

from ashl_core_v1.host_body import (
    host_body_readback_internal_action_influence as package_112,
)
from ashl_core_v1.host_body.host_body_working_readback_integration import (
    build_demo_trace_spine_raw_evidence_boundary,
)
from ashl_core_v1.runtime.bounded_embodied_session_runtime import (
    _readback_signal_theme_for_item,
    _working_readback_visibility_from_loaded_item,
)


ACTIVE_PERCEPTION_EVIDENCE_THEME = "active_perception_sequence_observed"
ACTIVE_PERCEPTION_SIGNAL_THEME = "prior_active_perception_sequence"
SCORER_ID = "host_body_readback_internal_action_influence"


def score_extension_candidate_with_working_readback(
    *,
    extension_candidate: Any,
    working_readback_items: tuple[dict[str, Any], ...]
    | list[dict[str, Any]],
    expected_evidence_snapshot_id: str,
    expected_evidence_identity_sha256: str,
    base_candidate_priority: int = 5,
) -> dict[str, Any]:
    """Score one real Package 125 candidate without granting policy authority."""

    candidate = (
        extension_candidate.to_dict()
        if hasattr(extension_candidate, "to_dict")
        else dict(extension_candidate)
    )
    candidate_id = str(
        candidate.get("extension_candidate_id")
        or candidate.get("internal_action_candidate_id")
        or ""
    )
    if not candidate_id:
        raise ValueError("Package 129 scoring requires an actual candidate id")
    score_candidate = {
        "internal_action_candidate_id": candidate_id,
        "candidate_action_kind": "extend_observation_window",
        "candidate_priority": int(base_candidate_priority),
        "source_trace_refs": tuple(candidate.get("source_trace_refs") or ()),
    }
    matched = tuple(
        dict(item)
        for item in working_readback_items
        if _matches_approved_cycle_one_evidence(
            item,
            expected_evidence_snapshot_id=expected_evidence_snapshot_id,
            expected_evidence_identity_sha256=(
                expected_evidence_identity_sha256
            ),
        )
    )
    if not matched:
        demo = package_112.build_demo_no_matching_readback_signal_no_change()
        signal = tuple(demo["readback_internal_action_signals"])[0]
        score = (
            package_112.build_host_body_internal_action_candidate_readback_score(
                readback_signal=signal,
                internal_action_candidate=score_candidate,
            )
        )
        return {
            "matched": False,
            "matched_readback_items": tuple(),
            "influence_plan": None,
            "signal": signal,
            "score": score,
            "contribution": int(score.readback_delta),
            "policy_authority_created": False,
        }

    item = matched[0]
    source_trace_refs = tuple(item.get("source_trace_refs") or ())
    if not source_trace_refs:
        raise ValueError("approved working readback is missing source trace refs")
    boundary_payload = build_demo_trace_spine_raw_evidence_boundary()
    plan = package_112.build_host_body_readback_internal_action_influence_plan(
        working_readback_integration_audit={
            "working_readback_integration_audit_id": (
                "package_129_approved_working_readback_integration"
            ),
            "source_trace_refs": source_trace_refs,
        },
        internal_action_choice_audit={
            "internal_action_choice_audit_id": (
                f"package_129_extension_candidate_ready:{candidate_id}"
            ),
            "source_trace_refs": tuple(
                candidate.get("source_trace_refs") or source_trace_refs
            ),
        },
        trace_spine_boundary=boundary_payload[
            "trace_spine_raw_evidence_boundary"
        ],
    )
    _ensure_valid(
        package_112.validate_host_body_readback_internal_action_influence_plan(
            plan
        )
    )
    theme = _readback_signal_theme_for_item(item)
    if theme != ACTIVE_PERCEPTION_SIGNAL_THEME:
        raise ValueError("approved readback did not normalize to active perception")
    visibility = _working_readback_visibility_from_loaded_item(item, theme)
    signal = package_112.build_host_body_readback_internal_action_signal(
        influence_plan=plan,
        working_readback_visibility=visibility,
        signal_theme=theme,
    )
    _ensure_valid(
        package_112.validate_host_body_readback_internal_action_signal(signal)
    )
    score = package_112.build_host_body_internal_action_candidate_readback_score(
        readback_signal=signal,
        internal_action_candidate=score_candidate,
    )
    _ensure_valid(
        package_112.validate_host_body_internal_action_candidate_readback_score(
            score
        )
    )
    return {
        "matched": True,
        "matched_readback_items": matched,
        "influence_plan": plan,
        "visibility": visibility,
        "signal": signal,
        "score": score,
        "contribution": int(score.readback_delta),
        "policy_authority_created": False,
    }


def validate_readback_loaded_before_candidate(
    *,
    readback_loaded_monotonic_ns: int,
    candidate_evaluated_monotonic_ns: int,
) -> None:
    if int(readback_loaded_monotonic_ns) > int(
        candidate_evaluated_monotonic_ns
    ):
        raise ValueError("working readback was loaded after candidate evaluation")


def reject_stimulus_matching_provenance(provenance: dict[str, Any]) -> None:
    forbidden = {
        "experiment_id",
        "stimulus_config_hash",
        "stimulus_schedule",
        "expected_focus_grid",
        "expected_event_start_time",
        "expected_stop_time",
        "window_title",
        "process_id",
    }.intersection(str(key) for key in provenance)
    if forbidden:
        raise ValueError(
            "readback matching provenance contains forbidden fixture keys: "
            + ",".join(sorted(forbidden))
        )


def _matches_approved_cycle_one_evidence(
    item: dict[str, Any],
    *,
    expected_evidence_snapshot_id: str,
    expected_evidence_identity_sha256: str,
) -> bool:
    return bool(
        item.get("active_for_future_sessions", True)
        and item.get("evidence_theme") == ACTIVE_PERCEPTION_EVIDENCE_THEME
        and item.get("source_evidence_snapshot_id")
        == expected_evidence_snapshot_id
        and item.get("evidence_identity_sha256")
        == expected_evidence_identity_sha256
        and item.get("working_readback_commit_id")
        and item.get("source_trace_refs")
    )


def _ensure_valid(validation: dict[str, object]) -> None:
    if validation.get("valid"):
        return
    raise ValueError(f"canonical Package 112 validation failed: {validation}")
