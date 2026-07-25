from __future__ import annotations

import tempfile
import unittest

from ashl_core_v1.runtime.package_125_observation_extension_runtime import (
    run_synthetic_observation_extension_scenario,
)


class Package125LateEventRunTests(unittest.TestCase):
    def test_synthetic_late_event_extends_once_and_observes_closure(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            result = run_synthetic_observation_extension_scenario(state_dir=state_dir)
        self.assertEqual(result["status"], "extension_executed")
        self.assertEqual(result["execution"]["previous_deadline_ns"], 5_000_000_000)
        self.assertEqual(result["execution"]["applied_new_deadline_ns"], 6_500_000_000)
        self.assertEqual(result["final_window_state"]["extension_count"], 1)
        self.assertTrue(result["closure_links"])
        self.assertTrue(
            all(item["closure_event_time_ns"] > 5_000_000_000 for item in result["closure_links"])
        )
        self.assertGreater(result["outcome"]["post_event_context_ns"], 0)
        self.assertEqual(result["outcome"]["required_lane_drops"], 0)
        self.assertEqual(result["outcome"]["transport_faults"], 0)
        self.assertFalse(result["memory_write_created"])
        self.assertFalse(result["external_action_created"])
        self.assertFalse(result["output_created"])


if __name__ == "__main__":
    unittest.main()
