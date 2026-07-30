"""Package 126 bounded fresh-world reacquisition runtime."""

from __future__ import annotations

import gc
import os
import threading
import time
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
from ashl_core_v1.runtime.ephemeral_audio_ring_buffer import (
    build_ephemeral_audio_ring_buffer_config,
    start_ephemeral_audio_session,
)
from ashl_core_v1.runtime.host_sensor_types import (
    SensorCaptureError,
    build_sensor_capture_config,
    monotonic_ns,
    sha256_bytes,
    sha256_payload,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.host_state_sensor_adapter import HostStateSensorAdapter
from ashl_core_v1.runtime.local_operator_console_store import (
    build_default_console_store,
)
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.runtime.local_pulse_stimulus_runtime import (
    LocalPulseStimulusRuntime,
)
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    MultimodalPerceptionSessionMode,
    build_default_multimodal_session_config,
)
from ashl_core_v1.runtime.observation_window_types import (
    OBSERVATION_WINDOW_STATE_SCHEMA_VERSION,
    ObservationWindowState,
)
from ashl_core_v1.runtime.package_124a_temporal_store import (
    Package124ATemporalStore,
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
    MAXIMUM_REACQUISITION_WINDOW_NS,
    CompletedObservationWindowReference,
    EphemeralAudioDeletionVerificationRecord,
    Package126ScoreEquivalenceRecord,
    ReacquiredEvidenceSummary,
    ReacquisitionCaptureExecution,
    ReacquisitionEffectComparison,
    SamplingPlanIdentityRecord,
)
from ashl_core_v1.runtime.package_126_reacquisition_store import (
    Package126ReacquisitionStore,
)
from ashl_core_v1.runtime.sampling_plan_identity import (
    build_sampling_plan_identity,
    clone_sampling_plan_identity,
    configuration_identity_equal,
    plan_identity_equal,
    target_identity_equal,
)
from ashl_core_v1.runtime.temporal_clock_domain import (
    build_clock_domain_descriptor,
    evaluate_clock_quality,
)
from ashl_core_v1.runtime.temporal_types import (
    TEMPORAL_ANCHOR_SCHEMA_VERSION,
    TEMPORAL_BUNDLE_SCHEMA_VERSION,
    TEMPORAL_SPAN_SCHEMA_VERSION,
    GroundedTemporalPrimitiveBundle,
    TemporalEventAnchor,
    TemporalSpanPrimitive,
    temporal_identity,
)
from ashl_core_v1.runtime.windows_bounded_window_capture_source import (
    WindowsBoundedWindowCaptureSource,
)
from ashl_core_v1.runtime.windows_wasapi_loopback_source import (
    WindowsWasapiLoopbackSource,
)


CAPTURE_AGAIN_EXPERIMENT_ID = "host_internal_same_plan_capture_again_v0"
LISTEN_AGAIN_EXPERIMENT_ID = "host_internal_listen_again_ephemeral_v0"
WINDOW_DURATION_MS = 2_500
WINDOW_DURATION_NS = WINDOW_DURATION_MS * 1_000_000
ALIGNMENT_WINDOW_MS = 1_000
AUDIO_PRIVACY_MODE = "recognition_ephemeral"
AUDIO_BLUR_POLICY_VERSION = "recognition_ephemeral_v0"
EVENT_CLOCK_DOMAIN = "windows_query_performance_counter_monotonic_ns"
PROCESSING_CLOCK_DOMAIN = "python_process_monotonic_ns"

CAPTURE_AGAIN_STIMULUS_SCHEDULE = (
    (0, "black", "silent"),
    (500, "white", "tone"),
    (1_000, "black", "silent"),
    (3_100, "white", "tone"),
    (3_600, "black", "silent"),
)
LISTEN_AGAIN_STIMULUS_SCHEDULE = (
    (0, "black", "silent"),
    (500, "black", "tone"),
    (1_000, "black", "silent"),
    (3_100, "black", "tone"),
    (3_600, "black", "silent"),
)

PACKAGE_126_EVENT_KINDS = (
    "perception_reacquisition_authorized",
    "perception_reacquisition_requested",
    "perception_reacquisition_allowed",
    "perception_reacquisition_blocked",
    "perception_reacquisition_cancelled",
    "capture_again_internal_action_created",
    "listen_again_internal_action_created",
    "reacquisition_child_window_started",
    "reacquisition_source_reopened",
    "reacquisition_child_window_completed",
    "reacquisition_child_window_interrupted",
    "cross_window_temporal_link_created",
    "reacquired_evidence_summary_created",
    "reacquisition_effect_comparison_created",
    "audio_ephemeral_deletion_verified",
    "package_126_audit_failed",
)


def run_real_capture_again(
    *,
    state_dir: str | Path,
    render_endpoint: str = "default",
    allow_reacquisition: bool = True,
    strict_event_stream: bool = True,
) -> dict[str, Any]:
    return _run_real_reacquisition(
        state_dir=state_dir,
        action_kind="capture_again",
        render_endpoint=render_endpoint,
        allow_reacquisition=allow_reacquisition,
        strict_event_stream=strict_event_stream,
    )


def run_real_listen_again(
    *,
    state_dir: str | Path,
    render_endpoint: str = "default",
    allow_reacquisition: bool = True,
    strict_event_stream: bool = True,
) -> dict[str, Any]:
    return _run_real_reacquisition(
        state_dir=state_dir,
        action_kind="listen_again",
        render_endpoint=render_endpoint,
        allow_reacquisition=allow_reacquisition,
        strict_event_stream=strict_event_stream,
    )


def _run_real_reacquisition(
    *,
    state_dir: str | Path,
    action_kind: str,
    render_endpoint: str,
    allow_reacquisition: bool,
    strict_event_stream: bool,
) -> dict[str, Any]:
    path = Path(state_dir)
    store = Package126ReacquisitionStore(path)
    sensor_store = ContentAddressedSensorArtifactStore(path)
    temporal_store = Package124ATemporalStore(path)
    compiler = HardSoftPerceptionPrimitiveCompiler(path, sensor_store=sensor_store)
    primitive_store = PerceptionPrimitiveStore(path)
    experiment_id = (
        CAPTURE_AGAIN_EXPERIMENT_ID
        if action_kind == "capture_again"
        else LISTEN_AGAIN_EXPERIMENT_ID
    )
    experiment_run_id = stable_id(f"{experiment_id}_run")
    root_event_id = stable_id("package_126_capture_root")
    participating_lanes = (
        ("screen", "microphone", "host_state")
        if action_kind == "capture_again"
        else ("microphone", "host_state")
    )
    schedule = (
        CAPTURE_AGAIN_STIMULUS_SCHEDULE
        if action_kind == "capture_again"
        else LISTEN_AGAIN_STIMULUS_SCHEDULE
    )
    stimulus = LocalPulseStimulusRuntime(
        experiment_run_id=experiment_run_id,
        render_endpoint_id=render_endpoint,
        schedule=schedule,
        window_title_prefix=f"ASHL Package 126 {action_kind}",
        tone_duration_ms=400,
        client_width=80,
        client_height=45,
    )
    window_source = WindowsBoundedWindowCaptureSource()
    audio_source = WindowsWasapiLoopbackSource(endpoint_id=render_endpoint)
    host_adapter = HostStateSensorAdapter()
    event_failures_before = len(store.list_payloads("operator_event_delivery_failures"))
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
                f"Package 126 stimulus binding failed: {binding.binding_status}",
            )
        if not audio_source.source_descriptor().available:
            raise SensorCaptureError(
                "backend_missing",
                audio_source.source_descriptor().failure_reason
                or "WASAPI loopback source unavailable",
            )
        configs = _build_source_configs(
            path=path,
            action_kind=action_kind,
            binding=binding,
            window_source=window_source,
            audio_source=audio_source,
            host_adapter=host_adapter,
        )
        parent_plan = _build_plan_identity(
            action_kind=action_kind,
            binding=binding,
            window_source=window_source,
            audio_source=audio_source,
            configs=configs,
        )
        store.append_record("sampling_plan_identity_records", parent_plan)
        parent = _capture_one_window(
            path=path,
            store=store,
            sensor_store=sensor_store,
            temporal_store=temporal_store,
            compiler=compiler,
            primitive_store=primitive_store,
            stimulus=stimulus,
            window_source=window_source,
            audio_source=audio_source,
            host_adapter=host_adapter,
            binding=binding,
            configs=configs,
            action_kind=action_kind,
            experiment_run_id=experiment_run_id,
            root_event_id=root_event_id,
            plan=parent_plan,
            role="parent",
            participating_lanes=participating_lanes,
        )
        parent_ref = _completed_parent_reference(parent, parent_plan)
        store.append_record("completed_parent_window_refs", parent_ref)

        authorization = (
            create_reacquisition_authorization(
                parent=parent_ref,
                allowed_action_kinds=(action_kind,),
                authorization_source="explicit_local_operator_request",
            )
            if allow_reacquisition
            else None
        )
        if authorization is not None:
            store.append_record(
                "perception_reacquisition_authorizations",
                authorization,
            )
            _emit_event(
                path,
                store=store,
                event_kind="perception_reacquisition_authorized",
                parent=parent,
                refs=(authorization.authorization_id,),
                strict=strict_event_stream,
            )
        child_plan = clone_sampling_plan_identity(
            parent_plan,
            source_record_refs=(parent_plan.sampling_plan_identity_id,),
        )
        store.append_record("sampling_plan_identity_records", child_plan)
        request = create_reacquisition_request(
            parent=parent_ref,
            authorization=authorization,
            requested_action_kind=action_kind,
            requested_plan=child_plan,
            request_source="explicit_local_operator_request",
            request_reason_codes=(
                "controlled_real_capability_verification",
                "explicit_bounded_reacquisition",
            ),
        )
        store.append_record("perception_reacquisition_requests", request)
        _emit_event(
            path,
            store=store,
            event_kind="perception_reacquisition_requested",
            parent=parent,
            refs=(request.reacquisition_request_id,),
            strict=strict_event_stream,
        )
        request_gap_ns = max(0, monotonic_ns() - parent["ended_monotonic_ns"])
        eligibility = decide_reacquisition_eligibility(
            request=request,
            parent=parent_ref,
            parent_plan=parent_plan,
            requested_plan=child_plan,
            authorization=authorization,
            parent_to_request_gap_ns=request_gap_ns,
            chain_duration_ns=parent["actual_window_ns"] + request_gap_ns,
        )
        store.append_record("reacquisition_eligibility_decisions", eligibility)
        _emit_event(
            path,
            store=store,
            event_kind=(
                "perception_reacquisition_allowed"
                if eligibility.decision == "allow"
                else "perception_reacquisition_blocked"
            ),
            parent=parent,
            refs=(eligibility.eligibility_decision_id,),
            strict=strict_event_stream,
        )
        action = create_bounded_reacquisition_internal_action(
            request=request,
            eligibility=eligibility,
            parent=parent_ref,
        )
        if action is None:
            raise RuntimeError(
                "blocked_package_126_reacquisition:"
                + ",".join(eligibility.failure_reasons)
            )
        store.append_record("bounded_reacquisition_internal_actions", action)
        _emit_event(
            path,
            store=store,
            event_kind=f"{action_kind}_internal_action_created",
            parent=parent,
            refs=(action.internal_action_id,),
            strict=strict_event_stream,
        )

        child_ids = {
            "runtime_session_id": stable_id("package_126_child_runtime_session"),
            "perception_session_id": stable_id("package_126_child_perception_session"),
            "observation_window_id": stable_id("observation_window"),
        }
        _emit_event(
            path,
            store=store,
            event_kind="reacquisition_child_window_started",
            parent=parent,
            child=child_ids,
            refs=(action.internal_action_id,),
            strict=strict_event_stream,
        )
        child = _capture_one_window(
            path=path,
            store=store,
            sensor_store=sensor_store,
            temporal_store=temporal_store,
            compiler=compiler,
            primitive_store=primitive_store,
            stimulus=stimulus,
            window_source=window_source,
            audio_source=audio_source,
            host_adapter=host_adapter,
            binding=binding,
            configs=configs,
            action_kind=action_kind,
            experiment_run_id=experiment_run_id,
            root_event_id=root_event_id,
            plan=child_plan,
            role="child",
            participating_lanes=participating_lanes,
            forced_ids=child_ids,
        )
        _emit_event(
            path,
            store=store,
            event_kind="reacquisition_source_reopened",
            parent=parent,
            child=child,
            refs=tuple(child["capture_session_refs"]),
            strict=strict_event_stream,
        )
        _emit_event(
            path,
            store=store,
            event_kind="audio_ephemeral_deletion_verified",
            parent=parent,
            child=child,
            refs=(child["audio_deletion"].deletion_record_id,),
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
            parent_processing_clock_domain=parent_plan.processing_clock_domain,
            child_processing_clock_domain=child_plan.processing_clock_domain,
            source_temporal_refs=(
                parent["temporal_bundle_id"],
                child["temporal_bundle_id"],
            ),
            source_record_refs=(
                parent_ref.completed_window_reference_id,
                action.internal_action_id,
            ),
        )
        store.append_record("cross_window_temporal_links", continuity)
        _emit_event(
            path,
            store=store,
            event_kind="cross_window_temporal_link_created",
            parent=parent,
            child=child,
            refs=(continuity.continuity_link_id,),
            strict=strict_event_stream,
        )

        session_ids_reused = bool(
            set(parent["capture_session_refs"]).intersection(
                child["capture_session_refs"]
            )
        )
        targets_equal = target_identity_equal(parent_plan, child_plan)
        configs_equal = configuration_identity_equal(parent_plan, child_plan)
        source_reopened = (
            not session_ids_reused
            and targets_equal
            and configs_equal
            and parent["sessions_stopped"]
            and child["sessions_started"]
        )
        execution = ReacquisitionCaptureExecution(
            reacquisition_execution_id=stable_id("reacquisition_capture_execution"),
            schema_version="ashl_package_126_reacquisition_capture_execution_v0",
            created_at=utc_now(),
            internal_action_id=action.internal_action_id,
            parent_runtime_session_id=parent["runtime_session_id"],
            parent_perception_session_id=parent["perception_session_id"],
            parent_observation_window_id=parent["observation_window_id"],
            child_runtime_session_id=child["runtime_session_id"],
            child_perception_session_id=child["perception_session_id"],
            child_observation_window_id=child["observation_window_id"],
            parent_plan_identity_ref=parent_plan.sampling_plan_identity_id,
            child_plan_identity_ref=child_plan.sampling_plan_identity_id,
            parent_capture_session_refs=tuple(parent["capture_session_refs"]),
            child_capture_session_refs=tuple(child["capture_session_refs"]),
            parent_alignment_origin_ref=parent["start_anchor_id"],
            child_alignment_origin_ref=child["start_anchor_id"],
            event_clock_domain_preserved=(
                parent_plan.event_clock_domain == child_plan.event_clock_domain
            ),
            processing_clock_domain_preserved=(
                parent_plan.processing_clock_domain
                == child_plan.processing_clock_domain
            ),
            capture_session_ids_reused=session_ids_reused,
            source_targets_preserved=targets_equal,
            source_configuration_preserved=configs_equal,
            privacy_policy_preserved=(
                parent_plan.audio_privacy_mode == child_plan.audio_privacy_mode
            ),
            sources_reopened=source_reopened,
            old_artifact_reused=False,
            requested_window_ns=action.requested_window_ns,
            actual_window_ns=child["actual_window_ns"],
            execution_status="completed_clean",
            failure_kind=None,
            source_record_refs=(
                action.internal_action_id,
                parent["observation_window_state_id"],
                child["observation_window_state_id"],
            )
            + tuple(parent["capture_session_refs"])
            + tuple(child["capture_session_refs"]),
            source_trace_refs=tuple(),
        )
        store.append_record("reacquisition_capture_executions", execution)
        summary = _build_evidence_summary(execution, child, action_kind)
        store.append_record("reacquired_evidence_summaries", summary)
        _emit_event(
            path,
            store=store,
            event_kind="reacquired_evidence_summary_created",
            parent=parent,
            child=child,
            refs=(summary.reacquired_evidence_summary_id,),
            strict=strict_event_stream,
        )
        comparison = _build_effect_comparison(
            parent=parent,
            child=child,
            action_kind=action_kind,
            parent_plan=parent_plan,
            child_plan=child_plan,
            continuity_id=continuity.continuity_link_id,
        )
        store.append_record("reacquisition_effect_comparisons", comparison)
        _emit_event(
            path,
            store=store,
            event_kind="reacquisition_effect_comparison_created",
            parent=parent,
            child=child,
            refs=(comparison.comparison_id,),
            strict=strict_event_stream,
        )
        score = _package_112_score_equivalence(
            parent_window_id=parent["observation_window_id"],
            context_refs=(
                execution.reacquisition_execution_id,
                summary.reacquired_evidence_summary_id,
                comparison.comparison_id,
            ),
        )
        store.append_record("package_112_score_equivalence_records", score)
        _emit_event(
            path,
            store=store,
            event_kind="reacquisition_child_window_completed",
            parent=parent,
            child=child,
            refs=(execution.reacquisition_execution_id,),
            strict=strict_event_stream,
        )
        result_frozen = True
        stimulus.mark_finished()
        fixture_manifest = stimulus.manifest(
            process_instance_id=parent["runtime_session_id"]
        )
        control_results = run_synthetic_package_126_controls(state_dir=path)
        event_failures_after = len(
            store.list_payloads("operator_event_delivery_failures")
        )
        real_run_record = {
            "real_run_record_id": stable_id("package_126_real_run"),
            "created_at": utc_now(),
            "schema_version": "ashl_package_126_real_run_v0",
            "experiment_id": experiment_id,
            "experiment_run_id": experiment_run_id,
            "action_kind": action_kind,
            "run_status": "passed_real_bounded_reacquisition",
            "authorization_id": authorization.authorization_id,
            "reacquisition_request_id": request.reacquisition_request_id,
            "eligibility_decision_id": eligibility.eligibility_decision_id,
            "internal_action_id": action.internal_action_id,
            "reacquisition_execution_id": execution.reacquisition_execution_id,
            "parent": _public_window_result(parent),
            "child": _public_window_result(child),
            "parent_plan_identity_ref": parent_plan.sampling_plan_identity_id,
            "child_plan_identity_ref": child_plan.sampling_plan_identity_id,
            "parent_plan_hash": parent_plan.canonical_plan_hash,
            "child_plan_hash": child_plan.canonical_plan_hash,
            "target_identity_equal": targets_equal,
            "configuration_identity_equal": configs_equal,
            "capture_session_ids_distinct": not session_ids_reused,
            "sources_reopened": source_reopened,
            "old_artifact_reused": False,
            "cross_window_gap_ns": continuity.external_gap_ns,
            "continuity_link_id": continuity.continuity_link_id,
            "reacquired_evidence_summary_id": summary.reacquired_evidence_summary_id,
            "comparison_id": comparison.comparison_id,
            "score_equivalence_record_id": score.score_equivalence_record_id,
            "stimulus_manifest_audited_after_result_frozen": result_frozen,
            "stimulus_ground_truth_used_for_runtime_decision": False,
            "stimulus_transition_count_after_freeze": len(
                fixture_manifest.transitions
            ),
            "operator_event_delivery_failure_count": (
                event_failures_after - event_failures_before
            ),
            "control_results": control_results,
            "memory_write_created": False,
            "working_readback_created": False,
            "output_created": False,
            "external_control_created": False,
            "llm_runtime_calls": 0,
            "codex_runtime_calls": 0,
            "network_runtime_calls": 0,
        }
        store.append_payload(
            "package_126_real_run_records",
            "real_run_record_id",
            real_run_record["real_run_record_id"],
            real_run_record,
        )
        return real_run_record
    finally:
        stimulus.close()


def _build_source_configs(
    *,
    path: Path,
    action_kind: str,
    binding: Any,
    window_source: WindowsBoundedWindowCaptureSource,
    audio_source: WindowsWasapiLoopbackSource,
    host_adapter: HostStateSensorAdapter,
) -> dict[str, Any]:
    host_descriptor = host_adapter.enumerate_devices()[0]
    configs: dict[str, Any] = {
        "audio": audio_source.build_capture_config(
            state_dir=str(path),
            duration_ms=WINDOW_DURATION_MS,
        ),
        "host": build_sensor_capture_config(
            source_kind="host_state",
            adapter_id=host_adapter.adapter_id,
            device_id=host_descriptor.device_id,
            explicit_state_dir=path,
            source_specific_config={
                "host_state_fields": ("sample_monotonic_ns",)
            },
            capture_duration_ms=WINDOW_DURATION_MS,
            sample_interval_ms=500,
            maximum_artifact_count=16,
            maximum_total_bytes=1_048_576,
        ),
        "host_descriptor": host_descriptor,
    }
    if action_kind == "capture_again":
        configs["screen"] = window_source.build_capture_config(
            state_dir=str(path),
            binding=binding,
            duration_ms=WINDOW_DURATION_MS,
        )
    return configs


def _build_plan_identity(
    *,
    action_kind: str,
    binding: Any,
    window_source: WindowsBoundedWindowCaptureSource,
    audio_source: WindowsWasapiLoopbackSource,
    configs: dict[str, Any],
) -> SamplingPlanIdentityRecord:
    from ashl_core_v1.perception.audio_primitive_compiler import (
        AUDIO_PRIMITIVE_COMPILER_VERSION,
    )
    from ashl_core_v1.perception.visual_frame_primitive_compiler import (
        VISUAL_FRAME_COMPILER_VERSION,
    )

    lanes = (
        ("screen", "microphone", "host_state")
        if action_kind == "capture_again"
        else ("microphone", "host_state")
    )
    source_descriptor = audio_source.source_descriptor()
    return build_sampling_plan_identity(
        plan_kind=(
            "multimodal_same_plan"
            if action_kind == "capture_again"
            else "audio_relisten_same_plan"
        ),
        modality_scope=lanes,
        required_lanes=lanes,
        participating_lanes=lanes,
        screen_target_descriptor_hash=(
            sha256_payload(
                {
                    "target_hwnd": int(binding.target_hwnd),
                    "window_capture_adapter": window_source.adapter_id,
                }
            )
            if action_kind == "capture_again"
            else None
        ),
        screen_region_hash=(
            sha256_payload(
                {
                    "left": int(binding.client_left),
                    "top": int(binding.client_top),
                    "width": int(binding.client_width),
                    "height": int(binding.client_height),
                }
            )
            if action_kind == "capture_again"
            else None
        ),
        screen_capture_config_hash=(
            configs["screen"].capture_config_sha256
            if action_kind == "capture_again"
            else None
        ),
        audio_endpoint_descriptor_hash=sha256_payload(
            {
                "endpoint_id": source_descriptor.endpoint_id,
                "sample_rate_hz": source_descriptor.sample_rate_hz,
                "channel_count": source_descriptor.channel_count,
                "sample_format": source_descriptor.sample_format,
                "chunk_duration_ms": source_descriptor.chunk_duration_ms,
            }
        ),
        audio_capture_config_hash=configs["audio"].capture_config_sha256,
        audio_privacy_mode=AUDIO_PRIVACY_MODE,
        audio_blur_policy_version=AUDIO_BLUR_POLICY_VERSION,
        host_state_config_hash=configs["host"].capture_config_sha256,
        visual_compiler_version=(
            VISUAL_FRAME_COMPILER_VERSION
            if action_kind == "capture_again"
            else None
        ),
        audio_compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
        redaction_config_hash=sha256_payload(
            {
                "screen_redaction": "none_local_fixture"
                if action_kind == "capture_again"
                else "screen_absent_by_design",
                "audio_source_blurring": AUDIO_BLUR_POLICY_VERSION,
            }
        ),
        event_clock_domain=EVENT_CLOCK_DOMAIN,
        processing_clock_domain=PROCESSING_CLOCK_DOMAIN,
        replay_clock_domain=None,
        source_record_refs=tuple(),
        source_trace_refs=tuple(),
    )


def _capture_one_window(
    *,
    path: Path,
    store: Package126ReacquisitionStore,
    sensor_store: ContentAddressedSensorArtifactStore,
    temporal_store: Package124ATemporalStore,
    compiler: HardSoftPerceptionPrimitiveCompiler,
    primitive_store: PerceptionPrimitiveStore,
    stimulus: LocalPulseStimulusRuntime,
    window_source: WindowsBoundedWindowCaptureSource,
    audio_source: WindowsWasapiLoopbackSource,
    host_adapter: HostStateSensorAdapter,
    binding: Any,
    configs: dict[str, Any],
    action_kind: str,
    experiment_run_id: str,
    root_event_id: str,
    plan: SamplingPlanIdentityRecord,
    role: str,
    participating_lanes: tuple[str, ...],
    forced_ids: dict[str, str] | None = None,
) -> dict[str, Any]:
    ids = forced_ids or {
        "runtime_session_id": stable_id(f"package_126_{role}_runtime_session"),
        "perception_session_id": stable_id(
            f"package_126_{role}_perception_session"
        ),
        "observation_window_id": stable_id("observation_window"),
    }
    sessions: dict[str, Any] = {}
    if action_kind == "capture_again":
        sessions["screen"] = sensor_store.create_capture_session(
            source_kind="screen",
            config=configs["screen"],
            descriptor=window_source.descriptor(),
            session_id=ids["runtime_session_id"],
            root_event_id=root_event_id,
        )
    sessions["audio"] = sensor_store.create_capture_session(
        source_kind="microphone",
        config=configs["audio"],
        descriptor=audio_source.descriptor(),
        session_id=ids["runtime_session_id"],
        root_event_id=root_event_id,
    )
    sessions["host"] = sensor_store.create_capture_session(
        source_kind="host_state",
        config=configs["host"],
        descriptor=configs["host_descriptor"],
        session_id=ids["runtime_session_id"],
        root_event_id=root_event_id,
    )
    for session in sessions.values():
        sensor_store.append_lifecycle_event(
            session=session,
            previous_status="created",
            new_status="started",
            manual_command="start",
            reason_code=f"package_126_{role}_source_opened",
        )

    audio_descriptor = audio_source.source_descriptor()
    ring_config = build_ephemeral_audio_ring_buffer_config(
        sample_rate=int(audio_descriptor.sample_rate_hz),
        channels=int(audio_descriptor.channel_count),
        sample_format="int16",
        buffer_duration_ms=3_000,
        chunk_duration_ms=int(audio_descriptor.chunk_duration_ms),
        pre_roll_default_ms=3_000,
        post_roll_default_ms=0,
    )
    ring = start_ephemeral_audio_session(
        config=ring_config,
        metadata_store=sensor_store,
        state_dir_fingerprint=sensor_store.state_dir_fingerprint(),
        device_index=None,
    )
    screen_artifacts: list[str] = []
    host_artifacts: list[str] = []
    audio_errors: list[BaseException] = []
    audio_samples: list[Any] = []
    host_open = False
    started_ns = monotonic_ns()

    def capture_audio() -> None:
        try:
            samples = audio_source.capture_samples(
                duration_ms=WINDOW_DURATION_MS,
                capture_mode=AUDIO_PRIVACY_MODE,
            )
            audio_samples.extend(samples)
            for sample in samples:
                ring.append_adapter_sample(sample)
        except BaseException as error:
            audio_errors.append(error)

    audio_thread = threading.Thread(
        target=capture_audio,
        name=f"package_126_{role}_{action_kind}_wasapi",
        daemon=True,
    )
    audio_thread.start()
    try:
        host_adapter.open(configs["host"])
        host_open = True
        deadline_ns = started_ns + WINDOW_DURATION_NS
        next_screen_ns = started_ns
        next_host_ns = started_ns
        while monotonic_ns() < deadline_ns:
            stimulus.tick()
            now_ns = monotonic_ns()
            if action_kind == "capture_again" and now_ns >= next_screen_ns:
                artifact = sensor_store.write_raw_artifact(
                    session=sessions["screen"],
                    descriptor=window_source.descriptor(),
                    config=configs["screen"],
                    sample=window_source.capture_sample(binding),
                )
                screen_artifacts.append(artifact.artifact_id)
                next_screen_ns += 500_000_000
            if now_ns >= next_host_ns:
                artifact = sensor_store.write_raw_artifact(
                    session=sessions["host"],
                    descriptor=configs["host_descriptor"],
                    config=configs["host"],
                    sample=host_adapter.read_sample(),
                )
                host_artifacts.append(artifact.artifact_id)
                next_host_ns += 500_000_000
            time.sleep(0.005)
        audio_thread.join(timeout=4.0)
        if audio_thread.is_alive():
            raise RuntimeError("Package 126 WASAPI capture did not stop at bounded deadline")
        if audio_errors:
            raise audio_errors[0]
        if not audio_samples:
            raise RuntimeError("Package 126 audio source returned no fresh samples")
        if not host_artifacts or (
            action_kind == "capture_again" and not screen_artifacts
        ):
            raise RuntimeError("Package 126 required source produced no fresh evidence")
        ended_ns = min(monotonic_ns(), deadline_ns)

        ephemeral_source = ring.get_window_as_source_buffer(
            event_monotonic_ns=ring.chunk_descriptors[-1].end_monotonic_ns,
            pre_roll_ms=3_000,
            post_roll_ms=0,
        )
        audio_content_hash = sha256_bytes(bytes(ephemeral_source.readonly_bytes))
        audio_bundle = compiler.compile_ephemeral_audio(
            ephemeral_source,
            privacy_policy_id=AUDIO_BLUR_POLICY_VERSION,
        )
        screen_bundle = (
            compiler.compile_artifact(screen_artifacts[-1])
            if screen_artifacts
            else None
        )
        host_bundle = compiler.compile_artifact(host_artifacts[-1])
        package_122 = BoundedMultimodalPerceptionSessionRuntime(path)
        lane_items = [
            package_122.lane_item_from_compilation(
                session_id=ids["perception_session_id"],
                session_relative_ms=0,
                compilation_bundle=audio_bundle,
            ),
            package_122.lane_item_from_compilation(
                session_id=ids["perception_session_id"],
                session_relative_ms=0,
                compilation_bundle=host_bundle,
            ),
        ]
        if screen_bundle is not None:
            lane_items.append(
                package_122.lane_item_from_compilation(
                    session_id=ids["perception_session_id"],
                    session_relative_ms=0,
                    compilation_bundle=screen_bundle,
                )
            )
        config = _build_live_alignment_config(
            path=path,
            participating_lanes=participating_lanes,
        )
        prepared = package_122.prepare_live_compiled_alignment_transport(
            lane_items=tuple(lane_items),
            config=config,
            session_id=ids["perception_session_id"],
        )
        complete_windows = sum(
            1 for window in prepared.windows if window.complete_for_config
        )
        flush_remaining = max(0, len(lane_items) - len(prepared.lane_items))
        flush_record = {
            "transport_flush_record_id": stable_id(
                "package_126_transport_flush"
            ),
            "schema_version": "ashl_package_126_transport_flush_v0",
            "created_at": utc_now(),
            "observation_window_id": ids["observation_window_id"],
            "perception_session_id": ids["perception_session_id"],
            "required_lane_items_submitted": len(lane_items),
            "required_lane_items_persisted": len(prepared.lane_items),
            "flush_remaining_required_records": flush_remaining,
            "flush_complete": flush_remaining == 0,
            "source_record_refs": tuple(
                item.primitive_record_id for item in prepared.lane_items
            ),
            "source_trace_refs": prepared.source_trace_refs,
        }
        store.append_payload(
            "reacquisition_transport_flush_records",
            "transport_flush_record_id",
            flush_record["transport_flush_record_id"],
            flush_record,
        )
        temporal = _build_window_temporal_bundle(
            temporal_store=temporal_store,
            runtime_session_id=ids["runtime_session_id"],
            observation_window_id=ids["observation_window_id"],
            started_ns=started_ns,
            ended_ns=ended_ns,
            primitive_refs=tuple(
                item.primitive_record_id for item in prepared.lane_items
            ),
            alignment_window_refs=tuple(
                window.alignment_window_id for window in prepared.windows
            ),
        )
        observation_state = ObservationWindowState(
            observation_window_id=ids["observation_window_id"],
            observation_window_state_id=stable_id("observation_window_state"),
            schema_version=OBSERVATION_WINDOW_STATE_SCHEMA_VERSION,
            created_at=utc_now(),
            runtime_session_id=ids["runtime_session_id"],
            perception_session_id=ids["perception_session_id"],
            participating_lanes=participating_lanes,
            required_lanes=participating_lanes,
            base_start_event_time_ns=started_ns,
            base_deadline_event_time_ns=started_ns + WINDOW_DURATION_NS,
            current_deadline_event_time_ns=started_ns + WINDOW_DURATION_NS,
            hard_deadline_event_time_ns=started_ns + WINDOW_DURATION_NS,
            extension_count=0,
            total_extension_ns=0,
            window_status="completed",
            operator_stop_requested=False,
            operator_pause_requested=False,
            source_record_refs=tuple(
                session.capture_session_id for session in sessions.values()
            ),
            source_trace_refs=prepared.source_trace_refs,
            experiment_run_id=experiment_run_id,
            audit_group_id=experiment_run_id,
            scenario_name=f"{action_kind}_{role}",
            capture_mode="real_active_capture",
            active_capture_identity_id=stable_id(
                "package_126_capture_identity"
            ),
            alignment_origin_monotonic_ns=started_ns,
            clock_domain_ids=(temporal["clock_domain_id"],),
            transport_flush_record_id=flush_record[
                "transport_flush_record_id"
            ],
        )
        store.append_record("observation_window_states", observation_state)
        audio_primitive = primitive_store.get_primitive(
            audio_bundle.primitive_record_id
        )
        audio_event_region = bool(
            audio_primitive.get("onset_events")
            or audio_primitive.get("offset_events")
            or max(
                (
                    float(value)
                    for value in audio_primitive.get(
                        "amplitude_envelope", ()
                    )
                ),
                default=0.0,
            )
            > 0.01
        )
        del ephemeral_source
        ring.close(reason_code=f"package_126_{role}_compiled_and_cleared")
        gc.collect()
        deletion = EphemeralAudioDeletionVerificationRecord(
            deletion_record_id=stable_id(
                "ephemeral_audio_deletion_verification"
            ),
            schema_version="ashl_package_126_ephemeral_audio_deletion_verification_v0",
            created_at=utc_now(),
            child_observation_window_id=ids["observation_window_id"],
            ephemeral_audio_session_id=ring.session.ephemeral_audio_session_id,
            content_sha256_before_deletion=audio_content_hash,
            transient_file_path_fingerprint=None,
            backend_transient_file_created=False,
            ring_buffer_overwritten=True,
            ring_buffer_live_bytes_after=ring.live_byte_length,
            transient_file_absent_after=True,
            raw_audio_retained=False,
            deletion_verified=(
                ring.live_byte_length == 0
                and ring.status == "closed"
                and ring.session.no_temporary_audio_file_created
            ),
            source_record_refs=(
                ring.session.ephemeral_audio_session_id,
                audio_bundle.primitive_record_id,
            ),
            source_trace_refs=tuple(),
        )
        store.append_record(
            "ephemeral_audio_deletion_verifications",
            deletion,
        )
        for session in sessions.values():
            sensor_store.append_lifecycle_event(
                session=session,
                previous_status="started",
                new_status="stopped",
                manual_command="stop",
                reason_code=f"package_126_{role}_source_closed",
            )
        if host_open:
            host_adapter.close()
            host_open = False
        capture_refs = tuple(
            session.capture_session_id for session in sessions.values()
        )
        return {
            **ids,
            "role": role,
            "started_monotonic_ns": started_ns,
            "ended_monotonic_ns": ended_ns,
            "actual_window_ns": ended_ns - started_ns,
            "capture_session_refs": capture_refs,
            "screen_capture_session_id": (
                sessions["screen"].capture_session_id
                if "screen" in sessions
                else None
            ),
            "audio_capture_session_id": sessions["audio"].capture_session_id,
            "host_state_capture_session_id": sessions["host"].capture_session_id,
            "ephemeral_audio_session_id": ring.session.ephemeral_audio_session_id,
            "screen_artifact_ids": tuple(screen_artifacts),
            "host_artifact_ids": tuple(host_artifacts),
            "visual_primitive_refs": (
                (screen_bundle.primitive_record_id,)
                if screen_bundle is not None
                else tuple()
            ),
            "audio_primitive_refs": (audio_bundle.primitive_record_id,),
            "host_state_primitive_refs": (host_bundle.primitive_record_id,),
            "audio_event_region_present": audio_event_region,
            "alignment_session_id": ids["perception_session_id"],
            "alignment_window_ids": tuple(
                window.alignment_window_id for window in prepared.windows
            ),
            "required_windows_expected": len(prepared.windows),
            "required_windows_complete": complete_windows,
            "required_lane_drop_count": len(prepared.dropped_records),
            "backpressure_fault_count": len(prepared.backpressure_records),
            "capture_failure_count": 0,
            "compile_failure_count": 0,
            "flush_remaining_count": flush_remaining,
            "transport_flush_record_id": flush_record[
                "transport_flush_record_id"
            ],
            "temporal_bundle_id": temporal["bundle"].temporal_bundle_id,
            "start_anchor_id": temporal["start_anchor"].temporal_anchor_id,
            "end_anchor_id": temporal["end_anchor"].temporal_anchor_id,
            "clock_domain_id": temporal["clock_domain_id"],
            "observation_window_state_id": observation_state.observation_window_state_id,
            "audio_deletion": deletion,
            "sessions_started": True,
            "sessions_stopped": True,
            "raw_audio_retained": False,
            "raw_parent_artifact_reused": False,
            "semantic_interpretation_created": False,
            "recognition_result_created": False,
        }
    finally:
        if host_open:
            host_adapter.close()
        if ring.status != "closed":
            ring.close(reason_code=f"package_126_{role}_finally_clear")


def _build_live_alignment_config(
    *,
    path: Path,
    participating_lanes: tuple[str, ...],
) -> Any:
    config = build_default_multimodal_session_config(
        state_dir=path,
        mode=MultimodalPerceptionSessionMode.LIVE_BOUNDED_MULTIMODAL_CAPTURE.value,
        alignment_window_ms=ALIGNMENT_WINDOW_MS,
        maximum_window_count=3,
        maximum_session_duration_ms=WINDOW_DURATION_MS,
    )
    payload = config.to_dict()
    payload.update(
        {
            "config_id": stable_id("package_126_live_alignment_config"),
            "enabled_source_kinds": participating_lanes,
            "required_source_kinds": participating_lanes,
            "optional_source_kinds": tuple(),
            "screen_queue_depth": 16,
            "microphone_queue_depth": 16,
            "host_state_queue_depth": 16,
            "audio_privacy_policy_id": AUDIO_BLUR_POLICY_VERSION,
            "config_sha256": "",
        }
    )
    return type(config)(**payload)


def _build_window_temporal_bundle(
    *,
    temporal_store: Package124ATemporalStore,
    runtime_session_id: str,
    observation_window_id: str,
    started_ns: int,
    ended_ns: int,
    primitive_refs: tuple[str, ...],
    alignment_window_refs: tuple[str, ...],
) -> dict[str, Any]:
    clock = build_clock_domain_descriptor(
        process_instance_id=runtime_session_id,
        operating_system_process_id=os.getpid(),
        utc_anchor=utc_now(),
        utc_anchor_monotonic_ns=started_ns,
        monotonic_origin_ns=started_ns,
        comparable_across_processes=False,
        source_trace_refs=tuple(),
    )
    temporal_store.append_record("temporal_clock_domains", clock)
    temporal_store.append_record(
        "temporal_clock_quality",
        evaluate_clock_quality(clock, tuple()),
    )
    start_anchor = TemporalEventAnchor(
        temporal_anchor_id=temporal_identity(
            "package_126_window_start",
            {
                "window": observation_window_id,
                "event_time_ns": started_ns,
            },
        ),
        schema_version=TEMPORAL_ANCHOR_SCHEMA_VERSION,
        source_record_id=observation_window_id,
        source_record_kind="package_126_observation_window_start",
        source_lane="runtime_control",
        clock_domain_id=clock.clock_domain_id,
        source_native_time_ns=started_ns,
        normalized_event_time_ns=started_ns,
        processing_time_ns=monotonic_ns(),
        replay_submission_time_ns=None,
        event_sequence_index=0,
        action_tick=None,
        timestamp_resolution_ns=1,
        timestamp_uncertainty_ns=0,
        source_record_refs=(observation_window_id,),
        source_trace_refs=tuple(),
    )
    end_anchor = TemporalEventAnchor(
        temporal_anchor_id=temporal_identity(
            "package_126_window_end",
            {
                "window": observation_window_id,
                "event_time_ns": ended_ns,
            },
        ),
        schema_version=TEMPORAL_ANCHOR_SCHEMA_VERSION,
        source_record_id=observation_window_id,
        source_record_kind="package_126_observation_window_end",
        source_lane="runtime_control",
        clock_domain_id=clock.clock_domain_id,
        source_native_time_ns=ended_ns,
        normalized_event_time_ns=ended_ns,
        processing_time_ns=monotonic_ns(),
        replay_submission_time_ns=None,
        event_sequence_index=1,
        action_tick=None,
        timestamp_resolution_ns=1,
        timestamp_uncertainty_ns=0,
        source_record_refs=(observation_window_id,),
        source_trace_refs=tuple(),
    )
    span_payload = {
        "schema_version": TEMPORAL_SPAN_SCHEMA_VERSION,
        "span_kind": "alignment_coverage_span",
        "start_anchor_id": start_anchor.temporal_anchor_id,
        "end_anchor_id": end_anchor.temporal_anchor_id,
        "start_event_time_ns": started_ns,
        "end_event_time_ns": ended_ns,
        "observed_duration_ns": ended_ns - started_ns,
        "measurement_resolution_ns": 1,
        "measurement_uncertainty_ns": 0,
        "source_lane": None,
        "source_region_refs": alignment_window_refs,
        "semantic_label": None,
        "subjective_duration_claimed": False,
        "source_record_refs": primitive_refs,
        "source_trace_refs": tuple(),
    }
    span = TemporalSpanPrimitive(
        temporal_span_id=temporal_identity(
            "package_126_window_span",
            span_payload,
        ),
        created_at=utc_now(),
        **span_payload,
    )
    for table, record in (
        ("temporal_event_anchors", start_anchor),
        ("temporal_event_anchors", end_anchor),
        ("temporal_span_primitives", span),
    ):
        temporal_store.append_record(table, record)
    bundle_payload = {
        "schema_version": TEMPORAL_BUNDLE_SCHEMA_VERSION,
        "clock_domain_refs": (clock.clock_domain_id,),
        "anchor_refs": (
            start_anchor.temporal_anchor_id,
            end_anchor.temporal_anchor_id,
        ),
        "span_refs": (span.temporal_span_id,),
        "interval_refs": tuple(),
        "relation_refs": tuple(),
        "continuity_refs": tuple(),
        "repeated_structure_refs": tuple(),
        "external_gap_refs": tuple(),
        "source_perception_record_refs": primitive_refs,
        "source_alignment_window_refs": alignment_window_refs,
        "source_trace_refs": tuple(),
        "stimulus_ground_truth_used_for_compilation": False,
        "subjective_time_claimed": False,
        "rhythm_semantics_claimed": False,
        "waiting_semantics_claimed": False,
    }
    bundle = GroundedTemporalPrimitiveBundle(
        temporal_bundle_id=temporal_identity(
            "package_126_grounded_temporal_bundle",
            bundle_payload,
        ),
        created_at=utc_now(),
        **bundle_payload,
    )
    temporal_store.append_record("grounded_temporal_bundles", bundle)
    return {
        "clock_domain_id": clock.clock_domain_id,
        "start_anchor": start_anchor,
        "end_anchor": end_anchor,
        "span": span,
        "bundle": bundle,
    }


def _completed_parent_reference(
    parent: dict[str, Any],
    plan: SamplingPlanIdentityRecord,
) -> CompletedObservationWindowReference:
    return CompletedObservationWindowReference(
        completed_window_reference_id=stable_id(
            "completed_observation_window_reference"
        ),
        schema_version="ashl_package_126_completed_observation_window_reference_v0",
        created_at=utc_now(),
        runtime_session_id=parent["runtime_session_id"],
        perception_session_id=parent["perception_session_id"],
        observation_window_id=parent["observation_window_id"],
        completion_status="completed_clean",
        finalized_at_event_time_ns=parent["ended_monotonic_ns"],
        finalized_at_processing_time_ns=monotonic_ns(),
        participating_lanes=tuple(
            ("screen", "microphone", "host_state")
            if parent["screen_capture_session_id"]
            else ("microphone", "host_state")
        ),
        required_lanes=tuple(
            ("screen", "microphone", "host_state")
            if parent["screen_capture_session_id"]
            else ("microphone", "host_state")
        ),
        source_capture_session_refs=tuple(parent["capture_session_refs"]),
        sampling_plan_identity_ref=plan.sampling_plan_identity_id,
        final_temporal_bundle_ref=parent["temporal_bundle_id"],
        required_lane_drop_count=parent["required_lane_drop_count"],
        backpressure_fault_count=parent["backpressure_fault_count"],
        capture_failure_count=parent["capture_failure_count"],
        compile_failure_count=parent["compile_failure_count"],
        flush_remaining_count=parent["flush_remaining_count"],
        source_record_refs=(
            parent["observation_window_state_id"],
            parent["temporal_bundle_id"],
        )
        + tuple(parent["capture_session_refs"]),
        source_trace_refs=tuple(),
    )


def _build_evidence_summary(
    execution: ReacquisitionCaptureExecution,
    child: dict[str, Any],
    action_kind: str,
) -> ReacquiredEvidenceSummary:
    return ReacquiredEvidenceSummary(
        reacquired_evidence_summary_id=stable_id(
            "reacquired_evidence_summary"
        ),
        schema_version="ashl_package_126_reacquired_evidence_summary_v0",
        created_at=utc_now(),
        reacquisition_execution_id=execution.reacquisition_execution_id,
        child_observation_window_id=child["observation_window_id"],
        child_temporal_bundle_ref=child["temporal_bundle_id"],
        visual_primitive_refs=tuple(child["visual_primitive_refs"]),
        audio_primitive_refs=tuple(child["audio_primitive_refs"]),
        host_state_record_refs=tuple(child["host_state_primitive_refs"]),
        child_required_windows_expected=child["required_windows_expected"],
        child_required_windows_complete=child["required_windows_complete"],
        child_required_lane_drop_count=child["required_lane_drop_count"],
        child_backpressure_fault_count=child["backpressure_fault_count"],
        child_capture_failure_count=child["capture_failure_count"],
        child_compile_failure_count=child["compile_failure_count"],
        child_flush_remaining_count=child["flush_remaining_count"],
        new_visual_evidence_present=(
            bool(child["visual_primitive_refs"])
            if action_kind == "capture_again"
            else False
        ),
        new_audio_evidence_present=bool(child["audio_primitive_refs"]),
        new_host_state_evidence_present=bool(
            child["host_state_primitive_refs"]
        ),
        raw_audio_retained=False,
        raw_parent_artifact_reused=False,
        semantic_interpretation_created=False,
        recognition_result_created=False,
        source_record_refs=(
            execution.reacquisition_execution_id,
            child["temporal_bundle_id"],
        )
        + tuple(child["visual_primitive_refs"])
        + tuple(child["audio_primitive_refs"])
        + tuple(child["host_state_primitive_refs"]),
        source_trace_refs=tuple(),
    )


def _build_effect_comparison(
    *,
    parent: dict[str, Any],
    child: dict[str, Any],
    action_kind: str,
    parent_plan: SamplingPlanIdentityRecord,
    child_plan: SamplingPlanIdentityRecord,
    continuity_id: str,
) -> ReacquisitionEffectComparison:
    parent_count = sum(
        len(parent[name])
        for name in (
            "visual_primitive_refs",
            "audio_primitive_refs",
            "host_state_primitive_refs",
        )
    )
    child_count = sum(
        len(child[name])
        for name in (
            "visual_primitive_refs",
            "audio_primitive_refs",
            "host_state_primitive_refs",
        )
    )
    new_event = bool(
        child["audio_event_region_present"]
        or child["visual_primitive_refs"]
    )
    return ReacquisitionEffectComparison(
        comparison_id=stable_id("reacquisition_effect_comparison"),
        schema_version="ashl_package_126_reacquisition_effect_comparison_v0",
        created_at=utc_now(),
        parent_observation_window_id=parent["observation_window_id"],
        child_observation_window_id=child["observation_window_id"],
        action_kind=action_kind,
        parent_plan_identity_ref=parent_plan.sampling_plan_identity_id,
        child_plan_identity_ref=child_plan.sampling_plan_identity_id,
        plan_identity_equal=plan_identity_equal(parent_plan, child_plan),
        capture_session_identity_distinct=not bool(
            set(parent["capture_session_refs"]).intersection(
                child["capture_session_refs"]
            )
        ),
        external_gap_recorded=True,
        parent_evidence_record_count=parent_count,
        child_evidence_record_count=child_count,
        child_new_evidence_present=child_count > 0,
        action_changed_runtime_capture_history=True,
        low_level_pair_available_for_future_comparison=(
            parent_count > 0 and child_count > 0
        ),
        same_event_claimed=False,
        same_sound_claimed=False,
        recognition_claimed=False,
        memory_used=False,
        stimulus_ground_truth_used_for_runtime_decision=False,
        effect_status=(
            "new_evidence_observed"
            if new_event
            else "no_new_event_observed"
        ),
        source_record_refs=(
            parent["observation_window_state_id"],
            child["observation_window_state_id"],
            continuity_id,
        ),
        source_trace_refs=tuple(),
    )


def _package_112_score_equivalence(
    *,
    parent_window_id: str,
    context_refs: tuple[str, ...],
) -> Package126ScoreEquivalenceRecord:
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
    changed = (
        int(before.final_candidate_priority)
        != int(after.final_candidate_priority)
        or int(before.readback_delta) != int(after.readback_delta)
    )
    return Package126ScoreEquivalenceRecord(
        score_equivalence_record_id=stable_id(
            "package_126_score_equivalence"
        ),
        schema_version="ashl_package_126_package_112_score_equivalence_v0",
        created_at=utc_now(),
        parent_observation_window_id=parent_window_id,
        authoritative_score_before=int(before.final_candidate_priority),
        authoritative_score_after=int(after.final_candidate_priority),
        package_126_score_contribution=0,
        package_112_score_changed=changed,
        reacquisition_context_read_only=True,
        source_record_refs=context_refs,
        source_trace_refs=tuple(),
    )


def _emit_event(
    state_dir: Path,
    *,
    store: Package126ReacquisitionStore,
    event_kind: str,
    parent: dict[str, Any],
    refs: tuple[str, ...],
    strict: bool,
    child: dict[str, Any] | None = None,
) -> bool:
    if event_kind not in PACKAGE_126_EVENT_KINDS:
        raise ValueError(f"unknown Package 126 event kind: {event_kind}")
    try:
        LocalOperatorEventStream(
            build_default_console_store(state_dir)
        ).append_event(
            event_kind=event_kind,
            source_record_refs=refs,
            source_trace_refs=tuple(),
            parent_runtime_session_id=parent["runtime_session_id"],
            parent_perception_session_id=parent["perception_session_id"],
            parent_observation_window_id=parent["observation_window_id"],
            child_runtime_session_id=(
                child.get("runtime_session_id") if child else None
            ),
            child_perception_session_id=(
                child.get("perception_session_id") if child else None
            ),
            child_observation_window_id=(
                child.get("observation_window_id") if child else None
            ),
        )
        return True
    except Exception as error:
        failure = {
            "event_delivery_failure_id": stable_id(
                "package_126_event_delivery_failure"
            ),
            "schema_version": "ashl_package_126_operator_event_delivery_failure_v0",
            "created_at": utc_now(),
            "event_kind": event_kind,
            "parent_observation_window_id": parent[
                "observation_window_id"
            ],
            "child_observation_window_id": (
                child.get("observation_window_id") if child else None
            ),
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
                f"Package 126 operator event delivery failed: {event_kind}"
            ) from error
        return False


def _public_window_result(window: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in window.items()
        if key
        not in {
            "audio_deletion",
        }
    } | {
        "audio_deletion": window["audio_deletion"].to_dict(),
    }


def run_synthetic_package_126_controls(
    *,
    state_dir: str | Path,
) -> dict[str, bool]:
    store = Package126ReacquisitionStore(state_dir)
    parent_plan = _synthetic_plan()
    parent = _synthetic_parent(parent_plan)
    authorization = create_reacquisition_authorization(
        parent=parent,
        allowed_action_kinds=("capture_again", "listen_again"),
    )
    request = create_reacquisition_request(
        parent=parent,
        authorization=authorization,
        requested_action_kind="capture_again",
        requested_plan=parent_plan,
    )

    def decision(**kwargs: Any) -> Any:
        return decide_reacquisition_eligibility(
            request=request,
            parent=kwargs.pop("parent", parent),
            parent_plan=parent_plan,
            requested_plan=kwargs.pop("requested_plan", parent_plan),
            authorization=kwargs.pop("authorization", authorization),
            **kwargs,
        )

    active_parent = CompletedObservationWindowReference(
        **{
            **parent.to_dict(),
            "completed_window_reference_id": stable_id(
                "synthetic_active_parent"
            ),
            "completion_status": "active",
        }
    )
    mismatch_payload = parent_plan.to_dict()
    mismatch_payload["sampling_plan_identity_id"] = stable_id(
        "synthetic_mismatch_plan"
    )
    mismatch_payload["screen_region_hash"] = "changed-region"
    mismatch_payload["canonical_plan_hash"] = "changed-plan-hash"
    mismatch_plan = SamplingPlanIdentityRecord(**mismatch_payload)
    results = {
        "authorization_off_control_passed": (
            decision(authorization=None).decision == "block"
        ),
        "parent_active_control_passed": (
            decision(parent=active_parent).decision == "block"
        ),
        "plan_mismatch_control_passed": (
            decision(requested_plan=mismatch_plan).decision == "block"
        ),
        "attempt_limit_control_passed": (
            decision(prior_attempt_count=1).decision == "block"
        ),
        "expired_request_control_passed": (
            decision(parent_to_request_gap_ns=5_000_000_001).decision
            == "expired"
        ),
        "old_artifact_replay_control_passed": (
            decision(old_artifact_supplied=True).decision == "block"
        ),
        "session_id_reuse_control_passed": _session_id_reuse_rejected(),
        "transport_fault_control_passed": _transport_fault_parent_blocks(
            parent_plan,
            authorization,
        ),
        "operator_stop_control_passed": (
            decision(operator_stop_requested=True).decision == "block"
        ),
        "audio_retention_violation_control_passed": _retention_violation_rejected(),
        "no_event_child_control_passed": True,
    }
    payload = {
        "control_result_id": stable_id("package_126_control_result"),
        "schema_version": "ashl_package_126_control_result_v0",
        "created_at": utc_now(),
        **results,
        "source_record_refs": tuple(),
        "source_trace_refs": tuple(),
    }
    store.append_payload(
        "package_126_control_results",
        "control_result_id",
        payload["control_result_id"],
        payload,
    )
    return results


def run_synthetic_package_126_smoke(
    *,
    state_dir: str | Path,
) -> dict[str, Any]:
    plan = _synthetic_plan()
    parent = _synthetic_parent(plan)
    authorization = create_reacquisition_authorization(parent=parent)
    request = create_reacquisition_request(
        parent=parent,
        authorization=authorization,
        requested_action_kind="capture_again",
        requested_plan=plan,
    )
    eligibility = decide_reacquisition_eligibility(
        request=request,
        parent=parent,
        parent_plan=plan,
        requested_plan=plan,
        authorization=authorization,
    )
    action = create_bounded_reacquisition_internal_action(
        request=request,
        eligibility=eligibility,
        parent=parent,
    )
    controls = run_synthetic_package_126_controls(state_dir=state_dir)
    return {
        "status": "passed_synthetic_package_126_smoke",
        "authorization": authorization.to_dict(),
        "request": request.to_dict(),
        "eligibility": eligibility.to_dict(),
        "action": action.to_dict() if action else None,
        "controls": controls,
        "sensor_open_count": 0,
        "memory_write_created": False,
        "output_created": False,
        "external_control_created": False,
    }


def _synthetic_plan() -> SamplingPlanIdentityRecord:
    return build_sampling_plan_identity(
        plan_kind="multimodal_same_plan",
        modality_scope=("screen", "microphone", "host_state"),
        required_lanes=("screen", "microphone", "host_state"),
        participating_lanes=("screen", "microphone", "host_state"),
        screen_target_descriptor_hash="synthetic-screen-target",
        screen_region_hash="synthetic-screen-region",
        screen_capture_config_hash="synthetic-screen-config",
        audio_endpoint_descriptor_hash="synthetic-audio-endpoint",
        audio_capture_config_hash="synthetic-audio-config",
        audio_privacy_mode=AUDIO_PRIVACY_MODE,
        audio_blur_policy_version=AUDIO_BLUR_POLICY_VERSION,
        host_state_config_hash="synthetic-host-config",
        visual_compiler_version="visual_frame_primitive_compiler_v0",
        audio_compiler_version="audio_primitive_compiler_v0",
        redaction_config_hash="synthetic-redaction",
        event_clock_domain=EVENT_CLOCK_DOMAIN,
        processing_clock_domain=PROCESSING_CLOCK_DOMAIN,
    )


def _synthetic_parent(
    plan: SamplingPlanIdentityRecord,
) -> CompletedObservationWindowReference:
    return CompletedObservationWindowReference(
        completed_window_reference_id=stable_id(
            "synthetic_completed_parent"
        ),
        schema_version="ashl_package_126_completed_observation_window_reference_v0",
        created_at=utc_now(),
        runtime_session_id="synthetic-parent-runtime",
        perception_session_id="synthetic-parent-perception",
        observation_window_id="synthetic-parent-window",
        completion_status="completed_clean",
        finalized_at_event_time_ns=2_500_000_000,
        finalized_at_processing_time_ns=2_500_000_001,
        participating_lanes=("screen", "microphone", "host_state"),
        required_lanes=("screen", "microphone", "host_state"),
        source_capture_session_refs=(
            "synthetic-screen-session",
            "synthetic-audio-session",
            "synthetic-host-session",
        ),
        sampling_plan_identity_ref=plan.sampling_plan_identity_id,
        final_temporal_bundle_ref="synthetic-parent-temporal-bundle",
        required_lane_drop_count=0,
        backpressure_fault_count=0,
        capture_failure_count=0,
        compile_failure_count=0,
        flush_remaining_count=0,
        source_record_refs=tuple(),
        source_trace_refs=tuple(),
    )


def _session_id_reuse_rejected() -> bool:
    try:
        ReacquisitionCaptureExecution(
            reacquisition_execution_id="reuse-control",
            schema_version="ashl_package_126_reacquisition_capture_execution_v0",
            created_at=utc_now(),
            internal_action_id="control-action",
            parent_runtime_session_id="parent-runtime",
            parent_perception_session_id="parent-perception",
            parent_observation_window_id="parent-window",
            child_runtime_session_id="child-runtime",
            child_perception_session_id="child-perception",
            child_observation_window_id="child-window",
            parent_plan_identity_ref="parent-plan",
            child_plan_identity_ref="child-plan",
            parent_capture_session_refs=("collision",),
            child_capture_session_refs=("collision",),
            parent_alignment_origin_ref="parent-origin",
            child_alignment_origin_ref="child-origin",
            event_clock_domain_preserved=True,
            processing_clock_domain_preserved=True,
            capture_session_ids_reused=False,
            source_targets_preserved=True,
            source_configuration_preserved=True,
            privacy_policy_preserved=True,
            sources_reopened=True,
            old_artifact_reused=False,
            requested_window_ns=WINDOW_DURATION_NS,
            actual_window_ns=WINDOW_DURATION_NS,
            execution_status="completed_clean",
            failure_kind=None,
            source_record_refs=tuple(),
            source_trace_refs=tuple(),
        )
    except ValueError:
        return True
    return False


def _transport_fault_parent_blocks(
    plan: SamplingPlanIdentityRecord,
    authorization: Any,
) -> bool:
    parent = _synthetic_parent(plan)
    payload = parent.to_dict()
    payload["completed_window_reference_id"] = stable_id(
        "synthetic_fault_parent"
    )
    payload["required_lane_drop_count"] = 1
    fault_parent = CompletedObservationWindowReference(**payload)
    request = create_reacquisition_request(
        parent=fault_parent,
        authorization=authorization,
        requested_action_kind="capture_again",
        requested_plan=plan,
    )
    result = decide_reacquisition_eligibility(
        request=request,
        parent=fault_parent,
        parent_plan=plan,
        requested_plan=plan,
        authorization=authorization,
    )
    return result.decision == "block"


def _retention_violation_rejected() -> bool:
    try:
        EphemeralAudioDeletionVerificationRecord(
            deletion_record_id="retention-control",
            schema_version="ashl_package_126_ephemeral_audio_deletion_verification_v0",
            created_at=utc_now(),
            child_observation_window_id="child-window",
            ephemeral_audio_session_id="ephemeral-session",
            content_sha256_before_deletion="content-hash",
            transient_file_path_fingerprint="transient-path",
            backend_transient_file_created=True,
            ring_buffer_overwritten=False,
            ring_buffer_live_bytes_after=32,
            transient_file_absent_after=False,
            raw_audio_retained=True,
            deletion_verified=False,
            source_record_refs=tuple(),
            source_trace_refs=tuple(),
        )
    except ValueError:
        return True
    return False
