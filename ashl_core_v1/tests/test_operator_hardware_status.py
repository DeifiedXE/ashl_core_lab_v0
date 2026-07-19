import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import (
    DEVICE_DESCRIPTOR_SCHEMA_VERSION,
    SensorDeviceDescriptor,
    build_sensor_capture_config,
    utc_now,
)
from ashl_core_v1.runtime.local_operator_console_store import build_default_console_store
from ashl_core_v1.runtime.operator_hardware_status import (
    build_hardware_device_console_status,
    build_hardware_settings_snapshot,
    find_active_capture_session_id,
    set_output_volume_state,
)


def _descriptor(source_kind: str) -> SensorDeviceDescriptor:
    return SensorDeviceDescriptor(
        device_descriptor_id=f"sensor_device_descriptor:{source_kind}",
        schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
        created_at=utc_now(),
        source_kind=source_kind,
        adapter_id=f"{source_kind}_real_adapter_v0",
        adapter_version="v0",
        device_id=f"{source_kind}:0",
        device_index=0,
        device_display_name=f"{source_kind} device",
        backend_name="test_backend",
        available=True,
        permission_status="granted",
        supported_format_summary=("adapter_output",),
        read_only=True,
        external_control_allowed=False,
    )


def _active_sensor_session(state_dir: str, source_kind: str) -> str:
    sensor_store = ContentAddressedSensorArtifactStore(state_dir)
    descriptor = _descriptor(source_kind)
    if source_kind == "camera":
        source_specific = {
            "device_index": 0,
            "requested_width": 2,
            "requested_height": 2,
            "requested_fps": 1,
            "capture_frame_count": 1,
            "read_timeout_ms": 100,
        }
    else:
        source_specific = {
            "input_device_index": 0,
            "requested_sample_rate": 16000,
            "requested_channels": 1,
            "requested_sample_format": "int16",
            "chunk_duration_ms": 100,
            "capture_duration_ms": 100,
        }
    config = build_sensor_capture_config(
        source_kind=source_kind,
        adapter_id=descriptor.adapter_id,
        device_id=descriptor.device_id,
        explicit_state_dir=state_dir,
        source_specific_config=source_specific,
    )
    session = sensor_store.create_capture_session(source_kind=source_kind, config=config, descriptor=descriptor)
    sensor_store.append_lifecycle_event(
        session=session,
        previous_status="created",
        new_status="running",
        manual_command="start",
        reason_code="test_active_capture",
    )
    return session.capture_session_id


class OperatorHardwareStatusTests(unittest.TestCase):
    def test_enabled_preference_does_not_open_device(self) -> None:
        with TemporaryDirectory() as state_dir:
            store = build_default_console_store(state_dir)
            preference = store.set_hardware_preference(device_kind="microphone", enabled=True)
            status = build_hardware_device_console_status(state_dir=state_dir, store=store, device_kind="microphone")

            self.assertTrue(preference["enabled_preference"])
            self.assertFalse(preference["device_opened"])
            self.assertEqual(status.indicator_state, "enabled_idle")
            self.assertIsNone(status.active_capture_session_id)

    def test_active_indicator_requires_actual_capture_session(self) -> None:
        with TemporaryDirectory() as state_dir:
            active_session_id = _active_sensor_session(state_dir, "camera")
            store = build_default_console_store(state_dir)
            store.set_hardware_preference(device_kind="camera", enabled=True)

            active, error, _refs = find_active_capture_session_id(state_dir, "camera")
            status = build_hardware_device_console_status(state_dir=state_dir, store=store, device_kind="camera")

            self.assertEqual(active, active_session_id)
            self.assertIsNone(error)
            self.assertEqual(status.indicator_state, "active")
            self.assertEqual(status.active_capture_session_id, active_session_id)

    def test_hardware_settings_sanitizes_device_descriptors_and_volume(self) -> None:
        with TemporaryDirectory() as state_dir:
            _active_sensor_session(state_dir, "microphone")
            store = build_default_console_store(state_dir)
            set_output_volume_state(store, gain=0.25)

            settings = build_hardware_settings_snapshot(state_dir=state_dir, store=store)

            self.assertEqual(settings.output_gain, 0.25)
            self.assertEqual(settings.available_microphone_devices[0]["device_id"], "microphone:0")
            self.assertNotIn("payload_json", settings.available_microphone_devices[0])
            self.assertNotIn("raw_pcm", str(settings.to_dict()).lower())


if __name__ == "__main__":
    unittest.main()
