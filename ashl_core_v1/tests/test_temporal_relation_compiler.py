import unittest

from ashl_core_v1.runtime.temporal_relation_compiler import derive_temporal_relation
from ashl_core_v1.tests._temporal_test_helpers import span


class TemporalRelationCompilerTests(unittest.TestCase):
    def test_before_meets_overlap_contains(self):
        left = span("clock:test", 0, 100)
        before = derive_temporal_relation(left, span("clock:test", 300, 400), comparison_tolerance_ns=0)
        meets = derive_temporal_relation(left, span("clock:test", 100, 200), comparison_tolerance_ns=0)
        overlaps = derive_temporal_relation(left, span("clock:test", 50, 150), comparison_tolerance_ns=0)
        contains = derive_temporal_relation(left, span("clock:test", 25, 75), comparison_tolerance_ns=0)
        self.assertEqual(before.relation_kind, "before")
        self.assertEqual(meets.relation_kind, "meets")
        self.assertEqual(overlaps.relation_kind, "overlaps")
        self.assertEqual(overlaps.overlap_ns, 50)
        self.assertEqual(contains.relation_kind, "contains")
        self.assertIsNone(before.semantic_label)


if __name__ == "__main__":
    unittest.main()

