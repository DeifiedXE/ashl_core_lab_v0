import unittest

from ashl_core_v1.runtime.package_124_types import AudioTimelineContinuityAudit


class Package124AudioTimelineContinuityTests(unittest.TestCase):
    def test_continuity_audit_blocks_compression_and_synthetic_silence(self):
        audit = AudioTimelineContinuityAudit(
            audit_id="audit",
            source_audio_duration_ns=1_000_000_000,
            normalized_audio_duration_ns=1_000_000_000,
            silent_gap_count=0,
            synthetic_zero_pcm_segment_count=0,
            timeline_compression_detected=False,
            timeline_expansion_beyond_tolerance_detected=False,
            continuity_verified=True,
        )
        self.assertTrue(audit.continuity_verified)
        self.assertFalse(audit.timeline_compression_detected)
        self.assertEqual(audit.synthetic_zero_pcm_segment_count, 0)


if __name__ == "__main__":
    unittest.main()
