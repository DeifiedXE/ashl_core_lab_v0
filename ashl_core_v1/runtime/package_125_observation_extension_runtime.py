"""Runtime helpers for Package 125 bounded observation-window extension."""

from __future__ import annotations

import os
import threading
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.bounded_capture_deadline_controller import BoundedCaptureDeadlineController
from ashl_core_v1.perception.hard_soft_perception_primitive_compiler import (
    HardSoftPerceptionPrimitiveCompiler,
)
from ashl_core_v1.perception.perception_primitive_store import PerceptionPrimitiveStore
from ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime import (
    BoundedMultimodalPerceptionSessionRuntime,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
    ContentAddressedSensorArtifactStore,
)
from ashl_core_v1.runtime.host_sensor_types import (
    SensorCaptureError,
    build_sensor_capture_config,
    monotonic_ns,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.host_state_sensor_adapter import HostStateSensorAdapter
from ashl_core_v1.runtime.local_pulse_stimulus_runtime import LocalPulseStimulusRuntime
from ashl_core_v1.runtime.local_operator_console_store import build_default_console_store
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.runtime.observation_extension_candidate import create_observation_extension_candidate
from ashl_core_v1.runtime.observation_extension_internal_action import (
    cancel_pending_observation_extension,
    create_bounded_observation_extension_internal_action,
    execute_bounded_observation_extension,
)
from ashl_core_v1.runtime.observation_extension_policy import decide_observation_extension_policy
from ashl_core_v1.runtime.observation_window_types import (
    DEFAULT_BASE_OBSERVATION_NS,
    DEFAULT_EXTENSION_NS,
    DEFAULT_FINAL_DEADLINE_NS,
    DEFAULT_HARD_SESSION_NS,
    ACTIVE_CAPTURE_SESSION_IDENTITY_SCHEMA_VERSION,
    OPERATOR_EVENT_DELIVERY_FAILURE_SCHEMA_VERSION,
    PACKAGE_125_STIMULUS_AUDIT_MANIFEST_SCHEMA_VERSION,
    OBSERVATION_EXTENSION_COMPARISON_SCHEMA_VERSION,
    OBSERVATION_EXTENSION_OUTCOME_SCHEMA_VERSION,
    OBSERVATION_WINDOW_AUTHORIZATION_SCHEMA_VERSION,
    OBSERVATION_WINDOW_STATE_SCHEMA_VERSION,
    REQUIRED_LANES,
    ActiveCaptureSessionIdentity,
    ObservationOperatorEventDeliveryFailure,
    Package125StimulusAuditManifest,
    ObservationExtensionEffectComparison,
    ObservationWindowExtensionAuthorization,
    ObservationWindowExtensionOutcome,
    ObservationWindowState,
)
from ashl_core_v1.runtime.package_123_transport_integrity import (
    ALIGNMENT_LANE_COVERAGE_SCHEMA_VERSION,
    ALIGNMENT_WINDOW_COVERAGE_SCHEMA_VERSION,
    AlignmentLaneCoverage,
    AlignmentWindowCoverageRecord,
    HOST_STATE_INTERVAL_MS,
)
from ashl_core_v1.runtime.package_123_cycle_runtime import (
    _build_replay_manifest,
    _persist_transport_integrity,
    package_123_transport_configuration_hash,
)
from ashl_core_v1.runtime.package_123_cycle_store import Package123CycleStore
from ashl_core_v1.runtime.package_123_preflight import build_package_123_multimodal_config
from ashl_core_v1.runtime.package_124a_temporal_store import Package124ATemporalStore
from ashl_core_v1.runtime.temporal_clock_domain import (
    build_clock_domain_descriptor,
    evaluate_clock_quality,
)
from ashl_core_v1.runtime.temporal_types import (
    TEMPORAL_BUNDLE_SCHEMA_VERSION,
    GroundedTemporalPrimitiveBundle,
    TemporalEventAnchor,
    TemporalSpanPrimitive,
    temporal_identity,
)
from ashl_core_v1.runtime.package_125_observation_extension_audit import (
    audit_package_125_observation_extension,
    package_112_score_equivalence_context,
)
from ashl_core_v1.runtime.package_125_observation_extension_store import Package125ObservationExtensionStore
from ashl_core_v1.runtime.temporal_tail_evidence_adapter import build_closure_links, build_temporal_tail_evidence
from ashl_core_v1.runtime.windows_bounded_window_capture_source import (
    WindowsBoundedWindowCaptureSource,
)
from ashl_core_v1.runtime.windows_wasapi_loopback_source import WindowsWasapiLoopbackSource


PACKAGE_125_EXPERIMENT_ID = "host_internal_late_visual_audio_event_extension_v0"
PACKAGE_125_REAL_STIMULUS_SCHEDULE = (
    (0, "black", "silent"),
    (4_400, "white", "tone"),
    (5_250, "white", "silent"),
    (5_400, "black", "silent"),
)
PACKAGE_125_TAIL_CHECKPOINT_NS = (
    4_250_000_000,
    4_500_000_000,
    4_750_000_000,
)
PACKAGE_125_FINAL_COVERAGE_CHECKPOINT_NS = (
    5_500_000_000,
    6_000_000_000,
    6_450_000_000,
)
PACKAGE_125_EVENT_FAMILIES = (
    "observation_window_started",
    "temporal_tail_evidence_created",
    "observation_extension_candidate_created",
    "observation_extension_policy_allowed",
    "observation_extension_policy_blocked",
    "observation_extension_action_created",
    "observation_deadline_extended",
    "observation_extension_cancelled",
    "observation_window_operator_interrupted",
    "observation_extension_outcome_created",
    "observation_extension_audit_failed",
)


def build_observation_window_state(
    *,
    runtime_session_id: str,
    perception_session_id: str,
    observation_window_id: str | None = None,
    experiment_run_id: str | None = None,
    audit_group_id: str | None = None,
    scenario_name: str = "late_event",
    capture_mode: str = "synthetic_test",
    active_capture_identity_id: str = "active_capture_identity:unbound",
    alignment_origin_monotonic_ns: int = 0,
    clock_domain_ids: tuple[str, ...] = ("package_125_same_process_clock_domain",),
    transport_flush_record_id: str | None = None,
    status: str = "observing_base_window",
    current_deadline_ns: int = DEFAULT_BASE_OBSERVATION_NS,
    extension_count: int = 0,
    total_extension_ns: int = 0,
    operator_stop_requested: bool = False,
    operator_pause_requested: bool = False,
    source_record_refs: tuple[str, ...] = tuple(),
    source_trace_refs: tuple[str, ...] = tuple(),
) -> ObservationWindowState:
    return ObservationWindowState(
        observation_window_id=observation_window_id or stable_id("observation_window"),
        observation_window_state_id=stable_id("observation_window_state"),
        schema_version=OBSERVATION_WINDOW_STATE_SCHEMA_VERSION,
        created_at=utc_now(),
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        participating_lanes=REQUIRED_LANES,
        required_lanes=REQUIRED_LANES,
        base_start_event_time_ns=0,
        base_deadline_event_time_ns=DEFAULT_BASE_OBSERVATION_NS,
        current_deadline_event_time_ns=current_deadline_ns,
        hard_deadline_event_time_ns=DEFAULT_HARD_SESSION_NS,
        extension_count=extension_count,
        total_extension_ns=total_extension_ns,
        window_status=status,
        operator_stop_requested=operator_stop_requested,
        operator_pause_requested=operator_pause_requested,
        source_record_refs=source_record_refs,
        source_trace_refs=source_trace_refs,
        experiment_run_id=experiment_run_id or stable_id("package_125_experiment_run"),
        audit_group_id=audit_group_id or stable_id("package_125_audit_group"),
        scenario_name=scenario_name,
        capture_mode=capture_mode,
        active_capture_identity_id=active_capture_identity_id,
        alignment_origin_monotonic_ns=alignment_origin_monotonic_ns,
        clock_domain_ids=clock_domain_ids,
        transport_flush_record_id=transport_flush_record_id,
    )


def build_observation_extension_authorization(
    *,
    runtime_session_id: str,
    perception_session_id: str,
    bounded_extension_allowed: bool = True,
) -> ObservationWindowExtensionAuthorization:
    return ObservationWindowExtensionAuthorization(
        authorization_id=stable_id("observation_window_authorization"),
        schema_version=OBSERVATION_WINDOW_AUTHORIZATION_SCHEMA_VERSION,
        created_at=utc_now(),
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        authorization_source="explicit_session_configuration",
        authorized_by="local_operator",
        bounded_extension_allowed=bounded_extension_allowed,
        maximum_extension_count=1,
        maximum_single_extension_ns=DEFAULT_EXTENSION_NS,
        maximum_total_extension_ns=DEFAULT_EXTENSION_NS,
        hard_session_duration_ns=DEFAULT_HARD_SESSION_NS,
        allowed_reason_codes=(
            "visual_region_open_near_window_boundary",
            "audio_region_open_near_window_boundary",
            "recent_visual_onset_without_observed_offset",
            "recent_audio_onset_without_observed_offset",
            "insufficient_post_change_source_coverage",
        ),
        expires_at_session_end=True,
        source_trace_refs=(f"experiment:{PACKAGE_125_EXPERIMENT_ID}",),
    )


def run_synthetic_observation_extension_scenario(
    *,
    state_dir: str | Path,
    scenario: str = "late_event",
    allow_bounded_window_extension: bool = True,
    append_audit: bool = False,
    audit_group_id: str | None = None,
    experiment_run_id: str | None = None,
    strict_event_stream: bool = False,
) -> dict[str, Any]:
    path = Path(state_dir)
    store = Package125ObservationExtensionStore(path)
    runtime_session_id = stable_id("package_125_runtime_session")
    perception_session_id = stable_id("package_125_perception_session")
    observation_window_id = stable_id("observation_window")
    group_id = audit_group_id or stable_id("package_125_audit_group")
    run_id = experiment_run_id or stable_id(f"package_125_{scenario}_run")
    alignment_origin_ns = 1_000_000_000
    identity_before = _build_synthetic_capture_identity(
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        experiment_run_id=run_id,
        audit_group_id=group_id,
        scenario_name=scenario,
        alignment_origin_monotonic_ns=alignment_origin_ns,
        observed_deadline_ns=DEFAULT_BASE_OBSERVATION_NS,
        identity_stage="capture_started",
    )
    store.append_record("active_capture_session_identities", identity_before)
    observation_window = build_observation_window_state(
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        experiment_run_id=run_id,
        audit_group_id=group_id,
        scenario_name=scenario,
        active_capture_identity_id=identity_before.active_capture_identity_id,
        alignment_origin_monotonic_ns=alignment_origin_ns,
        operator_stop_requested=scenario == "operator_stop_control",
        source_record_refs=(scenario, PACKAGE_125_EXPERIMENT_ID, identity_before.active_capture_identity_id),
    )
    authorization = build_observation_extension_authorization(
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        bounded_extension_allowed=allow_bounded_window_extension,
    )
    store.append_record("observation_window_states", observation_window)
    store.append_record("observation_window_authorizations", authorization)
    _emit_event(
        path,
        store=store,
        event_kind="observation_window_started",
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        experiment_run_id=run_id,
        audit_group_id=group_id,
        scenario_name=scenario,
        refs=(observation_window.observation_window_state_id,),
        strict=strict_event_stream,
    )

    coverage = build_synthetic_package_123_coverage(scenario=scenario, experiment_run_id=run_id)
    backpressure_fault_count = 1 if scenario == "transport_fault_control" else 0
    tail_result = build_temporal_tail_evidence(
        observation_window=observation_window,
        coverage_records=coverage,
        temporal_bundle_or_context_id=f"temporal_context:{PACKAGE_125_EXPERIMENT_ID}",
        evaluated_at_event_time_ns=DEFAULT_BASE_OBSERVATION_NS - 250_000_000,
        backpressure_fault_count=backpressure_fault_count,
    )
    for region in tail_result.open_regions:
        store.append_record("open_temporal_region_observations", region)
    store.append_record("temporal_tail_evidence", tail_result.tail_evidence)
    _emit_event(
        path,
        store=store,
        event_kind="temporal_tail_evidence_created",
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        experiment_run_id=run_id,
        audit_group_id=group_id,
        scenario_name=scenario,
        refs=(tail_result.tail_evidence.temporal_tail_evidence_id,),
        strict=strict_event_stream,
    )

    candidate = create_observation_extension_candidate(
        observation_window=observation_window,
        tail_evidence=tail_result.tail_evidence,
        authorization=authorization,
    )
    if candidate:
        store.append_record("observation_extension_candidates", candidate)
        _emit_event(
            path,
            store=store,
            event_kind="observation_extension_candidate_created",
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
            experiment_run_id=run_id,
            audit_group_id=group_id,
            scenario_name=scenario,
            refs=(candidate.extension_candidate_id,),
            strict=strict_event_stream,
        )

    policy = decide_observation_extension_policy(
        candidate=candidate,
        authorization=authorization,
        observation_window=observation_window,
        transport_integrity_valid=scenario != "transport_fault_control",
        same_sensor_configuration=True,
    )
    store.append_record("observation_extension_policy_decisions", policy)
    _emit_event(
        path,
        store=store,
        event_kind="observation_extension_policy_allowed" if policy.decision == "allow" else "observation_extension_policy_blocked",
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        experiment_run_id=run_id,
        audit_group_id=group_id,
        scenario_name=scenario,
        refs=(policy.extension_policy_decision_id,),
        strict=strict_event_stream,
    )

    controller = BoundedCaptureDeadlineController(
        base_deadline_ns=DEFAULT_BASE_OBSERVATION_NS,
        hard_deadline_ns=DEFAULT_HARD_SESSION_NS,
        participating_lanes=REQUIRED_LANES,
        maximum_extension_count=1,
        maximum_total_extension_ns=DEFAULT_EXTENSION_NS,
    )
    action = create_bounded_observation_extension_internal_action(
        policy_decision=policy,
        observation_window=observation_window,
    )
    execution = None
    identity_after: ActiveCaptureSessionIdentity | None = None
    closure_links = tuple()
    if action:
        store.append_record("observation_extension_internal_actions", action)
        _emit_event(
            path,
            store=store,
            event_kind="observation_extension_action_created",
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
            experiment_run_id=run_id,
            audit_group_id=group_id,
            scenario_name=scenario,
            refs=(action.internal_action_id,),
            strict=strict_event_stream,
        )

        def snapshot_after(deadline_ns: int) -> ActiveCaptureSessionIdentity:
            nonlocal identity_after
            identity_after = replace(
                identity_before,
                active_capture_identity_id=stable_id("active_capture_identity"),
                created_at=utc_now(),
                identity_stage="deadline_extended",
                observed_deadline_ns=deadline_ns,
            )
            store.append_record("active_capture_session_identities", identity_after)
            return identity_after

        execution = execute_bounded_observation_extension(
            action=action,
            controller=controller,
            previous_deadline_ns=DEFAULT_BASE_OBSERVATION_NS,
            participating_lanes=REQUIRED_LANES,
            capture_identity_before=identity_before,
            capture_identity_snapshotter=snapshot_after,
        )
        store.append_record("observation_extension_executions", execution)
        _emit_event(
            path,
            store=store,
            event_kind="observation_deadline_extended",
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
            experiment_run_id=run_id,
            audit_group_id=group_id,
            scenario_name=scenario,
            refs=(execution.extension_execution_id,),
            strict=strict_event_stream,
        )
        extended_state = build_observation_window_state(
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
            experiment_run_id=run_id,
            audit_group_id=group_id,
            scenario_name=scenario,
            active_capture_identity_id=identity_after.active_capture_identity_id if identity_after else identity_before.active_capture_identity_id,
            alignment_origin_monotonic_ns=alignment_origin_ns,
            status="observing_extended_window",
            current_deadline_ns=execution.applied_new_deadline_ns,
            extension_count=1,
            total_extension_ns=DEFAULT_EXTENSION_NS,
            source_record_refs=(observation_window.observation_window_state_id, execution.extension_execution_id),
            source_trace_refs=execution.source_trace_refs,
        )
        store.append_record("observation_window_states", extended_state)
        closure_links = build_closure_links(
            open_regions=tail_result.open_regions,
            coverage_records=coverage,
            base_deadline_event_time_ns=DEFAULT_BASE_OBSERVATION_NS,
            final_deadline_event_time_ns=DEFAULT_FINAL_DEADLINE_NS,
        )
        for link in closure_links:
            store.append_record("temporal_region_closure_links", link)
    elif candidate and scenario == "operator_stop_control":
        cancellation = cancel_pending_observation_extension(
            candidate=candidate,
            reason="operator_stop",
            deadline_already_extended=False,
        )
        store.append_record("observation_extension_cancellations", cancellation)
        _emit_event(
            path,
            store=store,
            event_kind="observation_extension_cancelled",
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
            experiment_run_id=run_id,
            audit_group_id=group_id,
            scenario_name=scenario,
            refs=(cancellation.cancellation_id,),
            strict=strict_event_stream,
        )

    outcome = _build_outcome(
        observation_window=observation_window,
        scenario=scenario,
        execution_id=execution.extension_execution_id if execution else "extension_execution:none",
        open_region_count=len(tail_result.open_regions),
        visual_open_count=len([item for item in tail_result.open_regions if item.source_lane == "screen"]),
        audio_open_count=len([item for item in tail_result.open_regions if item.source_lane == "microphone"]),
        closure_links=closure_links,
        coverage_records=coverage,
        additional_ns=(DEFAULT_EXTENSION_NS if execution and execution.execution_status == "applied" else 0),
        transport_faults=backpressure_fault_count,
    )
    store.append_record("observation_extension_outcomes", outcome)
    _emit_event(
        path,
        store=store,
        event_kind="observation_extension_outcome_created",
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        experiment_run_id=run_id,
        audit_group_id=group_id,
        scenario_name=scenario,
        refs=(outcome.extension_outcome_id,),
        strict=strict_event_stream,
    )
    flush_record_id = f"synthetic_transport_flush:{run_id}"
    flush_verified = scenario != "transport_fault_control"
    comparison = ObservationExtensionEffectComparison(
        comparison_id=stable_id("observation_extension_effect_comparison"),
        schema_version=OBSERVATION_EXTENSION_COMPARISON_SCHEMA_VERSION,
        created_at=utc_now(),
        observation_window_id=observation_window.observation_window_id,
        base_boundary_event_time_ns=DEFAULT_BASE_OBSERVATION_NS,
        final_boundary_event_time_ns=controller.current_deadline_ns(),
        base_tail_evidence_id=tail_result.tail_evidence.temporal_tail_evidence_id,
        final_temporal_bundle_id=f"temporal_context:{PACKAGE_125_EXPERIMENT_ID}:final",
        base_open_region_count=len(tail_result.open_regions),
        final_open_region_count=max(0, len(tail_result.open_regions) - len(closure_links)),
        newly_observed_closure_count=len(closure_links),
        newly_observed_post_event_context_ns=outcome.post_event_context_ns,
        same_source_sessions=bool(execution and execution.same_capture_sessions_preserved),
        same_alignment_origin=bool(
            execution and execution.alignment_origin_before_ns == execution.alignment_origin_after_ns
        ),
        extension_changed_capture_result=bool(execution and execution.execution_status == "applied"),
        memory_influence_used=False,
        stimulus_ground_truth_used_for_runtime_decision=False,
        source_trace_refs=outcome.source_trace_refs,
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        experiment_run_id=run_id,
        audit_group_id=group_id,
        scenario_name=scenario,
        extension_execution_id=execution.extension_execution_id if execution else "extension_execution:none",
        extension_outcome_id=outcome.extension_outcome_id,
        capture_identity_before_id=identity_before.active_capture_identity_id,
        capture_identity_after_id=(
            identity_after.active_capture_identity_id if identity_after else identity_before.active_capture_identity_id
        ),
        transport_flush_record_id=flush_record_id,
        transport_flush_verified=flush_verified,
        flush_remaining_required_records=0 if flush_verified else 1,
    )
    store.append_record("observation_extension_comparisons", comparison)
    score_equivalence = package_112_score_equivalence_context(
        observation_window=observation_window,
        extension_context_record_ids=(
            tail_result.tail_evidence.temporal_tail_evidence_id,
            candidate.extension_candidate_id if candidate else "candidate:none",
            execution.extension_execution_id if execution else "execution:none",
        ),
    )
    store.append_record("package_112_score_equivalence_records", score_equivalence)
    final_status = "failed" if scenario == "transport_fault_control" else (
        "operator_interrupted" if scenario == "operator_stop_control" else "completed"
    )
    final_state = build_observation_window_state(
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        experiment_run_id=run_id,
        audit_group_id=group_id,
        scenario_name=scenario,
        active_capture_identity_id=(
            identity_after.active_capture_identity_id if identity_after else identity_before.active_capture_identity_id
        ),
        alignment_origin_monotonic_ns=alignment_origin_ns,
        transport_flush_record_id=flush_record_id,
        status=final_status,
        current_deadline_ns=controller.current_deadline_ns(),
        extension_count=controller.extension_count,
        total_extension_ns=controller.total_extension_ns,
        operator_stop_requested=scenario == "operator_stop_control",
        source_record_refs=(outcome.extension_outcome_id, comparison.comparison_id, score_equivalence.score_equivalence_record_id),
        source_trace_refs=outcome.source_trace_refs,
    )
    store.append_record("observation_window_states", final_state)
    audit = (
        audit_package_125_observation_extension(
            state_dir=path,
            observation_window_id=observation_window_id,
            append=append_audit,
            require_real_source_capture=False,
        )
        if append_audit
        else None
    )
    return {
        "status": "extension_executed" if execution and execution.execution_status == "applied" else "extension_not_executed",
        "scenario": scenario,
        "experiment_id": PACKAGE_125_EXPERIMENT_ID,
        "experiment_run_id": run_id,
        "audit_group_id": group_id,
        "observation_window": observation_window.to_dict(),
        "authorization": authorization.to_dict(),
        "tail_evidence": tail_result.tail_evidence.to_dict(),
        "open_regions": [item.to_dict() for item in tail_result.open_regions],
        "candidate": candidate.to_dict() if candidate else None,
        "policy": policy.to_dict(),
        "action": action.to_dict() if action else None,
        "execution": execution.to_dict() if execution else None,
        "closure_links": [item.to_dict() for item in closure_links],
        "outcome": outcome.to_dict(),
        "comparison": comparison.to_dict(),
        "score_equivalence": score_equivalence.to_dict(),
        "audit": audit.to_dict() if audit else None,
        "runtime_session_created": False,
        "teacher_review_created": False,
        "memory_write_created": False,
        "external_action_created": False,
        "output_created": False,
        "active_capture_identity_before": identity_before.to_dict(),
        "active_capture_identity_after": identity_after.to_dict() if identity_after else None,
        "final_window_state": final_state.to_dict(),
    }


def build_synthetic_package_123_coverage(
    *,
    scenario: str,
    experiment_run_id: str = PACKAGE_125_EXPERIMENT_ID,
) -> tuple[AlignmentWindowCoverageRecord, ...]:
    records: list[AlignmentWindowCoverageRecord] = []
    for index in range(26):
        start_ns = index * 250_000_000
        end_ns = start_ns + 250_000_000
        if scenario == "stable_baseline_control":
            visual = audio = False
        elif scenario == "early_complete_control":
            visual = audio = 2_000_000_000 <= start_ns < 2_500_000_000
        else:
            visual = start_ns < 5_500_000_000 and end_ns > 4_400_000_000
            audio = start_ns < 5_250_000_000 and end_ns > 4_400_000_000
        drop_count = 1 if scenario == "transport_fault_control" and index == 18 else 0
        complete = drop_count == 0
        records.append(
            AlignmentWindowCoverageRecord(
                coverage_record_id=stable_id("package_125_coverage"),
                schema_version=ALIGNMENT_WINDOW_COVERAGE_SCHEMA_VERSION,
                created_at=utc_now(),
                experiment_run_id=experiment_run_id,
                cycle_index=0,
                alignment_window_id=f"alignment_window:{scenario}:{index}",
                window_index=index,
                start_event_time_ns=start_ns,
                end_event_time_ns=end_ns,
                screen=_lane("screen", visual, drop_count=drop_count),
                audio=_lane("microphone", audio, drop_count=0),
                host_state=_lane("host_state", False, drop_count=0),
                full_window_inside_common_envelope=True,
                partial_edge_window=False,
                required_lanes_complete=complete,
                visual_audio_overlap_present=visual and audio,
                incomplete_reason_codes=tuple() if complete else ("required_lane_drop",),
                source_trace_refs=(f"trace:{scenario}:{index}",),
            )
        )
    return tuple(records)


def _lane(lane: str, salient: bool, *, drop_count: int = 0) -> AlignmentLaneCoverage:
    return AlignmentLaneCoverage(
        lane=lane,
        schema_version=ALIGNMENT_LANE_COVERAGE_SCHEMA_VERSION,
        source_artifact_present=True,
        compiled_primitive_present=True,
        delivered_to_alignment=drop_count == 0,
        salient_change_present=salient,
        dropped_record_count=drop_count,
        capture_failure_count=0,
        compile_failure_count=0,
        source_artifact_refs=(f"{lane}:artifact",),
        primitive_record_refs=(f"{lane}:primitive",),
    )


def _build_outcome(
    *,
    observation_window: ObservationWindowState,
    scenario: str,
    execution_id: str,
    open_region_count: int,
    visual_open_count: int,
    audio_open_count: int,
    closure_links: tuple[Any, ...],
    coverage_records: tuple[AlignmentWindowCoverageRecord, ...],
    additional_ns: int,
    transport_faults: int,
) -> ObservationWindowExtensionOutcome:
    drops = sum(record.screen.dropped_record_count + record.audio.dropped_record_count + record.host_state.dropped_record_count for record in coverage_records)
    closure_times = [int(item.closure_event_time_ns) for item in closure_links]
    post_context = max(0, DEFAULT_FINAL_DEADLINE_NS - max(closure_times)) if closure_times and additional_ns else 0
    if scenario == "operator_stop_control":
        status = "operator_interrupted"
    elif scenario == "transport_fault_control":
        status = "transport_failed"
    elif additional_ns and closure_links:
        status = "event_closure_observed"
    elif additional_ns:
        status = "additional_context_observed"
    else:
        status = "no_material_extension_effect"
    return ObservationWindowExtensionOutcome(
        extension_outcome_id=stable_id("observation_extension_outcome"),
        schema_version=OBSERVATION_EXTENSION_OUTCOME_SCHEMA_VERSION,
        created_at=utc_now(),
        extension_execution_id=execution_id,
        observation_window_id=observation_window.observation_window_id,
        additional_observation_ns=additional_ns,
        open_visual_regions_before=visual_open_count,
        open_audio_regions_before=audio_open_count,
        finalized_visual_spans_after=min(visual_open_count, len(closure_links)),
        finalized_audio_spans_after=min(audio_open_count, max(0, len(closure_links) - visual_open_count)),
        post_event_context_ns=post_context,
        required_lane_drops=drops,
        transport_faults=transport_faults,
        capture_failures=0,
        compile_failures=0,
        extension_effect_status=status,
        semantic_interpretation_created=False,
        source_record_refs=(scenario, PACKAGE_125_EXPERIMENT_ID, execution_id),
        source_trace_refs=(f"trace:{scenario}:outcome",),
        runtime_session_id=observation_window.runtime_session_id,
        perception_session_id=observation_window.perception_session_id,
        experiment_run_id=observation_window.experiment_run_id,
        audit_group_id=observation_window.audit_group_id,
        scenario_name=observation_window.scenario_name,
    )


def _emit_event(
    state_dir: Path,
    *,
    store: Package125ObservationExtensionStore,
    event_kind: str,
    runtime_session_id: str,
    perception_session_id: str,
    observation_window_id: str,
    experiment_run_id: str,
    audit_group_id: str,
    scenario_name: str,
    refs: tuple[str, ...],
    strict: bool = False,
) -> bool:
    try:
        stream = LocalOperatorEventStream(build_default_console_store(state_dir))
        stream.append_event(
            event_kind=event_kind,
            source_record_refs=refs,
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
        )
        return True
    except Exception as error:
        failure = ObservationOperatorEventDeliveryFailure(
            event_delivery_failure_id=stable_id("observation_event_delivery_failure"),
            schema_version=OPERATOR_EVENT_DELIVERY_FAILURE_SCHEMA_VERSION,
            created_at=utc_now(),
            event_kind=event_kind,
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
            experiment_run_id=experiment_run_id,
            audit_group_id=audit_group_id,
            scenario_name=scenario_name,
            exception_kind=type(error).__name__,
            exception_message=str(error),
            strict_mode=bool(strict),
            source_record_refs=refs,
            source_trace_refs=tuple(),
        )
        store.append_record("operator_event_delivery_failures", failure)
        if strict:
            raise
        return False


def _build_synthetic_capture_identity(
    *,
    runtime_session_id: str,
    perception_session_id: str,
    observation_window_id: str,
    experiment_run_id: str,
    audit_group_id: str,
    scenario_name: str,
    alignment_origin_monotonic_ns: int,
    observed_deadline_ns: int,
    identity_stage: str,
) -> ActiveCaptureSessionIdentity:
    return ActiveCaptureSessionIdentity(
        active_capture_identity_id=stable_id("active_capture_identity"),
        schema_version=ACTIVE_CAPTURE_SESSION_IDENTITY_SCHEMA_VERSION,
        created_at=utc_now(),
        identity_stage=identity_stage,
        experiment_run_id=experiment_run_id,
        audit_group_id=audit_group_id,
        scenario_name=scenario_name,
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        screen_capture_session_id=f"synthetic_screen_capture:{experiment_run_id}",
        audio_capture_session_id=f"synthetic_audio_capture:{experiment_run_id}",
        host_state_capture_session_id=f"synthetic_host_state_capture:{experiment_run_id}",
        screen_descriptor_id="synthetic_screen_descriptor",
        audio_descriptor_id="synthetic_audio_descriptor",
        host_state_descriptor_id="synthetic_host_state_descriptor",
        screen_config_sha256="synthetic_screen_config_sha256",
        audio_config_sha256="synthetic_audio_config_sha256",
        host_state_config_sha256="synthetic_host_state_config_sha256",
        window_handle=1,
        render_endpoint_id="synthetic",
        alignment_origin_monotonic_ns=alignment_origin_monotonic_ns,
        clock_domain_ids=("package_125_same_process_clock_domain",),
        observed_deadline_ns=observed_deadline_ns,
        real_source_capture=False,
        sources_open=True,
        sources_reopened=False,
        source_record_refs=(experiment_run_id, observation_window_id),
        source_trace_refs=(f"trace:{scenario_name}:active_capture",),
    )


def run_synthetic_package_125_suite(
    *,
    state_dir: str | Path,
    append_audit: bool = True,
    strict_event_stream: bool = False,
) -> dict[str, Any]:
    group_id = stable_id("package_125_audit_group")
    scenarios = (
        ("late_event", True),
        ("stable_baseline_control", True),
        ("early_complete_control", True),
        ("authorization_off_control", False),
        ("transport_fault_control", True),
        ("operator_stop_control", True),
    )
    results: dict[str, dict[str, Any]] = {}
    for scenario, allowed in scenarios:
        results[scenario] = run_synthetic_observation_extension_scenario(
            state_dir=state_dir,
            scenario=scenario,
            allow_bounded_window_extension=allowed,
            append_audit=False,
            audit_group_id=group_id,
            strict_event_stream=strict_event_stream,
        )
    target_window = str(results["late_event"]["observation_window"]["observation_window_id"])
    audit = audit_package_125_observation_extension(
        state_dir=state_dir,
        observation_window_id=target_window,
        append=append_audit,
        require_real_source_capture=False,
    )
    return {
        "status": audit.audit_status,
        "audit_group_id": group_id,
        "target_observation_window_id": target_window,
        "results": results,
        "audit": audit.to_dict(),
    }


def run_real_late_event_observation_extension(
    *,
    state_dir: str | Path,
    render_endpoint: str = "default",
    allow_bounded_window_extension: bool = True,
    run_isolated_controls: bool = True,
    strict_event_stream: bool = False,
) -> dict[str, Any]:
    """Run the official Package 125 late-event experiment on real local sources."""

    path = Path(state_dir)
    store = Package125ObservationExtensionStore(path)
    sensor_store = ContentAddressedSensorArtifactStore(path)
    temporal_store = Package124ATemporalStore(path)
    package_123_store = Package123CycleStore(path)
    compiler = HardSoftPerceptionPrimitiveCompiler(path, sensor_store=sensor_store)
    primitive_store = PerceptionPrimitiveStore(path)
    runtime_session_id = stable_id("package_125_real_runtime_session")
    perception_session_id = stable_id("package_125_real_perception_session")
    observation_window_id = stable_id("observation_window")
    experiment_run_id = stable_id("package_125_real_experiment_run")
    audit_group_id = stable_id("package_125_real_audit_group")
    scenario = "late_event"
    root_event_id = stable_id("package_125_capture_root_event")
    stimulus = LocalPulseStimulusRuntime(
        experiment_run_id=experiment_run_id,
        render_endpoint_id=render_endpoint,
        schedule=PACKAGE_125_REAL_STIMULUS_SCHEDULE,
        window_title_prefix="ASHL Package 125 Late Event",
        tone_duration_ms=850,
        client_width=80,
        client_height=45,
    )
    window_source = WindowsBoundedWindowCaptureSource()
    loopback_source = WindowsWasapiLoopbackSource(endpoint_id=render_endpoint)
    host_adapter = HostStateSensorAdapter()
    controller = BoundedCaptureDeadlineController(
        base_deadline_ns=DEFAULT_BASE_OBSERVATION_NS,
        hard_deadline_ns=DEFAULT_HARD_SESSION_NS,
        participating_lanes=REQUIRED_LANES,
        maximum_extension_count=1,
        maximum_total_extension_ns=DEFAULT_EXTENSION_NS,
    )
    screen_artifacts: list[str] = []
    audio_artifacts: list[str] = []
    host_artifacts: list[str] = []
    coverage_records: list[AlignmentWindowCoverageRecord] = []
    primitive_cache: dict[str, tuple[str, dict[str, Any]]] = {}
    audio_errors: list[BaseException] = []
    abort_capture = threading.Event()
    host_open = False
    sessions_started = False
    sessions_stopped = False
    screen_session = audio_session = host_session = None
    binding = None
    identity_before: ActiveCaptureSessionIdentity | None = None
    identity_after: ActiveCaptureSessionIdentity | None = None
    observation_window: ObservationWindowState | None = None
    authorization: ObservationWindowExtensionAuthorization | None = None
    tail_result = None
    candidate = None
    policy = None
    action = None
    execution = None
    started_monotonic_ns = 0
    clock_domain = None

    try:
        stimulus.open()
        binding = window_source.bind_by_title(
            experiment_run_id=experiment_run_id,
            window_title=stimulus.window_title,
        )
        if binding.binding_status != "bound":
            raise SensorCaptureError(
                "device_unavailable",
                f"Package 125 stimulus binding failed: {binding.binding_status}",
            )
        if not loopback_source.source_descriptor().available:
            raise SensorCaptureError(
                "backend_missing",
                loopback_source.source_descriptor().failure_reason
                or "WASAPI loopback source unavailable",
            )

        screen_config = window_source.build_capture_config(
            state_dir=str(path),
            binding=binding,
            duration_ms=7_000,
        )
        audio_config = loopback_source.build_capture_config(
            state_dir=str(path),
            duration_ms=7_000,
        )
        host_descriptor = host_adapter.enumerate_devices()[0]
        host_config = build_sensor_capture_config(
            source_kind="host_state",
            adapter_id=host_adapter.adapter_id,
            device_id=host_descriptor.device_id,
            explicit_state_dir=path,
            source_specific_config={"host_state_fields": ("sample_monotonic_ns",)},
            capture_duration_ms=7_000,
            sample_interval_ms=HOST_STATE_INTERVAL_MS,
            maximum_artifact_count=64,
            maximum_total_bytes=1_048_576,
        )
        screen_session = sensor_store.create_capture_session(
            source_kind="screen",
            config=screen_config,
            descriptor=window_source.descriptor(),
            root_event_id=root_event_id,
        )
        audio_session = sensor_store.create_capture_session(
            source_kind="microphone",
            config=audio_config,
            descriptor=loopback_source.descriptor(),
            root_event_id=root_event_id,
        )
        host_session = sensor_store.create_capture_session(
            source_kind="host_state",
            config=host_config,
            descriptor=host_descriptor,
            root_event_id=root_event_id,
        )
        for session in (screen_session, audio_session, host_session):
            sensor_store.append_lifecycle_event(
                session=session,
                previous_status="created",
                new_status="started",
                manual_command="start",
                reason_code="package_125_active_capture_started",
            )
        sessions_started = True
        host_adapter.open(host_config)
        host_open = True
        started_monotonic_ns = monotonic_ns()
        clock_domain = build_clock_domain_descriptor(
            process_instance_id=runtime_session_id,
            operating_system_process_id=os.getpid(),
            utc_anchor=utc_now(),
            utc_anchor_monotonic_ns=started_monotonic_ns,
            monotonic_origin_ns=started_monotonic_ns,
            comparable_across_processes=False,
            source_trace_refs=(root_event_id,),
        )
        temporal_store.append_record("temporal_clock_domains", clock_domain)
        temporal_store.append_record(
            "temporal_clock_quality",
            evaluate_clock_quality(clock_domain, tuple()),
        )
        identity_before = _build_real_capture_identity(
            identity_stage="capture_started",
            experiment_run_id=experiment_run_id,
            audit_group_id=audit_group_id,
            scenario_name=scenario,
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
            screen_session=screen_session,
            audio_session=audio_session,
            host_session=host_session,
            screen_descriptor_id=window_source.descriptor().device_descriptor_id,
            audio_descriptor_id=loopback_source.descriptor().device_descriptor_id,
            host_state_descriptor_id=host_descriptor.device_descriptor_id,
            screen_config_sha256=screen_config.capture_config_sha256,
            audio_config_sha256=audio_config.capture_config_sha256,
            host_state_config_sha256=host_config.capture_config_sha256,
            window_handle=int(binding.target_hwnd),
            render_endpoint_id=loopback_source.source_descriptor().endpoint_id,
            alignment_origin_monotonic_ns=started_monotonic_ns,
            clock_domain_ids=(clock_domain.clock_domain_id,),
            observed_deadline_ns=DEFAULT_BASE_OBSERVATION_NS,
            sources_open=True,
        )
        store.append_record("active_capture_session_identities", identity_before)
        observation_window = build_observation_window_state(
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
            experiment_run_id=experiment_run_id,
            audit_group_id=audit_group_id,
            scenario_name=scenario,
            capture_mode="real_active_capture",
            active_capture_identity_id=identity_before.active_capture_identity_id,
            alignment_origin_monotonic_ns=started_monotonic_ns,
            clock_domain_ids=(clock_domain.clock_domain_id,),
            source_record_refs=(
                screen_session.capture_session_id,
                audio_session.capture_session_id,
                host_session.capture_session_id,
                identity_before.active_capture_identity_id,
            ),
            source_trace_refs=(root_event_id,),
        )
        authorization = build_observation_extension_authorization(
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            bounded_extension_allowed=allow_bounded_window_extension,
        )
        store.append_record("observation_window_states", observation_window)
        store.append_record("observation_window_authorizations", authorization)

        def emit(event_kind: str, refs: tuple[str, ...]) -> bool:
            return _emit_event(
                path,
                store=store,
                event_kind=event_kind,
                runtime_session_id=runtime_session_id,
                perception_session_id=perception_session_id,
                observation_window_id=observation_window_id,
                experiment_run_id=experiment_run_id,
                audit_group_id=audit_group_id,
                scenario_name=scenario,
                refs=refs,
                strict=strict_event_stream,
            )

        emit("observation_window_started", (observation_window.observation_window_state_id,))

        def absolute_deadline_ns() -> int:
            if abort_capture.is_set():
                return monotonic_ns()
            return started_monotonic_ns + controller.current_deadline_ns()

        def persist_audio_sample(sample: Any) -> None:
            artifact = sensor_store.write_raw_artifact(
                session=audio_session,
                descriptor=loopback_source.descriptor(),
                config=audio_config,
                sample=sample,
            )
            audio_artifacts.append(artifact.artifact_id)

        def capture_audio() -> None:
            try:
                loopback_source.capture_samples_until_deadline(
                    deadline_ns_getter=absolute_deadline_ns,
                    on_sample=persist_audio_sample,
                )
            except BaseException as error:
                audio_errors.append(error)
                abort_capture.set()

        audio_thread = threading.Thread(
            target=capture_audio,
            name="package_125_shared_deadline_loopback",
            daemon=True,
        )
        audio_thread.start()
        next_screen_ns = started_monotonic_ns
        next_host_ns = started_monotonic_ns
        checkpoint_index = 0
        coverage_index = 0
        while monotonic_ns() < started_monotonic_ns + controller.current_deadline_ns():
            if abort_capture.is_set():
                break
            stimulus.tick()
            now_ns = monotonic_ns()
            if now_ns >= next_screen_ns:
                artifact = sensor_store.write_raw_artifact(
                    session=screen_session,
                    descriptor=window_source.descriptor(),
                    config=screen_config,
                    sample=window_source.capture_sample(binding),
                )
                screen_artifacts.append(artifact.artifact_id)
                next_screen_ns += 100_000_000
            if now_ns >= next_host_ns:
                artifact = sensor_store.write_raw_artifact(
                    session=host_session,
                    descriptor=host_descriptor,
                    config=host_config,
                    sample=host_adapter.read_sample(),
                )
                host_artifacts.append(artifact.artifact_id)
                next_host_ns += HOST_STATE_INTERVAL_MS * 1_000_000
            elapsed_ns = now_ns - started_monotonic_ns
            if (
                checkpoint_index < len(PACKAGE_125_TAIL_CHECKPOINT_NS)
                and elapsed_ns >= PACKAGE_125_TAIL_CHECKPOINT_NS[checkpoint_index]
            ):
                checkpoint_ns = PACKAGE_125_TAIL_CHECKPOINT_NS[checkpoint_index]
                evidence_event_time_ns = min(
                    DEFAULT_BASE_OBSERVATION_NS,
                    max(
                        checkpoint_ns,
                        monotonic_ns() - started_monotonic_ns,
                    ),
                )
                coverage = _build_real_checkpoint_coverage(
                    sensor_store=sensor_store,
                    compiler=compiler,
                    primitive_store=primitive_store,
                    primitive_cache=primitive_cache,
                    experiment_run_id=experiment_run_id,
                    alignment_origin_monotonic_ns=started_monotonic_ns,
                    checkpoint_event_time_ns=evidence_event_time_ns,
                    window_index=coverage_index,
                    screen_artifact_ids=screen_artifacts,
                    audio_artifact_ids=audio_artifacts,
                    host_artifact_ids=host_artifacts,
                )
                coverage_index += 1
                checkpoint_index += 1
                coverage_records.append(coverage)
                package_123_store.append_alignment_window_coverage(coverage)
                tail_result = build_temporal_tail_evidence(
                    observation_window=observation_window,
                    coverage_records=tuple(coverage_records),
                    temporal_bundle_or_context_id=f"temporal_context:{experiment_run_id}:live_tail",
                    evaluated_at_event_time_ns=evidence_event_time_ns,
                    clock_domain_id=clock_domain.clock_domain_id,
                )
                for region in tail_result.open_regions:
                    store.append_record("open_temporal_region_observations", region)
                store.append_record("temporal_tail_evidence", tail_result.tail_evidence)
                emit(
                    "temporal_tail_evidence_created",
                    (tail_result.tail_evidence.temporal_tail_evidence_id,),
                )
                candidate = create_observation_extension_candidate(
                    observation_window=observation_window,
                    tail_evidence=tail_result.tail_evidence,
                    authorization=authorization,
                )
                if candidate is not None:
                    store.append_record("observation_extension_candidates", candidate)
                    emit(
                        "observation_extension_candidate_created",
                        (candidate.extension_candidate_id,),
                    )
                    policy = decide_observation_extension_policy(
                        candidate=candidate,
                        authorization=authorization,
                        observation_window=observation_window,
                        transport_integrity_valid=not audio_errors,
                        same_sensor_configuration=True,
                    )
                    store.append_record("observation_extension_policy_decisions", policy)
                    emit(
                        "observation_extension_policy_allowed"
                        if policy.decision == "allow"
                        else "observation_extension_policy_blocked",
                        (policy.extension_policy_decision_id,),
                    )
                    action = create_bounded_observation_extension_internal_action(
                        policy_decision=policy,
                        observation_window=observation_window,
                    )
                    if action is not None:
                        if monotonic_ns() >= (
                            started_monotonic_ns + DEFAULT_BASE_OBSERVATION_NS
                        ):
                            raise RuntimeError(
                                "extension decision processing crossed the base deadline"
                            )
                        store.append_record("observation_extension_internal_actions", action)
                        emit("observation_extension_action_created", (action.internal_action_id,))

                        def snapshot_after(deadline_ns: int) -> ActiveCaptureSessionIdentity:
                            nonlocal identity_after
                            identity_after = _build_real_capture_identity(
                                identity_stage="deadline_extended",
                                experiment_run_id=experiment_run_id,
                                audit_group_id=audit_group_id,
                                scenario_name=scenario,
                                runtime_session_id=runtime_session_id,
                                perception_session_id=perception_session_id,
                                observation_window_id=observation_window_id,
                                screen_session=screen_session,
                                audio_session=audio_session,
                                host_session=host_session,
                                screen_descriptor_id=window_source.descriptor().device_descriptor_id,
                                audio_descriptor_id=loopback_source.descriptor().device_descriptor_id,
                                host_state_descriptor_id=host_descriptor.device_descriptor_id,
                                screen_config_sha256=screen_config.capture_config_sha256,
                                audio_config_sha256=audio_config.capture_config_sha256,
                                host_state_config_sha256=host_config.capture_config_sha256,
                                window_handle=int(binding.target_hwnd),
                                render_endpoint_id=loopback_source.source_descriptor().endpoint_id,
                                alignment_origin_monotonic_ns=started_monotonic_ns,
                                clock_domain_ids=(clock_domain.clock_domain_id,),
                                observed_deadline_ns=deadline_ns,
                                sources_open=True,
                            )
                            store.append_record(
                                "active_capture_session_identities",
                                identity_after,
                            )
                            return identity_after

                        execution = execute_bounded_observation_extension(
                            action=action,
                            controller=controller,
                            previous_deadline_ns=DEFAULT_BASE_OBSERVATION_NS,
                            participating_lanes=REQUIRED_LANES,
                            capture_identity_before=identity_before,
                            capture_identity_snapshotter=snapshot_after,
                        )
                        store.append_record("observation_extension_executions", execution)
                        emit("observation_deadline_extended", (execution.extension_execution_id,))
                        store.append_record(
                            "observation_window_states",
                            build_observation_window_state(
                                runtime_session_id=runtime_session_id,
                                perception_session_id=perception_session_id,
                                observation_window_id=observation_window_id,
                                experiment_run_id=experiment_run_id,
                                audit_group_id=audit_group_id,
                                scenario_name=scenario,
                                capture_mode="real_active_capture",
                                active_capture_identity_id=identity_after.active_capture_identity_id,
                                alignment_origin_monotonic_ns=started_monotonic_ns,
                                clock_domain_ids=(clock_domain.clock_domain_id,),
                                status="observing_extended_window",
                                current_deadline_ns=execution.applied_new_deadline_ns,
                                extension_count=controller.extension_count,
                                total_extension_ns=controller.total_extension_ns,
                                source_record_refs=(
                                    observation_window.observation_window_state_id,
                                    execution.extension_execution_id,
                                    identity_after.active_capture_identity_id,
                                ),
                                source_trace_refs=(root_event_id,),
                            ),
                        )
                        checkpoint_index = len(PACKAGE_125_TAIL_CHECKPOINT_NS)
            time.sleep(0.005)

        stimulus.mark_finished()
        audio_thread.join(timeout=5.0)
        if audio_thread.is_alive():
            abort_capture.set()
            raise RuntimeError("WASAPI loopback did not stop at the shared deadline")
        if audio_errors:
            raise audio_errors[0]
        host_adapter.close()
        host_open = False
        for session in (screen_session, audio_session, host_session):
            sensor_store.append_lifecycle_event(
                session=session,
                previous_status="started",
                new_status="stopped",
                manual_command="stop",
                reason_code="package_125_shared_deadline_capture_stopped",
            )
        sessions_stopped = True

        if execution is None or execution.execution_status != "applied":
            raise RuntimeError("real late-event evidence did not authorize one bounded extension")

        for checkpoint_ns in PACKAGE_125_FINAL_COVERAGE_CHECKPOINT_NS:
            coverage = _build_real_checkpoint_coverage(
                sensor_store=sensor_store,
                compiler=compiler,
                primitive_store=primitive_store,
                primitive_cache=primitive_cache,
                experiment_run_id=experiment_run_id,
                alignment_origin_monotonic_ns=started_monotonic_ns,
                checkpoint_event_time_ns=checkpoint_ns,
                window_index=coverage_index,
                screen_artifact_ids=screen_artifacts,
                audio_artifact_ids=audio_artifacts,
                host_artifact_ids=host_artifacts,
            )
            coverage_index += 1
            coverage_records.append(coverage)
            package_123_store.append_alignment_window_coverage(coverage)

        replay_manifest = _build_replay_manifest(
            path,
            screen_artifacts,
            audio_artifacts,
            host_artifacts,
            started_monotonic_ns,
        )
        package_122_config = build_package_123_multimodal_config(state_dir=path)
        package_122_runtime = BoundedMultimodalPerceptionSessionRuntime(path)
        prepared = package_122_runtime.prepare_artifact_backed_alignment_replay_transport(
            replay_manifest,
            config=package_122_config,
            session_id=perception_session_id,
        )
        configuration_hash = package_123_transport_configuration_hash(
            config=package_122_config,
            render_endpoint=render_endpoint,
        )
        transport = _persist_transport_integrity(
            path,
            experiment_run_id=experiment_run_id,
            cycle_index=0,
            prepared_transport=prepared,
            configuration_hash=configuration_hash,
            source_capture_session_ids=(
                screen_session.capture_session_id,
                audio_session.capture_session_id,
                host_session.capture_session_id,
            ),
        )
        flush_record = transport["flush_record"]
        transport_summary = transport["integrity_summary"]

        compiled_temporal_records: list[Any] = []
        closure_links = build_closure_links(
            open_regions=tail_result.open_regions,
            coverage_records=tuple(coverage_records),
            base_deadline_event_time_ns=DEFAULT_BASE_OBSERVATION_NS,
            final_deadline_event_time_ns=DEFAULT_FINAL_DEADLINE_NS,
            clock_domain_id=clock_domain.clock_domain_id,
            compiled_temporal_records=compiled_temporal_records,
        )
        for link in closure_links:
            store.append_record("temporal_region_closure_links", link)
        anchors = tuple(
            item for item in compiled_temporal_records if isinstance(item, TemporalEventAnchor)
        )
        spans = tuple(
            item for item in compiled_temporal_records if isinstance(item, TemporalSpanPrimitive)
        )
        for item in anchors:
            temporal_store.append_record("temporal_event_anchors", item)
        for item in spans:
            temporal_store.append_record("temporal_span_primitives", item)
        final_temporal_bundle = _build_package_125_temporal_bundle(
            clock_domain_id=clock_domain.clock_domain_id,
            anchors=anchors,
            spans=spans,
            coverage_records=tuple(coverage_records),
        )
        temporal_store.append_record("grounded_temporal_bundles", final_temporal_bundle)

        drop_count = int(transport_summary.required_lane_drop_count)
        transport_fault_count = int(transport_summary.backpressure_event_count)
        capture_failure_count = int(transport_summary.capture_failure_count)
        compile_failure_count = int(transport_summary.compile_failure_count)
        closure_times = tuple(int(item.closure_event_time_ns) for item in closure_links)
        post_context_ns = (
            max(0, DEFAULT_FINAL_DEADLINE_NS - max(closure_times))
            if closure_times
            else 0
        )
        visual_open_count = len(tail_result.tail_evidence.open_visual_region_refs)
        audio_open_count = len(tail_result.tail_evidence.open_audio_region_refs)
        outcome = ObservationWindowExtensionOutcome(
            extension_outcome_id=stable_id("observation_extension_outcome"),
            schema_version=OBSERVATION_EXTENSION_OUTCOME_SCHEMA_VERSION,
            created_at=utc_now(),
            extension_execution_id=execution.extension_execution_id,
            observation_window_id=observation_window_id,
            additional_observation_ns=DEFAULT_EXTENSION_NS,
            open_visual_regions_before=visual_open_count,
            open_audio_regions_before=audio_open_count,
            finalized_visual_spans_after=sum(
                1
                for item in closure_links
                if item.open_region_observation_id
                in tail_result.tail_evidence.open_visual_region_refs
            ),
            finalized_audio_spans_after=sum(
                1
                for item in closure_links
                if item.open_region_observation_id
                in tail_result.tail_evidence.open_audio_region_refs
            ),
            post_event_context_ns=post_context_ns,
            required_lane_drops=drop_count,
            transport_faults=transport_fault_count,
            capture_failures=capture_failure_count,
            compile_failures=compile_failure_count,
            extension_effect_status=(
                "event_closure_observed"
                if closure_links
                else "no_material_extension_effect"
            ),
            semantic_interpretation_created=False,
            source_record_refs=(
                execution.extension_execution_id,
                flush_record.flush_record_id,
                final_temporal_bundle.temporal_bundle_id,
            ),
            source_trace_refs=tuple(prepared.source_trace_refs),
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            experiment_run_id=experiment_run_id,
            audit_group_id=audit_group_id,
            scenario_name=scenario,
        )
        store.append_record("observation_extension_outcomes", outcome)
        emit("observation_extension_outcome_created", (outcome.extension_outcome_id,))
        comparison = ObservationExtensionEffectComparison(
            comparison_id=stable_id("observation_extension_effect_comparison"),
            schema_version=OBSERVATION_EXTENSION_COMPARISON_SCHEMA_VERSION,
            created_at=utc_now(),
            observation_window_id=observation_window_id,
            base_boundary_event_time_ns=DEFAULT_BASE_OBSERVATION_NS,
            final_boundary_event_time_ns=execution.applied_new_deadline_ns,
            base_tail_evidence_id=tail_result.tail_evidence.temporal_tail_evidence_id,
            final_temporal_bundle_id=final_temporal_bundle.temporal_bundle_id,
            base_open_region_count=visual_open_count + audio_open_count,
            final_open_region_count=max(
                0,
                visual_open_count + audio_open_count - len(closure_links),
            ),
            newly_observed_closure_count=len(closure_links),
            newly_observed_post_event_context_ns=post_context_ns,
            same_source_sessions=execution.same_capture_sessions_preserved,
            same_alignment_origin=(
                execution.alignment_origin_before_ns
                == execution.alignment_origin_after_ns
            ),
            extension_changed_capture_result=bool(closure_links and post_context_ns > 0),
            memory_influence_used=False,
            stimulus_ground_truth_used_for_runtime_decision=False,
            source_trace_refs=tuple(prepared.source_trace_refs),
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            experiment_run_id=experiment_run_id,
            audit_group_id=audit_group_id,
            scenario_name=scenario,
            extension_execution_id=execution.extension_execution_id,
            extension_outcome_id=outcome.extension_outcome_id,
            capture_identity_before_id=identity_before.active_capture_identity_id,
            capture_identity_after_id=identity_after.active_capture_identity_id,
            transport_flush_record_id=flush_record.flush_record_id,
            transport_flush_verified=bool(flush_record.passed),
            flush_remaining_required_records=sum(
                int(value) for value in flush_record.remaining_record_counts.values()
            ),
        )
        store.append_record("observation_extension_comparisons", comparison)
        score_equivalence = package_112_score_equivalence_context(
            observation_window=observation_window,
            extension_context_record_ids=(
                tail_result.tail_evidence.temporal_tail_evidence_id,
                candidate.extension_candidate_id,
                execution.extension_execution_id,
                outcome.extension_outcome_id,
            ),
        )
        store.append_record("package_112_score_equivalence_records", score_equivalence)
        final_state = build_observation_window_state(
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
            experiment_run_id=experiment_run_id,
            audit_group_id=audit_group_id,
            scenario_name=scenario,
            capture_mode="real_active_capture",
            active_capture_identity_id=identity_after.active_capture_identity_id,
            alignment_origin_monotonic_ns=started_monotonic_ns,
            clock_domain_ids=(clock_domain.clock_domain_id,),
            transport_flush_record_id=flush_record.flush_record_id,
            status="completed" if transport_summary.teacher_review_eligible else "failed",
            current_deadline_ns=execution.applied_new_deadline_ns,
            extension_count=controller.extension_count,
            total_extension_ns=controller.total_extension_ns,
            source_record_refs=(
                outcome.extension_outcome_id,
                comparison.comparison_id,
                score_equivalence.score_equivalence_record_id,
            ),
            source_trace_refs=tuple(prepared.source_trace_refs),
        )
        store.append_record("observation_window_states", final_state)

        runtime_result_frozen_at = utc_now()
        stimulus_manifest = Package125StimulusAuditManifest(
            stimulus_audit_manifest_id=stable_id("package_125_stimulus_audit_manifest"),
            schema_version=PACKAGE_125_STIMULUS_AUDIT_MANIFEST_SCHEMA_VERSION,
            created_at=utc_now(),
            experiment_run_id=experiment_run_id,
            audit_group_id=audit_group_id,
            scenario_name=scenario,
            runtime_result_frozen_at=runtime_result_frozen_at,
            window_title=stimulus.window_title,
            window_handle=int(binding.target_hwnd),
            render_endpoint_id=render_endpoint,
            stimulus_started_monotonic_ns=int(
                stimulus.started_monotonic_ns or started_monotonic_ns
            ),
            stimulus_finished_monotonic_ns=int(
                stimulus.finished_monotonic_ns or monotonic_ns()
            ),
            transition_records=tuple(
                item.to_dict() for item in stimulus.transition_records
            ),
            consumed_by_runtime_decision=False,
            source_record_refs=(outcome.extension_outcome_id, comparison.comparison_id),
        )
        store.append_record("package_125_stimulus_audit_manifests", stimulus_manifest)

        control_results: dict[str, Any] = {}
        if run_isolated_controls:
            for control_scenario, allowed in (
                ("stable_baseline_control", True),
                ("early_complete_control", True),
                ("authorization_off_control", False),
                ("transport_fault_control", True),
                ("operator_stop_control", True),
            ):
                control_results[control_scenario] = (
                    run_synthetic_observation_extension_scenario(
                        state_dir=path,
                        scenario=control_scenario,
                        allow_bounded_window_extension=allowed,
                        append_audit=False,
                        audit_group_id=audit_group_id,
                        strict_event_stream=strict_event_stream,
                    )
                )
        audit = audit_package_125_observation_extension(
            state_dir=path,
            observation_window_id=observation_window_id,
            append=True,
            require_real_source_capture=True,
        )
        return {
            "status": audit.audit_status,
            "experiment_id": PACKAGE_125_EXPERIMENT_ID,
            "experiment_run_id": experiment_run_id,
            "audit_group_id": audit_group_id,
            "runtime_session_id": runtime_session_id,
            "perception_session_id": perception_session_id,
            "observation_window_id": observation_window_id,
            "capture_session_ids": {
                "screen": screen_session.capture_session_id,
                "microphone": audio_session.capture_session_id,
                "host_state": host_session.capture_session_id,
            },
            "active_capture_identity_before": identity_before.to_dict(),
            "active_capture_identity_after": identity_after.to_dict(),
            "original_deadline_ns": execution.previous_deadline_ns,
            "applied_deadline_ns": execution.applied_new_deadline_ns,
            "extension_count": controller.extension_count,
            "tail_evidence": tail_result.tail_evidence.to_dict(),
            "candidate": candidate.to_dict(),
            "policy": policy.to_dict(),
            "action": action.to_dict(),
            "execution": execution.to_dict(),
            "closure_links": [item.to_dict() for item in closure_links],
            "final_temporal_bundle": final_temporal_bundle.to_dict(),
            "transport_flush": flush_record.to_dict(),
            "transport_integrity_summary": transport_summary.to_dict(),
            "outcome": outcome.to_dict(),
            "comparison": comparison.to_dict(),
            "score_equivalence": score_equivalence.to_dict(),
            "stimulus_audit_manifest": stimulus_manifest.to_dict(),
            "control_results": control_results,
            "audit": audit.to_dict(),
            "memory_write_count": 0,
            "output_count": 0,
            "external_action_count": 0,
            "llm_runtime_calls": 0,
            "codex_runtime_calls": 0,
            "network_runtime_calls": 0,
        }
    finally:
        abort_capture.set()
        if host_open:
            try:
                host_adapter.close()
            except Exception:
                pass
        if sessions_started and not sessions_stopped:
            for session in (screen_session, audio_session, host_session):
                if session is None:
                    continue
                try:
                    sensor_store.append_lifecycle_event(
                        session=session,
                        previous_status="started",
                        new_status="failed",
                        manual_command="stop",
                        reason_code="package_125_capture_aborted",
                    )
                except Exception:
                    pass
        stimulus.close()


def _build_real_capture_identity(
    *,
    identity_stage: str,
    experiment_run_id: str,
    audit_group_id: str,
    scenario_name: str,
    runtime_session_id: str,
    perception_session_id: str,
    observation_window_id: str,
    screen_session: Any,
    audio_session: Any,
    host_session: Any,
    screen_descriptor_id: str,
    audio_descriptor_id: str,
    host_state_descriptor_id: str,
    screen_config_sha256: str,
    audio_config_sha256: str,
    host_state_config_sha256: str,
    window_handle: int,
    render_endpoint_id: str,
    alignment_origin_monotonic_ns: int,
    clock_domain_ids: tuple[str, ...],
    observed_deadline_ns: int,
    sources_open: bool,
) -> ActiveCaptureSessionIdentity:
    return ActiveCaptureSessionIdentity(
        active_capture_identity_id=stable_id("active_capture_identity"),
        schema_version=ACTIVE_CAPTURE_SESSION_IDENTITY_SCHEMA_VERSION,
        created_at=utc_now(),
        identity_stage=identity_stage,
        experiment_run_id=experiment_run_id,
        audit_group_id=audit_group_id,
        scenario_name=scenario_name,
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        screen_capture_session_id=screen_session.capture_session_id,
        audio_capture_session_id=audio_session.capture_session_id,
        host_state_capture_session_id=host_session.capture_session_id,
        screen_descriptor_id=screen_descriptor_id,
        audio_descriptor_id=audio_descriptor_id,
        host_state_descriptor_id=host_state_descriptor_id,
        screen_config_sha256=screen_config_sha256,
        audio_config_sha256=audio_config_sha256,
        host_state_config_sha256=host_state_config_sha256,
        window_handle=window_handle,
        render_endpoint_id=render_endpoint_id,
        alignment_origin_monotonic_ns=alignment_origin_monotonic_ns,
        clock_domain_ids=clock_domain_ids,
        observed_deadline_ns=observed_deadline_ns,
        real_source_capture=True,
        sources_open=sources_open,
        sources_reopened=False,
        source_record_refs=(
            screen_session.capture_session_id,
            audio_session.capture_session_id,
            host_session.capture_session_id,
        ),
        source_trace_refs=tuple(),
    )


def _build_real_checkpoint_coverage(
    *,
    sensor_store: ContentAddressedSensorArtifactStore,
    compiler: HardSoftPerceptionPrimitiveCompiler,
    primitive_store: PerceptionPrimitiveStore,
    primitive_cache: dict[str, tuple[str, dict[str, Any]]],
    experiment_run_id: str,
    alignment_origin_monotonic_ns: int,
    checkpoint_event_time_ns: int,
    window_index: int,
    screen_artifact_ids: list[str],
    audio_artifact_ids: list[str],
    host_artifact_ids: list[str],
) -> AlignmentWindowCoverageRecord:
    deadline_absolute_ns = alignment_origin_monotonic_ns + checkpoint_event_time_ns
    selected = {
        "screen": _latest_artifact_before(
            sensor_store,
            screen_artifact_ids,
            deadline_absolute_ns,
        ),
        "microphone": _latest_artifact_before(
            sensor_store,
            audio_artifact_ids,
            deadline_absolute_ns,
        ),
        "host_state": _latest_artifact_before(
            sensor_store,
            host_artifact_ids,
            deadline_absolute_ns,
        ),
    }
    baseline_screen_id = _latest_artifact_before(
        sensor_store,
        screen_artifact_ids,
        alignment_origin_monotonic_ns + 500_000_000,
    )
    lane_payloads: dict[str, AlignmentLaneCoverage] = {}
    selected_times: list[int] = []
    source_traces: list[str] = []
    for lane in REQUIRED_LANES:
        artifact_id = selected[lane]
        if artifact_id is None:
            lane_payloads[lane] = AlignmentLaneCoverage(
                lane=lane,
                schema_version=ALIGNMENT_LANE_COVERAGE_SCHEMA_VERSION,
                source_artifact_present=False,
                compiled_primitive_present=False,
                delivered_to_alignment=False,
                salient_change_present=False,
                dropped_record_count=0,
                capture_failure_count=1,
                compile_failure_count=0,
                source_artifact_refs=tuple(),
                primitive_record_refs=tuple(),
            )
            continue
        artifact = sensor_store.get_artifact(artifact_id)
        selected_times.append(int(artifact["captured_at_monotonic_ns"]))
        source_traces.extend(tuple(artifact.get("source_trace_refs") or ()))
        compile_failure = 0
        primitive_id = ""
        primitive_payload: dict[str, Any] = {}
        try:
            primitive_id, primitive_payload = _compile_artifact_cached(
                compiler=compiler,
                primitive_store=primitive_store,
                primitive_cache=primitive_cache,
                artifact_id=artifact_id,
            )
        except Exception:
            compile_failure = 1
        salient = False
        if lane == "screen" and primitive_payload and baseline_screen_id:
            _, baseline = _compile_artifact_cached(
                compiler=compiler,
                primitive_store=primitive_store,
                primitive_cache=primitive_cache,
                artifact_id=baseline_screen_id,
            )
            salient = (
                abs(
                    float(primitive_payload.get("luminance_mean", 0.0))
                    - float(baseline.get("luminance_mean", 0.0))
                )
                >= 0.50
            )
        elif lane == "microphone" and primitive_payload:
            salient = max(
                (float(value) for value in primitive_payload.get("amplitude_envelope", ())),
                default=0.0,
            ) > 0.0
        lane_payloads[lane] = AlignmentLaneCoverage(
            lane=lane,
            schema_version=ALIGNMENT_LANE_COVERAGE_SCHEMA_VERSION,
            source_artifact_present=True,
            compiled_primitive_present=compile_failure == 0,
            delivered_to_alignment=compile_failure == 0,
            salient_change_present=salient,
            dropped_record_count=0,
            capture_failure_count=0,
            compile_failure_count=compile_failure,
            source_artifact_refs=(artifact_id,),
            primitive_record_refs=(primitive_id,) if primitive_id else tuple(),
        )
    required_complete = all(item.complete for item in lane_payloads.values())
    latest_selected_event_time_ns = max(
        0,
        max(selected_times, default=deadline_absolute_ns)
        - alignment_origin_monotonic_ns,
    )
    start_event_time_ns = latest_selected_event_time_ns
    end_event_time_ns = latest_selected_event_time_ns
    return AlignmentWindowCoverageRecord(
        coverage_record_id=stable_id("package_125_real_alignment_coverage"),
        schema_version=ALIGNMENT_WINDOW_COVERAGE_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_run_id=experiment_run_id,
        cycle_index=0,
        alignment_window_id=f"package_125_real_alignment_window:{window_index}",
        window_index=window_index,
        start_event_time_ns=start_event_time_ns,
        end_event_time_ns=end_event_time_ns,
        screen=lane_payloads["screen"],
        audio=lane_payloads["microphone"],
        host_state=lane_payloads["host_state"],
        full_window_inside_common_envelope=True,
        partial_edge_window=False,
        required_lanes_complete=required_complete,
        visual_audio_overlap_present=(
            lane_payloads["screen"].salient_change_present
            and lane_payloads["microphone"].salient_change_present
        ),
        incomplete_reason_codes=(
            tuple() if required_complete else ("required_lane_delivery_incomplete",)
        ),
        source_trace_refs=tuple(dict.fromkeys(source_traces)),
    )


def _latest_artifact_before(
    sensor_store: ContentAddressedSensorArtifactStore,
    artifact_ids: list[str],
    deadline_absolute_ns: int,
) -> str | None:
    eligible: list[tuple[int, str]] = []
    for artifact_id in tuple(artifact_ids):
        artifact = sensor_store.get_artifact(artifact_id)
        captured_ns = int(artifact["captured_at_monotonic_ns"])
        if captured_ns <= deadline_absolute_ns:
            eligible.append((captured_ns, artifact_id))
    return max(eligible)[1] if eligible else None


def _compile_artifact_cached(
    *,
    compiler: HardSoftPerceptionPrimitiveCompiler,
    primitive_store: PerceptionPrimitiveStore,
    primitive_cache: dict[str, tuple[str, dict[str, Any]]],
    artifact_id: str,
) -> tuple[str, dict[str, Any]]:
    if artifact_id not in primitive_cache:
        bundle = compiler.compile_artifact(artifact_id)
        primitive_cache[artifact_id] = (
            bundle.primitive_record_id,
            primitive_store.get_primitive(bundle.primitive_record_id),
        )
    return primitive_cache[artifact_id]


def _build_package_125_temporal_bundle(
    *,
    clock_domain_id: str,
    anchors: tuple[TemporalEventAnchor, ...],
    spans: tuple[TemporalSpanPrimitive, ...],
    coverage_records: tuple[AlignmentWindowCoverageRecord, ...],
) -> GroundedTemporalPrimitiveBundle:
    source_perception_refs = tuple(
        dict.fromkeys(
            ref
            for coverage in coverage_records
            for lane in (coverage.screen, coverage.audio, coverage.host_state)
            for ref in lane.primitive_record_refs
        )
    )
    source_trace_refs = tuple(
        dict.fromkeys(
            ref for coverage in coverage_records for ref in coverage.source_trace_refs
        )
    )
    payload = {
        "schema_version": TEMPORAL_BUNDLE_SCHEMA_VERSION,
        "clock_domain_refs": (clock_domain_id,),
        "anchor_refs": tuple(item.temporal_anchor_id for item in anchors),
        "span_refs": tuple(item.temporal_span_id for item in spans),
        "interval_refs": tuple(),
        "relation_refs": tuple(),
        "continuity_refs": tuple(),
        "repeated_structure_refs": tuple(),
        "external_gap_refs": tuple(),
        "source_perception_record_refs": source_perception_refs,
        "source_alignment_window_refs": tuple(
            item.coverage_record_id for item in coverage_records
        ),
        "source_trace_refs": source_trace_refs,
        "stimulus_ground_truth_used_for_compilation": False,
        "subjective_time_claimed": False,
        "rhythm_semantics_claimed": False,
        "waiting_semantics_claimed": False,
    }
    return GroundedTemporalPrimitiveBundle(
        temporal_bundle_id=temporal_identity(
            "package_125_grounded_temporal_bundle",
            payload,
        ),
        created_at=utc_now(),
        **payload,
    )
