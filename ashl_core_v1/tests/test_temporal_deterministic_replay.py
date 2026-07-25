import unittest

from ashl_core_v1.runtime.grounded_temporal_primitive_compiler import verify_temporal_deterministic_replay
from ashl_core_v1.tests._temporal_test_helpers import ARCHIVE, archive_available


class TemporalDeterministicReplayTests(unittest.TestCase):
    @unittest.skipUnless(archive_available(), "Package 124 archive not available")
    def test_same_archive_evidence_recompiles_to_same_ids(self):
        result = verify_temporal_deterministic_replay(ARCHIVE)
        self.assertTrue(result["deterministic_identity_verified"])


if __name__ == "__main__":
    unittest.main()

