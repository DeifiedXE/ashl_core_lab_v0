import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.package_123_cycle_store import Package123CycleStore
from ashl_core_v1.runtime.package_123_types import (
    PREFLIGHT_SCHEMA_VERSION,
    Package123PreflightRecord,
)
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now


class Package123CycleStoreTests(unittest.TestCase):
    def test_store_creates_required_tables_and_appends_preflight(self):
        with TemporaryDirectory() as state_dir:
            store = Package123CycleStore(state_dir)
            schema = store.validate_schema()
            self.assertTrue(schema["valid"])
            record = Package123PreflightRecord(
                preflight_id=stable_id("package_123_preflight"),
                schema_version=PREFLIGHT_SCHEMA_VERSION,
                created_at=utc_now(),
                experiment_run_id="experiment:test",
                cycle_index=1,
                window_capture_ready=True,
                visual_contrast_verified=True,
                loopback_source_ready=True,
                loopback_tone_verified=True,
                background_audio_silent=True,
                host_state_ready=True,
                compiler_compatibility_verified=True,
                perception_profile_verified=True,
                llm_runtime_available=False,
                network_required=False,
                preflight_status="passed",
                failure_reasons=tuple(),
            )
            store.append_preflight(record)
            latest = store.latest_preflight(1)
            self.assertIsNotNone(latest)
            self.assertEqual(latest["preflight_id"], record.preflight_id)


if __name__ == "__main__":
    unittest.main()
