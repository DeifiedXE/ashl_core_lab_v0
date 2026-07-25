import unittest

from ashl_core_v1.runtime.temporal_context_sidecar import verify_package_112_score_equivalence


class Package124AScoreEquivalenceTests(unittest.TestCase):
    def test_temporal_sidecar_contributes_zero_score(self):
        result = verify_package_112_score_equivalence(93.0, 93.0)
        self.assertFalse(result["package_112_score_changed"])
        self.assertEqual(result["temporal_score_contribution"], 0.0)


if __name__ == "__main__":
    unittest.main()

