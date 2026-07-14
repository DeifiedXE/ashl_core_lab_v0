import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime import BoundedHostSensorIngressRuntime
from ashl_core_v1.runtime.host_sensor_types import build_sensor_capture_config
from ashl_core_v1.tests.test_sensor_adapter_protocol import FixtureSensorAdapter


class SensorCaptureLifecycleTests(unittest.TestCase):
    def _config(self, directory: str, artifact_count: int = 2, byte_budget: int = 1024):
        return build_sensor_capture_config(
            source_kind="host_state",
            adapter_id="fixture_sensor_adapter_v0",
            device_id="fixture:host_state",
            explicit_state_dir=directory,
            source_specific_config={"host_state_fields": "restricted_v0"},
            maximum_artifact_count=artifact_count,
            maximum_total_bytes=byte_budget,
        )

    def test_manual_start_pause_resume_stop_lifecycle(self) -> None:
        with TemporaryDirectory() as directory:
            runtime = BoundedHostSensorIngressRuntime(
                state_dir=directory,
                adapter=FixtureSensorAdapter(),
            )
            session = runtime.start(self._config(directory))
            self.assertEqual(runtime.status, "running")
            runtime.pause()
            self.assertEqual(runtime.status, "paused")
            with self.assertRaises(RuntimeError):
                runtime.capture_next_sample()
            runtime.resume()
            artifact_id = runtime.capture_next_sample()
            self.assertTrue(artifact_id.startswith("sensor_raw_artifact:"))
            runtime.stop()
            self.assertEqual(runtime.status, "stopped")
            result = runtime.result(session)
            self.assertFalse(result.memory_write_created)
            self.assertFalse(result.learning_feedback_candidate_created)

    def test_hard_artifact_count_stop_works(self) -> None:
        with TemporaryDirectory() as directory:
            runtime = BoundedHostSensorIngressRuntime(
                state_dir=directory,
                adapter=FixtureSensorAdapter(),
            )
            runtime.run_once(self._config(directory, artifact_count=1))
            self.assertEqual(runtime.status, "hard_budget_stopped")

    def test_hard_byte_budget_stop_works(self) -> None:
        with TemporaryDirectory() as directory:
            runtime = BoundedHostSensorIngressRuntime(
                state_dir=directory,
                adapter=FixtureSensorAdapter(),
            )
            runtime.start(self._config(directory, artifact_count=2, byte_budget=1))
            with self.assertRaises(Exception):
                runtime.capture_next_sample()
            self.assertEqual(runtime.status, "capture_failed")
            self.assertTrue(runtime.failure_ids)

    def test_invalid_lifecycle_transitions_are_blocked(self) -> None:
        with TemporaryDirectory() as directory:
            runtime = BoundedHostSensorIngressRuntime(
                state_dir=directory,
                adapter=FixtureSensorAdapter(),
            )
            with self.assertRaises(RuntimeError):
                runtime.pause()
            session = runtime.start(self._config(directory))
            with self.assertRaises(RuntimeError):
                runtime.resume()
            runtime.stop()
            with self.assertRaises(RuntimeError):
                runtime.stop()
            self.assertEqual(runtime.result(session).capture_status, "stopped")


if __name__ == "__main__":
    unittest.main()
