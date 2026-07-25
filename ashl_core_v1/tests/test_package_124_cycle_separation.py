import os
import unittest
from pathlib import Path

from ashl_core_v1.runtime.package_124_source_audit import audit_package_124_source


PACKAGE_123_STATE_DIR = Path(
    r"C:\Users\zxc12\AppData\Local\Temp\ashl_package123_run_e1c462d77e4d46d099bc9947c38c3e4d"
)


@unittest.skipUnless(
    os.environ.get("ASHL_PACKAGE124_SOURCE_AUDIT_SMOKE") == "1" and PACKAGE_123_STATE_DIR.exists(),
    "set ASHL_PACKAGE124_SOURCE_AUDIT_SMOKE=1 to audit the real Package 123 state dir",
)
class Package124CycleSeparationSmokeTests(unittest.TestCase):
    def test_real_source_cycle_two_readback_and_process_boundary_pass(self):
        result = audit_package_124_source(PACKAGE_123_STATE_DIR, expected_commit="8c38918")
        audit = result["audit"]
        self.assertTrue(audit["cycle_process_separation_verified"])
        self.assertTrue(audit["cycle_2_readback_timing_verified"])
        self.assertTrue(audit["cycle_2_package_112_influence_verified"])


if __name__ == "__main__":
    unittest.main()
