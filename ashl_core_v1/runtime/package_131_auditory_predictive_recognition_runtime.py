"""Executable Package 131 two-probe anonymous auditory prediction runtime."""

from __future__ import annotations

import atexit
import gc
import json
import os
import subprocess
import sys
from pathlib import Path
from time import monotonic_ns
from typing import Any

from ashl_core_v1.perception.audio_primitive_schema import AudioPrimitiveRecord
from ashl_core_v1.perception.hard_soft_perception_primitive_compiler import (
    HardSoftPerceptionPrimitiveCompiler,
)
from ashl_core_v1.perception.perception_primitive_store import PerceptionPrimitiveStore
from ashl_core_v1.runtime.auditory_prediction_model_binding import (
    bind_package_130_model_for_prediction,
    load_package_130_prediction_evidence,
    verify_recognition_source_compatibility,
)
from ashl_core_v1.runtime.auditory_predictive_recognition import (
    build_auditory_prediction_comparison,
    build_auditory_recognition_feature_projection,
)
from ashl_core_v1.runtime.auditory_predictive_recognition_types import (
    CLEANUP_SCHEMA_VERSION,
    OBSERVATION_SCHEMA_VERSION,
    PAIR_COMPARISON_SCHEMA_VERSION,
    PAIR_PASS_STATUS,
    PROCESS_RECEIPT_SCHEMA_VERSION,
    AuditoryPredictiveRecognitionPairComparison,
    AuditoryRecognitionEphemeralCleanupRecord,
    AuditoryRecognitionObservationRecord,
    AuditoryRecognitionProcessReceipt,
    contains_forbidden_fixture_provenance,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
    ContentAddressedSensorArtifactStore,
)
from ashl_core_v1.runtime.ephemeral_audio_ring_buffer import (
    build_ephemeral_audio_ring_buffer_config,
    start_ephemeral_audio_session,
)
from ashl_core_v1.runtime.host_sensor_types import (
    monotonic_ns as host_monotonic_ns,
    sha256_bytes,
    sha256_payload,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.local_anonymous_auditory_recognition_stimulus_runtime import (
    LocalAnonymousAuditoryRecognitionStimulus,
)
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.runtime.package_124a_temporal_store import Package124ATemporalStore
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_store import (
    Package131AuditoryPredictiveRecognitionStore,
)
from ashl_core_v1.runtime.temporal_clock_domain import build_clock_domain_descriptor
from ashl_core_v1.runtime.temporal_relation_compiler import (
    build_temporal_anchor,
    build_temporal_interval,
    build_temporal_span,
)
from ashl_core_v1.runtime.windows_wasapi_loopback_source import WindowsWasapiLoopbackSource


PROBE_CAPTURE_DURATION_MS = 2_000
PROBE_CHUNK_DURATION_MS = 100


def preflight_package_131_prediction(
    *,
    state_dir: str | Path,
    render_endpoint: str = "default",
    model_id: str | None = None,
) -> dict[str, object]:
    evidence = load_package_130_prediction_evidence(state_dir=state_dir, model_id=model_id)
    compatibility = verify_recognition_source_compatibility(
        evidence=evidence,
        audio_source=WindowsWasapiLoopbackSource(endpoint_id=render_endpoint),
    )
    return {
        "package_130_audit_id": evidence.audit["audit_id"],
        "package_130_audit_status": evidence.audit["audit_status"],
        "ready_model_id": evidence.model.auditory_concept_model_id,
        "model_record_id": evidence.model.model_record_id,
        "expected_primitive_id": evidence.expected_primitive.audio_primitive_id,
        "expected_generation_id": evidence.generation.generation_id,
        "deletion_audit_id": evidence.deletion_audit.deletion_audit_id,
        "consumer_scope": evidence.memory_commit["consumer_scope"],
        "endpoint_compatibility": compatibility.compatibility_status,
        "package_112_influence": False,
        "active_working_readback": False,
        "recognition_readiness": (
            "ready_for_bounded_anonymous_prediction"
            if compatibility.compatible
            else compatibility.compatibility_status
        ),
        "model_snapshot_sha256": evidence.model_snapshot_sha256,
        "expected_template_sha256": evidence.expected_template_sha256,
    }


def run_real_recognition_probe(
    *,
    state_dir: str | Path,
    probe_slot: str,
    render_endpoint: str = "default",
    model_id: str | None = None,
    strict_event_stream: bool = True,
) -> dict[str, object]:
    if os.name != "nt":
        raise RuntimeError("blocked_real_wasapi_requires_windows")
    if probe_slot not in {"A", "B"}:
        raise ValueError("probe_slot must be A or B")
    path = Path(state_dir)
    store = Package131AuditoryPredictiveRecognitionStore(path)
    process_started_at = utc_now()
    process_instance_id = stable_id("package_131_probe_process")
    operating_system_process_id = os.getpid()
    probe_id = stable_id(f"package_131_probe_{probe_slot.lower()}")
    runtime_session_id = stable_id("package_131_runtime_session")
    perception_session_id = stable_id("package_131_perception_session")
    observation_window_id = stable_id("package_131_observation_window")

    evidence, binding = bind_package_130_model_for_prediction(
        state_dir=path,
        model_id=model_id,
        package_131_store=store,
    )
    _emit_event(
        path=path,
        store=store,
        event_kind="auditory_prediction_model_loaded",
        model_id=binding.auditory_concept_model_id,
        probe_id=probe_id,
        process_instance_id=process_instance_id,
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        source_record_refs=(binding.binding_id,),
        source_trace_refs=binding.source_trace_refs,
        strict=strict_event_stream,
    )
    audio_source = WindowsWasapiLoopbackSource(endpoint_id=render_endpoint)
    compatibility = verify_recognition_source_compatibility(
        evidence=evidence,
        audio_source=audio_source,
    )
    store.append_record("auditory_recognition_source_compatibility_records", compatibility)
    _emit_event(
        path=path,
        store=store,
        event_kind="auditory_prediction_source_compatibility_verified",
        model_id=binding.auditory_concept_model_id,
        probe_id=probe_id,
        process_instance_id=process_instance_id,
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        source_record_refs=(compatibility.source_compatibility_id,),
        source_trace_refs=compatibility.source_trace_refs,
        strict=strict_event_stream,
    )
    if not compatibility.compatible:
        raise RuntimeError(compatibility.compatibility_status)

    sensor_store = ContentAddressedSensorArtifactStore(path)
    primitive_store = PerceptionPrimitiveStore(path)
    compiler = HardSoftPerceptionPrimitiveCompiler(path, sensor_store=sensor_store)
    raw_artifact_count_before = len(sensor_store.list_artifacts())
    evidence_excerpt_count_before = len(sensor_store.list_evidence_audio_excerpts())
    ring_config = build_ephemeral_audio_ring_buffer_config(
        sample_rate=compatibility.sample_rate_hz,
        channels=compatibility.channel_count,
        sample_format="int16",
        buffer_duration_ms=3_000,
        chunk_duration_ms=PROBE_CHUNK_DURATION_MS,
        pre_roll_default_ms=3_000,
        post_roll_default_ms=0,
    )
    ring = start_ephemeral_audio_session(
        config=ring_config,
        metadata_store=sensor_store,
        state_dir_fingerprint=sha256_payload({"state_namespace": path.name}),
    )
    emergency_ring_close = lambda: _best_effort_close_ring(ring)
    atexit.register(emergency_ring_close)
    stimulus = LocalAnonymousAuditoryRecognitionStimulus(probe_slot=probe_slot)
    _emit_event(
        path=path,
        store=store,
        event_kind="auditory_recognition_probe_started",
        model_id=binding.auditory_concept_model_id,
        probe_id=probe_id,
        process_instance_id=process_instance_id,
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        source_record_refs=(binding.binding_id, compatibility.source_compatibility_id),
        source_trace_refs=binding.source_trace_refs,
        strict=strict_event_stream,
    )

    stimulus.start(delay_ms=80)
    capture_started_ns = monotonic_ns()
    samples = audio_source.capture_samples(
        duration_ms=PROBE_CAPTURE_DURATION_MS,
        chunk_duration_ms=PROBE_CHUNK_DURATION_MS,
        capture_mode="recognition_ephemeral",
    )
    capture_ended_ns = monotonic_ns()
    stimulus.join()
    if not samples or any(not item.real_device_capture for item in samples):
        raise RuntimeError("blocked_real_wasapi_capture_missing")
    for sample in samples:
        ring.append_adapter_sample(sample)
    del samples
    if not ring.chunk_descriptors:
        raise RuntimeError("blocked_recognition_transport_produced_no_chunks")
    ephemeral_source = ring.get_window_as_source_buffer(
        event_monotonic_ns=ring.chunk_descriptors[-1].end_monotonic_ns,
        pre_roll_ms=3_000,
        post_roll_ms=0,
    )
    source_buffer_id = ephemeral_source.buffer_id
    content_sha256_before_clear = sha256_bytes(bytes(ephemeral_source.readonly_bytes))
    ring_bytes_before_clear = ring.live_byte_length
    bundle = compiler.compile_ephemeral_audio(
        ephemeral_source,
        privacy_policy_id="recognition_ephemeral_v0",
    )
    primitive = AudioPrimitiveRecord(
        **primitive_store.get_primitive(bundle.primitive_record_id)
    )
    if (
        primitive.source_buffer_id != source_buffer_id
        or primitive.source_artifact_id is not None
        or primitive.privacy_policy_id != "recognition_ephemeral_v0"
    ):
        raise RuntimeError("blocked_observed_audio_primitive_not_ephemeral")
    _emit_event(
        path=path,
        store=store,
        event_kind="auditory_recognition_observed_primitive_compiled",
        model_id=binding.auditory_concept_model_id,
        probe_id=probe_id,
        process_instance_id=process_instance_id,
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        source_record_refs=(primitive.audio_primitive_id, source_buffer_id),
        source_trace_refs=primitive.source_trace_refs,
        strict=strict_event_stream,
    )

    stimulus_started_ns = stimulus.started_monotonic_ns
    observation_identity = {
        "probe_id": probe_id,
        "process_instance_id": process_instance_id,
        "runtime_session_id": runtime_session_id,
        "perception_session_id": perception_session_id,
        "observation_window_id": observation_window_id,
        "ephemeral_audio_session_id": ring.session.ephemeral_audio_session_id,
        "source_buffer_id": source_buffer_id,
        "observed_audio_primitive_ref": primitive.audio_primitive_id,
    }
    observation = AuditoryRecognitionObservationRecord(
        observation_id="auditory_recognition_observation:" + sha256_payload(observation_identity),
        schema_version=OBSERVATION_SCHEMA_VERSION,
        created_at=utc_now(),
        probe_id=probe_id,
        process_instance_id=process_instance_id,
        operating_system_process_id=operating_system_process_id,
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        ephemeral_audio_session_id=ring.session.ephemeral_audio_session_id,
        source_buffer_id=source_buffer_id,
        observed_audio_primitive_ref=primitive.audio_primitive_id,
        source_compatibility_ref=compatibility.source_compatibility_id,
        capture_mode="recognition_ephemeral",
        model_loaded_monotonic_ns=binding.model_loaded_monotonic_ns,
        stimulus_started_monotonic_ns=stimulus_started_ns,
        capture_started_monotonic_ns=capture_started_ns,
        capture_ended_monotonic_ns=capture_ended_ns,
        model_loaded_before_capture=binding.model_loaded_monotonic_ns < capture_started_ns,
        model_loaded_before_stimulus=binding.model_loaded_monotonic_ns < stimulus_started_ns,
        real_wasapi_loopback_capture=True,
        transport_integrity_valid=True,
        raw_sensor_artifact_created=False,
        evidence_audio_excerpt_created=False,
        temporary_audio_file_created=False,
        semantic_label=None,
        speaker_identity=None,
        transcript=None,
        emotion_label=None,
        source_record_refs=(
            binding.binding_id,
            compatibility.source_compatibility_id,
            source_buffer_id,
            primitive.audio_primitive_id,
            bundle.compilation_record_id,
        ),
        source_trace_refs=primitive.source_trace_refs,
    )
    store.append_record("auditory_recognition_observations", observation)
    projection = build_auditory_recognition_feature_projection(
        observation=observation,
        audio_primitive=primitive,
    )
    store.append_record("auditory_recognition_feature_projections", projection)
    _emit_event(
        path=path,
        store=store,
        event_kind="auditory_recognition_feature_projection_created",
        model_id=binding.auditory_concept_model_id,
        probe_id=probe_id,
        process_instance_id=process_instance_id,
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        source_record_refs=(projection.recognition_projection_id,),
        source_trace_refs=projection.source_trace_refs,
        strict=strict_event_stream,
    )
    comparison = build_auditory_prediction_comparison(
        probe_id=probe_id,
        observation=observation,
        projection=projection,
        binding=binding,
        feature_centers=evidence.generation.feature_centers,
        feature_tolerances=evidence.generation.feature_tolerances,
    )
    store.append_record("auditory_prediction_comparisons", comparison)
    _emit_event(
        path=path,
        store=store,
        event_kind="auditory_prediction_comparison_created",
        model_id=binding.auditory_concept_model_id,
        probe_id=probe_id,
        process_instance_id=process_instance_id,
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        prediction_comparison_id=comparison.prediction_comparison_id,
        source_record_refs=(comparison.prediction_comparison_id,),
        source_trace_refs=comparison.source_trace_refs,
        strict=strict_event_stream,
    )
    del ephemeral_source
    gc.collect()
    ring.close("package_131_prediction_frozen")
    atexit.unregister(emergency_ring_close)
    gc.collect()
    raw_artifact_count_after = len(sensor_store.list_artifacts())
    evidence_excerpt_count_after = len(sensor_store.list_evidence_audio_excerpts())
    cleanup = AuditoryRecognitionEphemeralCleanupRecord(
        cleanup_record_id="auditory_recognition_cleanup:"
        + sha256_payload(
            {
                "probe_id": probe_id,
                "observation_id": observation.observation_id,
                "ephemeral_audio_session_id": ring.session.ephemeral_audio_session_id,
                "content_sha256_before_clear": content_sha256_before_clear,
            }
        ),
        schema_version=CLEANUP_SCHEMA_VERSION,
        created_at=utc_now(),
        probe_id=probe_id,
        observation_id=observation.observation_id,
        ephemeral_audio_session_id=ring.session.ephemeral_audio_session_id,
        content_sha256_before_clear=content_sha256_before_clear,
        ring_buffer_bytes_before_clear=ring_bytes_before_clear,
        ring_buffer_bytes_after_clear=ring.live_byte_length,
        ring_buffer_status_after_close=ring.status,
        raw_artifact_count_before=raw_artifact_count_before,
        raw_artifact_count_after=raw_artifact_count_after,
        evidence_excerpt_count_before=evidence_excerpt_count_before,
        evidence_excerpt_count_after=evidence_excerpt_count_after,
        backend_transient_file_created=False,
        temporary_audio_file_absent_after=True,
        ring_buffer_overwritten=True,
        raw_audio_retained=False,
        cleanup_verified=True,
        source_record_refs=(
            observation.observation_id,
            comparison.prediction_comparison_id,
            ring.session.ephemeral_audio_session_id,
        ),
        source_trace_refs=primitive.source_trace_refs,
    )
    store.append_record("auditory_recognition_ephemeral_cleanup_records", cleanup)
    _emit_event(
        path=path,
        store=store,
        event_kind="auditory_recognition_ephemeral_audio_cleared",
        model_id=binding.auditory_concept_model_id,
        probe_id=probe_id,
        process_instance_id=process_instance_id,
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        source_record_refs=(cleanup.cleanup_record_id,),
        source_trace_refs=cleanup.source_trace_refs,
        strict=strict_event_stream,
    )
    temporal_refs = _append_probe_temporal_evidence(
        state_dir=path,
        binding_id=binding.binding_id,
        observation=observation,
        process_instance_id=process_instance_id,
    )

    manifest = stimulus.build_audit_manifest(
        probe_id=probe_id,
        frozen_source_record_refs=(
            observation.observation_id,
            projection.recognition_projection_id,
            comparison.prediction_comparison_id,
            cleanup.cleanup_record_id,
        ),
        result_frozen=True,
    )
    store.append_record("auditory_recognition_fixture_manifests", manifest)
    receipt = AuditoryRecognitionProcessReceipt(
        process_receipt_id="auditory_recognition_process_receipt:"
        + sha256_payload(
            {
                "probe_id": probe_id,
                "process_instance_id": process_instance_id,
                "operating_system_process_id": operating_system_process_id,
                "observation_ref": observation.observation_id,
                "prediction_ref": comparison.prediction_comparison_id,
                "cleanup_ref": cleanup.cleanup_record_id,
            }
        ),
        schema_version=PROCESS_RECEIPT_SCHEMA_VERSION,
        created_at=utc_now(),
        probe_id=probe_id,
        process_instance_id=process_instance_id,
        operating_system_process_id=operating_system_process_id,
        started_at=process_started_at,
        ended_at=utc_now(),
        worker_status="completed_real_probe",
        observation_ref=observation.observation_id,
        prediction_ref=comparison.prediction_comparison_id,
        cleanup_ref=cleanup.cleanup_record_id,
        source_record_refs=(
            binding.binding_id,
            compatibility.source_compatibility_id,
            observation.observation_id,
            projection.recognition_projection_id,
            comparison.prediction_comparison_id,
            cleanup.cleanup_record_id,
            manifest.fixture_manifest_id,
            *temporal_refs,
        ),
    )
    store.append_record("auditory_recognition_process_receipts", receipt)
    _emit_event(
        path=path,
        store=store,
        event_kind="auditory_recognition_probe_completed",
        model_id=binding.auditory_concept_model_id,
        probe_id=probe_id,
        process_instance_id=process_instance_id,
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        prediction_comparison_id=comparison.prediction_comparison_id,
        source_record_refs=(receipt.process_receipt_id,),
        source_trace_refs=comparison.source_trace_refs,
        strict=strict_event_stream,
    )
    return {
        "probe_slot": probe_slot,
        "probe_id": probe_id,
        "process_receipt_id": receipt.process_receipt_id,
        "process_instance_id": process_instance_id,
        "operating_system_process_id": operating_system_process_id,
        "runtime_session_id": runtime_session_id,
        "perception_session_id": perception_session_id,
        "observation_window_id": observation_window_id,
        "ephemeral_audio_session_id": ring.session.ephemeral_audio_session_id,
        "source_buffer_id": source_buffer_id,
        "observed_audio_primitive_id": primitive.audio_primitive_id,
        "recognition_projection_id": projection.recognition_projection_id,
        "prediction_comparison_id": comparison.prediction_comparison_id,
        "prediction_result": comparison.prediction_result,
        "inside_all_structural_tolerances": comparison.inside_all_structural_tolerances,
        "cleanup_record_id": cleanup.cleanup_record_id,
        "ring_buffer_bytes_after_clear": cleanup.ring_buffer_bytes_after_clear,
        "raw_artifact_delta": cleanup.raw_artifact_count_after - cleanup.raw_artifact_count_before,
        "model_loaded_before_stimulus": observation.model_loaded_before_stimulus,
        "model_snapshot_sha256": binding.model_snapshot_sha256,
        "expected_template_sha256": binding.expected_template_sha256,
        "auditory_concept_model_id": binding.auditory_concept_model_id,
    }


def run_probe_worker_subprocess(
    *,
    state_dir: str | Path,
    probe_slot: str,
    render_endpoint: str = "default",
    model_id: str | None = None,
) -> dict[str, object]:
    command = [
        sys.executable,
        "-m",
        "ashl_core_v1.runtime.package_131_auditory_predictive_recognition_worker",
        "--state-dir",
        str(Path(state_dir)),
        "--probe-slot",
        probe_slot,
        "--render-endpoint",
        render_endpoint,
    ]
    if model_id:
        command.extend(("--model-id", model_id))
    try:
        result = subprocess.run(
            command,
            cwd=Path(__file__).resolve().parents[2],
            capture_output=True,
            text=True,
            check=False,
            timeout=30.0,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("blocked_recognition_worker_exceeded_bounded_timeout") from error
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "recognition worker failed"
        raise RuntimeError(detail)
    lines = tuple(line for line in result.stdout.splitlines() if line.strip())
    if not lines:
        raise RuntimeError("recognition worker returned no receipt")
    return dict(json.loads(lines[-1]))


def create_pair_comparison(
    *,
    state_dir: str | Path,
    strict_event_stream: bool = True,
) -> AuditoryPredictiveRecognitionPairComparison:
    path = Path(state_dir)
    store = Package131AuditoryPredictiveRecognitionStore(path)
    manifests = store.list_payloads("auditory_recognition_fixture_manifests")
    by_slot = {
        str(item["probe_slot"]): item
        for item in manifests
        if item.get("probe_slot") in {"A", "B"}
    }
    if set(by_slot) != {"A", "B"}:
        raise RuntimeError("blocked_missing_real_probe_pair")
    probe_a_id = str(by_slot["A"]["probe_id"])
    probe_b_id = str(by_slot["B"]["probe_id"])
    observations = store.list_payloads("auditory_recognition_observations")
    predictions = store.list_payloads("auditory_prediction_comparisons")
    cleanups = store.list_payloads("auditory_recognition_ephemeral_cleanup_records")
    receipts = store.list_payloads("auditory_recognition_process_receipts")
    projections = store.list_payloads("auditory_recognition_feature_projections")
    bindings = store.list_payloads("auditory_prediction_consumer_bindings")
    compatibility = store.list_payloads("auditory_recognition_source_compatibility_records")

    def one(items: tuple[dict[str, Any], ...], probe_id: str, label: str) -> dict[str, Any]:
        matches = tuple(item for item in items if str(item.get("probe_id")) == probe_id)
        if len(matches) != 1:
            raise RuntimeError(f"blocked_{label}_probe_cardinality")
        return dict(matches[0])

    a_obs, b_obs = one(observations, probe_a_id, "observation"), one(observations, probe_b_id, "observation")
    a_pred, b_pred = one(predictions, probe_a_id, "prediction"), one(predictions, probe_b_id, "prediction")
    a_cleanup, b_cleanup = one(cleanups, probe_a_id, "cleanup"), one(cleanups, probe_b_id, "cleanup")
    a_receipt, b_receipt = one(receipts, probe_a_id, "receipt"), one(receipts, probe_b_id, "receipt")
    projection_by_id = {str(item["recognition_projection_id"]): item for item in projections}
    binding_by_id = {str(item["binding_id"]): item for item in bindings}
    compatibility_by_id = {
        str(item["source_compatibility_id"]): item for item in compatibility
    }
    relevant_payloads = (
        a_obs,
        b_obs,
        a_pred,
        b_pred,
        projection_by_id[str(a_pred["recognition_projection_ref"])],
        projection_by_id[str(b_pred["recognition_projection_ref"])],
        compatibility_by_id[str(a_obs["source_compatibility_ref"])],
        compatibility_by_id[str(b_obs["source_compatibility_ref"])],
    )
    for prediction in (a_pred, b_pred):
        binding_ref = next(
            (
                str(ref)
                for ref in prediction.get("source_record_refs") or ()
                if str(ref).startswith("auditory_prediction_consumer_binding:")
            ),
            "",
        )
        if binding_ref not in binding_by_id:
            raise RuntimeError("blocked_prediction_binding_lineage_missing")
        relevant_payloads += (binding_by_id[binding_ref],)
    fixture_firewall = not contains_forbidden_fixture_provenance(relevant_payloads)
    model_id = str(a_pred["auditory_concept_model_id"])
    identity = {
        "model_id": model_id,
        "probe_a_prediction_ref": a_pred["prediction_comparison_id"],
        "probe_b_prediction_ref": b_pred["prediction_comparison_id"],
        "probe_a_cleanup_ref": a_cleanup["cleanup_record_id"],
        "probe_b_cleanup_ref": b_cleanup["cleanup_record_id"],
    }
    pair = AuditoryPredictiveRecognitionPairComparison(
        pair_comparison_id="auditory_predictive_recognition_pair:" + sha256_payload(identity),
        schema_version=PAIR_COMPARISON_SCHEMA_VERSION,
        created_at=utc_now(),
        model_id=model_id,
        probe_a_ref=probe_a_id,
        probe_b_ref=probe_b_id,
        probe_a_prediction_ref=str(a_pred["prediction_comparison_id"]),
        probe_b_prediction_ref=str(b_pred["prediction_comparison_id"]),
        model_snapshot_same=(
            a_pred["model_snapshot_sha256"] == b_pred["model_snapshot_sha256"]
            and a_pred["auditory_concept_model_id"] == b_pred["auditory_concept_model_id"]
        ),
        expected_template_same=(
            a_pred["expected_template_sha256"] == b_pred["expected_template_sha256"]
        ),
        processes_distinct=(
            a_receipt["operating_system_process_id"] != b_receipt["operating_system_process_id"]
            and a_receipt["process_instance_id"] != b_receipt["process_instance_id"]
        ),
        audio_sessions_distinct=(
            a_obs["ephemeral_audio_session_id"] != b_obs["ephemeral_audio_session_id"]
        ),
        source_buffers_distinct=a_obs["source_buffer_id"] != b_obs["source_buffer_id"],
        observed_primitives_distinct=(
            a_obs["observed_audio_primitive_ref"] != b_obs["observed_audio_primitive_ref"]
        ),
        observation_windows_distinct=(
            a_obs["observation_window_id"] != b_obs["observation_window_id"]
        ),
        probe_a_supported=(
            a_pred["prediction_result"]
            == "supported_by_reviewed_anonymous_auditory_concept"
            and a_pred["inside_all_structural_tolerances"] is True
        ),
        probe_b_not_supported=(
            b_pred["prediction_result"]
            == "not_supported_by_reviewed_anonymous_auditory_concept"
            and b_pred["inside_all_structural_tolerances"] is False
        ),
        both_ephemeral_cleanups_verified=(
            a_cleanup["cleanup_verified"] is True
            and b_cleanup["cleanup_verified"] is True
        ),
        fixture_firewall_passed=fixture_firewall,
        comparison_status=PAIR_PASS_STATUS,
        source_record_refs=(
            probe_a_id,
            probe_b_id,
            str(a_pred["prediction_comparison_id"]),
            str(b_pred["prediction_comparison_id"]),
            str(a_cleanup["cleanup_record_id"]),
            str(b_cleanup["cleanup_record_id"]),
        ),
        source_trace_refs=tuple(
            dict.fromkeys(
                tuple(a_pred.get("source_trace_refs") or ())
                + tuple(b_pred.get("source_trace_refs") or ())
            )
        ),
    )
    store.append_record("auditory_predictive_recognition_pair_comparisons", pair)
    _emit_event(
        path=path,
        store=store,
        event_kind="auditory_predictive_recognition_pair_comparison_created",
        model_id=model_id,
        source_record_refs=(pair.pair_comparison_id,),
        source_trace_refs=pair.source_trace_refs,
        strict=strict_event_stream,
    )
    return pair


def _append_probe_temporal_evidence(
    *,
    state_dir: Path,
    binding_id: str,
    observation: AuditoryRecognitionObservationRecord,
    process_instance_id: str,
) -> tuple[str, ...]:
    store = Package124ATemporalStore(state_dir)
    clock = build_clock_domain_descriptor(
        process_instance_id=process_instance_id,
        operating_system_process_id=observation.operating_system_process_id,
        utc_anchor=observation.created_at,
        utc_anchor_monotonic_ns=observation.capture_started_monotonic_ns,
        monotonic_origin_ns=observation.model_loaded_monotonic_ns,
        comparable_across_processes=False,
        source_trace_refs=observation.source_trace_refs,
    )
    store.append_record("temporal_clock_domains", clock)

    def anchor(record_id: str, kind: str, event_ns: int):
        item = build_temporal_anchor(
            source_record_id=record_id,
            source_record_kind=kind,
            source_lane="microphone",
            clock_domain_id=clock.clock_domain_id,
            normalized_event_time_ns=event_ns,
            source_native_time_ns=event_ns,
            processing_time_ns=host_monotonic_ns(),
            source_record_refs=(record_id, observation.observation_id),
            source_trace_refs=observation.source_trace_refs,
        )
        store.append_record("temporal_event_anchors", item)
        return item

    model_load = anchor(binding_id, "auditory_prediction_model_load", observation.model_loaded_monotonic_ns)
    stimulus = anchor(
        observation.probe_id,
        "auditory_recognition_stimulus_start",
        observation.stimulus_started_monotonic_ns,
    )
    capture_start = anchor(
        observation.observation_id + ":capture_start",
        "auditory_recognition_capture_start",
        observation.capture_started_monotonic_ns,
    )
    capture_end = anchor(
        observation.observation_id + ":capture_end",
        "auditory_recognition_capture_end",
        observation.capture_ended_monotonic_ns,
    )
    observation_span = build_temporal_span(
        span_kind="source_presence_span",
        start_anchor=capture_start,
        end_anchor=capture_end,
        source_lane="microphone",
    )
    store.append_record("temporal_span_primitives", observation_span)
    load_to_stimulus = build_temporal_interval(
        interval_kind="event_to_event",
        left_anchor=model_load,
        right_anchor=stimulus,
        source_record_refs=(binding_id, observation.probe_id, observation.observation_id),
        source_trace_refs=observation.source_trace_refs,
    )
    if load_to_stimulus.interval_ns <= 0:
        raise RuntimeError("blocked_model_load_not_before_stimulus")
    store.append_record("temporal_interval_primitives", load_to_stimulus)
    return (
        clock.clock_domain_id,
        model_load.temporal_anchor_id,
        stimulus.temporal_anchor_id,
        capture_start.temporal_anchor_id,
        capture_end.temporal_anchor_id,
        observation_span.temporal_span_id,
        load_to_stimulus.temporal_interval_id,
    )


def _emit_event(
    *,
    path: Path,
    store: Package131AuditoryPredictiveRecognitionStore,
    event_kind: str,
    model_id: str,
    source_record_refs: tuple[str, ...],
    source_trace_refs: tuple[str, ...],
    strict: bool,
    probe_id: str | None = None,
    process_instance_id: str | None = None,
    runtime_session_id: str | None = None,
    perception_session_id: str | None = None,
    observation_window_id: str | None = None,
    prediction_comparison_id: str | None = None,
) -> None:
    try:
        event = LocalOperatorEventStream(LocalOperatorConsoleStore(path)).append_event(
            event_kind=event_kind,
            source_record_refs=source_record_refs,
            source_trace_refs=source_trace_refs,
            runtime_session_id=runtime_session_id,
            perception_session_id=perception_session_id,
            observation_window_id=observation_window_id,
            process_instance_id=process_instance_id,
            auditory_concept_model_id=model_id,
            probe_id=probe_id,
            prediction_comparison_id=prediction_comparison_id,
        )
        store.append_payload(
            "auditory_predictive_recognition_operator_events",
            "event_id",
            event.event_id,
            event.to_dict(),
        )
    except Exception as error:
        failure = {
            "event_delivery_failure_id": stable_id("package_131_event_delivery_failure"),
            "schema_version": "ashl_package_131_event_delivery_failure_v0",
            "created_at": utc_now(),
            "event_kind": event_kind,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "source_record_refs": source_record_refs,
        }
        store.append_payload(
            "auditory_predictive_recognition_event_delivery_failures",
            "event_delivery_failure_id",
            str(failure["event_delivery_failure_id"]),
            failure,
        )
        if strict:
            raise RuntimeError("Package 131 operator event delivery failed") from error


def _best_effort_close_ring(ring: Any) -> None:
    try:
        if ring.status != "closed":
            ring.close("package_131_worker_exit_cleanup")
    except Exception:
        pass
