from __future__ import annotations

import tempfile
import unittest

from ashl_core_v1.runtime.package_125_observation_extension_runtime import (
    run_synthetic_package_125_suite,
)


class Package125ControlTests(unittest.TestCase):
    def test_all_isolated_controls_hold(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            suite = run_synthetic_package_125_suite(state_dir=state_dir)
        audit = suite["audit"]
        self.assertTrue(audit["stable_control_did_not_extend"])
        self.assertTrue(audit["early_complete_control_did_not_extend"])
        self.assertTrue(audit["authorization_off_control_blocked"])
        self.assertTrue(audit["operator_interrupt_verified"])
        self.assertEqual(
            suite["results"]["transport_fault_control"]["final_window_state"]["window_status"],
            "failed",
        )


if __name__ == "__main__":
    unittest.main()
