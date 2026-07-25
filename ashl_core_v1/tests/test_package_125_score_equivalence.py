from __future__ import annotations

import tempfile
import unittest

from ashl_core_v1.runtime.package_125_observation_extension_runtime import (
    run_synthetic_observation_extension_scenario,
)


class Package125ScoreEquivalenceTests(unittest.TestCase):
    def test_authoritative_package_112_score_is_identical(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            result = run_synthetic_observation_extension_scenario(state_dir=state_dir)
        score = result["score_equivalence"]
        self.assertEqual(score["authoritative_score_before"], score["authoritative_score_after"])
        self.assertEqual(
            score["authoritative_readback_delta_before"],
            score["authoritative_readback_delta_after"],
        )
        self.assertEqual(score["observation_extension_score_contribution"], 0)
        self.assertFalse(score["package_112_score_changed"])
        self.assertTrue(score["extension_context_read_only"])


if __name__ == "__main__":
    unittest.main()
