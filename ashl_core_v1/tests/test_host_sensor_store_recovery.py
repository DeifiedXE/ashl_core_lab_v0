import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime import BoundedHostSensorIngressRuntime
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import SensorCaptureSessionRecord, build_sensor_capture_config
from ashl_core_v1.tests.test_sensor_adapter_protocol import FixtureSensorAdapter


class HostSensorStoreRecoveryTests(unittest.TestCase):
    def test_temporary_files_are_quarantined_on_open(self) -> None:
        with TemporaryDirectory() as directory:
            store = ContentAddressedSensorArtifactStore(directory)
            tmp = store.root_dir / ".sensor_blob_test.tmp"
            tmp.write_bytes(b"partial")
            reopened = ContentAddressedSensorArtifactStore(directory)
            self.assertFalse(tmp.exists())
            self.assertTrue(tuple(reopened.quarantine_dir.glob("*.tmp")))
            self.assertGreaterEqual(reopened.audit_store().temporary_file_count, 1)

    def test_running_session_is_recovered_aborted_on_reopen(self) -> None:
        with TemporaryDirectory() as directory:
            config = build_sensor_capture_config(
                source_kind="host_state",
                adapter_id="fixture_sensor_adapter_v0",
                device_id="fixture:host_state",
                explicit_state_dir=directory,
                source_specific_config={"host_state_fields": "restricted_v0"},
            )
            runtime = BoundedHostSensorIngressRuntime(
                state_dir=directory,
                adapter=FixtureSensorAdapter(),
            )
            session = runtime.start(config)
            reopened = ContentAddressedSensorArtifactStore(directory)
            statuses = [
                item["new_status"]
                for item in reopened._payloads("sensor_capture_lifecycle_events", "sequence_index")
                if item["session_id"] == session.session_id
            ]
            self.assertEqual(statuses[-1], "recovered_aborted")

    def test_recovered_aborted_session_is_not_synthesized_as_artifact(self) -> None:
        with TemporaryDirectory() as directory:
            store = ContentAddressedSensorArtifactStore(directory)
            sessions = store.list_capture_sessions()
            self.assertEqual(sessions, tuple())
            self.assertEqual(store.list_artifacts(), tuple())


if __name__ == "__main__":
    unittest.main()
