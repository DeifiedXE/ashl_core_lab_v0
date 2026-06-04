import unittest

from ashl_core.deliberation import deliberate


class DeliberationTests(unittest.TestCase):
    def test_fatigue_outranks_self_check(self):
        result = deliberate(
            None,
            [{"type": "user_fatigue_possible", "confidence": 0.9}, {"type": "memory_candidate_possible", "confidence": 0.9}],
            {"self_check_pressure": 1.0, "user_fatigue": 0.9},
        )

        self.assertEqual(result["intent"], "fatigue_close")

    def test_memory_candidate_triggers_self_check(self):
        result = deliberate(None, [{"type": "memory_candidate_possible", "confidence": 0.9}], {})

        self.assertEqual(result["intent"], "self_check")

    def test_formal_reasoning_precedes_arithmetic(self):
        result = deliberate(
            None,
            [{"type": "requires_formal_reasoning", "confidence": 0.9}, {"type": "simple_arithmetic", "confidence": 0.9}],
            {},
        )

        self.assertEqual(result["intent"], "unknown_need_tool")


if __name__ == "__main__":
    unittest.main()
