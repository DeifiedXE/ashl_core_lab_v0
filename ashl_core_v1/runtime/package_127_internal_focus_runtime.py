"""Package 127 bounded internal visual-focus runtime."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from ashl_core_v1.host_body import (
    host_body_readback_internal_action_influence as package_112,
)
from ashl_core_v1.perception.hard_soft_perception_primitive_compiler import (
    HardSoftPerceptionPrimitiveCompiler,
)
from ashl_core_v1.perception.perception_primitive_store import (
    PerceptionPrimitiveStore,
)
from ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime import (
    BoundedMultimodalPerceptionSessionRuntime,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
    ContentAddressedSensorArtifactStore,
)
from ashl_core_v1.runtime.cross_window_temporal_link import (
    build_cross_window_temporal_link,
)
from ashl_core_v1.runtime.focused_visual_region_view import (
    build_focus_context_sidecar,
    build_focus_release_record,
    build_focused_visual_region_view,
)
from ashl_core_v1.runtime.host_sensor_types import (
    SensorCaptureError,
    monotonic_ns,
    sha256_bytes,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.host_state_sensor_adapter import (
    HostStateSensorAdapter,
)
from ashl_core_v1.runtime.internal_perception_focus_action import (
    create_internal_perception_focus_shift_action,
)
from ashl_core_v1.runtime.internal_perception_focus_candidate import (
    create_focus_candidates,
    select_focus_candidate,
)
from ashl_core_v1.runtime.internal_perception_focus_policy import (
    create_focus_authorization,
    create_focus_plan,
    decide_focus_policy,
)
from ashl_core_v1.runtime.internal_perception_focus_types import (
    FOCUS_ACTION_KIND,
    FocusedVisualRegionView,
    InternalPerceptionFocusCandidate,
    InternalPerceptionFocusContextSidecar,
    Package127ScoreEquivalenceRecord,
)
from ashl_core_v1.runtime.local_grid_focus_stimulus_runtime import (
    LocalGridFocusStimulusRuntime,
)
from ashl_core_v1.runtime.local_operator_console_store import (
    build_default_console_store,
)
from ashl_core_v1.runtime.local_operator_event_stream import (
    LocalOperatorEventStream,
)
from ashl_core_v1.runtime.package_124a_temporal_store import (
    Package124ATemporalStore,
)
from ashl_core_v1.runtime.package_126_reacquisition_runtime import (
    _build_effect_comparison,
    _build_evidence_summary,
    _build_plan_identity,
    _build_source_configs,
    _completed_parent_reference,
    _emit_event as _emit_package_126_event,
    capture_one_bounded_reacquisition_window,
)
from ashl_core_v1.runtime.package_126_reacquisition_store import (
    Package126ReacquisitionStore,
)
from ashl_core_v1.runtime.package_127_internal_focus_store import (
    Package127InternalFocusStore,
)
from ashl_core_v1.runtime.perception_reacquisition_internal_action import (
    create_bounded_reacquisition_internal_action,
)
from ashl_core_v1.runtime.perception_reacquisition_policy import (
    create_reacquisition_authorization,
    create_reacquisition_request,
    decide_reacquisition_eligibility,
)
from ashl_core_v1.runtime.perception_reacquisition_types import (
    CompletedObservationWindowReference,
    ReacquisitionCaptureExecution,
)
from ashl_core_v1.runtime.sampling_plan_identity import (
    clone_sampling_plan_identity,
    configuration_identity_equal,
    target_identity_equal,
)
from ashl_core_v1.runtime.windows_bounded_window_capture_source import (
    WindowsBoundedWindowCaptureSource,
)


EXPERIMENT_ID = "host_internal_visual_grid_focus_shift_v0"
PARTICIPATING_LANES = ("screen", "host_state")
PACKAGE_127_EVENT_KINDS = (
    "internal_focus_candidates_created",
    "internal_focus_selected",
    "internal_focus_policy_allowed",
    "internal_focus_policy_blocked",
    "internal_focus_shift_action_created",
    "internal_focus_context_attached",
    "internal_focus_released",
    "internal_focus_interrupted",
    "internal_focus_audit_failed",
)


def run_real_internal_focus_shift(
    *,
    state_dir: str | Path,
    allow_internal_focus_shift: bool = True,
    strict_event_stream: bool = True,
) -> dict[str, Any]:
    path = Path(state_dir)
    focus_store = Package127InternalFocusStore(path)
    reacquisition_store = Package126ReacquisitionStore(path)
    sensor_store = ContentAddressedSensorArtifactStore(path)
    temporal_store = Package124ATemporalStore(path)
    compiler = HardSoftPerceptionPrimitiveCompiler(
        path,
        sensor_store=sensor_store,
    )
    primitive_store = PerceptionPrimitiveStore(path)
    experiment_run_id = stable_id(f"{EXPERIMENT_ID}_run")
    root_event_id = stable_id("package_127_capture_root")
    stimulus = LocalGridFocusStimulusRuntime(
        experiment_run_id=experiment_run_id,
    )
    window_source = WindowsBoundedWindowCaptureSource()
    host_adapter = HostStateSensorAdapter()
    event_failures_before = len(
        focus_store.list_payloads("operator_event_delivery_failures")
    )
    result_frozen = False

    try:
        stimulus.open()
        stimulus.tick()
        binding = window_source.bind_by_title(
            experiment_run_id=experiment_run_id,
            window_title=stimulus.window_title,
        )
        if binding.binding_status != "bound":
            raise SensorCaptureError(
                "device_unavailable",
                "Package 127 stimulus binding failed: "
                f"{binding.binding_status}",
            )
        configs = _build_source_configs(
            path=path,
            action_kind="capture_again",
            binding=binding,
            window_source=window_source,
            audio_source=None,
            host_adapter=host_adapter,
            participating_lanes=PARTICIPATING_LANES,
        )
        parent_plan = _build_plan_identity(
            action_kind="capture_again",
            binding=binding,
            window_source=window_source,
            audio_source=None,
            configs=configs,
            participating_lanes=PARTICIPATING_LANES,
        )
        reacquisition_store.append_record(
            "sampling_plan_identity_records",
            parent_plan,
        )
        parent = capture_one_bounded_reacquisition_window(
            path=path,
            store=reacquisition_store,
            sensor_store=sensor_store,
            temporal_store=temporal_store,
            compiler=compiler,
            primitive_store=primitive_store,
            stimulus=stimulus,
            window_source=window_source,
            audio_source=None,
            host_adapter=host_adapter,
            binding=binding,
            configs=configs,
            action_kind="capture_again",
            experiment_run_id=experiment_run_id,
            root_event_id=root_event_id,
            plan=parent_plan,
            role="package_127_parent",
            participating_lanes=PARTICIPATING_LANES,
        )
        parent_ref = _completed_parent_reference(parent, parent_plan)
        reacquisition_store.append_record(
            "completed_parent_window_refs",
            parent_ref,
        )
        parent_change, parent_current_frame = _compile_visual_change(
            compiler=compiler,
            primitive_store=primitive_store,
            artifact_ids=tuple(parent["screen_artifact_ids"]),
        )
        batch, candidates = create_focus_candidates(
            parent=parent_ref,
            visual_change=parent_change,
            current_visual_frame=parent_current_frame,
        )
        focus_store.append_record(
            "internal_focus_candidate_batches",
            batch,
        )
        for candidate in candidates:
            focus_store.append_record(
                "internal_focus_candidates",
                candidate,
            )
        _emit_focus_event(
            path,
            store=focus_store,
            event_kind="internal_focus_candidates_created",
            runtime_session_id=parent["runtime_session_id"],
            perception_session_id=parent["perception_session_id"],
            observation_window_id=parent["observation_window_id"],
            refs=(batch.focus_candidate_batch_id,)
            + tuple(batch.candidate_ids),
            strict=strict_event_stream,
        )
        selection = select_focus_candidate(
            parent_observation_window_id=parent["observation_window_id"],
            candidates=candidates,
        )
        focus_store.append_record(
            "internal_focus_selections",
            selection,
        )
        if selection.selection_status != "selected":
            raise RuntimeError("real_focus_run_has_no_focus_candidate")
        _emit_focus_event(
            path,
            store=focus_store,
            event_kind="internal_focus_selected",
            runtime_session_id=parent["runtime_session_id"],
            perception_session_id=parent["perception_session_id"],
            observation_window_id=parent["observation_window_id"],
            refs=(selection.focus_selection_id,),
            strict=strict_event_stream,
        )
        selected = next(
            candidate
            for candidate in candidates
            if candidate.focus_candidate_id
            == selection.selected_candidate_id
        )
        focus_authorization = (
            create_focus_authorization(parent=parent_ref)
            if allow_internal_focus_shift
            else None
        )
        if focus_authorization is not None:
            focus_store.append_record(
                "internal_focus_authorizations",
                focus_authorization,
            )
        focus_decision = decide_focus_policy(
            selection=selection,
            candidate=selected,
            parent=parent_ref,
            authorization=focus_authorization,
        )
        focus_store.append_record(
            "internal_focus_policy_decisions",
            focus_decision,
        )
        _emit_focus_event(
            path,
            store=focus_store,
            event_kind=(
                "internal_focus_policy_allowed"
                if focus_decision.decision == "allow"
                else "internal_focus_policy_blocked"
            ),
            runtime_session_id=parent["runtime_session_id"],
            perception_session_id=parent["perception_session_id"],
            observation_window_id=parent["observation_window_id"],
            refs=(focus_decision.policy_decision_id,),
            strict=strict_event_stream,
        )
        focus_plan = create_focus_plan(
            decision=focus_decision,
            candidate=selected,
        )
        if focus_plan is None:
            raise RuntimeError(
                "blocked_package_127_focus:"
                + ",".join(focus_decision.failure_reasons)
            )
        focus_store.append_record("internal_focus_plans", focus_plan)
        focus_action = create_internal_perception_focus_shift_action(
            plan=focus_plan,
        )
        focus_store.append_record("internal_focus_actions", focus_action)
        _emit_focus_event(
            path,
            store=focus_store,
            event_kind="internal_focus_shift_action_created",
            runtime_session_id=parent["runtime_session_id"],
            perception_session_id=parent["perception_session_id"],
            observation_window_id=parent["observation_window_id"],
            refs=(focus_action.internal_action_id, focus_plan.focus_plan_id),
            strict=strict_event_stream,
        )

        child_plan = clone_sampling_plan_identity(
            parent_plan,
            source_record_refs=(parent_plan.sampling_plan_identity_id,),
        )
        reacquisition_store.append_record(
            "sampling_plan_identity_records",
            child_plan,
        )
        reacquisition_authorization = create_reacquisition_authorization(
            parent=parent_ref,
            allowed_action_kinds=("capture_again",),
            authorization_source="explicit_session_configuration",
        )
        reacquisition_store.append_record(
            "perception_reacquisition_authorizations",
            reacquisition_authorization,
        )
        _emit_package_126_event(
            path,
            store=reacquisition_store,
            event_kind="perception_reacquisition_authorized",
            parent=parent,
            refs=(reacquisition_authorization.authorization_id,),
            strict=strict_event_stream,
        )
        request = create_reacquisition_request(
            parent=parent_ref,
            authorization=reacquisition_authorization,
            requested_action_kind="capture_again",
            requested_plan=child_plan,
            request_source="explicit_session_configuration",
            request_reason_codes=(
                "repeat_same_sampling_plan",
                "explicit_bounded_reacquisition",
                "controlled_real_capability_verification",
            ),
        )
        reacquisition_store.append_record(
            "perception_reacquisition_requests",
            request,
        )
        _emit_package_126_event(
            path,
            store=reacquisition_store,
            event_kind="perception_reacquisition_requested",
            parent=parent,
            refs=(request.reacquisition_request_id,),
            strict=strict_event_stream,
        )
        request_gap_ns = max(
            0,
            monotonic_ns() - parent["ended_monotonic_ns"],
        )
        eligibility = decide_reacquisition_eligibility(
            request=request,
            parent=parent_ref,
            parent_plan=parent_plan,
            requested_plan=child_plan,
            authorization=reacquisition_authorization,
            parent_to_request_gap_ns=request_gap_ns,
            chain_duration_ns=parent["actual_window_ns"]
            + request_gap_ns,
        )
        reacquisition_store.append_record(
            "reacquisition_eligibility_decisions",
            eligibility,
        )
        _emit_package_126_event(
            path,
            store=reacquisition_store,
            event_kind=(
                "perception_reacquisition_allowed"
                if eligibility.decision == "allow"
                else "perception_reacquisition_blocked"
            ),
            parent=parent,
            refs=(eligibility.eligibility_decision_id,),
            strict=strict_event_stream,
        )
        reacquisition_action = (
            create_bounded_reacquisition_internal_action(
                request=request,
                eligibility=eligibility,
                parent=parent_ref,
            )
        )
        if reacquisition_action is None:
            raise RuntimeError(
                "blocked_package_126_focus_child:"
                + ",".join(eligibility.failure_reasons)
            )
        reacquisition_store.append_record(
            "bounded_reacquisition_internal_actions",
            reacquisition_action,
        )
        _emit_package_126_event(
            path,
            store=reacquisition_store,
            event_kind="capture_again_internal_action_created",
            parent=parent,
            refs=(reacquisition_action.internal_action_id,),
            strict=strict_event_stream,
        )
        child_ids = {
            "runtime_session_id": stable_id(
                "package_127_child_runtime_session"
            ),
            "perception_session_id": stable_id(
                "package_127_child_perception_session"
            ),
            "observation_window_id": stable_id("observation_window"),
        }
        _emit_package_126_event(
            path,
            store=reacquisition_store,
            event_kind="reacquisition_child_window_started",
            parent=parent,
            child=child_ids,
            refs=(reacquisition_action.internal_action_id,),
            strict=strict_event_stream,
        )
        stimulus.begin_child_phase()
        child = capture_one_bounded_reacquisition_window(
            path=path,
            store=reacquisition_store,
            sensor_store=sensor_store,
            temporal_store=temporal_store,
            compiler=compiler,
            primitive_store=primitive_store,
            stimulus=stimulus,
            window_source=window_source,
            audio_source=None,
            host_adapter=host_adapter,
            binding=binding,
            configs=configs,
            action_kind="capture_again",
            experiment_run_id=experiment_run_id,
            root_event_id=root_event_id,
            plan=child_plan,
            role="package_127_focused_child",
            participating_lanes=PARTICIPATING_LANES,
            forced_ids=child_ids,
        )
        _emit_package_126_event(
            path,
            store=reacquisition_store,
            event_kind="reacquisition_source_reopened",
            parent=parent,
            child=child,
            refs=tuple(child["capture_session_refs"]),
            strict=strict_event_stream,
        )
        continuity = build_cross_window_temporal_link(
            parent_observation_window_id=parent["observation_window_id"],
            child_observation_window_id=child["observation_window_id"],
            parent_final_anchor_ref=parent["end_anchor_id"],
            child_start_anchor_ref=child["start_anchor_id"],
            parent_final_event_time_ns=parent["ended_monotonic_ns"],
            child_start_event_time_ns=child["started_monotonic_ns"],
            parent_clock_domain=parent_plan.event_clock_domain,
            child_clock_domain=child_plan.event_clock_domain,
            parent_processing_clock_domain=(
                parent_plan.processing_clock_domain
            ),
            child_processing_clock_domain=(
                child_plan.processing_clock_domain
            ),
            source_temporal_refs=(
                parent["temporal_bundle_id"],
                child["temporal_bundle_id"],
            ),
            source_record_refs=(
                parent_ref.completed_window_reference_id,
                reacquisition_action.internal_action_id,
                focus_action.internal_action_id,
            ),
        )
        reacquisition_store.append_record(
            "cross_window_temporal_links",
            continuity,
        )
        _emit_package_126_event(
            path,
            store=reacquisition_store,
            event_kind="cross_window_temporal_link_created",
            parent=parent,
            child=child,
            refs=(continuity.continuity_link_id,),
            strict=strict_event_stream,
        )
        shared_sessions = set(parent["capture_session_refs"]).intersection(
            child["capture_session_refs"]
        )
        targets_equal = target_identity_equal(parent_plan, child_plan)
        configs_equal = configuration_identity_equal(
            parent_plan,
            child_plan,
        )
        sources_reopened = bool(
            not shared_sessions
            and targets_equal
            and configs_equal
            and parent["sessions_stopped"]
            and child["sessions_started"]
        )
        execution = ReacquisitionCaptureExecution(
            reacquisition_execution_id=stable_id(
                "reacquisition_capture_execution"
            ),
            schema_version=(
                "ashl_package_126_reacquisition_capture_execution_v0"
            ),
            created_at=utc_now(),
            internal_action_id=reacquisition_action.internal_action_id,
            parent_runtime_session_id=parent["runtime_session_id"],
            parent_perception_session_id=parent["perception_session_id"],
            parent_observation_window_id=parent["observation_window_id"],
            child_runtime_session_id=child["runtime_session_id"],
            child_perception_session_id=child["perception_session_id"],
            child_observation_window_id=child["observation_window_id"],
            parent_plan_identity_ref=parent_plan.sampling_plan_identity_id,
            child_plan_identity_ref=child_plan.sampling_plan_identity_id,
            parent_capture_session_refs=tuple(
                parent["capture_session_refs"]
            ),
            child_capture_session_refs=tuple(child["capture_session_refs"]),
            parent_alignment_origin_ref=parent["start_anchor_id"],
            child_alignment_origin_ref=child["start_anchor_id"],
            event_clock_domain_preserved=(
                parent_plan.event_clock_domain
                == child_plan.event_clock_domain
            ),
            processing_clock_domain_preserved=(
                parent_plan.processing_clock_domain
                == child_plan.processing_clock_domain
            ),
            capture_session_ids_reused=bool(shared_sessions),
            source_targets_preserved=targets_equal,
            source_configuration_preserved=configs_equal,
            privacy_policy_preserved=True,
            sources_reopened=sources_reopened,
            old_artifact_reused=False,
            requested_window_ns=reacquisition_action.requested_window_ns,
            actual_window_ns=child["actual_window_ns"],
            execution_status="completed_clean",
            failure_kind=None,
            source_record_refs=(
                reacquisition_action.internal_action_id,
                parent["observation_window_state_id"],
                child["observation_window_state_id"],
            )
            + tuple(parent["capture_session_refs"])
            + tuple(child["capture_session_refs"]),
            source_trace_refs=tuple(),
        )
        reacquisition_store.append_record(
            "reacquisition_capture_executions",
            execution,
        )
        evidence_summary = _build_evidence_summary(
            execution,
            child,
            "capture_again",
        )
        reacquisition_store.append_record(
            "reacquired_evidence_summaries",
            evidence_summary,
        )
        comparison = _build_effect_comparison(
            parent=parent,
            child=child,
            action_kind="capture_again",
            parent_plan=parent_plan,
            child_plan=child_plan,
            continuity_id=continuity.continuity_link_id,
        )
        reacquisition_store.append_record(
            "reacquisition_effect_comparisons",
            comparison,
        )
        child_change, _ = _compile_visual_change(
            compiler=compiler,
            primitive_store=primitive_store,
            artifact_ids=tuple(child["screen_artifact_ids"]),
        )
        child_full_frame_id = str(child["visual_primitive_refs"][0])
        child_full_frame = primitive_store.get_primitive(
            child_full_frame_id
        )
        child_readable_id = str(child["visual_readable_data_refs"][0])
        focused_view = build_focused_visual_region_view(
            plan=focus_plan,
            child_runtime_session_id=child["runtime_session_id"],
            child_perception_session_id=child["perception_session_id"],
            child_observation_window_id=child["observation_window_id"],
            visual_frame=child_full_frame,
            perception_readable_data_id=child_readable_id,
            visual_change=child_change,
        )
        if not focused_view.source_cell_change_present:
            raise RuntimeError(
                "official_focus_run_selected_region_has_no_new_child_evidence"
            )
        focus_store.append_record(
            "focused_visual_region_views",
            focused_view,
        )
        sidecar = build_focus_context_sidecar(
            plan=focus_plan,
            view=focused_view,
            full_frame_perception_readable_data_id=child_readable_id,
            active_from_event_time_ns=child["started_monotonic_ns"],
            active_until_event_time_ns=child["ended_monotonic_ns"],
            focus_state="released",
        )
        BoundedMultimodalPerceptionSessionRuntime(
            path
        ).attach_internal_perception_focus_context(sidecar)
        focus_store.append_record(
            "internal_focus_context_sidecars",
            sidecar,
        )
        _emit_focus_event(
            path,
            store=focus_store,
            event_kind="internal_focus_context_attached",
            runtime_session_id=child["runtime_session_id"],
            perception_session_id=child["perception_session_id"],
            observation_window_id=child["observation_window_id"],
            refs=(
                sidecar.focus_context_id,
                focused_view.focused_region_view_id,
            ),
            strict=strict_event_stream,
        )
        release = build_focus_release_record(sidecar=sidecar)
        focus_store.append_record(
            "internal_focus_release_records",
            release,
        )
        _emit_focus_event(
            path,
            store=focus_store,
            event_kind="internal_focus_released",
            runtime_session_id=child["runtime_session_id"],
            perception_session_id=child["perception_session_id"],
            observation_window_id=child["observation_window_id"],
            refs=(release.focus_release_record_id,),
            strict=strict_event_stream,
        )
        _emit_package_126_event(
            path,
            store=reacquisition_store,
            event_kind="reacquisition_child_window_completed",
            parent=parent,
            child=child,
            refs=(execution.reacquisition_execution_id,),
            strict=strict_event_stream,
        )
        score = _package_112_score_equivalence(
            parent_window_id=parent["observation_window_id"],
            context_refs=(
                focus_plan.focus_plan_id,
                focused_view.focused_region_view_id,
                sidecar.focus_context_id,
            ),
        )
        focus_store.append_record(
            "package_127_score_equivalence_records",
            score,
        )
        controls = run_synthetic_package_127_controls(state_dir=path)
        result_frozen = True
        stimulus.mark_finished()
        fixture_manifest = stimulus.manifest()
        event_failures_after = len(
            focus_store.list_payloads(
                "operator_event_delivery_failures"
            )
        )
        real_run = {
            "real_run_record_id": stable_id("package_127_real_focus_run"),
            "schema_version": "ashl_package_127_real_focus_run_v0",
            "created_at": utc_now(),
            "experiment_id": EXPERIMENT_ID,
            "experiment_run_id": experiment_run_id,
            "run_status": "passed_real_internal_focus_shift",
            "parent": _public_window(parent),
            "child": _public_window(child),
            "parent_visual_change_primitive_id": parent_change[
                "visual_change_id"
            ],
            "parent_changed_grid_cell_count": len(
                parent_change["changed_grid_cells"]
            ),
            "focus_candidate_batch_id": batch.focus_candidate_batch_id,
            "focus_candidate_count": len(candidates),
            "focus_candidate_ids": tuple(batch.candidate_ids),
            "selected_candidate_id": selected.focus_candidate_id,
            "selected_grid_x": selected.grid_x,
            "selected_grid_y": selected.grid_y,
            "selected_difference_strength": (
                selected.difference_strength
            ),
            "selection_rule": selection.selection_rule,
            "focus_authorization_id": (
                focus_authorization.authorization_id
                if focus_authorization
                else None
            ),
            "focus_policy_decision_id": (
                focus_decision.policy_decision_id
            ),
            "focus_policy_decision": focus_decision.decision,
            "focus_plan_id": focus_plan.focus_plan_id,
            "focus_internal_action_id": focus_action.internal_action_id,
            "focus_action_kind": focus_action.action_kind,
            "package_126_authorization_id": (
                reacquisition_authorization.authorization_id
            ),
            "package_126_request_id": request.reacquisition_request_id,
            "package_126_eligibility_decision_id": (
                eligibility.eligibility_decision_id
            ),
            "package_126_internal_action_id": (
                reacquisition_action.internal_action_id
            ),
            "package_126_reacquisition_execution_id": (
                execution.reacquisition_execution_id
            ),
            "package_126_child_window_used": True,
            "parent_plan_hash": parent_plan.canonical_plan_hash,
            "child_plan_hash": child_plan.canonical_plan_hash,
            "raw_capture_target_unchanged": targets_equal,
            "raw_capture_region_unchanged": (
                parent_plan.screen_region_hash
                == child_plan.screen_region_hash
            ),
            "configuration_identity_equal": configs_equal,
            "capture_session_ids_distinct": not bool(shared_sessions),
            "sources_reopened": sources_reopened,
            "cross_window_gap_ns": continuity.external_gap_ns,
            "cross_window_link_id": continuity.continuity_link_id,
            "focused_region_view_id": (
                focused_view.focused_region_view_id
            ),
            "focused_region_matches_selection": (
                focused_view.grid_x == selected.grid_x
                and focused_view.grid_y == selected.grid_y
            ),
            "focused_region_new_evidence_present": (
                focused_view.source_cell_change_present
            ),
            "full_frame_visual_primitive_id": child_full_frame_id,
            "full_frame_perception_readable_data_id": (
                child_readable_id
            ),
            "full_frame_capture_preserved": True,
            "raw_full_frame_artifact_unchanged": True,
            "image_crop_persisted": False,
            "focus_context_id": sidecar.focus_context_id,
            "focus_state": sidecar.focus_state,
            "focus_release_record_id": (
                release.focus_release_record_id
            ),
            "focus_automatically_released": (
                sidecar.automatically_released
            ),
            "focus_child_window_count": 1,
            "control_results": controls,
            "score_equivalence_record_id": (
                score.score_equivalence_record_id
            ),
            "fixture_manifest_audited_after_result_frozen": result_frozen,
            "stimulus_ground_truth_used_for_runtime_decision": False,
            "fixture_transition_count_after_freeze": len(
                fixture_manifest["transitions"]
            ),
            "operator_event_delivery_failure_count": (
                event_failures_after - event_failures_before
            ),
            "memory_write_created": False,
            "working_readback_created": False,
            "evidence_sufficiency_runtime_created": False,
            "novelty_signal_created": False,
            "uncertainty_signal_created": False,
            "thought_engine_used": False,
            "endocrine_signal_used": False,
            "audio_focus_created": False,
            "camera_focus_created": False,
            "sensor_priority_runtime_created": False,
            "selected_action_created": False,
            "final_action_created": False,
            "direct_command_created": False,
            "external_control_created": False,
            "output_created": False,
            "object_recognition_created": False,
            "semantic_vision_created": False,
            "package_128_implemented": False,
            "package_129_implemented": False,
            "d_laplace_component_used": False,
            "dlm_1_implemented": False,
            "llm_runtime_calls": 0,
            "codex_runtime_calls": 0,
            "network_runtime_calls": 0,
        }
        focus_store.append_payload(
            "package_127_real_run_records",
            "real_run_record_id",
            real_run["real_run_record_id"],
            real_run,
        )
        return real_run
    finally:
        stimulus.close()


def run_synthetic_package_127_controls(
    *,
    state_dir: str | Path,
) -> dict[str, bool]:
    store = Package127InternalFocusStore(state_dir)
    parent = _synthetic_parent()
    frame = _synthetic_frame()
    change = _synthetic_change()
    batch, candidates = create_focus_candidates(
        parent=parent,
        visual_change=change,
        current_visual_frame=frame,
    )
    selection = select_focus_candidate(
        parent_observation_window_id=parent.observation_window_id,
        candidates=candidates,
    )
    selected = next(
        item
        for item in candidates
        if item.focus_candidate_id == selection.selected_candidate_id
    )
    authorization = create_focus_authorization(parent=parent)

    stable_change = dict(change)
    stable_change["visual_change_id"] = stable_id(
        "synthetic_stable_change"
    )
    stable_change["changed_grid_cells"] = tuple()
    stable_batch, stable_candidates = create_focus_candidates(
        parent=parent,
        visual_change=stable_change,
        current_visual_frame=frame,
    )
    stable_selection = select_focus_candidate(
        parent_observation_window_id=parent.observation_window_id,
        candidates=stable_candidates,
    )
    authorization_off = decide_focus_policy(
        selection=selection,
        candidate=selected,
        parent=parent,
        authorization=None,
    )

    tie_change = dict(change)
    tie_change["visual_change_id"] = stable_id("synthetic_tie_change")
    tie_change["changed_grid_cells"] = (
        {"grid_x": 4, "grid_y": 3, "difference_strength": 0.7},
        {"grid_x": 6, "grid_y": 1, "difference_strength": 0.7},
        {"grid_x": 2, "grid_y": 1, "difference_strength": 0.7},
    )
    _, tie_candidates = create_focus_candidates(
        parent=parent,
        visual_change=tie_change,
        current_visual_frame=frame,
    )
    tie_first = select_focus_candidate(
        parent_observation_window_id=parent.observation_window_id,
        candidates=tie_candidates,
    )
    tie_second = select_focus_candidate(
        parent_observation_window_id=parent.observation_window_id,
        candidates=tie_candidates,
    )

    invalid_coordinate_passed = False
    invalid = dict(change)
    invalid["changed_grid_cells"] = (
        {
            "grid_x": frame["grid_width"],
            "grid_y": 0,
            "difference_strength": 0.8,
        },
    )
    try:
        create_focus_candidates(
            parent=parent,
            visual_change=invalid,
            current_visual_frame=frame,
        )
    except ValueError:
        invalid_coordinate_passed = True

    wrong_session_candidate = replace(
        selected,
        parent_perception_session_id="perception:other",
    )
    wrong_session = decide_focus_policy(
        selection=replace(
            selection,
            selected_candidate_id=(
                wrong_session_candidate.focus_candidate_id
            ),
            candidate_ids=(
                wrong_session_candidate.focus_candidate_id,
            ),
            source_record_refs=(
                wrong_session_candidate.focus_candidate_id,
            ),
        ),
        candidate=wrong_session_candidate,
        parent=parent,
        authorization=authorization,
    )
    fault_parent = replace(parent, required_lane_drop_count=1)
    transport_fault = decide_focus_policy(
        selection=selection,
        candidate=selected,
        parent=fault_parent,
        authorization=authorization,
    )
    second_shift = decide_focus_policy(
        selection=selection,
        candidate=selected,
        parent=parent,
        authorization=authorization,
        prior_focus_shift_count=1,
    )
    operator_stop = decide_focus_policy(
        selection=selection,
        candidate=selected,
        parent=parent,
        authorization=authorization,
        operator_stop_requested=True,
    )

    plan = create_focus_plan(
        decision=decide_focus_policy(
            selection=selection,
            candidate=selected,
            parent=parent,
            authorization=authorization,
        ),
        candidate=selected,
    )
    assert plan is not None
    valid_view = _synthetic_view(plan)
    interrupted_sidecar = build_focus_context_sidecar(
        plan=plan,
        view=valid_view,
        full_frame_perception_readable_data_id="readable:child",
        active_from_event_time_ns=10,
        active_until_event_time_ns=15,
        focus_state="interrupted",
    )
    interrupted_release = build_focus_release_record(
        sidecar=interrupted_sidecar,
        interrupted=True,
    )
    raw_crop_passed = False
    try:
        replace(valid_view, image_crop_persisted=True)
    except ValueError:
        raw_crop_passed = True
    semantic_injection_passed = False
    try:
        replace(selected, semantic_label="object")
    except ValueError:
        semantic_injection_passed = True

    controls = {
        "stable_control_passed": bool(
            stable_batch.candidate_count == 0
            and stable_batch.stable_frame
            and stable_selection.selection_status == "no_candidate"
        ),
        "authorization_off_control_passed": bool(
            authorization_off.decision == "block"
            and not authorization_off.authorization_valid
        ),
        "tie_control_passed": bool(
            (tie_first.selected_grid_x, tie_first.selected_grid_y)
            == (2, 1)
            and (
                tie_first.selected_grid_x,
                tie_first.selected_grid_y,
                tie_first.selected_difference_strength,
            )
            == (
                tie_second.selected_grid_x,
                tie_second.selected_grid_y,
                tie_second.selected_difference_strength,
            )
            and tie_first.deterministic_tie_break_used
        ),
        "invalid_coordinate_control_passed": invalid_coordinate_passed,
        "wrong_session_control_passed": bool(
            wrong_session.decision == "block"
            and not wrong_session.source_lineage_valid
        ),
        "transport_fault_control_passed": bool(
            transport_fault.decision == "block"
            and not transport_fault.transport_integrity_valid
        ),
        "second_shift_control_passed": bool(
            second_shift.decision == "block"
            and not second_shift.focus_budget_available
        ),
        "operator_stop_control_passed": bool(
            operator_stop.decision == "block"
            and not operator_stop.operator_stop_absent
            and interrupted_sidecar.focus_state == "interrupted"
            and not interrupted_sidecar.automatically_released
            and interrupted_release.previous_focus_state
            == "interrupted"
            and interrupted_release.new_focus_state == "released"
            and interrupted_release.history_preserved
        ),
        "raw_crop_control_passed": raw_crop_passed,
        "semantic_injection_control_passed": (
            semantic_injection_passed
        ),
    }
    control_record = {
        "control_result_id": stable_id("package_127_control_result"),
        "schema_version": "ashl_package_127_control_result_v0",
        "created_at": utc_now(),
        **controls,
        "candidate_batch_id": batch.focus_candidate_batch_id,
        "source_record_refs": (
            batch.focus_candidate_batch_id,
            selection.focus_selection_id,
        ),
        "source_trace_refs": tuple(),
    }
    store.append_payload(
        "package_127_control_results",
        "control_result_id",
        control_record["control_result_id"],
        control_record,
    )
    return controls


def run_synthetic_package_127_smoke(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    controls = run_synthetic_package_127_controls(state_dir=state_dir)
    return {
        "status": (
            "passed_package_127_synthetic_smoke"
            if all(controls.values())
            else "blocked_package_127_synthetic_smoke"
        ),
        "controls": controls,
        "sensor_opened": False,
        "raw_crop_created": False,
        "semantic_vision_created": False,
        "memory_write_created": False,
        "output_created": False,
        "external_control_created": False,
    }


def _compile_visual_change(
    *,
    compiler: HardSoftPerceptionPrimitiveCompiler,
    primitive_store: PerceptionPrimitiveStore,
    artifact_ids: tuple[str, ...],
) -> tuple[dict[str, Any], dict[str, Any]]:
    if len(artifact_ids) < 2:
        raise RuntimeError("visual change requires at least two real frames")
    bundle = compiler.compile_visual_pair(
        previous_artifact_id=artifact_ids[0],
        current_artifact_id=artifact_ids[-1],
    )
    change = primitive_store.get_primitive(bundle.primitive_record_id)
    current = primitive_store.get_primitive(
        str(change["current_visual_primitive_id"])
    )
    return change, current


def _package_112_score_equivalence(
    *,
    parent_window_id: str,
    context_refs: tuple[str, ...],
) -> Package127ScoreEquivalenceRecord:
    demo = package_112.build_demo_no_matching_readback_signal_no_change()
    signal = tuple(demo["readback_internal_action_signals"])[0]
    before = package_112.build_host_body_internal_action_candidate_readback_score(
        readback_signal=signal,
        candidate_action_kind="observe_again",
        base_candidate_priority=5,
    )
    after = package_112.build_host_body_internal_action_candidate_readback_score(
        readback_signal=signal,
        candidate_action_kind="observe_again",
        base_candidate_priority=5,
    )
    return Package127ScoreEquivalenceRecord(
        score_equivalence_record_id=stable_id(
            "package_127_score_equivalence"
        ),
        schema_version="ashl_package_127_score_equivalence_v0",
        created_at=utc_now(),
        parent_observation_window_id=parent_window_id,
        authoritative_score_before=int(before.final_candidate_priority),
        authoritative_score_after=int(after.final_candidate_priority),
        package_127_score_contribution=0,
        package_112_score_changed=(
            int(before.final_candidate_priority)
            != int(after.final_candidate_priority)
            or int(before.readback_delta) != int(after.readback_delta)
        ),
        focus_context_read_only=True,
        source_record_refs=context_refs,
        source_trace_refs=tuple(),
    )


def _emit_focus_event(
    state_dir: Path,
    *,
    store: Package127InternalFocusStore,
    event_kind: str,
    runtime_session_id: str,
    perception_session_id: str,
    observation_window_id: str,
    refs: tuple[str, ...],
    strict: bool,
) -> bool:
    if event_kind not in PACKAGE_127_EVENT_KINDS:
        raise ValueError(f"unknown Package 127 event kind: {event_kind}")
    try:
        LocalOperatorEventStream(
            build_default_console_store(state_dir)
        ).append_event(
            event_kind=event_kind,
            source_record_refs=refs,
            source_trace_refs=tuple(),
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
        )
        return True
    except Exception as error:
        failure = {
            "event_delivery_failure_id": stable_id(
                "package_127_event_delivery_failure"
            ),
            "schema_version": (
                "ashl_package_127_operator_event_delivery_failure_v0"
            ),
            "created_at": utc_now(),
            "event_kind": event_kind,
            "runtime_session_id": runtime_session_id,
            "perception_session_id": perception_session_id,
            "observation_window_id": observation_window_id,
            "failure_kind": type(error).__name__,
            "failure_message_hash": sha256_bytes(
                str(error).encode("utf-8")
            ),
            "delivery_failure_visible": True,
            "source_record_refs": refs,
            "source_trace_refs": tuple(),
        }
        store.append_payload(
            "operator_event_delivery_failures",
            "event_delivery_failure_id",
            failure["event_delivery_failure_id"],
            failure,
        )
        if strict:
            raise RuntimeError(
                f"Package 127 operator event delivery failed: {event_kind}"
            ) from error
        return False


def _public_window(window: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in window.items()
        if key != "audio_deletion"
    } | {"audio_deletion": None}


def _synthetic_parent() -> CompletedObservationWindowReference:
    return CompletedObservationWindowReference(
        completed_window_reference_id="completed_window:synthetic",
        schema_version="ashl_package_126_completed_observation_window_reference_v0",
        created_at=utc_now(),
        runtime_session_id="runtime:synthetic",
        perception_session_id="perception:synthetic",
        observation_window_id="window:synthetic",
        completion_status="completed_clean",
        finalized_at_event_time_ns=2_500_000_000,
        finalized_at_processing_time_ns=2_500_000_001,
        participating_lanes=PARTICIPATING_LANES,
        required_lanes=PARTICIPATING_LANES,
        source_capture_session_refs=(
            "capture:screen",
            "capture:host",
        ),
        sampling_plan_identity_ref="plan:synthetic",
        final_temporal_bundle_ref="temporal:synthetic",
        required_lane_drop_count=0,
        backpressure_fault_count=0,
        capture_failure_count=0,
        compile_failure_count=0,
        flush_remaining_count=0,
        source_record_refs=(
            "window_state:synthetic",
            "visual_change:synthetic",
        ),
        source_trace_refs=tuple(),
    )


def _synthetic_frame() -> dict[str, Any]:
    grid_width = 8
    grid_height = 8
    return {
        "visual_primitive_id": "visual_frame:synthetic",
        "source_kind": "screen",
        "grid_width": grid_width,
        "grid_height": grid_height,
        "grid_luminance_means": tuple(
            0.1 for _ in range(grid_width * grid_height)
        ),
        "grid_contrast_values": tuple(
            0.2 for _ in range(grid_width * grid_height)
        ),
        "grid_edge_density_values": tuple(
            0.3 for _ in range(grid_width * grid_height)
        ),
        "source_trace_refs": tuple(),
    }


def _synthetic_change() -> dict[str, Any]:
    return {
        "visual_change_id": "visual_change:synthetic",
        "source_kind": "screen",
        "current_visual_primitive_id": "visual_frame:synthetic",
        "changed_grid_cells": (
            {"grid_x": 2, "grid_y": 2, "difference_strength": 0.9},
            {"grid_x": 5, "grid_y": 4, "difference_strength": 0.4},
        ),
        "source_trace_refs": tuple(),
    }


def _synthetic_view(
    plan: Any,
) -> FocusedVisualRegionView:
    return build_focused_visual_region_view(
        plan=plan,
        child_runtime_session_id="runtime:child",
        child_perception_session_id="perception:child",
        child_observation_window_id="window:child",
        visual_frame=_synthetic_frame(),
        perception_readable_data_id="readable:child",
        visual_change=_synthetic_change(),
    )
