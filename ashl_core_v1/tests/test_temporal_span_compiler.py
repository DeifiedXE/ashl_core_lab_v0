import unittest

from ashl_core_v1.tests._temporal_test_helpers import anchor
from ashl_core_v1.runtime.temporal_relation_compiler import build_temporal_span


class TemporalSpanCompilerTests(unittest.TestCase):
    def test_negative_duration_rejected(self):
        with self.assertRaises(ValueError):
            build_temporal_span(
                span_kind="observed_change_region",
                start_anchor=anchor("clock:test", 100),
                end_anchor=anchor("clock:test", 50),
                source_lane="screen",
            )

    def test_zero_duration_remains_anchor_not_span(self):
        with self.assertRaises(ValueError):
            build_temporal_span(
                span_kind="observed_change_region",
                start_anchor=anchor("clock:test", 100),
                end_anchor=anchor("clock:test", 100),
                source_lane="screen",
            )

    def test_visual_change_region_produces_span_without_semantics(self):
        record = build_temporal_span(
            span_kind="observed_change_region",
            start_anchor=anchor("clock:test", 0),
            end_anchor=anchor("clock:test", 500),
            source_lane="screen",
        )
        self.assertEqual(record.observed_duration_ns, 500)
        self.assertIsNone(record.semantic_label)
        self.assertFalse(record.subjective_duration_claimed)


if __name__ == "__main__":
    unittest.main()

