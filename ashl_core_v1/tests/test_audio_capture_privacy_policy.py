import unittest

from ashl_core_v1.perception.audio_capture_privacy_policy import (
    AUDIO_CAPTURE_PRIVACY_POLICY_SCHEMA_VERSION,
    AudioCapturePrivacyPolicy,
    build_recognition_ephemeral_audio_privacy_policy,
    validate_audio_capture_privacy_policy,
)


class AudioCapturePrivacyPolicyTests(unittest.TestCase):
    def test_recognition_ephemeral_policy_blocks_raw_and_semantic_audio(self) -> None:
        policy = build_recognition_ephemeral_audio_privacy_policy()

        self.assertEqual(policy.schema_version, AUDIO_CAPTURE_PRIVACY_POLICY_SCHEMA_VERSION)
        self.assertFalse(policy.raw_disk_persistence_allowed)
        self.assertFalse(policy.exact_speaker_embedding_allowed)
        self.assertFalse(policy.absolute_pitch_storage_allowed)
        self.assertFalse(policy.speech_content_interpretation_allowed)
        self.assertTrue(policy.relative_pitch_contour_allowed)
        self.assertTrue(policy.provisional_policy)
        self.assertTrue(validate_audio_capture_privacy_policy(policy)["valid"])

    def test_policy_rejects_speaker_embedding(self) -> None:
        with self.assertRaises(ValueError):
            AudioCapturePrivacyPolicy(
                **{
                    **build_recognition_ephemeral_audio_privacy_policy().to_dict(),
                    "policy_id": "policy:bad",
                    "exact_speaker_embedding_allowed": True,
                }
            )


if __name__ == "__main__":
    unittest.main()
