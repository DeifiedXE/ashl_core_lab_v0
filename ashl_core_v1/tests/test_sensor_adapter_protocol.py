import unittest
import json
from tempfile import TemporaryDirectory
from unittest.mock import patch

from ashl_core_v1.runtime.camera_sensor_adapter import CameraSensorAdapter
from ashl_core_v1.runtime.host_state_sensor_adapter import HostStateSensorAdapter
from ashl_core_v1.runtime.host_sensor_types import (
    DEVICE_DESCRIPTOR_SCHEMA_VERSION,
    SensorCaptureError,
    SensorDeviceDescriptor,
    build_sensor_capture_config,
    monotonic_ns,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.sensor_adapter_protocol import AdapterOutputSample, SensorAdapter


class FixtureSensorAdapter:
    source_kind = "host_state"
    adapter_id = "fixture_sensor_adapter_v0"
    adapter_version = "v0"

    def __init__(self) -> None:
        self.opened = False
        self.closed = False

    def enumerate_devices(self) -> tuple[SensorDeviceDescriptor, ...]:
        return (
            SensorDeviceDescriptor(
                device_descriptor_id=stable_id("sensor_device_descriptor"),
                schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
                created_at=utc_now(),
                source_kind="host_state",
                adapter_id=self.adapter_id,
                adapter_version=self.adapter_version,
                device_id="fixture:host_state",
                device_index=None,
                device_display_name="fixture host-state adapter",
                backend_name="fixture",
                available=True,
                permission_status="not_applicable",
                supported_format_summary=("fixture_bytes",),
                read_only=True,
                external_control_allowed=False,
                real_device_capture=False,
                fixture_device=True,
            ),
        )

    def open(self, config):
        self.opened = True

    def read_sample(self) -> AdapterOutputSample:
        captured = monotonic_ns()
        return AdapterOutputSample(
            sample_id=stable_id("fixture_sample"),
            source_kind="host_state",
            adapter_id=self.adapter_id,
            adapter_version=self.adapter_version,
            device_descriptor_id=self.enumerate_devices()[0].device_descriptor_id,
            captured_at_utc=utc_now(),
            captured_at_monotonic_ns=captured,
            capture_duration_ns=1,
            raw_level="adapter_output",
            media_type="application/octet-stream",
            storage_format="fixture_bytes",
            data=b"fixture",
            metadata={"fixture_capture": True},
            real_device_capture=False,
        )

    def pause(self):
        return None

    def resume(self):
        return None

    def close(self):
        self.closed = True


class SensorAdapterProtocolTests(unittest.TestCase):
    def test_fixture_adapter_is_explicitly_not_real_capture(self) -> None:
        adapter = FixtureSensorAdapter()
        self.assertIsInstance(adapter, SensorAdapter)
        descriptor = adapter.enumerate_devices()[0]
        self.assertTrue(descriptor.fixture_device)
        self.assertFalse(descriptor.real_device_capture)
        self.assertTrue(descriptor.read_only)
        self.assertFalse(descriptor.external_control_allowed)

    def test_adapter_open_read_close_do_not_create_learning_or_actions(self) -> None:
        adapter = FixtureSensorAdapter()
        with TemporaryDirectory() as directory:
            config = build_sensor_capture_config(
                source_kind="host_state",
                adapter_id=adapter.adapter_id,
                device_id="fixture:host_state",
                explicit_state_dir=directory,
                source_specific_config={"host_state_fields": "restricted_v0"},
            )
            adapter.open(config)
            sample = adapter.read_sample()
            adapter.close()
        self.assertTrue(adapter.opened)
        self.assertTrue(adapter.closed)
        self.assertEqual(sample.raw_level, "adapter_output")
        self.assertFalse(sample.real_device_capture)

    def test_missing_camera_backend_reports_backend_missing(self) -> None:
        with patch("importlib.util.find_spec", return_value=None):
            adapter = CameraSensorAdapter()
            descriptor = adapter.enumerate_devices()[0]
            self.assertFalse(descriptor.available)
            self.assertEqual(descriptor.backend_name, "missing")
            with TemporaryDirectory() as directory:
                config = build_sensor_capture_config(
                    source_kind="camera",
                    adapter_id=adapter.adapter_id,
                    device_id="camera:opencv:0",
                    explicit_state_dir=directory,
                    source_specific_config={"device_index": 0, "requested_fps": 1},
                )
                with self.assertRaises(SensorCaptureError) as ctx:
                    adapter.open(config)
            self.assertEqual(ctx.exception.failure_kind, "backend_missing")

    def test_host_state_adapter_outputs_only_restricted_fields(self) -> None:
        adapter = HostStateSensorAdapter()
        with TemporaryDirectory() as directory:
            config = build_sensor_capture_config(
                source_kind="host_state",
                adapter_id=adapter.adapter_id,
                device_id="host_state:restricted",
                explicit_state_dir=directory,
                source_specific_config={"host_state_fields": "restricted_v0"},
            )
            adapter.open(config)
            sample = adapter.read_sample()
            adapter.close()
        payload = json.loads(sample.data.decode("utf-8"))
        self.assertIn("sample_monotonic_ns", payload)
        forbidden = {
            "process_list",
            "window_titles",
            "clipboard",
            "browser_history",
            "file_listing",
            "account_names",
        }
        self.assertFalse(forbidden.intersection(payload))
        self.assertTrue(sample.real_device_capture)


if __name__ == "__main__":
    unittest.main()
