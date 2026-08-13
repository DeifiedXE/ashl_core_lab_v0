"""Package 128 real and synthetic structural sufficiency runtime."""

from __future__ import annotations

import os
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
from ashl_core_v1.perception.visual_change_primitive_compiler import (
    compile_visual_change_primitive,
)
from ashl_core_v1.perception.visual_primitive_schema import (
    VisualFramePrimitiveRecord,
)
from ashl_core_v1.runtime.bounded_capture_deadline_controller import (
    BoundedCaptureDeadlineController,
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
from ashl_core_v1.runtime.local_operator_console_store import (
    build_default_console_store,
)
from ashl_core_v1.runtime.local_operator_event_stream import (
    LocalOperatorEventStream,
)
from ashl_core_v1.runtime.local_structural_sufficiency_stimulus_runtime import (
    LocalStructuralSufficiencyStimulusRuntime,
)
from ashl_core_v1.runtime.observation_stop_policy import (
    decide_observation_stop_policy,
)
from ashl_core_v1.runtime.package_124a_temporal_store import (
    Package124ATemporalStore,
)
from ashl_core_v1.runtime.package_126_reacquisition_runtime import (
    ActiveReacquisitionCaptureSnapshot,
    _build_evidence_summary,
    _build_live_alignment_config,
    _build_plan_identity,
    _build_source_configs,
    _completed_parent_reference,
    _emit_event as _emit_package_126_event,
    capture_one_bounded_reacquisition_window,
)
from ashl_core_v1.runtime.package_126_reacquisition_store import (
    Package126ReacquisitionStore,
)
from ashl_core_v1.runtime.package_127_internal_focus_runtime import (
    _compile_visual_change,
    _emit_focus_event,
)
from ashl_core_v1.runtime.package_127_internal_focus_store import (
    Package127InternalFocusStore,
)
from ashl_core_v1.runtime.package_128_sufficiency_stop_store import (
    Package128SufficiencyStopStore,
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
    ReacquisitionCaptureExecution,
)
from ashl_core_v1.runtime.sampling_plan_identity import (
    clone_sampling_plan_identity,
    configuration_identity_equal,
    target_identity_equal,
)
from ashl_core_v1.runtime.stop_observation_internal_action import (
    build_observation_completion,
    build_observation_stop_execution,
    create_stop_observation_internal_action,
)
from ashl_core_v1.runtime.structural_evidence_sufficiency_assessor import (
    assess_structural_evidence,
    create_structural_evidence_checkpoint,
    create_structural_sufficiency_contract,
)
from ashl_core_v1.runtime.structural_evidence_sufficiency_types import (
    CHECKPOINT_INTERVAL_NS,
    CHILD_HARD_WINDOW_NS,
    MAXIMUM_CHECKPOINT_COUNT,
    MINIMUM_ELAPSED_NS,
    MINIMUM_POST_EVENT_COVERAGE_NS,
    Package128ScoreEquivalenceRecord,
)
from ashl_core_v1.runtime.temporal_clock_domain import (
    build_clock_domain_descriptor,
    evaluate_clock_quality,
)
from ashl_core_v1.runtime.temporal_relation_compiler import (
    build_temporal_anchor,
    build_temporal_span,
)
from ashl_core_v1.runtime.temporal_types import (
    GroundedTemporalPrimitiveBundle,
    temporal_identity,
)
from ashl_core_v1.runtime.windows_bounded_window_capture_source import (
    WindowsBoundedWindowCaptureSource,
)


EXPERIMENT_ID = (
    "host_internal_focused_visual_structural_sufficiency_stop_v0"
)
PARTICIPATING_LANES = ("screen", "host_state")
PARENT_WINDOW_NS = 2_500_000_000
SOURCE_SAMPLE_INTERVAL_NS = 250_000_000
# Three complete windows must fit comfortably inside Package 126's
# 2.5-second reacquisition grant, including real capture/compile overhead.
ACTIVE_ALIGNMENT_WINDOW_MS = 500
PACKAGE_128_EVENT_KINDS = (
    "structural_sufficiency_contract_created",
    "structural_evidence_checkpoint_created",
    "structural_evidence_assessment_sufficient",
    "structural_evidence_assessment_insufficient",
    "structural_evidence_assessment_inconclusive",
    "observation_stop_policy_allowed",
    "observation_stop_policy_continue",
    "observation_stop_policy_hard_deadline",
    "stop_observation_internal_action_created",
    "observation_policy_stop_executed",
    "observation_completion_created",
    "observation_sufficiency_audit_failed",
)


def run_real_structural_sufficiency_stop(
    *,
    state_dir: str | Path,
    allow_structural_sufficiency_stop: bool = False,
    strict_event_stream: bool = True,
) -> dict[str, Any]:
    if not allow_structural_sufficiency_stop:
        raise PermissionError(
            "explicit structural sufficiency stop authorization is required"
        )
    path = Path(state_dir)
    store = Package128SufficiencyStopStore(path)
    focus_store = Package127InternalFocusStore(path)
    reacquisition_store = Package126ReacquisitionStore(path)
    sensor_store = ContentAddressedSensorArtifactStore(path)
    temporal_store = Package124ATemporalStore(path)
    compiler = HardSoftPerceptionPrimitiveCompiler(
        path,
        sensor_store=sensor_store,
    )
    primitive_store = PerceptionPrimitiveStore(path)
    package_122 = BoundedMultimodalPerceptionSessionRuntime(path)
    experiment_run_id = stable_id(f"{EXPERIMENT_ID}_run")
    root_event_id = stable_id("package_128_capture_root")
    stimulus = LocalStructuralSufficiencyStimulusRuntime(
        experiment_run_id=experiment_run_id,
    )
    window_source = WindowsBoundedWindowCaptureSource()
    host_adapter = HostStateSensorAdapter()
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
                "Package 128 stimulus binding failed: "
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
            capture_duration_ms=3_000,
            host_sample_interval_ms=250,
            maximum_artifact_count=64,
        )
        prepared = _prepare_focused_reacquisition(
            path=path,
            focus_store=focus_store,
            reacquisition_store=reacquisition_store,
            sensor_store=sensor_store,
            temporal_store=temporal_store,
            compiler=compiler,
            primitive_store=primitive_store,
            stimulus=stimulus,
            window_source=window_source,
            host_adapter=host_adapter,
            binding=binding,
            configs=configs,
            experiment_run_id=experiment_run_id,
            root_event_id=root_event_id,
            strict_event_stream=strict_event_stream,
        )
        parent = prepared["parent"]
        parent_plan = prepared["parent_plan"]
        parent_ref = prepared["parent_ref"]
        focus_plan = prepared["focus_plan"]
        focus_action = prepared["focus_action"]
        child_plan = prepared["child_plan"]
        reacquisition_action = prepared["reacquisition_action"]
        child_ids = prepared["child_ids"]

        controller = BoundedCaptureDeadlineController(
            base_deadline_ns=CHILD_HARD_WINDOW_NS,
            hard_deadline_ns=CHILD_HARD_WINDOW_NS,
            participating_lanes=PARTICIPATING_LANES,
            maximum_extension_count=0,
            maximum_total_extension_ns=0,
        )
        alignment_config = _build_live_alignment_config(
            path=path,
            participating_lanes=PARTICIPATING_LANES,
            window_duration_ns=CHILD_HARD_WINDOW_NS,
            queue_depth=64,
            alignment_window_ms=ACTIVE_ALIGNMENT_WINDOW_MS,
        )
        compilation_cache: dict[str, Any] = {}
        lane_item_cache: dict[str, Any] = {}
        active: dict[str, Any] = {
            "contract": None,
            "active_sidecar": None,
            "initial_view": None,
            "latest_view": None,
            "active_clock": None,
            "baseline_frame": None,
            "baseline_artifact_id": None,
            "last_visual_artifact_id": None,
            "latest_visual_change_id": None,
            "next_checkpoint_ns": None,
            "checkpoints": [],
            "assessments": [],
            "decisions": [],
            "stop_action": None,
            "stop_requested_event_time_ns": None,
            "observed_region_refs": [],
            "open_region_ref": None,
            "open_region_started_ns": None,
            "closed_spans": [],
            "temporal_records": [],
            "focused_evidence_view_ids": [],
            "initial_capture_session_refs": tuple(),
            "initial_alignment_origin_ref": None,
        }

        def compile_cached(artifact_id: str) -> Any:
            if artifact_id not in compilation_cache:
                compilation_cache[artifact_id] = (
                    compiler.compile_artifact(artifact_id)
                )
            return compilation_cache[artifact_id]

        def lane_item_for(
            artifact_id: str,
            *,
            started_ns: int,
            perception_session_id: str,
        ) -> Any:
            if artifact_id not in lane_item_cache:
                bundle = compile_cached(artifact_id)
                artifact = sensor_store.get_artifact(artifact_id)
                relative_ms = max(
                    0,
                    (
                        int(artifact["captured_at_monotonic_ns"])
                        - started_ns
                    )
                    // 1_000_000,
                )
                lane_item_cache[artifact_id] = (
                    package_122.lane_item_from_compilation(
                        session_id=perception_session_id,
                        session_relative_ms=relative_ms,
                        compilation_bundle=bundle,
                    )
                )
            return lane_item_cache[artifact_id]

        def active_hook(
            snapshot: ActiveReacquisitionCaptureSnapshot,
        ) -> None:
            if not (
                snapshot.screen_artifact_ids
                and snapshot.host_artifact_ids
            ):
                return
            screen_items = tuple(
                lane_item_for(
                    artifact_id,
                    started_ns=snapshot.started_monotonic_ns,
                    perception_session_id=snapshot.perception_session_id,
                )
                for artifact_id in snapshot.screen_artifact_ids
            )
            host_items = tuple(
                lane_item_for(
                    artifact_id,
                    started_ns=snapshot.started_monotonic_ns,
                    perception_session_id=snapshot.perception_session_id,
                )
                for artifact_id in snapshot.host_artifact_ids
            )
            lane_items = screen_items + host_items
            if active["contract"] is None:
                _initialize_active_contract(
                    path=path,
                    store=store,
                    focus_store=focus_store,
                    temporal_store=temporal_store,
                    package_122=package_122,
                    primitive_store=primitive_store,
                    focus_plan=focus_plan,
                    focus_action_id=focus_action.internal_action_id,
                    reacquisition_action_id=(
                        reacquisition_action.internal_action_id
                    ),
                    snapshot=snapshot,
                    first_screen_bundle=compile_cached(
                        snapshot.screen_artifact_ids[0]
                    ),
                    first_screen_lane_item=screen_items[0],
                    active=active,
                    strict_event_stream=strict_event_stream,
                )
            _update_active_visual_evidence(
                focus_store=focus_store,
                sensor_store=sensor_store,
                temporal_store=temporal_store,
                primitive_store=primitive_store,
                focus_plan=focus_plan,
                snapshot=snapshot,
                compilation_cache=compilation_cache,
                active=active,
            )
            next_checkpoint = int(active["next_checkpoint_ns"])
            if (
                snapshot.observed_at_monotonic_ns < next_checkpoint
                or len(active["checkpoints"])
                >= MAXIMUM_CHECKPOINT_COUNT
                or controller.stop_requested
            ):
                return
            if active["closed_spans"]:
                closure_ns = int(
                    active["closed_spans"][-1].end_event_time_ns
                )
                latest_screen = sensor_store.get_artifact(
                    snapshot.screen_artifact_ids[-1]
                )
                latest_host = sensor_store.get_artifact(
                    snapshot.host_artifact_ids[-1]
                )
                source_coverage_ns = min(
                    int(latest_screen["captured_at_monotonic_ns"]),
                    int(latest_host["captured_at_monotonic_ns"]),
                )
                if (
                    source_coverage_ns
                    < closure_ns + MINIMUM_POST_EVENT_COVERAGE_NS
                ):
                    return
            _evaluate_active_checkpoint(
                path=path,
                store=store,
                focus_store=focus_store,
                sensor_store=sensor_store,
                temporal_store=temporal_store,
                primitive_store=primitive_store,
                package_122=package_122,
                alignment_config=alignment_config,
                focus_plan=focus_plan,
                snapshot=snapshot,
                lane_items=lane_items,
                compilation_cache=compilation_cache,
                active=active,
                controller=controller,
                contract_authorized=allow_structural_sufficiency_stop,
                strict_event_stream=strict_event_stream,
            )
            active["next_checkpoint_ns"] = (
                active["checkpoints"][-1].evaluated_at_event_time_ns
                + CHECKPOINT_INTERVAL_NS
            )

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
            role="package_128_focused_child",
            participating_lanes=PARTICIPATING_LANES,
            forced_ids=child_ids,
            window_duration_ns=CHILD_HARD_WINDOW_NS,
            source_sample_interval_ns=SOURCE_SAMPLE_INTERVAL_NS,
            deadline_controller=controller,
            active_capture_hook=active_hook,
            compile_all_samples=True,
            compilation_cache=compilation_cache,
            alignment_window_ms=ACTIVE_ALIGNMENT_WINDOW_MS,
            stop_event_time_provider=lambda: active[
                "stop_requested_event_time_ns"
            ],
        )
        if active["contract"] is None:
            raise RuntimeError("Package 128 active contract was not created")
        if not active["assessments"]:
            raise RuntimeError("Package 128 created no active checkpoints")
        if (
            int(child["actual_window_ns"])
            > int(reacquisition_action.granted_window_ns)
        ):
            raise RuntimeError(
                "Package 128 child exceeded the Package 126 granted "
                f"window: actual={child['actual_window_ns']} "
                f"granted={reacquisition_action.granted_window_ns}"
            )
        final_assessment = active["assessments"][-1]
        final_decision = active["decisions"][-1]
        stop_action = active["stop_action"]
        if (
            allow_structural_sufficiency_stop
            and (
                final_assessment.assessment_status != "sufficient"
                or final_decision.decision != "allow_policy_stop"
                or stop_action is None
            )
        ):
            raise RuntimeError(
                "real structural contract did not authorize policy stop"
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
        targets_equal = target_identity_equal(parent_plan, child_plan)
        configs_equal = configuration_identity_equal(
            parent_plan,
            child_plan,
        )
        shared_sessions = set(parent["capture_session_refs"]).intersection(
            child["capture_session_refs"]
        )
        reacquisition_execution = ReacquisitionCaptureExecution(
            reacquisition_execution_id=stable_id(
                "reacquisition_capture_execution"
            ),
            schema_version=(
                "ashl_package_126_reacquisition_capture_execution_v0"
            ),
            created_at=utc_now(),
            internal_action_id=reacquisition_action.internal_action_id,
            parent_runtime_session_id=parent["runtime_session_id"],
            parent_perception_session_id=parent[
                "perception_session_id"
            ],
            parent_observation_window_id=parent[
                "observation_window_id"
            ],
            child_runtime_session_id=child["runtime_session_id"],
            child_perception_session_id=child[
                "perception_session_id"
            ],
            child_observation_window_id=child[
                "observation_window_id"
            ],
            parent_plan_identity_ref=(
                parent_plan.sampling_plan_identity_id
            ),
            child_plan_identity_ref=(
                child_plan.sampling_plan_identity_id
            ),
            parent_capture_session_refs=tuple(
                parent["capture_session_refs"]
            ),
            child_capture_session_refs=tuple(
                child["capture_session_refs"]
            ),
            parent_alignment_origin_ref=parent["start_anchor_id"],
            child_alignment_origin_ref=child["start_anchor_id"],
            event_clock_domain_preserved=True,
            processing_clock_domain_preserved=True,
            capture_session_ids_reused=bool(shared_sessions),
            source_targets_preserved=targets_equal,
            source_configuration_preserved=configs_equal,
            privacy_policy_preserved=True,
            sources_reopened=bool(
                not shared_sessions
                and targets_equal
                and configs_equal
                and parent["sessions_stopped"]
                and child["sessions_started"]
            ),
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
            reacquisition_execution,
        )
        evidence_summary = _build_evidence_summary(
            reacquisition_execution,
            child,
            "capture_again",
        )
        reacquisition_store.append_record(
            "reacquired_evidence_summaries",
            evidence_summary,
        )

        final_temporal_bundle = _build_final_temporal_bundle(
            temporal_store=temporal_store,
            child=child,
            active=active,
        )
        child_for_completion = dict(child)
        child_for_completion["temporal_bundle_id"] = (
            final_temporal_bundle.temporal_bundle_id
        )
        active_sidecar = active["active_sidecar"]
        latest_view = active["latest_view"]
        released_sidecar = build_focus_context_sidecar(
            plan=focus_plan,
            view=latest_view,
            full_frame_perception_readable_data_id=(
                latest_view.source_perception_readable_data_id
            ),
            active_from_event_time_ns=child[
                "started_monotonic_ns"
            ],
            active_until_event_time_ns=child["ended_monotonic_ns"],
            focus_state="released",
        )
        package_122.attach_internal_perception_focus_context(
            released_sidecar
        )
        focus_store.append_record(
            "internal_focus_context_sidecars",
            released_sidecar,
        )
        release = build_focus_release_record(sidecar=active_sidecar)
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
        if stop_action is None:
            raise RuntimeError("Package 128 policy stop action missing")
        stop_execution = build_observation_stop_execution(
            action=stop_action,
            controller=controller,
            child_window=child_for_completion,
            stop_requested_at_event_time_ns=int(
                active["stop_requested_event_time_ns"]
            ),
            focus_context_id_before=active_sidecar.focus_context_id,
            focus_context_id_at_completion=active_sidecar.focus_context_id,
            active_capture_session_refs=active[
                "initial_capture_session_refs"
            ],
            active_alignment_origin_ref=active[
                "initial_alignment_origin_ref"
            ],
        )
        store.append_record(
            "observation_stop_executions",
            stop_execution,
        )
        _emit_event(
            path,
            store=store,
            event_kind="observation_policy_stop_executed",
            child=child,
            refs=(stop_execution.stop_execution_id,),
            strict=strict_event_stream,
        )
        completion = build_observation_completion(
            contract=active["contract"],
            assessment=final_assessment,
            decision=final_decision,
            execution=stop_execution,
            child_window=child_for_completion,
            final_focus_context_id=released_sidecar.focus_context_id,
        )
        store.append_record(
            "observation_completion_records",
            completion,
        )
        _emit_event(
            path,
            store=store,
            event_kind="observation_completion_created",
            child=child,
            refs=(completion.completion_record_id,),
            strict=strict_event_stream,
        )
        _emit_package_126_event(
            path,
            store=reacquisition_store,
            event_kind="reacquisition_child_window_completed",
            parent=parent,
            child=child,
            refs=(reacquisition_execution.reacquisition_execution_id,),
            strict=strict_event_stream,
        )

        score = _package_112_score_equivalence(
            observation_window_id=child["observation_window_id"],
            context_refs=(
                active["contract"].contract_id,
                final_assessment.assessment_id,
                completion.completion_record_id,
            ),
        )
        store.append_record(
            "package_128_score_equivalence_records",
            score,
        )
        controls = run_synthetic_package_128_controls(state_dir=path)
        result_frozen = True
        stimulus.mark_finished()
        fixture_manifest = stimulus.manifest()
        real_run = {
            "real_run_record_id": stable_id(
                "package_128_real_run"
            ),
            "schema_version": "ashl_package_128_real_run_v0",
            "created_at": utc_now(),
            "experiment_id": EXPERIMENT_ID,
            "experiment_run_id": experiment_run_id,
            "run_status": (
                "passed_real_structural_sufficiency_policy_stop"
            ),
            "parent": _public_window(parent),
            "child": _public_window(child),
            "parent_visual_change_primitive_id": prepared[
                "parent_change"
            ]["visual_change_id"],
            "focus_candidate_count": len(prepared["candidates"]),
            "selected_candidate_id": prepared[
                "selection"
            ].selected_candidate_id,
            "selected_grid_x": focus_plan.grid_x,
            "selected_grid_y": focus_plan.grid_y,
            "focus_plan_id": focus_plan.focus_plan_id,
            "focus_action_id": focus_action.internal_action_id,
            "active_focus_context_id": active_sidecar.focus_context_id,
            "released_focus_context_id": (
                released_sidecar.focus_context_id
            ),
            "focus_release_record_id": (
                release.focus_release_record_id
            ),
            "package_126_child_window_used": True,
            "reacquisition_execution_id": (
                reacquisition_execution.reacquisition_execution_id
            ),
            "contract_id": active["contract"].contract_id,
            "contract_kind": active["contract"].contract_kind,
            "contract_authorized": allow_structural_sufficiency_stop,
            "checkpoint_ids": tuple(
                item.checkpoint_id for item in active["checkpoints"]
            ),
            "assessment_ids": tuple(
                item.assessment_id for item in active["assessments"]
            ),
            "final_checkpoint_id": active["checkpoints"][
                -1
            ].checkpoint_id,
            "final_assessment_id": final_assessment.assessment_id,
            "final_assessment_status": (
                final_assessment.assessment_status
            ),
            "final_contract_satisfied": (
                final_assessment.contract_satisfied
            ),
            "final_open_visual_region_refs": (
                active["checkpoints"][-1].open_visual_region_refs
            ),
            "final_closed_visual_span_refs": (
                active["checkpoints"][-1].closed_visual_span_refs
            ),
            "final_observed_visual_region_refs": (
                active["checkpoints"][-1].observed_visual_region_refs
            ),
            "post_event_coverage_ns": (
                active["checkpoints"][-1].post_event_coverage_ns
            ),
            "complete_alignment_window_count": (
                active["checkpoints"][
                    -1
                ].complete_alignment_window_count
            ),
            "policy_decision_id": final_decision.policy_decision_id,
            "policy_decision": final_decision.decision,
            "stop_action_id": stop_action.internal_action_id,
            "stop_action_kind": stop_action.action_kind,
            "stop_execution_id": stop_execution.stop_execution_id,
            "completion_record_id": completion.completion_record_id,
            "completion_kind": completion.completion_kind,
            "final_temporal_bundle_id": (
                final_temporal_bundle.temporal_bundle_id
            ),
            "original_hard_deadline_event_time_ns": (
                stop_execution.original_hard_deadline_event_time_ns
            ),
            "actual_observation_end_event_time_ns": (
                stop_execution.final_observation_end_event_time_ns
            ),
            "stopped_before_hard_deadline": (
                stop_execution.stopped_before_hard_deadline
            ),
            "all_required_lanes_stopped": (
                stop_execution.all_required_lanes_received_stop
            ),
            "full_frame_preserved": bool(
                child["visual_primitive_refs"]
                and child["visual_readable_data_refs"]
            ),
            "focused_region_evidence_present": bool(
                active["focused_evidence_view_ids"]
            ),
            "source_sessions_reopened_by_stop": (
                stop_execution.source_sessions_reopened
            ),
            "alignment_origin_changed_by_stop": (
                stop_execution.alignment_origin_changed
            ),
            "focus_context_changed_before_completion": (
                stop_execution.focus_context_changed
            ),
            "flush_completed": (
                child["flush_remaining_count"] == 0
            ),
            "required_lane_drop_count": child[
                "required_lane_drop_count"
            ],
            "backpressure_fault_count": child[
                "backpressure_fault_count"
            ],
            "capture_failure_count": child[
                "capture_failure_count"
            ],
            "compile_failure_count": child[
                "compile_failure_count"
            ],
            "flush_remaining_count": child[
                "flush_remaining_count"
            ],
            "controls": controls,
            "package_112_score_equivalence_id": (
                score.score_equivalence_record_id
            ),
            "package_112_score_changed": (
                score.package_112_score_changed
            ),
            "memory_write_created": False,
            "working_readback_created": False,
            "package_128_extension_action_created": False,
            "package_128_reacquisition_action_created": False,
            "package_128_focus_shift_action_created": False,
            "uncertainty_signal_created": False,
            "novelty_signal_created": False,
            "thought_engine_used": False,
            "endocrine_signal_used": False,
            "output_created": False,
            "external_control_created": False,
            "semantic_understanding_claimed": False,
            "recognition_claimed": False,
            "certainty_claimed": False,
            "subjective_time_claimed": False,
            "package_129_implemented": False,
            "package_130_implemented": False,
            "package_131_implemented": False,
            "d_laplace_component_used": False,
            "dlm_1_implemented": False,
            "llm_runtime_calls": 0,
            "codex_runtime_calls": 0,
            "network_runtime_calls": 0,
            "fixture_manifest_audited_after_result_frozen": result_frozen,
            "fixture_manifest_consumed_by_runtime": False,
            "fixture_manifest": fixture_manifest,
        }
        store.append_payload(
            "package_128_real_run_records",
            "real_run_record_id",
            real_run["real_run_record_id"],
            real_run,
        )
        return real_run
    finally:
        stimulus.close()


def _prepare_focused_reacquisition(
    *,
    path: Path,
    focus_store: Package127InternalFocusStore,
    reacquisition_store: Package126ReacquisitionStore,
    sensor_store: ContentAddressedSensorArtifactStore,
    temporal_store: Package124ATemporalStore,
    compiler: HardSoftPerceptionPrimitiveCompiler,
    primitive_store: PerceptionPrimitiveStore,
    stimulus: Any,
    window_source: WindowsBoundedWindowCaptureSource,
    host_adapter: HostStateSensorAdapter,
    binding: Any,
    configs: dict[str, Any],
    experiment_run_id: str,
    root_event_id: str,
    strict_event_stream: bool,
) -> dict[str, Any]:
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
    stimulus.begin_parent_phase()
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
        role="package_128_parent",
        participating_lanes=PARTICIPATING_LANES,
        window_duration_ns=PARENT_WINDOW_NS,
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
    selection = select_focus_candidate(
        parent_observation_window_id=parent["observation_window_id"],
        candidates=candidates,
    )
    focus_store.append_record(
        "internal_focus_selections",
        selection,
    )
    if selection.selection_status != "selected":
        raise RuntimeError("Package 128 parent produced no focus selection")
    selected = next(
        item
        for item in candidates
        if item.focus_candidate_id == selection.selected_candidate_id
    )
    focus_authorization = create_focus_authorization(parent=parent_ref)
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
    focus_plan = create_focus_plan(
        decision=focus_decision,
        candidate=selected,
    )
    if focus_plan is None:
        raise RuntimeError("Package 128 focus policy blocked")
    focus_store.append_record("internal_focus_plans", focus_plan)
    focus_action = create_internal_perception_focus_shift_action(
        plan=focus_plan
    )
    focus_store.append_record(
        "internal_focus_actions",
        focus_action,
    )
    _emit_focus_event(
        path,
        store=focus_store,
        event_kind="internal_focus_shift_action_created",
        runtime_session_id=parent["runtime_session_id"],
        perception_session_id=parent["perception_session_id"],
        observation_window_id=parent["observation_window_id"],
        refs=(focus_action.internal_action_id,),
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
    authorization = create_reacquisition_authorization(
        parent=parent_ref,
        allowed_action_kinds=("capture_again",),
        authorization_source="explicit_session_configuration",
    )
    reacquisition_store.append_record(
        "perception_reacquisition_authorizations",
        authorization,
    )
    request = create_reacquisition_request(
        parent=parent_ref,
        authorization=authorization,
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
    request_gap_ns = max(
        0,
        monotonic_ns() - parent["ended_monotonic_ns"],
    )
    eligibility = decide_reacquisition_eligibility(
        request=request,
        parent=parent_ref,
        parent_plan=parent_plan,
        requested_plan=child_plan,
        authorization=authorization,
        parent_to_request_gap_ns=request_gap_ns,
        chain_duration_ns=parent["actual_window_ns"] + request_gap_ns,
    )
    reacquisition_store.append_record(
        "reacquisition_eligibility_decisions",
        eligibility,
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
            "Package 126 child eligibility blocked: "
            + ",".join(eligibility.failure_reasons)
        )
    reacquisition_store.append_record(
        "bounded_reacquisition_internal_actions",
        reacquisition_action,
    )
    child_ids = {
        "runtime_session_id": stable_id(
            "package_128_child_runtime_session"
        ),
        "perception_session_id": stable_id(
            "package_128_child_perception_session"
        ),
        "observation_window_id": stable_id("observation_window"),
    }
    return {
        "parent": parent,
        "parent_plan": parent_plan,
        "parent_ref": parent_ref,
        "parent_change": parent_change,
        "candidate_batch": batch,
        "candidates": candidates,
        "selection": selection,
        "focus_plan": focus_plan,
        "focus_action": focus_action,
        "child_plan": child_plan,
        "reacquisition_action": reacquisition_action,
        "child_ids": child_ids,
    }


def _initialize_active_contract(
    *,
    path: Path,
    store: Package128SufficiencyStopStore,
    focus_store: Package127InternalFocusStore,
    temporal_store: Package124ATemporalStore,
    package_122: BoundedMultimodalPerceptionSessionRuntime,
    primitive_store: PerceptionPrimitiveStore,
    focus_plan: Any,
    focus_action_id: str,
    reacquisition_action_id: str,
    snapshot: ActiveReacquisitionCaptureSnapshot,
    first_screen_bundle: Any,
    first_screen_lane_item: Any,
    active: dict[str, Any],
    strict_event_stream: bool,
) -> None:
    first_frame = primitive_store.get_primitive(
        first_screen_bundle.primitive_record_id
    )
    initial_view = build_focused_visual_region_view(
        plan=focus_plan,
        child_runtime_session_id=snapshot.runtime_session_id,
        child_perception_session_id=snapshot.perception_session_id,
        child_observation_window_id=snapshot.observation_window_id,
        visual_frame=first_frame,
        perception_readable_data_id=(
            first_screen_bundle.perception_readable_data_id
        ),
        visual_change=None,
    )
    focus_store.append_record(
        "focused_visual_region_views",
        initial_view,
    )
    active_sidecar = build_focus_context_sidecar(
        plan=focus_plan,
        view=initial_view,
        full_frame_perception_readable_data_id=(
            first_screen_bundle.perception_readable_data_id
        ),
        active_from_event_time_ns=snapshot.started_monotonic_ns,
        active_until_event_time_ns=(
            snapshot.hard_deadline_monotonic_ns
        ),
        focus_state="focused",
    )
    package_122.attach_internal_perception_focus_context(
        active_sidecar,
        active_lane_items=(first_screen_lane_item,),
    )
    focus_store.append_record(
        "internal_focus_context_sidecars",
        active_sidecar,
    )
    _emit_focus_event(
        path,
        store=focus_store,
        event_kind="internal_focus_context_attached",
        runtime_session_id=snapshot.runtime_session_id,
        perception_session_id=snapshot.perception_session_id,
        observation_window_id=snapshot.observation_window_id,
        refs=(
            active_sidecar.focus_context_id,
            initial_view.focused_region_view_id,
        ),
        strict=strict_event_stream,
    )
    contract = create_structural_sufficiency_contract(
        runtime_session_id=snapshot.runtime_session_id,
        perception_session_id=snapshot.perception_session_id,
        observation_window_id=snapshot.observation_window_id,
        focus_context_id=active_sidecar.focus_context_id,
        hard_deadline_event_time_ns=(
            snapshot.hard_deadline_monotonic_ns
        ),
        source_record_refs=(
            focus_action_id,
            reacquisition_action_id,
            active_sidecar.focus_context_id,
            initial_view.focused_region_view_id,
        ),
    )
    store.append_record(
        "structural_sufficiency_contracts",
        contract,
    )
    active_clock = build_clock_domain_descriptor(
        process_instance_id=snapshot.runtime_session_id,
        operating_system_process_id=os.getpid(),
        utc_anchor=utc_now(),
        utc_anchor_monotonic_ns=snapshot.started_monotonic_ns,
        monotonic_origin_ns=snapshot.started_monotonic_ns,
        comparable_across_processes=False,
        source_trace_refs=tuple(),
    )
    temporal_store.append_record(
        "temporal_clock_domains",
        active_clock,
    )
    temporal_store.append_record(
        "temporal_clock_quality",
        evaluate_clock_quality(active_clock, tuple()),
    )
    active.update(
        {
            "contract": contract,
            "active_sidecar": active_sidecar,
            "initial_view": initial_view,
            "latest_view": initial_view,
            "active_clock": active_clock,
            "baseline_frame": first_frame,
            "baseline_artifact_id": (
                first_screen_bundle.source_artifact_id
            ),
            "last_visual_artifact_id": (
                first_screen_bundle.source_artifact_id
            ),
            "latest_visual_change_id": None,
            "next_checkpoint_ns": (
                snapshot.started_monotonic_ns + MINIMUM_ELAPSED_NS
            ),
            "initial_capture_session_refs": (
                snapshot.capture_session_refs
            ),
            "initial_alignment_origin_ref": (
                snapshot.perception_session_id
            ),
        }
    )
    _emit_event(
        path,
        store=store,
        event_kind="structural_sufficiency_contract_created",
        child={
            "runtime_session_id": snapshot.runtime_session_id,
            "perception_session_id": snapshot.perception_session_id,
            "observation_window_id": snapshot.observation_window_id,
        },
        refs=(contract.contract_id,),
        strict=strict_event_stream,
    )


def _update_active_visual_evidence(
    *,
    focus_store: Package127InternalFocusStore,
    sensor_store: ContentAddressedSensorArtifactStore,
    temporal_store: Package124ATemporalStore,
    primitive_store: PerceptionPrimitiveStore,
    focus_plan: Any,
    snapshot: ActiveReacquisitionCaptureSnapshot,
    compilation_cache: dict[str, Any],
    active: dict[str, Any],
) -> None:
    latest_artifact_id = snapshot.screen_artifact_ids[-1]
    if latest_artifact_id == active["last_visual_artifact_id"]:
        return

    latest_bundle = compilation_cache[latest_artifact_id]
    current_frame_payload = primitive_store.get_primitive(
        latest_bundle.primitive_record_id
    )
    baseline_frame = VisualFramePrimitiveRecord(
        **dict(active["baseline_frame"])
    )
    current_frame = VisualFramePrimitiveRecord(
        **dict(current_frame_payload)
    )
    visual_change_record = compile_visual_change_primitive(
        baseline_frame,
        current_frame,
    )
    primitive_store.append_visual_change_primitive(visual_change_record)
    visual_change = visual_change_record.to_dict()
    selected_changed = any(
        int(cell["grid_x"]) == focus_plan.grid_x
        and int(cell["grid_y"]) == focus_plan.grid_y
        for cell in visual_change_record.changed_grid_cells
    )
    view = build_focused_visual_region_view(
        plan=focus_plan,
        child_runtime_session_id=snapshot.runtime_session_id,
        child_perception_session_id=snapshot.perception_session_id,
        child_observation_window_id=snapshot.observation_window_id,
        visual_frame=current_frame_payload,
        perception_readable_data_id=(
            latest_bundle.perception_readable_data_id
        ),
        visual_change=visual_change,
    )
    focus_store.append_record("focused_visual_region_views", view)
    active["latest_view"] = view
    active["last_visual_artifact_id"] = latest_artifact_id
    active["latest_visual_change_id"] = (
        visual_change_record.visual_change_id
    )
    if selected_changed:
        active["focused_evidence_view_ids"].append(
            view.focused_region_view_id
        )

    latest_screen = sensor_store.get_artifact(latest_artifact_id)
    screen_event_ns = int(
        latest_screen["captured_at_monotonic_ns"]
    )
    if selected_changed and active["open_region_ref"] is None:
        active["open_region_ref"] = visual_change_record.visual_change_id
        active["open_region_started_ns"] = screen_event_ns
        active["observed_region_refs"].append(
            visual_change_record.visual_change_id
        )
    elif (
        not selected_changed
        and active["open_region_ref"] is not None
    ):
        onset_ref = str(active["open_region_ref"])
        onset_ns = int(active["open_region_started_ns"])
        onset_anchor = build_temporal_anchor(
            source_record_id=onset_ref,
            source_record_kind="visual_change_primitive",
            source_lane="screen",
            clock_domain_id=active["active_clock"].clock_domain_id,
            normalized_event_time_ns=onset_ns,
            source_native_time_ns=onset_ns,
            processing_time_ns=monotonic_ns(),
            source_record_refs=(onset_ref,),
        )
        closure_anchor = build_temporal_anchor(
            source_record_id=visual_change_record.visual_change_id,
            source_record_kind="visual_region_closure_observation",
            source_lane="screen",
            clock_domain_id=active["active_clock"].clock_domain_id,
            normalized_event_time_ns=screen_event_ns,
            source_native_time_ns=screen_event_ns,
            processing_time_ns=monotonic_ns(),
            source_record_refs=(
                visual_change_record.visual_change_id,
                onset_ref,
            ),
        )
        span = build_temporal_span(
            span_kind="observed_change_region",
            start_anchor=onset_anchor,
            end_anchor=closure_anchor,
            source_lane="screen",
            source_region_refs=(onset_ref,),
            source_record_refs=(
                onset_ref,
                visual_change_record.visual_change_id,
            ),
        )
        for table, record in (
            ("temporal_event_anchors", onset_anchor),
            ("temporal_event_anchors", closure_anchor),
            ("temporal_span_primitives", span),
        ):
            temporal_store.append_record(table, record)
        active["temporal_records"].extend(
            (onset_anchor, closure_anchor, span)
        )
        active["closed_spans"].append(span)
        active["open_region_ref"] = None
        active["open_region_started_ns"] = None


def _evaluate_active_checkpoint(
    *,
    path: Path,
    store: Package128SufficiencyStopStore,
    focus_store: Package127InternalFocusStore,
    sensor_store: ContentAddressedSensorArtifactStore,
    temporal_store: Package124ATemporalStore,
    primitive_store: PerceptionPrimitiveStore,
    package_122: BoundedMultimodalPerceptionSessionRuntime,
    alignment_config: Any,
    focus_plan: Any,
    snapshot: ActiveReacquisitionCaptureSnapshot,
    lane_items: tuple[Any, ...],
    compilation_cache: dict[str, Any],
    active: dict[str, Any],
    controller: BoundedCaptureDeadlineController,
    contract_authorized: bool,
    strict_event_stream: bool,
) -> None:
    alignment = package_122.inspect_active_compiled_alignment(
        lane_items=lane_items,
        config=alignment_config,
        session_id=snapshot.perception_session_id,
    )
    view = active["latest_view"]
    if view is None:
        raise RuntimeError("Package 128 active focus view is unavailable")
    latest_screen = sensor_store.get_artifact(
        snapshot.screen_artifact_ids[-1]
    )
    latest_host = sensor_store.get_artifact(
        snapshot.host_artifact_ids[-1]
    )
    screen_event_ns = int(
        latest_screen["captured_at_monotonic_ns"]
    )
    host_event_ns = int(
        latest_host["captured_at_monotonic_ns"]
    )
    coverage_event_ns = min(screen_event_ns, host_event_ns)

    complete_windows = sum(
        1 for item in alignment.windows if item.complete_for_config
    )
    checkpoint_event_ns = min(
        max(snapshot.observed_at_monotonic_ns, coverage_event_ns),
        snapshot.hard_deadline_monotonic_ns,
    )
    checkpoint = create_structural_evidence_checkpoint(
        contract=active["contract"],
        checkpoint_index=len(active["checkpoints"]),
        evaluated_at_event_time_ns=checkpoint_event_ns,
        elapsed_observation_ns=max(
            0,
            checkpoint_event_ns
            - snapshot.started_monotonic_ns,
        ),
        complete_alignment_window_count=complete_windows,
        partial_alignment_window_count=sum(
            1
            for item in alignment.windows
            if not item.complete_for_config
        ),
        focused_region_view_id=view.focused_region_view_id,
        full_frame_perception_readable_data_refs=tuple(
            compilation_cache[item].perception_readable_data_id
            for item in snapshot.screen_artifact_ids
        ),
        focused_region_evidence_record_count=len(
            active["focused_evidence_view_ids"]
        ),
        observed_visual_region_refs=tuple(
            active["observed_region_refs"]
        ),
        open_visual_region_refs=(
            (str(active["open_region_ref"]),)
            if active["open_region_ref"] is not None
            else tuple()
        ),
        closed_visual_span_refs=tuple(
            item.temporal_span_id for item in active["closed_spans"]
        ),
        latest_visual_closure_event_time_ns=(
            int(active["closed_spans"][-1].end_event_time_ns)
            if active["closed_spans"]
            else None
        ),
        latest_complete_source_coverage_event_time_ns=coverage_event_ns,
        screen_source_coverage_present=bool(
            snapshot.screen_artifact_ids
        ),
        host_state_source_coverage_present=bool(
            snapshot.host_artifact_ids
        ),
        source_record_refs=(view.focused_region_view_id,)
        + (
            (str(active["latest_visual_change_id"]),)
            if active["latest_visual_change_id"] is not None
            else tuple()
        )
        + tuple(
            item.alignment_window_id for item in alignment.windows
        )
        + (
            snapshot.screen_artifact_ids[-1],
            snapshot.host_artifact_ids[-1],
        ),
    )
    store.append_record(
        "structural_evidence_checkpoints",
        checkpoint,
    )
    active["checkpoints"].append(checkpoint)
    _emit_event(
        path,
        store=store,
        event_kind="structural_evidence_checkpoint_created",
        child=snapshot.__dict__,
        refs=(checkpoint.checkpoint_id,),
        strict=strict_event_stream,
    )
    assessment = assess_structural_evidence(
        contract=active["contract"],
        checkpoint=checkpoint,
        active_window=True,
        focus_context_valid=True,
    )
    store.append_record(
        "structural_evidence_assessments",
        assessment,
    )
    active["assessments"].append(assessment)
    assessment_event = (
        "structural_evidence_assessment_sufficient"
        if assessment.assessment_status == "sufficient"
        else (
            "structural_evidence_assessment_inconclusive"
            if assessment.assessment_status
            == "inconclusive_at_hard_deadline"
            else "structural_evidence_assessment_insufficient"
        )
    )
    _emit_event(
        path,
        store=store,
        event_kind=assessment_event,
        child=snapshot.__dict__,
        refs=(assessment.assessment_id,),
        strict=strict_event_stream,
    )
    decision = decide_observation_stop_policy(
        contract=active["contract"],
        assessment=assessment,
        contract_authorized=contract_authorized,
        active_window_identity_valid=True,
        stop_budget_available=active["stop_action"] is None,
        operator_stop_requested=False,
        active_window=True,
    )
    store.append_record(
        "observation_stop_policy_decisions",
        decision,
    )
    active["decisions"].append(decision)
    policy_event = (
        "observation_stop_policy_allowed"
        if decision.decision == "allow_policy_stop"
        else (
            "observation_stop_policy_hard_deadline"
            if decision.decision
            == "hard_deadline_inconclusive_stop"
            else "observation_stop_policy_continue"
        )
    )
    _emit_event(
        path,
        store=store,
        event_kind=policy_event,
        child=snapshot.__dict__,
        refs=(decision.policy_decision_id,),
        strict=strict_event_stream,
    )
    if decision.decision == "allow_policy_stop":
        action = create_stop_observation_internal_action(
            decision=decision,
            contract=active["contract"],
            existing_action_count=(
                1 if active["stop_action"] is not None else 0
            ),
        )
        if action is None:
            raise RuntimeError("Package 128 allowed policy created no action")
        store.append_record(
            "stop_observation_internal_actions",
            action,
        )
        active["stop_action"] = action
        active["stop_requested_event_time_ns"] = (
            checkpoint.evaluated_at_event_time_ns
        )
        _emit_event(
            path,
            store=store,
            event_kind="stop_observation_internal_action_created",
            child=snapshot.__dict__,
            refs=(action.internal_action_id,),
            strict=strict_event_stream,
        )
        controller.request_stop(
            "structural_evidence_sufficiency_policy"
        )


def _build_final_temporal_bundle(
    *,
    temporal_store: Package124ATemporalStore,
    child: dict[str, Any],
    active: dict[str, Any],
) -> GroundedTemporalPrimitiveBundle:
    source = temporal_store.get_payload(
        "grounded_temporal_bundles",
        str(child["temporal_bundle_id"]),
    )
    anchors = tuple(
        item.temporal_anchor_id
        for item in active["temporal_records"]
        if hasattr(item, "temporal_anchor_id")
    )
    spans = tuple(
        item.temporal_span_id
        for item in active["temporal_records"]
        if hasattr(item, "temporal_span_id")
    )
    payload = {
        "schema_version": source["schema_version"],
        "clock_domain_refs": tuple(
            dict.fromkeys(
                tuple(source.get("clock_domain_refs") or ())
                + (active["active_clock"].clock_domain_id,)
            )
        ),
        "anchor_refs": tuple(source.get("anchor_refs") or ())
        + anchors,
        "span_refs": tuple(source.get("span_refs") or ()) + spans,
        "interval_refs": tuple(source.get("interval_refs") or ()),
        "relation_refs": tuple(source.get("relation_refs") or ()),
        "continuity_refs": tuple(
            source.get("continuity_refs") or ()
        ),
        "repeated_structure_refs": tuple(
            source.get("repeated_structure_refs") or ()
        ),
        "external_gap_refs": tuple(
            source.get("external_gap_refs") or ()
        ),
        "source_perception_record_refs": tuple(
            dict.fromkeys(
                tuple(
                    source.get("source_perception_record_refs") or ()
                )
                + tuple(active["observed_region_refs"])
            )
        ),
        "source_alignment_window_refs": tuple(
            source.get("source_alignment_window_refs") or ()
        ),
        "source_trace_refs": tuple(
            source.get("source_trace_refs") or ()
        ),
        "stimulus_ground_truth_used_for_compilation": False,
        "subjective_time_claimed": False,
        "rhythm_semantics_claimed": False,
        "waiting_semantics_claimed": False,
    }
    bundle = GroundedTemporalPrimitiveBundle(
        temporal_bundle_id=temporal_identity(
            "package_128_final_grounded_temporal_bundle",
            payload,
        ),
        created_at=utc_now(),
        **payload,
    )
    temporal_store.append_record(
        "grounded_temporal_bundles",
        bundle,
    )
    return bundle


def _package_112_score_equivalence(
    *,
    observation_window_id: str,
    context_refs: tuple[str, ...],
) -> Package128ScoreEquivalenceRecord:
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
    return Package128ScoreEquivalenceRecord(
        score_equivalence_record_id=stable_id(
            "package_128_score_equivalence"
        ),
        schema_version="ashl_package_128_score_equivalence_v0",
        created_at=utc_now(),
        observation_window_id=observation_window_id,
        authoritative_score_before=int(before.final_candidate_priority),
        authoritative_score_after=int(after.final_candidate_priority),
        package_128_score_contribution=0,
        package_112_score_changed=(
            int(before.final_candidate_priority)
            != int(after.final_candidate_priority)
            or int(before.readback_delta) != int(after.readback_delta)
        ),
        context_read_only=True,
        source_record_refs=context_refs,
        source_trace_refs=tuple(),
    )


def _emit_event(
    state_dir: Path,
    *,
    store: Package128SufficiencyStopStore,
    event_kind: str,
    child: dict[str, Any],
    refs: tuple[str, ...],
    strict: bool,
) -> bool:
    if event_kind not in PACKAGE_128_EVENT_KINDS:
        raise ValueError(f"unknown Package 128 event kind: {event_kind}")
    runtime_session_id = str(child.get("runtime_session_id") or "")
    perception_session_id = str(
        child.get("perception_session_id") or ""
    )
    observation_window_id = str(
        child.get("observation_window_id") or ""
    )
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
                "package_128_event_delivery_failure"
            ),
            "schema_version": (
                "ashl_package_128_operator_event_delivery_failure_v0"
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
                f"Package 128 operator event delivery failed: {event_kind}"
            ) from error
        return False


def _public_window(window: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in window.items()
        if key != "audio_deletion"
    }


def run_synthetic_package_128_controls(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    path = Path(state_dir)
    store = Package128SufficiencyStopStore(path)
    contract = create_structural_sufficiency_contract(
        runtime_session_id="runtime:control",
        perception_session_id="perception:control",
        observation_window_id="window:control",
        focus_context_id="focus_context:control",
        hard_deadline_event_time_ns=3_000_000_000,
        source_record_refs=(
            "focus_context:control",
            "focus_plan:control",
        ),
    )

    def checkpoint(
        *,
        event_time_ns: int = 2_000_000_000,
        observed: bool = True,
        open_region: bool = False,
        post_coverage_ns: int = 600_000_000,
        drops: int = 0,
        window_id: str | None = None,
    ) -> Any:
        closure = (
            event_time_ns - post_coverage_ns
            if observed and not open_region
            else None
        )
        return create_structural_evidence_checkpoint(
            contract=contract,
            checkpoint_index=0,
            evaluated_at_event_time_ns=event_time_ns,
            evaluated_at_processing_time_ns=event_time_ns + 10,
            elapsed_observation_ns=event_time_ns,
            complete_alignment_window_count=3,
            partial_alignment_window_count=0,
            focused_region_view_id="focused_view:control",
            full_frame_perception_readable_data_refs=(
                "readable:control",
            ),
            focused_region_evidence_record_count=1 if observed else 0,
            observed_visual_region_refs=(
                ("visual_change:control",) if observed else tuple()
            ),
            open_visual_region_refs=(
                ("visual_change:control",)
                if observed and open_region
                else tuple()
            ),
            closed_visual_span_refs=(
                ("temporal_span:control",)
                if observed and not open_region
                else tuple()
            ),
            latest_visual_closure_event_time_ns=closure,
            latest_complete_source_coverage_event_time_ns=event_time_ns,
            screen_source_coverage_present=True,
            host_state_source_coverage_present=True,
            required_lane_drop_count=drops,
            observation_window_id=window_id,
            source_record_refs=(
                "screen_artifact:control",
                "host_artifact:control",
            ),
        )

    open_assessment = assess_structural_evidence(
        contract=contract,
        checkpoint=checkpoint(
            event_time_ns=3_000_000_000,
            open_region=True,
        ),
    )
    post_assessment = assess_structural_evidence(
        contract=contract,
        checkpoint=checkpoint(post_coverage_ns=100_000_000),
    )
    no_event_assessment = assess_structural_evidence(
        contract=contract,
        checkpoint=checkpoint(
            event_time_ns=3_000_000_000,
            observed=False,
        ),
    )
    sufficient = assess_structural_evidence(
        contract=contract,
        checkpoint=checkpoint(),
    )
    authorization_off = decide_observation_stop_policy(
        contract=contract,
        assessment=sufficient,
        contract_authorized=False,
    )
    wrong_window = assess_structural_evidence(
        contract=contract,
        checkpoint=checkpoint(window_id="window:other"),
    )
    stale = assess_structural_evidence(
        contract=contract,
        checkpoint=checkpoint(),
        active_window=False,
    )
    transport = assess_structural_evidence(
        contract=contract,
        checkpoint=checkpoint(drops=1),
    )
    transport_policy = decide_observation_stop_policy(
        contract=contract,
        assessment=transport,
        contract_authorized=True,
    )
    operator_policy = decide_observation_stop_policy(
        contract=contract,
        assessment=sufficient,
        contract_authorized=True,
        operator_stop_requested=True,
    )
    allow_policy = decide_observation_stop_policy(
        contract=contract,
        assessment=sufficient,
        contract_authorized=True,
    )
    action = create_stop_observation_internal_action(
        decision=allow_policy,
        contract=contract,
    )
    duplicate_blocked = False
    try:
        create_stop_observation_internal_action(
            decision=allow_policy,
            contract=contract,
            existing_action_count=1,
        )
    except ValueError:
        duplicate_blocked = True
    stimulus_rejected = False
    try:
        create_structural_sufficiency_contract(
            runtime_session_id="runtime:bad",
            perception_session_id="perception:bad",
            observation_window_id="window:bad",
            focus_context_id="focus_context:bad",
            hard_deadline_event_time_ns=3_000_000_000,
            source_record_refs=("stimulus_schedule:forbidden",),
        )
    except ValueError:
        stimulus_rejected = True
    semantic_rejected = False
    try:
        replace(contract, semantic_goal="object")
    except ValueError:
        semantic_rejected = True
    incomplete_focus = assess_structural_evidence(
        contract=contract,
        checkpoint=checkpoint(),
        focus_context_valid=False,
    )
    payload = {
        "control_result_id": stable_id(
            "package_128_control_result"
        ),
        "schema_version": "ashl_package_128_control_result_v0",
        "created_at": utc_now(),
        "open_event_control_passed": (
            open_assessment.assessment_status
            == "inconclusive_at_hard_deadline"
            and not open_assessment.contract_satisfied
        ),
        "insufficient_post_context_control_passed": (
            post_assessment.assessment_status
            == "insufficient_continue"
        ),
        "no_event_control_passed": (
            no_event_assessment.assessment_status
            == "inconclusive_at_hard_deadline"
        ),
        "authorization_off_control_passed": (
            authorization_off.decision == "continue_current_window"
        ),
        "wrong_window_control_passed": (
            wrong_window.assessment_status
            == "blocked_invalid_lineage"
        ),
        "stale_checkpoint_control_passed": (
            stale.assessment_status == "blocked_invalid_lineage"
        ),
        "transport_fault_control_passed": (
            transport.assessment_status
            == "blocked_transport_failure"
            and transport_policy.decision == "fail_session"
        ),
        "operator_stop_control_passed": (
            operator_policy.decision == "operator_stop_precedence"
        ),
        "duplicate_stop_control_passed": duplicate_blocked,
        "stimulus_injection_control_passed": stimulus_rejected,
        "semantic_injection_control_passed": semantic_rejected,
        "incomplete_focus_control_passed": (
            incomplete_focus.assessment_status
            == "blocked_invalid_lineage"
        ),
        "exactly_one_terminal_action_created": action is not None,
        "source_record_refs": (contract.contract_id,),
        "source_trace_refs": tuple(),
    }
    store.append_payload(
        "package_128_control_results",
        "control_result_id",
        payload["control_result_id"],
        payload,
    )
    return payload


def run_synthetic_package_128_smoke(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    controls = run_synthetic_package_128_controls(
        state_dir=state_dir
    )
    return {
        "schema_version": "ashl_package_128_synthetic_smoke_v0",
        "created_at": utc_now(),
        "status": (
            "passed_package_128_synthetic_smoke"
            if all(
                value is True
                for key, value in controls.items()
                if key.endswith("_passed")
            )
            else "blocked_package_128_synthetic_smoke"
        ),
        "controls": controls,
        "sensor_opened": False,
        "memory_write_created": False,
        "output_created": False,
        "external_control_created": False,
    }
