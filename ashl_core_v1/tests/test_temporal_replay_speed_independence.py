import unittest

from ashl_core_v1.runtime.grounded_temporal_primitive_compiler import verify_replay_speed_independence
from ashl_core_v1.tests._temporal_test_helpers import ARCHIVE, archive_available


class TemporalReplaySpeedIndependenceTests(unittest.TestCase):
    @unittest.skipUnless(archive_available(), "Package 124 archive not available")
    def test_1x_and_2x_replay_preserve_event_time_primitives(self):
        result = verify_replay_speed_independence(ARCHIVE)
        self.assertTrue(result["replay_speed_independence_verified"])


if __name__ == "__main__":
    unittest.main()

