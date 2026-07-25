import unittest

from ashl_core_v1.runtime.temporal_continuity_compiler import compile_repeated_occurrence_structure
from ashl_core_v1.tests._temporal_test_helpers import span


class TemporalRepeatedStructureTests(unittest.TestCase):
    def test_repeated_occurrences_have_no_rhythm_semantics(self):
        record = compile_repeated_occurrence_structure(
            (span("clock:test", 0, 100), span("clock:test", 1_000, 1_100), span("clock:test", 2_100, 2_200))
        )
        self.assertEqual(record.occurrence_count, 3)
        self.assertEqual(record.inter_onset_intervals_ns, (1_000, 1_100))
        self.assertIsNone(record.regularity_semantic_label)
        self.assertFalse(record.rhythm_semantics_claimed)


if __name__ == "__main__":
    unittest.main()

