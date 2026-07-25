import unittest

from ashl_core_v1.runtime.package_124_types import MilestoneReadbackTimingAudit


class Package124ReadbackInfluenceTests(unittest.TestCase):
    def test_readback_timing_requires_load_before_stimulus_and_candidate(self):
        audit = MilestoneReadbackTimingAudit(
            audit_id="timing",
            working_readback_id="working_readback_commit:cycle1",
            cycle_2_session_id="bounded_embodied_session:ca638e025eb6",
            readback_loaded_monotonic_ns=100,
            capture_started_monotonic_ns=150,
            stimulus_started_monotonic_ns=200,
            candidate_evaluated_monotonic_ns=300,
            loaded_before_capture=True,
            loaded_before_stimulus=True,
            loaded_before_candidate_evaluation=True,
            timing_verified=True,
        )
        self.assertTrue(audit.timing_verified)
        self.assertTrue(audit.loaded_before_stimulus)
        self.assertTrue(audit.loaded_before_candidate_evaluation)


if __name__ == "__main__":
    unittest.main()
