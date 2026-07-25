"""Observation-window extension candidate creation for Package 125."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.observation_window_types import (
    ALLOWED_EXTENSION_REASON_CODES,
    DEFAULT_EXTENSION_NS,
    DEFAULT_TAIL_GUARD_NS,
    OBSERVATION_EXTENSION_CANDIDATE_SCHEMA_VERSION,
    ObservationWindowExtensionAuthorization,
    ObservationWindowExtensionCandidate,
    ObservationWindowState,
    TemporalTailEvidenceRecord,
)


def reason_codes_from_tail_evidence(tail: TemporalTailEvidenceRecord) -> tuple[str, ...]:
    reasons: list[str] = []
    if tail.open_visual_region_refs:
        reasons.extend(
            [
                "visual_region_open_near_window_boundary",
                "recent_visual_onset_without_observed_offset",
            ]
        )
    if tail.open_audio_region_refs:
        reasons.extend(
            [
                "audio_region_open_near_window_boundary",
                "recent_audio_onset_without_observed_offset",
            ]
        )
    if tail.open_visual_region_refs or tail.open_audio_region_refs:
        reasons.append("insufficient_post_change_source_coverage")
    return tuple(dict.fromkeys(reasons))


def create_observation_extension_candidate(
    *,
    observation_window: ObservationWindowState,
    tail_evidence: TemporalTailEvidenceRecord,
    authorization: ObservationWindowExtensionAuthorization,
    requested_extension_ns: int = DEFAULT_EXTENSION_NS,
) -> ObservationWindowExtensionCandidate | None:
    if (
        tail_evidence.observation_window_id != observation_window.observation_window_id
        or tail_evidence.runtime_session_id != observation_window.runtime_session_id
        or tail_evidence.perception_session_id != observation_window.perception_session_id
        or tail_evidence.experiment_run_id != observation_window.experiment_run_id
        or tail_evidence.audit_group_id != observation_window.audit_group_id
        or tail_evidence.scenario_name != observation_window.scenario_name
    ):
        return None
    if (
        authorization.runtime_session_id != observation_window.runtime_session_id
        or authorization.perception_session_id != observation_window.perception_session_id
    ):
        return None
    if observation_window.window_status not in {"observing_base_window", "extension_candidate_pending"}:
        return None
    if observation_window.operator_stop_requested or observation_window.operator_pause_requested:
        return None
    if tail_evidence.evaluated_at_event_time_ns < observation_window.base_deadline_event_time_ns - DEFAULT_TAIL_GUARD_NS:
        return None
    if tail_evidence.evaluated_at_event_time_ns > observation_window.base_deadline_event_time_ns:
        return None
    if not tail_evidence.continuous_source_coverage or not tail_evidence.required_lane_delivery_complete:
        return None
    if any(
        (
            tail_evidence.capture_failure_count,
            tail_evidence.compile_failure_count,
            tail_evidence.dropped_required_record_count,
            tail_evidence.backpressure_fault_count,
        )
    ):
        return None
    if observation_window.extension_count >= authorization.maximum_extension_count:
        return None
    if observation_window.total_extension_ns + int(requested_extension_ns) > authorization.maximum_total_extension_ns:
        return None
    if observation_window.current_deadline_event_time_ns + int(requested_extension_ns) > observation_window.hard_deadline_event_time_ns:
        return None
    reasons = reason_codes_from_tail_evidence(tail_evidence)
    if not reasons:
        return None
    allowed = tuple(reason for reason in reasons if reason in set(ALLOWED_EXTENSION_REASON_CODES))
    if not allowed:
        return None
    source_lane_refs = tuple(tail_evidence.open_visual_region_refs + tail_evidence.open_audio_region_refs)
    return ObservationWindowExtensionCandidate(
        extension_candidate_id=stable_id("observation_extension_candidate"),
        schema_version=OBSERVATION_EXTENSION_CANDIDATE_SCHEMA_VERSION,
        created_at=utc_now(),
        observation_window_id=observation_window.observation_window_id,
        runtime_session_id=observation_window.runtime_session_id,
        perception_session_id=observation_window.perception_session_id,
        requested_extension_ns=int(requested_extension_ns),
        reason_codes=allowed,
        temporal_tail_evidence_id=tail_evidence.temporal_tail_evidence_id,
        source_temporal_refs=tuple(tail_evidence.recent_onset_anchor_refs),
        source_lane_refs=source_lane_refs,
        semantic_label=None,
        thought_engine_used=False,
        memory_used=False,
        endocrine_signal_used=False,
        stimulus_ground_truth_used=False,
        candidate_status="proposed",
        source_record_refs=(tail_evidence.temporal_tail_evidence_id,) + tail_evidence.source_record_refs,
        source_trace_refs=tail_evidence.source_trace_refs,
        experiment_run_id=observation_window.experiment_run_id,
        audit_group_id=observation_window.audit_group_id,
        scenario_name=observation_window.scenario_name,
        active_capture_identity_id=tail_evidence.active_capture_identity_id,
    )
