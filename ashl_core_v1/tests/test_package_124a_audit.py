import tempfile
import unittest

from ashl_core_v1.runtime.grounded_temporal_primitive_compiler import calibrate_against_stimulus_after_compilation, compile_package_124_archive_temporal_bundle
from ashl_core_v1.runtime.package_124a_temporal_audit import audit_package_124a_temporal_foundation
from ashl_core_v1.tests._temporal_test_helpers import ARCHIVE, archive_available


class Package124AAuditTests(unittest.TestCase):
    @unittest.skipUnless(archive_available(), "Package 124 archive not available")
    def test_audit_passes_after_temporal_compile_and_calibration(self):
        with tempfile.TemporaryDirectory() as state_dir:
            compile_package_124_archive_temporal_bundle(
                archive_dir=ARCHIVE,
                state_dir=state_dir,
                persist=True,
                verify_archive=False,
            )
            calibrate_against_stimulus_after_compilation(archive_dir=ARCHIVE, state_dir=state_dir)
            audit = audit_package_124a_temporal_foundation(
                archive_dir=ARCHIVE,
                state_dir=state_dir,
                deterministic_identity_verified=True,
                replay_speed_independence_verified=True,
                package_124_archive_verified=True,
            )
        self.assertEqual(audit.audit_status, "passed_grounded_temporal_primitive_foundation_v0")
        self.assertFalse(audit.subjective_time_claimed)
        self.assertFalse(audit.package_112_score_changed)


if __name__ == "__main__":
    unittest.main()

