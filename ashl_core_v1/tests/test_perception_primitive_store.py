import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.perception.hard_soft_perception_primitive_compiler import (
    HardSoftPerceptionPrimitiveCompiler,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
    ContentAddressedSensorArtifactStore,
)
from ashl_core_v1.runtime.host_sensor_types import (
    DEVICE_DESCRIPTOR_SCHEMA_VERSION,
    SensorDeviceDescriptor,
    build_sensor_capture_config,
    monotonic_ns,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.sensor_adapter_protocol import AdapterOutputSample


def _create_camera_artifact(state_dir: str, data: bytes) -> str:
    store = ContentAddressedSensorArtifactStore(state_dir)
    descriptor = SensorDeviceDescriptor(
        device_descriptor_id=stable_id("device"),
        schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
        created_at=utc_now(),
        source_kind="camera",
        adapter_id="fixture_camera",
        adapter_version="v0",
        device_id="0",
        device_index=0,
        device_display_name="fixture",
        backend_name="fixture",
        available=True,
        permission_status="granted",
        supported_format_summary=("BGR8",),
        read_only=True,
        external_control_allowed=False,
        fixture_device=True,
    )
    config = build_sensor_capture_config(
        source_kind="camera",
        adapter_id="fixture_camera",
        device_id="0",
        explicit_state_dir=state_dir,
        source_specific_config={
            "device_index": 0,
            "requested_width": 4,
            "requested_height": 4,
            "requested_fps": 1,
            "capture_frame_count": 1,
            "read_timeout_ms": 1000,
        },
        capture_duration_ms=1000,
        maximum_artifact_count=1,
        maximum_total_bytes=4096,
    )
    session = store.create_capture_session(source_kind="camera", config=config, descriptor=descriptor)
    sample = AdapterOutputSample(
        sample_id="sample",
        source_kind="camera",
        adapter_id="fixture_camera",
        adapter_version="v0",
        device_descriptor_id=descriptor.device_descriptor_id,
        captured_at_utc=utc_now(),
        captured_at_monotonic_ns=monotonic_ns(),
        capture_duration_ns=None,
        raw_level="adapter_output",
        media_type="image/raw",
        storage_format="BGR8",
        data=data,
        metadata={"pixel_format": "BGR8", "actual_width": 4, "actual_height": 4, "row_stride_bytes": 12},
        real_device_capture=False,
    )
    return store.write_raw_artifact(session=session, descriptor=descriptor, config=config, sample=sample).artifact_id


class PerceptionPrimitiveStoreTests(unittest.TestCase):
    def test_compile_artifact_persists_append_only_records_without_raw_blob_copy(self):
        with TemporaryDirectory() as state_dir:
            artifact_id = _create_camera_artifact(state_dir, bytes([0, 0, 0, 255, 255, 255, 0, 0, 255, 0, 255, 0] * 4))
            compiler = HardSoftPerceptionPrimitiveCompiler(state_dir)
            bundle = compiler.compile_artifact(artifact_id)
            primitive = compiler.store.get_primitive(bundle.primitive_record_id)
            readable = compiler.store.get_perception_readable_data(bundle.perception_readable_data_id)
            traces = compiler.store.list_trace_envelopes()
            self.assertEqual(bundle.bundle_status, "compiled_stored_artifact")
            self.assertEqual(primitive["source_artifact_id"], artifact_id)
            self.assertEqual(readable["readable_type"], "visual_frame_primitive")
            self.assertTrue(traces)
            self.assertTrue(all(trace.source_line == "hard_soft_perception" for trace in traces))
            self.assertFalse((compiler.store.root_dir / "blobs").exists())

    def test_store_audit_passes_after_compile(self):
        with TemporaryDirectory() as state_dir:
            artifact_id = _create_camera_artifact(state_dir, bytes([10, 20, 30] * 16))
            compiler = HardSoftPerceptionPrimitiveCompiler(state_dir)
            compiler.compile_artifact(artifact_id)
            audit = compiler.audit_store()
            self.assertEqual(audit.audit_status, "passed_hard_soft_perception_primitive_compiler")
            self.assertFalse(audit.learned_model_used)
            self.assertFalse(audit.sensor_driven_learning_created)
            self.assertFalse(audit.memory_write_created)


if __name__ == "__main__":
    unittest.main()
