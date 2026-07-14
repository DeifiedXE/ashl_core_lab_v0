import tempfile
import unittest

from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.ephemeral_audio_ring_buffer import (
    AudioCaptureMode,
    build_ephemeral_audio_ring_buffer_config,
    start_ephemeral_audio_session,
)
from ashl_core_v1.runtime.evidence_audio_excerpt import (
    build_audio_capture_consent_record,
    create_manual_retention_candidate,
    materialize_evidence_audio_excerpt,
    request_manual_audio_excerpt,
)


class EvidenceAudioExcerptTests(unittest.TestCase):
    def test_manual_excerpt_materializes_bounded_artifact_without_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = ContentAddressedSensorArtifactStore(temp)
            ring = start_ephemeral_audio_session(
                config=build_ephemeral_audio_ring_buffer_config(),
                metadata_store=store,
                state_dir_fingerprint=store.state_dir_fingerprint(),
                device_index=0,
            )
            ring.append_chunk(b"\x01\x00" * 160, start_monotonic_ns=1_000_000, end_monotonic_ns=11_000_000)
            consent = build_audio_capture_consent_record(
                state_dir_fingerprint=store.state_dir_fingerprint(),
                consent_text="I authorize this bounded local grounding capture.",
                capture_mode=AudioCaptureMode.SELECTIVE_EVIDENCE_EXCERPT.value,
                allowed_purposes=("counterexample",),
            )
            request = request_manual_audio_excerpt(
                ring_buffer_session_id=ring.session.ephemeral_audio_session_id,
                purpose="counterexample",
                event_monotonic_ns=5_000_000,
                pre_roll_ms=10,
                post_roll_ms=10,
                consent_record_id=consent.consent_record_id,
            )

            excerpt = materialize_evidence_audio_excerpt(store=store, ring_buffer=ring, request=request, consent=consent)
            artifact = store.get_artifact(excerpt.sensor_raw_artifact_id)

            self.assertEqual(excerpt.purpose, "counterexample")
            self.assertFalse(excerpt.automatic_retention)
            self.assertFalse(excerpt.permanent_retention_allowed)
            self.assertIsNone(artifact["semantic_label"])
            self.assertFalse(artifact["perception_compiled"])

    def test_retention_candidate_is_manual_and_not_permanent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = ContentAddressedSensorArtifactStore(temp)
            ring = start_ephemeral_audio_session(device_index=0)
            ring.append_chunk(b"\x01\x00" * 16, start_monotonic_ns=1, end_monotonic_ns=2)
            consent = build_audio_capture_consent_record(
                state_dir_fingerprint=store.state_dir_fingerprint(),
                consent_text="I authorize this bounded local grounding capture.",
                capture_mode=AudioCaptureMode.SELECTIVE_EVIDENCE_EXCERPT.value,
                allowed_purposes=("grounding_example",),
            )
            request = request_manual_audio_excerpt(
                ring_buffer_session_id=ring.session.ephemeral_audio_session_id,
                purpose="grounding_example",
                event_monotonic_ns=1,
                pre_roll_ms=1,
                post_roll_ms=1,
                consent_record_id=consent.consent_record_id,
            )
            excerpt = materialize_evidence_audio_excerpt(store=store, ring_buffer=ring, request=request, consent=consent)
            candidate = create_manual_retention_candidate(excerpt=excerpt, proposed_service_period="review_then_delete")

            self.assertEqual(candidate.trigger_source, "manual_teacher_command")
            self.assertTrue(candidate.teacher_review_required)
            self.assertFalse(candidate.automatic_candidate)
            self.assertFalse(candidate.approved_for_permanent_retention)


if __name__ == "__main__":
    unittest.main()
