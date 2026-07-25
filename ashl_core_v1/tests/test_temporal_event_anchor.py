import unittest

from ashl_core_v1.tests._temporal_test_helpers import anchor


class TemporalEventAnchorTests(unittest.TestCase):
    def test_processing_and_replay_time_do_not_change_anchor_identity(self):
        first = anchor("clock:test", 100)
        second = anchor("clock:test", 100)
        self.assertEqual(first.temporal_anchor_id, second.temporal_anchor_id)
        self.assertNotEqual(first.normalized_event_time_ns, first.processing_time_ns)
        self.assertNotEqual(first.normalized_event_time_ns, first.replay_submission_time_ns)
        self.assertIsNone(first.action_tick)


if __name__ == "__main__":
    unittest.main()

