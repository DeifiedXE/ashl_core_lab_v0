import unittest

from ashl_core_v1.runtime.temporal_clock_domain import build_cross_process_external_gap


class CrossProcessExternalGapTests(unittest.TestCase):
    def test_external_gap_uses_utc_not_cross_process_monotonic_subtraction(self):
        gap = build_cross_process_external_gap(
            previous_process_instance_id="process:a",
            current_process_instance_id="process:b",
            previous_last_event_utc="2026-07-24T00:00:00+00:00",
            current_first_event_utc="2026-07-24T00:00:02+00:00",
            previous_clock_domain_id="clock:a",
            current_clock_domain_id="clock:b",
        )
        self.assertEqual(gap.external_gap_ns, 2_000_000_000)
        self.assertFalse(gap.experienced_during_gap)
        self.assertFalse(gap.synthetic_ticks_created)

    def test_backward_wall_clock_is_indeterminate(self):
        gap = build_cross_process_external_gap(
            previous_process_instance_id="process:a",
            current_process_instance_id="process:b",
            previous_last_event_utc="2026-07-24T00:00:02+00:00",
            current_first_event_utc="2026-07-24T00:00:00+00:00",
            previous_clock_domain_id="clock:a",
            current_clock_domain_id="clock:b",
        )
        self.assertEqual(gap.gap_status, "indeterminate_clock_change")
        self.assertIsNone(gap.external_gap_ns)


if __name__ == "__main__":
    unittest.main()

