from __future__ import annotations

import tempfile
import unittest

from ashl_core_v1.runtime.package_125_observation_extension_runtime import (
    run_synthetic_observation_extension_scenario,
)


class ObservationExtensionPolicyTests(unittest.TestCase):
    def test_authorization_off_and_transport_fault_block(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            authorization_off = run_synthetic_observation_extension_scenario(
                state_dir=state_dir,
                scenario="authorization_off_control",
                allow_bounded_window_extension=False,
            )
            self.assertIsNotNone(authorization_off["candidate"])
            self.assertEqual(authorization_off["policy"]["decision"], "block")
            self.assertFalse(authorization_off["policy"]["authorization_valid"])
            self.assertIsNone(authorization_off["execution"])

            transport = run_synthetic_observation_extension_scenario(
                state_dir=state_dir,
                scenario="transport_fault_control",
                allow_bounded_window_extension=True,
            )
            self.assertEqual(transport["policy"]["decision"], "block")
            self.assertFalse(transport["policy"]["transport_integrity_valid"])
            self.assertIsNone(transport["execution"])
            self.assertEqual(transport["final_window_state"]["window_status"], "failed")

    def test_operator_stop_has_hard_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            result = run_synthetic_observation_extension_scenario(
                state_dir=state_dir,
                scenario="operator_stop_control",
            )
            self.assertEqual(result["policy"]["decision"], "block")
            self.assertIn("operator_stop_requested", result["policy"]["failure_reasons"])
            self.assertIsNone(result["execution"])
            self.assertEqual(result["final_window_state"]["window_status"], "operator_interrupted")


if __name__ == "__main__":
    unittest.main()
