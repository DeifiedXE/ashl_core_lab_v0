"""Package 123 real perception two-cycle runtime orchestration."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

from ashl_core_v1.perception.hard_soft_perception_primitive_compiler import compiler_ids
from ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime import BoundedMultimodalPerceptionSessionRuntime
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import (
    SensorCaptureError,
    build_sensor_capture_config,
    monotonic_ns,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.host_state_sensor_adapter import HostStateSensorAdapter
from ashl_core_v1.runtime.local_pulse_stimulus_runtime import LocalPulseStimulusRuntime
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
    TIMELINE_INPUT_REF_SCHEMA_VERSION,
    ArtifactBackedPerceptionTimelineManifest,
    PerceptionTimelineInputRef,
)
from ashl_core_v1.runtime.package_123_cycle_store import Package123CycleStore
from ashl_core_v1.runtime.package_123_preflight import build_package_123_multimodal_config, run_package_123_preflight
from ashl_core_v1.runtime.package_123_types import (
    AUDIT_SCHEMA_VERSION,
    CYCLE_RECORD_SCHEMA_VERSION,
    EXPERIMENT_ID,
    MAX_CAPTURE_DURATION_MS,
    READBACK_INFLUENCE_SCHEMA_VERSION,
    READBACK_TIMING_SCHEMA_VERSION,
    TWO_CYCLE_COMPARISON_SCHEMA_VERSION,
    Package123CycleRecord,
    Package123TwoCycleComparisonRecord,
    RealPerceptionReadbackInfluenceRecord,
    ReadbackLoadTimingRecord,
    build_source_profile,
    current_pid,
    new_experiment_run_id,
    new_process_instance_id,
)
from ashl_core_v1.runtime.package_123_transport_integrity import (
    HOST_STATE_INTERVAL_MS,
    REPLAY_SPEED,
    Package123RerunLineageRecord,
    Package123TransportSoakRecord,
    RERUN_LINEAGE_SCHEMA_VERSION,
    TRANSPORT_SOAK_SCHEMA_VERSION,
    build_transport_configuration_hash,
    build_transport_integrity_records,
)
from ashl_core_v1.runtime.teacher_gated_session_resume_commit import TeacherGatedSessionResumeCommitRuntime
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore
from ashl_core_v1.runtime.session_learning_evidence_identity import FULL_COMMIT_APPROVAL_SCOPE
from ashl_core_v1.runtime.windows_bounded_window_capture_source import WindowsBoundedWindowCaptureSource
from ashl_core_v1.runtime.windows_wasapi_loopback_source import WindowsWasapiLoopbackSource


def run_cycle_one(
    *,
    state_dir: str | Path,
    render_endpoint: str = "default",
    allow_dirty_tree: bool = False,
    require_passed_transport_soak: bool = False,
) -> dict[str, object]:
    path = Path(state_dir)
    _assert_no_unresolved_previous_cycle_one(path)
    experiment_run_id = new_experiment_run_id()
    process_instance_id = new_process_instance_id()
    config = build_package_123_multimodal_config(state_dir=path)
    expected_config_hash = package_123_transport_configuration_hash(config=config, render_endpoint=render_endpoint)
    if require_passed_transport_soak:
        _assert_passed_transport_soak(path, expected_config_hash)
    preflight = run_package_123_preflight(
        state_dir=path,
        render_endpoint=render_endpoint,
        cycle_index=1,
        experiment_run_id=experiment_run_id,
        allow_dirty_tree=allow_dirty_tree,
    )
    if preflight.preflight_status != "passed":
        _append_operator_status_log(
            path,
            level="error",
            event_kind="package_123_cycle_1_preflight_blocked",
            message=f"Cycle 1 preflight blocked: {', '.join(preflight.failure_reasons) or 'preflight blocked'}.",
            source_record_refs=(preflight.preflight_id,),
        )
        return {"status": "blocked_preflight", "preflight": preflight.to_dict()}
    capture = capture_package_123_sources(
        state_dir=path,
        experiment_run_id=experiment_run_id,
        process_instance_id=process_instance_id,
        render_endpoint=render_endpoint,
    )
    prepared, runtime = _prepare_package_122_transport(path, capture["manifest"], config=config)
    integrity = _persist_transport_integrity(
        path,
        experiment_run_id=experiment_run_id,
        cycle_index=1,
        prepared_transport=prepared,
        configuration_hash=expected_config_hash,
        source_capture_session_ids=tuple(str(item) for item in capture.get("capture_session_ids", ()) or ()),
    )
    summary = integrity["integrity_summary"]
    if not summary.teacher_review_eligible:
        cycle = _build_transport_blocked_cycle_record(
            cycle_index=1,
            experiment_run_id=experiment_run_id,
            process_instance_id=process_instance_id,
            preflight_id=preflight.preflight_id,
            capture=capture,
            prepared_transport=prepared,
        )
        Package123CycleStore(path).append_cycle_record(cycle)
        _append_operator_status_log(
            path,
            level="error",
            event_kind="package_123_transport_validation_failed",
            message="Cycle 1 transport validation failed before teacher review.",
            source_record_refs=(summary.integrity_summary_id,),
        )
        return {
            "status": "blocked_transport_integrity",
            "cycle_record": cycle.to_dict(),
            "transport_integrity_summary": summary.to_dict(),
            "teacher_review_created": False,
        }
    result = _run_prepared_package_122_session(runtime, prepared, working_readback_snapshot=None)
    if not result.stopped_at_teacher_gate or not result.package_115_session_id:
        raise RuntimeError("Cycle 1 did not reach WAITING_TEACHER_REVIEW")
    TeacherGatedSessionResumeCommitRuntime().persist_waiting_session(
        runtime.embodied_runtime,
        result.package_115_session_id,
        path,
    )
    cycle = _build_cycle_record(
        cycle_index=1,
        experiment_run_id=experiment_run_id,
        process_instance_id=process_instance_id,
        preflight_id=preflight.preflight_id,
        capture=capture,
        result=result,
        readback_loaded_before_event=False,
        readback_record_refs=tuple(),
    )
    store = Package123CycleStore(path)
    store.append_cycle_record(cycle)
    _append_rerun_lineage_if_rejected_cycle_exists(path, cycle)
    _append_operator_status_log(
        path,
        level="notice",
        event_kind="package_123_cycle_1_waiting_teacher_review",
        message="Cycle 1 waiting for teacher review.",
        source_record_refs=tuple(item for item in (cycle.cycle_record_id, getattr(summary, "integrity_summary_id", "")) if item),
    )
    return {
        "status": "cycle_1_waiting_teacher_review",
        "cycle_record": cycle.to_dict(),
        "pending_teacher_review_id": cycle.pending_teacher_review_id,
        "bounded_runtime_session_id": cycle.bounded_runtime_session_id,
        "transport_integrity_summary": summary.to_dict(),
    }


def review_cycle_one(
    *,
    state_dir: str | Path,
    decision: str,
    reviewer: str,
    approval_text: str | None,
    confirm: bool,
    pending_review_id: str | None = None,
    evidence_snapshot_id: str | None = None,
    evidence_identity: str | None = None,
    required_scope: str | None = None,
    allowed_interpretation_scope: str | None = None,
) -> dict[str, object]:
    if not confirm:
        raise ValueError("review-cycle-1 requires --confirm")
    path = Path(state_dir)
    cycle = Package123CycleStore(path).latest_cycle_record(1)
    if not cycle:
        raise RuntimeError("no Cycle 1 record found")
    session_id = str(cycle["bounded_runtime_session_id"])
    pending_id = str(cycle["pending_teacher_review_id"])
    if pending_review_id is not None and pending_review_id != pending_id:
        raise ValueError("pending review ID does not match latest Cycle 1 teacher target")
    store = TeacherGatedSessionStore(path)
    review = store.get_pending_review(pending_id)
    review_snapshot_id = getattr(review, "evidence_snapshot_id", None)
    if review_snapshot_id:
        snapshot = store.load_evidence_snapshot(review_snapshot_id)
    else:
        snapshot = type(
            "SnapshotShim",
            (),
            {
                "evidence_snapshot_id": evidence_snapshot_id or "",
                "evidence_identity_sha256": getattr(review, "evidence_identity_sha256"),
            },
        )()
    if evidence_snapshot_id is not None and evidence_snapshot_id != snapshot.evidence_snapshot_id:
        raise ValueError("evidence snapshot ID does not match persisted teacher target")
    if evidence_identity is not None and evidence_identity != snapshot.evidence_identity_sha256:
        raise ValueError("evidence identity hash does not match persisted evidence")
    if required_scope is not None and required_scope != FULL_COMMIT_APPROVAL_SCOPE:
        raise ValueError("required approval scope does not match Package 123 full commit scope")
    if allowed_interpretation_scope is not None and allowed_interpretation_scope != "low_level_observed_multimodal_pattern_only":
        raise ValueError("allowed interpretation scope does not match Package 123 review boundary")
    runtime = TeacherGatedSessionResumeCommitRuntime()
    normalized = "approved" if decision in {"approve", "approved"} else "rejected" if decision in {"reject", "rejected"} else decision
    if normalized == "approved" and not approval_text:
        raise ValueError("approved Package 123 review requires explicit --approval-text")
    if normalized == "rejected" and not approval_text:
        raise ValueError("rejected Package 123 review requires explicit --reason/--approval-text")
    teacher_note = approval_text or "Rejected Package 123 Cycle 1 evidence."
    reason_codes = (
        "package_123_teacher_review",
        f"reviewer:{reviewer}",
        f"pending_review:{pending_id}",
        f"evidence_snapshot:{snapshot.evidence_snapshot_id}",
        f"evidence_identity:{snapshot.evidence_identity_sha256}",
        f"required_scope:{FULL_COMMIT_APPROVAL_SCOPE}",
        "allowed_interpretation_scope:low_level_observed_multimodal_pattern_only",
    )
    decision_record = runtime.apply_teacher_decision(
        session_id,
        pending_id,
        normalized,
        reason_codes,
        teacher_note,
        path,
        approval_scope=FULL_COMMIT_APPROVAL_SCOPE if normalized == "approved" else None,
        expected_evidence_hash=evidence_identity or review.evidence_identity_sha256,
    )
    if normalized == "approved":
        commit_result = runtime.resume_after_approval(session_id, decision_record.teacher_decision_id, path)
    else:
        commit_result = runtime.close_rejected_session(session_id, decision_record.teacher_decision_id, path)
        _append_operator_status_log(
            path,
            level="notice",
            event_kind="package_123_previous_cycle_1_evidence_rejected",
            message="Previous Cycle 1 evidence rejected.",
            source_record_refs=(decision_record.teacher_decision_id, pending_id),
            source_trace_refs=decision_record.source_trace_refs,
        )
    return {
        "status": "cycle_1_committed" if str(commit_result.final_status).lower() == "committed" else "cycle_1_closed_without_commit",
        "teacher_decision": decision_record.to_dict(),
        "commit_result": commit_result.to_dict(),
    }


def run_cycle_two(
    *,
    state_dir: str | Path,
    render_endpoint: str = "default",
    allow_dirty_tree: bool = False,
) -> dict[str, object]:
    path = Path(state_dir)
    store = Package123CycleStore(path)
    cycle_one = store.latest_cycle_record(1)
    if not cycle_one:
        raise RuntimeError("Cycle 2 requires a completed Cycle 1 record")
    teacher_store = TeacherGatedSessionStore(path)
    active_readback = teacher_store.load_active_working_readback()
    if not active_readback:
        raise RuntimeError("Cycle 2 requires active working readback from approved Cycle 1")
    readback_loaded_at = monotonic_ns()
    experiment_run_id = new_experiment_run_id()
    process_instance_id = new_process_instance_id()
    preflight = run_package_123_preflight(
        state_dir=path,
        render_endpoint=render_endpoint,
        cycle_index=2,
        experiment_run_id=experiment_run_id,
        allow_dirty_tree=allow_dirty_tree,
    )
    if preflight.preflight_status != "passed":
        _append_operator_status_log(
            path,
            level="error",
            event_kind="package_123_cycle_2_preflight_blocked",
            message=f"Cycle 2 preflight blocked: {', '.join(preflight.failure_reasons) or 'preflight blocked'}.",
            source_record_refs=(preflight.preflight_id,),
        )
        return {"status": "blocked_preflight", "preflight": preflight.to_dict()}
    capture_started_at = monotonic_ns()
    capture = capture_package_123_sources(
        state_dir=path,
        experiment_run_id=experiment_run_id,
        process_instance_id=process_instance_id,
        render_endpoint=render_endpoint,
    )
    stimulus_started = int(capture["stimulus_started_monotonic_ns"])
    result, runtime = _run_package_122_session(path, capture["manifest"], working_readback_snapshot=active_readback)
    candidate_evaluated_at = monotonic_ns()
    if not result.stopped_at_teacher_gate or not result.package_115_session_id:
        raise RuntimeError("Cycle 2 did not reach WAITING_TEACHER_REVIEW")
    embodied_records = runtime.embodied_runtime._records[result.package_115_session_id]
    influence = _build_influence_record(embodied_records, active_readback)
    timing = ReadbackLoadTimingRecord(
        timing_record_id=stable_id("package_123_readback_load_timing"),
        schema_version=READBACK_TIMING_SCHEMA_VERSION,
        cycle_record_id="pending_cycle_record",
        readback_loaded_monotonic_ns=readback_loaded_at,
        capture_started_monotonic_ns=capture_started_at,
        stimulus_started_monotonic_ns=stimulus_started,
        candidate_evaluated_monotonic_ns=candidate_evaluated_at,
        loaded_before_capture=readback_loaded_at <= capture_started_at,
        loaded_before_stimulus=readback_loaded_at <= stimulus_started,
        loaded_before_candidate_evaluation=readback_loaded_at <= candidate_evaluated_at,
        readback_record_refs=tuple(str(item.get("working_readback_commit_id")) for item in active_readback),
    )
    cycle = _build_cycle_record(
        cycle_index=2,
        experiment_run_id=experiment_run_id,
        process_instance_id=process_instance_id,
        preflight_id=preflight.preflight_id,
        capture=capture,
        result=result,
        readback_loaded_before_event=True,
        readback_record_refs=timing.readback_record_refs,
    )
    timing_payload = timing.to_dict()
    timing = ReadbackLoadTimingRecord.from_dict({**timing_payload, "cycle_record_id": cycle.cycle_record_id})
    comparison = Package123TwoCycleComparisonRecord(
        comparison_id=stable_id("package_123_two_cycle_comparison"),
        schema_version=TWO_CYCLE_COMPARISON_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_id=EXPERIMENT_ID,
        cycle_1_record_id=str(cycle_one["cycle_record_id"]),
        cycle_2_record_id=cycle.cycle_record_id,
        cycle_1_process_instance_id=str(cycle_one["process_instance_id"]),
        cycle_2_process_instance_id=cycle.process_instance_id,
        process_instances_different=str(cycle_one["process_instance_id"]) != cycle.process_instance_id,
        raw_artifacts_different=not set(cycle_one.get("screen_artifact_refs", ())).intersection(set(cycle.screen_artifact_refs)),
        runtime_sessions_different=str(cycle_one["bounded_runtime_session_id"]) != cycle.bounded_runtime_session_id,
        cycle_1_commit_present=True,
        cycle_2_readback_loaded_before_event=True,
        readback_influence_record_id=influence.influence_record_id,
        readback_contribution_nonzero=influence.readback_contribution > 0,
        cycle_2_final_state=cycle.final_session_state,
        no_llm_runtime=True,
        no_codex_runtime=True,
        no_network_runtime=True,
    )
    store.append_readback_influence(influence)
    store.append_readback_load_timing(timing)
    store.append_cycle_record(cycle)
    store.append_two_cycle_comparison(comparison)
    return {
        "status": "cycle_2_waiting_teacher_review",
        "cycle_record": cycle.to_dict(),
        "readback_load_timing": timing.to_dict(),
        "readback_influence": influence.to_dict(),
        "comparison": comparison.to_dict(),
    }


def capture_package_123_sources(
    *,
    state_dir: str | Path,
    experiment_run_id: str,
    process_instance_id: str,
    render_endpoint: str,
    duration_ms: int = MAX_CAPTURE_DURATION_MS,
) -> dict[str, object]:
    path = Path(state_dir)
    sensor_store = ContentAddressedSensorArtifactStore(path)
    stimulus = LocalPulseStimulusRuntime(experiment_run_id=experiment_run_id, render_endpoint_id=render_endpoint)
    window_source = WindowsBoundedWindowCaptureSource()
    loopback_source = WindowsWasapiLoopbackSource(endpoint_id=render_endpoint)
    host_adapter = HostStateSensorAdapter()
    audio_samples: list[Any] = []
    audio_error: list[BaseException] = []
    screen_artifacts: list[str] = []
    host_artifacts: list[str] = []
    audio_artifacts: list[str] = []
    try:
        stimulus.open()
        binding = window_source.bind_by_title(experiment_run_id=experiment_run_id, window_title=stimulus.window_title)
        if binding.binding_status != "bound":
            raise SensorCaptureError("device_unavailable", f"stimulus window binding failed: {binding.binding_status}")
        screen_config = window_source.build_capture_config(state_dir=str(path), binding=binding, duration_ms=duration_ms)
        screen_session = sensor_store.create_capture_session(source_kind="screen", config=screen_config, descriptor=window_source.descriptor())
        audio_config = loopback_source.build_capture_config(state_dir=str(path), duration_ms=duration_ms)
        audio_session = sensor_store.create_capture_session(source_kind="microphone", config=audio_config, descriptor=loopback_source.descriptor())
        host_descriptor = host_adapter.enumerate_devices()[0]
        host_config = build_sensor_capture_config(
            source_kind="host_state",
            adapter_id=host_adapter.adapter_id,
            device_id=host_descriptor.device_id,
            explicit_state_dir=path,
            source_specific_config={"host_state_fields": ("sample_monotonic_ns",)},
            capture_duration_ms=duration_ms,
            sample_interval_ms=HOST_STATE_INTERVAL_MS,
            maximum_artifact_count=64,
            maximum_total_bytes=1_048_576,
        )
        host_session = sensor_store.create_capture_session(source_kind="host_state", config=host_config, descriptor=host_descriptor)
        sensor_store.append_lifecycle_event(session=screen_session, previous_status="created", new_status="started", manual_command="start", reason_code="package_123_cycle_capture_started")
        sensor_store.append_lifecycle_event(session=audio_session, previous_status="created", new_status="started", manual_command="start", reason_code="package_123_cycle_capture_started")
        sensor_store.append_lifecycle_event(session=host_session, previous_status="created", new_status="started", manual_command="start", reason_code="package_123_cycle_capture_started")

        def capture_audio() -> None:
            try:
                audio_samples.extend(loopback_source.capture_samples(duration_ms=duration_ms))
            except BaseException as error:
                audio_error.append(error)

        audio_thread = threading.Thread(target=capture_audio, name="package_123_loopback_capture", daemon=True)
        audio_thread.start()
        host_adapter.open(host_config)
        started = monotonic_ns()
        next_screen = started
        next_host = started
        deadline = started + int(duration_ms) * 1_000_000
        while monotonic_ns() < deadline:
            stimulus.tick()
            now = monotonic_ns()
            if now >= next_screen:
                artifact = sensor_store.write_raw_artifact(
                    session=screen_session,
                    descriptor=window_source.descriptor(),
                    config=screen_config,
                    sample=window_source.capture_sample(binding),
                )
                screen_artifacts.append(artifact.artifact_id)
                next_screen += 100_000_000
            if now >= next_host:
                artifact = sensor_store.write_raw_artifact(
                    session=host_session,
                    descriptor=host_descriptor,
                    config=host_config,
                    sample=host_adapter.read_sample(),
                )
                host_artifacts.append(artifact.artifact_id)
                next_host += HOST_STATE_INTERVAL_MS * 1_000_000
            time.sleep(0.005)
        stimulus._finished_monotonic_ns = monotonic_ns()
        audio_thread.join(timeout=3.0)
        if audio_error:
            raise audio_error[0]
        for sample in audio_samples:
            artifact = sensor_store.write_raw_artifact(
                session=audio_session,
                descriptor=loopback_source.descriptor(),
                config=audio_config,
                sample=sample,
            )
            audio_artifacts.append(artifact.artifact_id)
        host_adapter.close()
        sensor_store.append_lifecycle_event(session=screen_session, previous_status="started", new_status="stopped", manual_command="stop", reason_code="package_123_cycle_capture_stopped")
        sensor_store.append_lifecycle_event(session=audio_session, previous_status="started", new_status="stopped", manual_command="stop", reason_code="package_123_cycle_capture_stopped")
        sensor_store.append_lifecycle_event(session=host_session, previous_status="started", new_status="stopped", manual_command="stop", reason_code="package_123_cycle_capture_stopped")
        manifest = stimulus.manifest(process_instance_id=process_instance_id)
        profile = build_source_profile(
            experiment_run_id=experiment_run_id,
            screen_binding_id=binding.binding_id,
            audio_source_descriptor_id=loopback_source.source_descriptor().source_descriptor_id,
        )
        package_store = Package123CycleStore(path)
        package_store.append_window_binding(binding)
        package_store.append_loopback_descriptor(loopback_source.source_descriptor())
        package_store.append_source_profile(profile)
        package_store.append_stimulus_manifest(manifest)
        return {
            "binding": binding,
            "source_profile": profile,
            "stimulus_manifest": manifest,
            "stimulus_started_monotonic_ns": manifest.stimulus_started_monotonic_ns,
            "screen_artifact_ids": tuple(screen_artifacts),
            "audio_artifact_ids": tuple(audio_artifacts),
            "host_state_artifact_ids": tuple(host_artifacts),
            "capture_session_ids": (
                screen_session.capture_session_id,
                audio_session.capture_session_id,
                host_session.capture_session_id,
            ),
            "manifest": _build_replay_manifest(path, screen_artifacts, audio_artifacts, host_artifacts, started),
            "source_trace_refs": tuple(),
        }
    finally:
        stimulus.close()


def _run_package_122_session(
    state_dir: Path,
    manifest: ArtifactBackedPerceptionTimelineManifest,
    *,
    working_readback_snapshot: tuple[dict[str, Any], ...] | None,
):
    runtime = BoundedMultimodalPerceptionSessionRuntime(state_dir)
    config = build_package_123_multimodal_config(state_dir=state_dir)
    result = runtime.run_artifact_backed_alignment_replay(
        manifest,
        config=config,
        working_readback_snapshot=working_readback_snapshot,
    )
    return result, runtime


def _prepare_package_122_transport(
    state_dir: Path,
    manifest: ArtifactBackedPerceptionTimelineManifest,
    *,
    config: Any,
):
    runtime = BoundedMultimodalPerceptionSessionRuntime(state_dir)
    prepared = runtime.prepare_artifact_backed_alignment_replay_transport(manifest, config=config)
    return prepared, runtime


def _run_prepared_package_122_session(
    runtime: BoundedMultimodalPerceptionSessionRuntime,
    prepared: Any,
    *,
    working_readback_snapshot: tuple[dict[str, Any], ...] | None,
):
    return runtime.run_prepared_artifact_replay_to_teacher_gate(
        prepared,
        working_readback_snapshot=working_readback_snapshot,
    )


def _build_replay_manifest(
    state_dir: Path,
    screen_ids: list[str],
    audio_ids: list[str],
    host_ids: list[str],
    timeline_start_ns: int,
) -> ArtifactBackedPerceptionTimelineManifest:
    sensor_store = ContentAddressedSensorArtifactStore(state_dir)
    ids = compiler_ids()
    refs: list[PerceptionTimelineInputRef] = []
    window_centers = tuple(range(250, MAX_CAPTURE_DURATION_MS, 500))
    transition_centers = (2_100, 2_500, 3_100, 3_500, 4_100, 4_500, 5_100, 5_500)
    selected_by_source = {
        "screen": _select_nearest_artifacts(sensor_store, screen_ids, timeline_start_ns, window_centers + transition_centers),
        "microphone": _select_nearest_artifacts(sensor_store, audio_ids, timeline_start_ns, window_centers),
        "host_state": _select_nearest_artifacts(sensor_store, host_ids, timeline_start_ns, window_centers),
    }
    for source_kind, artifact_ids in (("host_state", selected_by_source["host_state"]), ("screen", selected_by_source["screen"]), ("microphone", selected_by_source["microphone"])):
        for artifact_id in artifact_ids:
            artifact = sensor_store.get_artifact(artifact_id)
            offset_ms = max(0, int((int(artifact["captured_at_monotonic_ns"]) - timeline_start_ns) / 1_000_000))
            refs.append(
                PerceptionTimelineInputRef(
                    input_ref_id=stable_id("package_123_timeline_input_ref"),
                    schema_version=TIMELINE_INPUT_REF_SCHEMA_VERSION,
                    source_kind=source_kind,
                    source_artifact_id=artifact_id,
                    source_ephemeral_buffer_id=None,
                    replay_relative_offset_ms=offset_ms,
                    compiler_id=_compiler_id_for_source(source_kind, ids),
                    compiler_config_id="canonical_package_121_default",
                    privacy_policy_id="grounding_conservative_v0" if source_kind == "microphone" else None,
                    source_trace_refs=tuple(str(item) for item in (artifact.get("source_trace_refs") or (artifact.get("trace_envelope_id"),))),
                )
            )
    refs.sort(key=lambda item: item.replay_relative_offset_ms)
    return ArtifactBackedPerceptionTimelineManifest(
        manifest_id=stable_id("package_123_artifact_backed_manifest"),
        schema_version=ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
        created_at=utc_now(),
        input_refs=tuple(refs),
        source_artifacts_are_real=True,
        sources_captured_simultaneously=False,
        deterministic_replay=True,
        manifest_sha256="",
    )


def _select_nearest_artifacts(
    sensor_store: ContentAddressedSensorArtifactStore,
    artifact_ids: list[str],
    timeline_start_ns: int,
    target_offsets_ms: tuple[int, ...],
) -> list[str]:
    if not artifact_ids:
        return []
    offsets: list[tuple[str, int]] = []
    for artifact_id in artifact_ids:
        artifact = sensor_store.get_artifact(artifact_id)
        offset_ms = max(0, int((int(artifact["captured_at_monotonic_ns"]) - timeline_start_ns) / 1_000_000))
        offsets.append((artifact_id, offset_ms))
    selected: dict[str, int] = {}
    for target in target_offsets_ms:
        artifact_id, offset = min(offsets, key=lambda item: abs(item[1] - target))
        selected[artifact_id] = offset
    return [artifact_id for artifact_id, _ in sorted(selected.items(), key=lambda item: item[1])]


def _compiler_id_for_source(source_kind: str, ids: dict[str, str]) -> str:
    if source_kind == "screen":
        return ids["visual_frame"]
    if source_kind == "microphone":
        return ids["audio"]
    if source_kind == "host_state":
        return ids["host_state"]
    raise ValueError("unsupported Package 123 source kind")


def package_123_transport_configuration_hash(
    *,
    config: Any,
    render_endpoint: str,
) -> str:
    return build_transport_configuration_hash(
        config=config,
        render_endpoint=render_endpoint,
        screen_binding_id="package_123_local_pulse_stimulus_window",
        audio_source_descriptor_id=f"render_endpoint:{render_endpoint}",
        replay_speed=REPLAY_SPEED,
    )


def run_transport_soak(
    *,
    state_dir: str | Path,
    render_endpoint: str = "default",
    allow_dirty_tree: bool = False,
) -> dict[str, object]:
    path = Path(state_dir)
    _append_operator_status_log(
        path,
        level="notice",
        event_kind="package_123_transport_soak_running",
        message="Transport soak running.",
    )
    experiment_run_id = new_experiment_run_id()
    process_instance_id = new_process_instance_id()
    preflight = run_package_123_preflight(
        state_dir=path,
        render_endpoint=render_endpoint,
        cycle_index=0,
        experiment_run_id=experiment_run_id,
        allow_dirty_tree=allow_dirty_tree,
    )
    if preflight.preflight_status != "passed":
        _append_operator_status_log(
            path,
            level="error",
            event_kind="package_123_transport_soak_failed",
            message=f"Transport soak failed: {', '.join(preflight.failure_reasons) or 'preflight blocked'}.",
            source_record_refs=(preflight.preflight_id,),
        )
        return {"status": "blocked_preflight", "preflight": preflight.to_dict()}
    capture = capture_package_123_sources(
        state_dir=path,
        experiment_run_id=experiment_run_id,
        process_instance_id=process_instance_id,
        render_endpoint=render_endpoint,
    )
    config = build_package_123_multimodal_config(state_dir=path)
    configuration_hash = package_123_transport_configuration_hash(config=config, render_endpoint=render_endpoint)
    prepared, runtime = _prepare_package_122_transport(path, capture["manifest"], config=config)
    integrity = _persist_transport_integrity(
        path,
        experiment_run_id=experiment_run_id,
        cycle_index=0,
        prepared_transport=prepared,
        configuration_hash=configuration_hash,
        source_capture_session_ids=tuple(str(item) for item in capture.get("capture_session_ids", ()) or ()),
    )
    summary = integrity["integrity_summary"]
    soak = Package123TransportSoakRecord(
        transport_soak_id=stable_id("package_123_transport_soak"),
        schema_version=TRANSPORT_SOAK_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_run_id=experiment_run_id,
        process_instance_id=process_instance_id,
        configuration_hash=configuration_hash,
        duration_ms=MAX_CAPTURE_DURATION_MS,
        replay_speed=REPLAY_SPEED,
        screen_record_count=len(tuple(capture["screen_artifact_ids"])),
        audio_record_count=len(tuple(capture["audio_artifact_ids"])),
        host_state_record_count=len(tuple(capture["host_state_artifact_ids"])),
        integrity_summary_id=summary.integrity_summary_id,
        learning_session_created=False,
        teacher_gate_created=False,
        memory_commit_created=False,
        preflight_transport_evidence_only=True,
        soak_status="passed" if summary.teacher_review_eligible else "blocked",
        source_trace_refs=tuple(prepared.source_trace_refs),
    )
    Package123CycleStore(path).append_transport_soak(soak)
    _append_operator_status_log(
        path,
        level="notice" if soak.soak_status == "passed" else "error",
        event_kind="package_123_transport_soak_passed" if soak.soak_status == "passed" else "package_123_transport_soak_failed",
        message="Transport soak passed: zero required-lane drops." if soak.soak_status == "passed" else f"Transport soak failed: {', '.join(summary.failure_reasons) or 'transport integrity blocked'}.",
        source_record_refs=(soak.transport_soak_id, summary.integrity_summary_id),
        source_trace_refs=soak.source_trace_refs,
    )
    return {
        "status": "transport_soak_passed" if soak.soak_status == "passed" else "transport_soak_blocked",
        "transport_soak": soak.to_dict(),
        "transport_integrity_summary": summary.to_dict(),
        "teacher_gate_created": False,
        "learning_session_created": False,
        "memory_commit_created": False,
    }


def _persist_transport_integrity(
    path: Path,
    *,
    experiment_run_id: str,
    cycle_index: int,
    prepared_transport: Any,
    configuration_hash: str,
    source_capture_session_ids: tuple[str, ...],
) -> dict[str, object]:
    records = build_transport_integrity_records(
        state_dir=str(path),
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        prepared_transport=prepared_transport,
        configuration_hash=configuration_hash,
        source_capture_session_ids=source_capture_session_ids,
    )
    store = Package123CycleStore(path)
    for record in records["readiness_records"]:
        store.append_transport_readiness(record)
    store.append_transport_flush(records["flush_record"])
    for record in records["coverage_records"]:
        store.append_alignment_window_coverage(record)
    for record in records["fault_records"]:
        store.append_transport_fault(record)
    store.append_transport_integrity_summary(records["integrity_summary"])
    return records


def _assert_passed_transport_soak(path: Path, configuration_hash: str) -> None:
    soak = Package123CycleStore(path).latest_payload("package_123_transport_soak_records")
    if not soak:
        raise RuntimeError("Cycle 1 requires a passed full-duration transport soak")
    if soak.get("soak_status") != "passed":
        raise RuntimeError("latest Package 123 transport soak did not pass")
    if soak.get("configuration_hash") != configuration_hash:
        raise RuntimeError("Package 123 transport configuration changed after the passed soak")


def _assert_no_unresolved_previous_cycle_one(path: Path) -> None:
    cycle = Package123CycleStore(path).latest_cycle_record(1)
    if not cycle:
        return
    pending_id = cycle.get("pending_teacher_review_id")
    if not pending_id:
        return
    try:
        review = TeacherGatedSessionStore(path).get_pending_review(str(pending_id))
    except Exception:
        return
    if not bool(getattr(review, "resolved", False)):
        raise RuntimeError("previous Cycle 1 pending review is unresolved; reject/approve/defer handling is required before rerun")


def _build_transport_blocked_cycle_record(
    *,
    cycle_index: int,
    experiment_run_id: str,
    process_instance_id: str,
    preflight_id: str,
    capture: dict[str, object],
    prepared_transport: Any,
) -> Package123CycleRecord:
    return Package123CycleRecord(
        cycle_record_id=stable_id("package_123_cycle_record"),
        schema_version=CYCLE_RECORD_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_id=EXPERIMENT_ID,
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        process_instance_id=process_instance_id,
        operating_system_process_id=current_pid(),
        preflight_id=preflight_id,
        source_profile_id=capture["source_profile"].source_profile_id,
        stimulus_manifest_id=capture["stimulus_manifest"].experiment_run_id,
        screen_artifact_refs=tuple(capture["screen_artifact_ids"]),
        audio_artifact_refs=tuple(capture["audio_artifact_ids"]),
        host_state_artifact_refs=tuple(capture["host_state_artifact_ids"]),
        perception_readable_data_refs=tuple(item.perception_readable_data_id for item in prepared_transport.lane_items),
        perception_session_id=prepared_transport.session_id,
        bounded_runtime_session_id="",
        final_session_state="TRANSPORT_INTEGRITY_BLOCKED",
        pending_teacher_review_id=None,
        readback_loaded_before_event=False,
        readback_record_refs=tuple(),
        source_trace_refs=tuple(prepared_transport.source_trace_refs),
    )


def _append_rerun_lineage_if_rejected_cycle_exists(path: Path, new_cycle: Package123CycleRecord) -> None:
    store = Package123CycleStore(path)
    cycles = tuple(
        item
        for item in store.list_payloads("package_123_cycle_records")
        if int(item.get("cycle_index", -1)) == 1 and item.get("cycle_record_id") != new_cycle.cycle_record_id
    )
    if not cycles:
        return
    previous = cycles[-1]
    pending_id = str(previous.get("pending_teacher_review_id") or "")
    if not pending_id:
        return
    teacher_store = TeacherGatedSessionStore(path)
    try:
        review = teacher_store.get_pending_review(pending_id)
    except Exception:
        return
    decisions = tuple(item for item in teacher_store.list_teacher_decisions(str(previous.get("bounded_runtime_session_id"))) if item.get("pending_teacher_review_id") == pending_id)
    rejected = tuple(item for item in decisions if item.get("decision") == "rejected")
    if not rejected:
        return
    lineage = Package123RerunLineageRecord(
        lineage_record_id=stable_id("package_123_rerun_lineage"),
        schema_version=RERUN_LINEAGE_SCHEMA_VERSION,
        created_at=utc_now(),
        rejected_experiment_run_id=str(previous.get("experiment_run_id")),
        rejected_pending_review_id=pending_id,
        rejected_evidence_identity=str(review.evidence_identity_sha256),
        rejection_decision_id=str(rejected[-1].get("teacher_decision_id")),
        new_experiment_run_id=new_cycle.experiment_run_id,
        new_cycle_record_id=new_cycle.cycle_record_id,
        old_evidence_reused=False,
        source_trace_refs=tuple(new_cycle.source_trace_refs),
    )
    store.append_rerun_lineage(lineage)


def _append_operator_status_log(
    path: Path,
    *,
    level: str,
    event_kind: str,
    message: str,
    source_record_refs: tuple[str, ...] = tuple(),
    source_trace_refs: tuple[str, ...] = tuple(),
) -> None:
    try:
        from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
        from ashl_core_v1.runtime.operator_status_log import build_operator_status_log_entry

        entry = build_operator_status_log_entry(
            level=level,
            event_kind=event_kind,
            operator_message=message,
            source_module="ashl_core_v1.runtime.package_123_cycle_runtime",
            source_record_refs=source_record_refs,
            source_trace_refs=source_trace_refs,
        )
        LocalOperatorConsoleStore(path).append_status_log(entry)
    except Exception:
        return


def _build_cycle_record(
    *,
    cycle_index: int,
    experiment_run_id: str,
    process_instance_id: str,
    preflight_id: str,
    capture: dict[str, object],
    result: Any,
    readback_loaded_before_event: bool,
    readback_record_refs: tuple[str, ...],
) -> Package123CycleRecord:
    return Package123CycleRecord(
        cycle_record_id=stable_id("package_123_cycle_record"),
        schema_version=CYCLE_RECORD_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_id=EXPERIMENT_ID,
        experiment_run_id=experiment_run_id,
        cycle_index=cycle_index,
        process_instance_id=process_instance_id,
        operating_system_process_id=current_pid(),
        preflight_id=preflight_id,
        source_profile_id=capture["source_profile"].source_profile_id,
        stimulus_manifest_id=capture["stimulus_manifest"].experiment_run_id,
        screen_artifact_refs=tuple(capture["screen_artifact_ids"]),
        audio_artifact_refs=tuple(capture["audio_artifact_ids"]),
        host_state_artifact_refs=tuple(capture["host_state_artifact_ids"]),
        perception_readable_data_refs=result.perception_readable_data_ids,
        perception_session_id=result.session_id,
        bounded_runtime_session_id=str(result.package_115_session_id),
        final_session_state="WAITING_TEACHER_REVIEW" if result.stopped_at_teacher_gate else "FAILED",
        pending_teacher_review_id=result.pending_teacher_review_ids[0] if result.pending_teacher_review_ids else None,
        readback_loaded_before_event=readback_loaded_before_event,
        readback_record_refs=readback_record_refs,
        source_trace_refs=tuple(result.source_trace_refs),
    )


def _build_influence_record(records: dict[str, Any], readback: tuple[dict[str, Any], ...]) -> RealPerceptionReadbackInfluenceRecord:
    scores = tuple(records.get("readback_candidate_scores", ()) or ())
    nonzero = [score for score in scores if int(score.readback_delta) > 0]
    if not nonzero:
        raise RuntimeError("Cycle 2 did not produce a nonzero readback contribution")
    score = nonzero[0]
    readback_refs = tuple(str(item.get("working_readback_commit_id")) for item in readback)
    return RealPerceptionReadbackInfluenceRecord(
        influence_record_id=stable_id("package_123_readback_influence"),
        schema_version=READBACK_INFLUENCE_SCHEMA_VERSION,
        created_at=utc_now(),
        cycle_1_memory_application_data_id=str(readback[0].get("memory_application_data_ref") or readback[0].get("interpretation_commit_id")),
        cycle_2_candidate_id=str(score.source_internal_action_candidate_id),
        scorer_id="host_body_readback_internal_action_influence",
        scorer_version=str(score.schema_version),
        score_without_readback=float(score.base_candidate_priority),
        score_with_readback=float(score.final_candidate_priority),
        readback_contribution=float(score.readback_delta),
        influencing_readback_refs=readback_refs,
        matching_evidence_refs=tuple(records.get("readback_consumption_evaluation", {}).get("matched_readback_item_ids", ())),
        actual_runtime_hot_path=True,
        hard_coded_experiment_match_used=False,
    )
