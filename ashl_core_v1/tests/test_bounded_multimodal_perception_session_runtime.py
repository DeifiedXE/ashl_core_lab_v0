import json
import math
import struct
import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime import (
    BoundedMultimodalPerceptionSessionRuntime,
    audit_bounded_multimodal_perception_session,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import (
    DEVICE_DESCRIPTOR_SCHEMA_VERSION,
    SensorDeviceDescriptor,
    build_sensor_capture_config,
    canonical_json,
    monotonic_ns,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
    TIMELINE_INPUT_REF_SCHEMA_VERSION,
    ArtifactBackedPerceptionTimelineManifest,
    PerceptionTimelineInputRef,
    build_default_multimodal_session_config,
)
from ashl_core_v1.runtime.sensor_adapter_protocol import AdapterOutputSample


def create_artifact(state_dir: str, source_kind: str, data: bytes, offset: int = 0) -> str:
    store = ContentAddressedSensorArtifactStore(state_dir)
    descriptor = SensorDeviceDescriptor(
        device_descriptor_id=stable_id("device"),
        schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
        created_at=utc_now(),
        source_kind=source_kind,
        adapter_id=f"fixture_{source_kind}",
        adapter_version="v0",
        device_id="0",
        device_index=0,
        device_display_name="fixture",
        backend_name="fixture",
        available=True,
        permission_status="granted",
        supported_format_summary=("fixture",),
        read_only=True,
        external_control_allowed=False,
        fixture_device=True,
    )
    config = build_sensor_capture_config(
        source_kind=source_kind,
        adapter_id=f"fixture_{source_kind}",
        device_id="0",
        explicit_state_dir=state_dir,
        source_specific_config=_source_config(source_kind),
        capture_duration_ms=1000,
        maximum_artifact_count=4,
        maximum_total_bytes=65536,
    )
    session = store.create_capture_session(source_kind=source_kind, config=config, descriptor=descriptor)
    sample = AdapterOutputSample(
        sample_id=f"sample:{source_kind}:{offset}",
        source_kind=source_kind,
        adapter_id=f"fixture_{source_kind}",
        adapter_version="v0",
        device_descriptor_id=descriptor.device_descriptor_id,
        captured_at_utc=utc_now(),
        captured_at_monotonic_ns=monotonic_ns() + offset,
        capture_duration_ns=None,
        raw_level="adapter_output",
        media_type=_media_type(source_kind),
        storage_format=_storage_format(source_kind),
        data=data,
        metadata=_metadata(source_kind),
        real_device_capture=False,
    )
    return store.write_raw_artifact(session=session, descriptor=descriptor, config=config, sample=sample).artifact_id


def build_manifest(state_dir: str) -> ArtifactBackedPerceptionTimelineManifest:
    camera = create_artifact(state_dir, "camera", bytes([0, 0, 0, 255, 255, 255, 0, 0, 255, 0, 255, 0] * 4), 100)
    screen_a = create_artifact(state_dir, "screen", bytes([0, 0, 0, 255] * 16), 400)
    screen_b = create_artifact(state_dir, "screen", bytes([255, 255, 255, 255] * 16), 650)
    audio = b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * 220 * index / 16000))) for index in range(1600))
    microphone = create_artifact(state_dir, "microphone", audio, 250)
    host_state = create_artifact(
        state_dir,
        "host_state",
        canonical_json(
            {
                "sample_monotonic_ns": 1,
                "process_uptime_ns": 2,
                "power_source": "unknown",
                "battery_percent": 80,
                "cpu_utilization_percent": 12,
                "memory_total_bytes": 1000,
                "memory_available_bytes": 500,
                "display_count": 1,
                "camera_adapter_available": True,
                "microphone_adapter_available": True,
                "screen_adapter_available": True,
            }
        ).encode("utf-8"),
        0,
    )
    specs = (
        ("host_state", host_state, 0),
        ("camera", camera, 100),
        ("microphone", microphone, 250),
        ("screen", screen_a, 400),
        ("screen", screen_b, 650),
    )
    refs = tuple(
        PerceptionTimelineInputRef(
            input_ref_id=stable_id("perception_timeline_input_ref"),
            schema_version=TIMELINE_INPUT_REF_SCHEMA_VERSION,
            source_kind=kind,
            source_artifact_id=artifact_id,
            source_ephemeral_buffer_id=None,
            replay_relative_offset_ms=offset,
            compiler_id="canonical",
            compiler_config_id="canonical",
            privacy_policy_id="grounding_conservative_v0" if kind == "microphone" else None,
            source_trace_refs=tuple(),
        )
        for kind, artifact_id, offset in specs
    )
    return ArtifactBackedPerceptionTimelineManifest(
        manifest_id=stable_id("artifact_backed_perception_manifest"),
        schema_version=ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
        created_at=utc_now(),
        input_refs=refs,
        source_artifacts_are_real=True,
        sources_captured_simultaneously=False,
        deterministic_replay=True,
        manifest_sha256="",
    )


class BoundedMultimodalPerceptionSessionRuntimeTests(unittest.TestCase):
    def test_artifact_backed_replay_reaches_teacher_gate(self):
        with TemporaryDirectory() as state_dir:
            manifest = build_manifest(state_dir)
            runtime = BoundedMultimodalPerceptionSessionRuntime(state_dir)
            config = build_default_multimodal_session_config(state_dir=state_dir, alignment_window_ms=250)
            result = runtime.run_artifact_backed_alignment_replay(manifest, config=config)
            self.assertTrue(result.stopped_at_teacher_gate)
            self.assertEqual(result.bounded_stop_reason, "teacher_review_boundary")
            self.assertTrue(result.bridge_record_ids)
            self.assertTrue(result.pending_teacher_review_ids)
            audit = audit_bounded_multimodal_perception_session(state_dir, result.session_id)
            self.assertEqual(audit.audit_status, "passed_bounded_multimodal_perception_session_runtime")
            self.assertFalse(audit.semantic_binding_created)
            self.assertFalse(audit.object_recognition_created)

    def test_manifest_rejects_simultaneous_claim(self):
        with TemporaryDirectory() as state_dir:
            manifest = build_manifest(state_dir)
            payload = manifest.to_dict()
            payload["sources_captured_simultaneously"] = True
            payload["manifest_sha256"] = ""
            with self.assertRaises(ValueError):
                ArtifactBackedPerceptionTimelineManifest.from_dict(payload)


def _source_config(source_kind: str) -> dict[str, object]:
    if source_kind == "camera":
        return {"device_index": 0, "requested_width": 4, "requested_height": 4, "requested_fps": 1, "capture_frame_count": 1, "read_timeout_ms": 1000}
    if source_kind == "screen":
        return {"monitor_index": 1, "left": 0, "top": 0, "width": 4, "height": 4}
    if source_kind == "microphone":
        return {"input_device_index": 0, "requested_sample_rate": 16000, "requested_channels": 1, "requested_sample_format": "int16", "chunk_duration_ms": 100, "capture_duration_ms": 1000}
    return {"host_state_fields": ("sample_monotonic_ns",)}


def _media_type(source_kind: str) -> str:
    return {"camera": "image/raw", "screen": "image/raw", "microphone": "audio/pcm", "host_state": "application/json"}[source_kind]


def _storage_format(source_kind: str) -> str:
    return {"camera": "BGR8", "screen": "BGRA8", "microphone": "PCM_S16LE", "host_state": "canonical_json_utf8"}[source_kind]


def _metadata(source_kind: str) -> dict[str, object]:
    if source_kind == "camera":
        return {"pixel_format": "BGR8", "actual_width": 4, "actual_height": 4, "row_stride_bytes": 12}
    if source_kind == "screen":
        return {"pixel_format": "BGRA8", "actual_width": 4, "actual_height": 4, "row_stride_bytes": 16, "left": 0, "top": 0, "width": 4, "height": 4}
    if source_kind == "microphone":
        return {"actual_sample_rate": 16000, "audio_channels": 1, "audio_sample_format": "int16", "audio_frame_count": 1600}
    return {}


if __name__ == "__main__":
    unittest.main()
