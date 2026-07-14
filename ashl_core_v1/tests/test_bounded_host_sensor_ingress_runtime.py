import os
import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime import (
    adapter_for_source,
    build_default_config_for_source,
    capture_once,
    list_sensor_backends,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore


class BoundedHostSensorIngressRuntimeTests(unittest.TestCase):
    def test_list_backends_reports_no_fixture_substitution(self) -> None:
        backends = list_sensor_backends()
        self.assertEqual(set(backends), {"camera", "screen", "microphone", "host_state"})
        for value in backends.values():
            self.assertFalse(value["fixture_capture"])

    def test_host_state_capture_does_not_enter_runtime_learning_or_memory(self) -> None:
        with TemporaryDirectory() as directory:
            result = capture_once(
                state_dir=directory,
                source_kind="host_state",
                duration_ms=1000,
            )
            self.assertEqual(result.source_kind, "host_state")
            self.assertTrue(result.artifact_ids)
            self.assertFalse(result.sensor_artifacts_entered_package_115)
            self.assertFalse(result.host_body_event_created)
            self.assertFalse(result.learning_feedback_candidate_created)
            self.assertFalse(result.teacher_review_created)
            self.assertFalse(result.memory_write_created)
            self.assertFalse(result.first_output_created)
            self.assertFalse(result.external_control_created)
            self.assertEqual(result.codex_runtime_call_count, 0)
            self.assertEqual(result.llm_runtime_call_count, 0)
            store = ContentAddressedSensorArtifactStore(directory)
            artifact = store.get_artifact(result.artifact_ids[0])
            self.assertGreater(artifact["byte_length"], 0)
            self.assertTrue(artifact["real_device_capture"])

    def test_default_config_requires_explicit_devices_or_screen_region(self) -> None:
        with TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                build_default_config_for_source(state_dir=directory, source_kind="camera")
            with self.assertRaises(ValueError):
                build_default_config_for_source(state_dir=directory, source_kind="microphone")
            with self.assertRaises(ValueError):
                build_default_config_for_source(state_dir=directory, source_kind="screen")

    def test_adapter_for_source_rejects_unknown_source(self) -> None:
        with self.assertRaises(ValueError):
            adapter_for_source("keyboard")


@unittest.skipUnless(
    os.environ.get("ASHL_REAL_SENSOR_SMOKE") == "1",
    "real_sensor_smoke tests run only when explicitly enabled",
)
class RealSensorSmokeTests(unittest.TestCase):
    def _assert_real_capture(self, source_kind: str, **kwargs) -> None:
        with TemporaryDirectory() as directory:
            result = capture_once(state_dir=directory, source_kind=source_kind, **kwargs)
            self.assertTrue(result.artifact_ids)
            store = ContentAddressedSensorArtifactStore(directory)
            artifact = store.get_artifact(result.artifact_ids[0])
            self.assertGreater(artifact["byte_length"], 0)
            self.assertTrue(artifact["real_device_capture"])
            self.assertTrue(store.verify_artifact(result.artifact_ids[0])["valid"])
            self.assertEqual(store.audit_store().audit_status, "passed_real_host_sensor_raw_artifact_store")

    def test_real_camera_smoke(self) -> None:
        self._assert_real_capture("camera", device_index=0)

    def test_real_screen_smoke(self) -> None:
        self._assert_real_capture("screen", monitor_index=1, region=(0, 0, 1, 1))

    def test_real_microphone_smoke(self) -> None:
        self._assert_real_capture("microphone", device_index=0, duration_ms=100)

    def test_real_host_state_smoke(self) -> None:
        self._assert_real_capture("host_state", duration_ms=1000)


if __name__ == "__main__":
    unittest.main()
