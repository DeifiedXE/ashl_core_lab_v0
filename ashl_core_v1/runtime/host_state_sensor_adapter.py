"""Restricted host-state sensor adapter for Package 120."""

from __future__ import annotations

import ctypes
import importlib.util
import os
import platform
import time
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import (
    DEVICE_DESCRIPTOR_SCHEMA_VERSION,
    SensorCaptureConfig,
    SensorCaptureError,
    SensorDeviceDescriptor,
    canonical_json,
    monotonic_ns,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.sensor_adapter_protocol import AdapterOutputSample


_PROCESS_STARTED_MONOTONIC_NS = time.monotonic_ns()


class _SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", ctypes.c_byte),
        ("BatteryFlag", ctypes.c_byte),
        ("BatteryLifePercent", ctypes.c_byte),
        ("SystemStatusFlag", ctypes.c_byte),
        ("BatteryLifeTime", ctypes.c_ulong),
        ("BatteryFullLifeTime", ctypes.c_ulong),
    ]


class _MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


class HostStateSensorAdapter:
    source_kind = "host_state"
    adapter_id = "host_state_restricted_json_v0"
    adapter_version = "v0"

    def __init__(self) -> None:
        self._config: SensorCaptureConfig | None = None
        self._descriptor = self._build_descriptor()

    def enumerate_devices(self) -> tuple[SensorDeviceDescriptor, ...]:
        return (self._descriptor,)

    def open(self, config: SensorCaptureConfig) -> None:
        if config.source_kind != self.source_kind:
            raise SensorCaptureError("unsupported_format", "host-state adapter received non-host-state config")
        self._config = config

    def read_sample(self) -> AdapterOutputSample:
        if self._config is None:
            raise SensorCaptureError("device_open_failed", "host-state adapter is not open")
        started = monotonic_ns()
        payload = _restricted_host_state_payload()
        data = canonical_json(payload).encode("utf-8")
        ended = monotonic_ns()
        return AdapterOutputSample(
            sample_id=stable_id("host_state_sample"),
            source_kind=self.source_kind,
            adapter_id=self.adapter_id,
            adapter_version=self.adapter_version,
            device_descriptor_id=self._descriptor.device_descriptor_id,
            captured_at_utc=utc_now(),
            captured_at_monotonic_ns=ended,
            capture_duration_ns=ended - started,
            raw_level="adapter_output",
            media_type="application/json",
            storage_format="utf8_canonical_json",
            data=data,
            metadata={
                "host_state_fields": tuple(payload.keys()),
                "forbidden_fields_excluded": True,
            },
            real_device_capture=True,
        )

    def pause(self) -> None:
        return None

    def resume(self) -> None:
        return None

    def close(self) -> None:
        self._config = None

    def _build_descriptor(self) -> SensorDeviceDescriptor:
        return SensorDeviceDescriptor(
            device_descriptor_id=stable_id("sensor_device_descriptor"),
            schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
            created_at=utc_now(),
            source_kind=self.source_kind,
            adapter_id=self.adapter_id,
            adapter_version=self.adapter_version,
            device_id="host_state:restricted",
            device_index=None,
            device_display_name="Restricted local host-state sample",
            backend_name=f"stdlib-{platform.system().lower()}",
            available=True,
            permission_status="not_applicable",
            supported_format_summary=("utf8_canonical_json",),
            read_only=True,
            external_control_allowed=False,
            real_device_capture=True,
        )


def _restricted_host_state_payload() -> dict[str, Any]:
    now = monotonic_ns()
    payload: dict[str, Any] = {
        "sample_monotonic_ns": now,
        "process_uptime_ns": now - _PROCESS_STARTED_MONOTONIC_NS,
        "power_source": None,
        "battery_percent": None,
        "cpu_utilization_percent": None,
        "memory_total_bytes": None,
        "memory_available_bytes": None,
        "display_count": _display_count(),
        "camera_adapter_available": importlib.util.find_spec("cv2") is not None,
        "microphone_adapter_available": _microphone_adapter_available(),
        "screen_adapter_available": _screen_adapter_available(),
    }
    payload.update(_windows_power_payload())
    payload.update(_windows_memory_payload())
    return payload


def _windows_power_payload() -> dict[str, Any]:
    if os.name != "nt":
        return {}
    status = _SYSTEM_POWER_STATUS()
    if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
        return {
            "power_source": {0: "battery", 1: "ac", 255: "unknown"}.get(int(status.ACLineStatus), "unknown"),
            "battery_percent": None if int(status.BatteryLifePercent) == 255 else int(status.BatteryLifePercent),
        }
    return {}


def _windows_memory_payload() -> dict[str, Any]:
    if os.name != "nt":
        return {}
    status = _MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(_MEMORYSTATUSEX)
    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return {
            "memory_total_bytes": int(status.ullTotalPhys),
            "memory_available_bytes": int(status.ullAvailPhys),
        }
    return {}


def _display_count() -> int | None:
    if os.name == "nt":
        try:
            return int(ctypes.windll.user32.GetSystemMetrics(80))
        except Exception:
            return None
    return None


def _screen_adapter_available() -> bool:
    return importlib.util.find_spec("mss") is not None or os.name == "nt"


def _microphone_adapter_available() -> bool:
    return importlib.util.find_spec("sounddevice") is not None or os.name == "nt"
