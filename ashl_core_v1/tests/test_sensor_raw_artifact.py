import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.host_sensor_types import (
    HARD_MAXIMUM_TOTAL_BYTES,
    HARD_MAX_CAPTURE_DURATION_MS,
    SensorRawArtifact,
    build_sensor_capture_config,
    stable_id,
    utc_now,
)


class SensorRawArtifactTests(unittest.TestCase):
    def test_raw_artifact_requires_null_semantic_and_no_learning_memory(self) -> None:
        base = dict(
            artifact_id=stable_id("sensor_raw_artifact"),
            schema_version="ashl_sensor_raw_artifact_v0",
            created_at=utc_now(),
            capture_session_id="capture:1",
            session_id="session:1",
            root_event_id="root:1",
            source_kind="camera",
            adapter_id="camera_opencv_bgr8_local_v0",
            adapter_version="v0",
            device_descriptor_id="device:1",
            capture_sequence_index=0,
            trace_sequence_index=0,
            captured_at_utc=utc_now(),
            captured_at_monotonic_ns=1,
            capture_duration_ns=1,
            raw_level="adapter_output",
            media_type="application/octet-stream",
            storage_format="bgr8",
            pixel_format="BGR8",
            width=1,
            height=1,
            row_stride_bytes=3,
            audio_sample_rate=None,
            audio_channels=None,
            audio_sample_format=None,
            audio_frame_count=None,
            byte_length=3,
            content_sha256="0" * 64,
            blob_relative_path="blobs/sha256/00/00.bin",
            capture_config_sha256="1" * 64,
            semantic_label=None,
            perception_compiled=False,
            learning_material_created=False,
            memory_write_created=False,
            immutable_artifact=True,
            append_only=True,
            trace_envelope_id="trace:1",
            source_trace_refs=("trace:0",),
        )
        artifact = SensorRawArtifact(**base)
        self.assertIsNone(artifact.semantic_label)
        self.assertFalse(artifact.perception_compiled)
        with self.assertRaises(ValueError):
            SensorRawArtifact(**{**base, "semantic_label": "face"})
        with self.assertRaises(ValueError):
            SensorRawArtifact(**{**base, "learning_material_created": True})
        with self.assertRaises(ValueError):
            SensorRawArtifact(**{**base, "memory_write_created": True})

    def test_capture_config_hash_and_limits_are_deterministic(self) -> None:
        with TemporaryDirectory() as directory:
            left = build_sensor_capture_config(
                source_kind="screen",
                adapter_id="screen_bgra8_local_v0",
                device_id="screen:local-display",
                explicit_state_dir=directory,
                source_specific_config={"left": 0, "top": 0, "width": 1, "height": 1},
            )
            right = build_sensor_capture_config(
                source_kind="screen",
                adapter_id="screen_bgra8_local_v0",
                device_id="screen:local-display",
                explicit_state_dir=directory,
                source_specific_config={"height": 1, "width": 1, "top": 0, "left": 0},
            )
            self.assertNotEqual(left.capture_config_id, right.capture_config_id)
            self.assertEqual(left.capture_config_sha256, right.capture_config_sha256)
            with self.assertRaises(ValueError):
                build_sensor_capture_config(
                    source_kind="host_state",
                    adapter_id="host_state_restricted_json_v0",
                    device_id="host_state:restricted",
                    explicit_state_dir=directory,
                    source_specific_config={"host_state_fields": "restricted_v0"},
                    capture_duration_ms=HARD_MAX_CAPTURE_DURATION_MS + 1,
                )
            with self.assertRaises(ValueError):
                build_sensor_capture_config(
                    source_kind="host_state",
                    adapter_id="host_state_restricted_json_v0",
                    device_id="host_state:restricted",
                    explicit_state_dir=directory,
                    source_specific_config={"host_state_fields": "restricted_v0"},
                    maximum_total_bytes=HARD_MAXIMUM_TOTAL_BYTES + 1,
                )
            with self.assertRaises(ValueError):
                build_sensor_capture_config(
                    source_kind="screen",
                    adapter_id="screen_bgra8_local_v0",
                    device_id="screen:local-display",
                    explicit_state_dir=directory,
                    source_specific_config={"clipboard": True},
                )


if __name__ == "__main__":
    unittest.main()
