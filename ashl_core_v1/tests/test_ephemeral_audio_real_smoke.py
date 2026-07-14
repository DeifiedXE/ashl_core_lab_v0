import os
import tempfile
import unittest

from ashl_core_v1.runtime.audio_artifact_deletion import request_artifact_deletion
from ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime import capture_once
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.ephemeral_audio_ring_buffer import (
    AudioCaptureMode,
    build_ephemeral_audio_ring_buffer_config,
    start_ephemeral_audio_session,
)
from ashl_core_v1.runtime.evidence_audio_excerpt import (
    build_audio_capture_consent_record,
    create_evidence_audio_excerpt_from_artifact,
    materialize_evidence_audio_excerpt,
    request_manual_audio_excerpt,
)
from ashl_core_v1.runtime.host_sensor_types import build_sensor_capture_config
from ashl_core_v1.runtime.microphone_sensor_adapter import MicrophoneSensorAdapter


REAL_AUDIO = os.environ.get("ASHL_REAL_AUDIO_EPHEMERAL_SMOKE") == "1"


@unittest.skipUnless(REAL_AUDIO, "set ASHL_REAL_AUDIO_EPHEMERAL_SMOKE=1 to run real microphone smoke")
class EphemeralAudioRealSmokeTests(unittest.TestCase):
    def test_real_microphone_ephemeral_excerpt_and_deletion_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ashl_120a_real_audio_") as temp:
            store = ContentAddressedSensorArtifactStore(temp)
            adapter = MicrophoneSensorAdapter()
            adapter.open(_mic_config(temp))
            ring = start_ephemeral_audio_session(
                config=build_ephemeral_audio_ring_buffer_config(buffer_duration_ms=1000, chunk_duration_ms=100),
                metadata_store=store,
                state_dir_fingerprint=store.state_dir_fingerprint(),
                device_index=0,
            )
            sample = adapter.read_sample()
            ring.append_adapter_sample(sample)
            adapter.close()

            self.assertEqual(store.list_artifacts(), tuple())
            self.assertEqual(tuple(store.blob_root.glob("*/*.bin")), tuple())

            consent = build_audio_capture_consent_record(
                state_dir_fingerprint=store.state_dir_fingerprint(),
                consent_text="I authorize this bounded local grounding capture.",
                capture_mode=AudioCaptureMode.SELECTIVE_EVIDENCE_EXCERPT.value,
                allowed_purposes=("grounding_example",),
            )
            request = request_manual_audio_excerpt(
                ring_buffer_session_id=ring.session.ephemeral_audio_session_id,
                purpose="grounding_example",
                event_monotonic_ns=sample.captured_at_monotonic_ns,
                pre_roll_ms=100,
                post_roll_ms=0,
                consent_record_id=consent.consent_record_id,
            )
            excerpt = materialize_evidence_audio_excerpt(store=store, ring_buffer=ring, request=request, consent=consent)
            ring.close()

            self.assertGreater(store.get_artifact(excerpt.sensor_raw_artifact_id)["byte_length"], 0)
            record = store.apply_artifact_deletion(
                request_artifact_deletion(
                    artifact_id=excerpt.sensor_raw_artifact_id,
                    expected_content_sha256=excerpt.content_sha256,
                    reason_code="service_period_complete",
                    approval_text="Delete this local waveform artifact.",
                )
            )
            self.assertTrue(record.blob_physically_removed)
            self.assertEqual(store.verify_artifact(excerpt.sensor_raw_artifact_id)["status"], "authorized_waveform_deletion")

    def test_real_grounding_capture_creates_nonsemantic_excerpt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ashl_120a_real_audio_") as temp:
            store = ContentAddressedSensorArtifactStore(temp)
            result = capture_once(state_dir=temp, source_kind="microphone", device_index=0, duration_ms=100)
            artifact = store.get_artifact(result.artifact_ids[0])
            consent = build_audio_capture_consent_record(
                state_dir_fingerprint=store.state_dir_fingerprint(),
                consent_text="I authorize this bounded local grounding capture.",
                capture_mode=AudioCaptureMode.GROUNDING_CAPTURE.value,
                allowed_purposes=("grounding_example",),
            )
            excerpt = create_evidence_audio_excerpt_from_artifact(
                store=store,
                artifact=artifact,
                purpose="grounding_example",
                consent=consent,
            )

            self.assertGreater(artifact["byte_length"], 0)
            self.assertFalse(excerpt.automatic_retention)
            self.assertFalse(excerpt.permanent_retention_allowed)


def _mic_config(state_dir: str):
    return build_sensor_capture_config(
        source_kind="microphone",
        adapter_id=MicrophoneSensorAdapter.adapter_id,
        device_id="microphone:0",
        explicit_state_dir=state_dir,
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


if __name__ == "__main__":
    unittest.main()
