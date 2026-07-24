import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.package_123_preflight import (
    build_package_123_multimodal_config,
    run_package_123_preflight,
)


class Package123PreflightTests(unittest.TestCase):
    def test_preflight_records_no_codex_boundaries_without_opening_devices(self):
        with TemporaryDirectory() as state_dir:
            record = run_package_123_preflight(
                state_dir=state_dir,
                cycle_index=1,
                allow_dirty_tree=True,
                perform_real_checks=False,
            )
            self.assertEqual(record.preflight_status, "passed")
            self.assertTrue(record.window_capture_ready)
            self.assertTrue(record.loopback_source_ready)
            self.assertTrue(record.host_state_ready)
            self.assertFalse(record.llm_runtime_available)
            self.assertFalse(record.network_required)

    def test_package_123_config_excludes_camera_by_design(self):
        with TemporaryDirectory() as state_dir:
            config = build_package_123_multimodal_config(state_dir=state_dir)
            self.assertEqual(config.required_source_kinds, ("screen", "microphone", "host_state"))
            self.assertNotIn("camera", config.required_source_kinds)
            self.assertEqual(config.alignment_window_ms, 500)


if __name__ == "__main__":
    unittest.main()
