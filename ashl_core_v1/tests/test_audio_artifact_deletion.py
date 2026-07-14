import tempfile
import unittest

from ashl_core_v1.runtime.audio_artifact_deletion import (
    apply_artifact_deletion,
    request_artifact_deletion,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import (
    DEVICE_DESCRIPTOR_SCHEMA_VERSION,
    SensorDeviceDescriptor,
    build_sensor_capture_config,
    monotonic_ns,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.sensor_adapter_protocol import AdapterOutputSample


class AudioArtifactDeletionTests(unittest.TestCase):
    def test_hash_bound_deletion_tombstones_without_updating_artifact_row(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = ContentAddressedSensorArtifactStore(temp)
            artifact = _write_audio_artifact(store, b"\x01\x00\x02\x00")
            before = store.get_artifact(artifact.artifact_id)
            request = request_artifact_deletion(
                artifact_id=artifact.artifact_id,
                expected_content_sha256=artifact.content_sha256,
                reason_code="service_period_complete",
                approval_text="Delete this local waveform artifact.",
            )

            record = apply_artifact_deletion(store, request)
            after = store.get_artifact(artifact.artifact_id)

            self.assertEqual(before, after)
            self.assertTrue(record.artifact_tombstoned)
            self.assertTrue(record.blob_physically_removed)
            self.assertEqual(store.verify_artifact(artifact.artifact_id)["status"], "authorized_waveform_deletion")
            self.assertEqual(store.audit_store().audit_status, "authorized_waveform_deletion")

    def test_wrong_content_hash_blocks_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = ContentAddressedSensorArtifactStore(temp)
            artifact = _write_audio_artifact(store, b"\x01\x00\x02\x00")
            request = request_artifact_deletion(
                artifact_id=artifact.artifact_id,
                expected_content_sha256="0" * 64,
                reason_code="service_period_complete",
                approval_text="Delete this local waveform artifact.",
            )

            with self.assertRaises(ValueError):
                apply_artifact_deletion(store, request)

    def test_shared_blob_is_not_removed_until_last_live_artifact_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = ContentAddressedSensorArtifactStore(temp)
            first = _write_audio_artifact(store, b"\x01\x00\x02\x00")
            second = _write_audio_artifact(store, b"\x01\x00\x02\x00")

            first_delete = apply_artifact_deletion(
                store,
                request_artifact_deletion(
                    artifact_id=first.artifact_id,
                    expected_content_sha256=first.content_sha256,
                    reason_code="service_period_complete",
                    approval_text="Delete this local waveform artifact.",
                ),
            )
            self.assertFalse(first_delete.blob_physically_removed)
            self.assertTrue(store._resolve_blob_path(first.blob_relative_path).exists())

            second_delete = apply_artifact_deletion(
                store,
                request_artifact_deletion(
                    artifact_id=second.artifact_id,
                    expected_content_sha256=second.content_sha256,
                    reason_code="service_period_complete",
                    approval_text="Delete this local waveform artifact.",
                ),
            )
            self.assertTrue(second_delete.blob_physically_removed)
            self.assertFalse(store._resolve_blob_path(second.blob_relative_path).exists())
            self.assertEqual(store.verify_artifact(first.artifact_id)["status"], "authorized_waveform_deletion")

    def test_accidental_missing_blob_fails_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = ContentAddressedSensorArtifactStore(temp)
            artifact = _write_audio_artifact(store, b"\x01\x00\x02\x00")
            store._resolve_blob_path(artifact.blob_relative_path).unlink()

            self.assertEqual(store.audit_store().audit_status, "blocked_missing_blob")


def _write_audio_artifact(store: ContentAddressedSensorArtifactStore, data: bytes):
    descriptor = SensorDeviceDescriptor(
        device_descriptor_id=stable_id("sensor_device_descriptor"),
        schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
        created_at=utc_now(),
        source_kind="microphone",
        adapter_id="test_audio_adapter",
        adapter_version="v0",
        device_id="microphone:test:0",
        device_index=0,
        device_display_name="test microphone",
        backend_name="test",
        available=True,
        permission_status="granted",
        supported_format_summary=("pcm_s16le",),
        read_only=True,
        external_control_allowed=False,
        real_device_capture=False,
        fixture_device=True,
    )
    config = build_sensor_capture_config(
        source_kind="microphone",
        adapter_id=descriptor.adapter_id,
        device_id=descriptor.device_id,
        explicit_state_dir=store.state_dir,
        capture_duration_ms=100,
        source_specific_config={
            "input_device_index": 0,
            "requested_sample_rate": 16000,
            "requested_channels": 1,
            "requested_sample_format": "int16",
            "chunk_duration_ms": 100,
            "capture_duration_ms": 100,
        },
    )
    session = store.create_capture_session(source_kind="microphone", config=config, descriptor=descriptor)
    captured_at = monotonic_ns()
    sample = AdapterOutputSample(
        sample_id=stable_id("test_audio_sample"),
        source_kind="microphone",
        adapter_id=descriptor.adapter_id,
        adapter_version=descriptor.adapter_version,
        device_descriptor_id=descriptor.device_descriptor_id,
        captured_at_utc=utc_now(),
        captured_at_monotonic_ns=captured_at,
        capture_duration_ns=1,
        raw_level="adapter_output",
        media_type="audio/pcm",
        storage_format="pcm_s16le",
        data=data,
        metadata={
            "actual_sample_rate": 16000,
            "audio_channels": 1,
            "audio_sample_format": "int16",
            "audio_frame_count": len(data) // 2,
            "speech_to_text_created": False,
        },
        real_device_capture=False,
    )
    return store.write_raw_artifact(session=session, descriptor=descriptor, config=config, sample=sample)


if __name__ == "__main__":
    unittest.main()
