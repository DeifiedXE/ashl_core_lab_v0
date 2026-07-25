import unittest

from ashl_core_v1.runtime.temporal_clock_domain import (
    build_action_ordinal_position,
    build_clock_domain_descriptor,
    evaluate_clock_quality,
)


class TemporalClockDomainTests(unittest.TestCase):
    def test_valid_process_creates_verified_clock_domain(self):
        domain = build_clock_domain_descriptor(
            process_instance_id="process:a",
            operating_system_process_id=1,
            utc_anchor="2026-07-24T00:00:00+00:00",
            utc_anchor_monotonic_ns=0,
        )
        quality = evaluate_clock_quality(domain, (0, 1, 2))
        self.assertTrue(domain.comparable_within_process)
        self.assertEqual(domain.cross_process_comparison_method, "persisted_utc_anchor_with_recorded_uncertainty")
        self.assertEqual(quality.quality_status, "verified")

    def test_invalid_clock_domain_fails_closed(self):
        with self.assertRaises(ValueError):
            build_clock_domain_descriptor(
                process_instance_id="process:a",
                operating_system_process_id=1,
                utc_anchor="not-a-time",
                utc_anchor_monotonic_ns=0,
            )

    def test_action_tick_is_ordinal_not_elapsed_time(self):
        position = build_action_ordinal_position(3, "session:x")
        self.assertFalse(position.elapsed_time_claimed)


if __name__ == "__main__":
    unittest.main()

