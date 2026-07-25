import unittest

from ashl_core_v1.tests._temporal_test_helpers import anchor
from ashl_core_v1.runtime.temporal_relation_compiler import build_temporal_interval


class TemporalIntervalCompilerTests(unittest.TestCase):
    def test_onset_to_onset_interval_is_numeric_only(self):
        interval = build_temporal_interval(
            interval_kind="onset_to_onset",
            left_anchor=anchor("clock:test", 1_000),
            right_anchor=anchor("clock:test", 3_000),
        )
        self.assertEqual(interval.interval_ns, 2_000)
        self.assertIsNone(interval.semantic_label)

    def test_offset_to_onset_interval_can_be_negative_but_not_semantic(self):
        interval = build_temporal_interval(
            interval_kind="offset_to_onset",
            left_anchor=anchor("clock:test", 3_000),
            right_anchor=anchor("clock:test", 2_000),
        )
        self.assertEqual(interval.interval_ns, -1_000)
        self.assertIsNone(interval.semantic_label)


if __name__ == "__main__":
    unittest.main()

