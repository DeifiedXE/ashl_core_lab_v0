"""Bounded Windows HWND client-area capture for Package 123."""

from __future__ import annotations

import ctypes
import os
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import (
    DEVICE_DESCRIPTOR_SCHEMA_VERSION,
    SensorCaptureConfig,
    SensorCaptureError,
    SensorCaptureSessionRecord,
    SensorDeviceDescriptor,
    build_sensor_capture_config,
    monotonic_ns,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.package_123_types import (
    WINDOW_BINDING_SCHEMA_VERSION,
    BoundedWindowCaptureBinding,
)
from ashl_core_v1.runtime.screen_sensor_adapter import _capture_bgra8_windows_gdi
from ashl_core_v1.runtime.sensor_adapter_protocol import AdapterOutputSample


WINDOW_CAPTURE_ADAPTER_ID = "windows_window_capture_bgra8_v0"
WINDOW_CAPTURE_ADAPTER_VERSION = "v0"


class _RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


class _POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class WindowsBoundedWindowCaptureSource:
    source_kind = "screen"
    adapter_id = WINDOW_CAPTURE_ADAPTER_ID
    adapter_version = WINDOW_CAPTURE_ADAPTER_VERSION

    def __init__(self) -> None:
        self._descriptor = self.build_descriptor()
        self._frame_index = 0

    def build_descriptor(self) -> SensorDeviceDescriptor:
        available = os.name == "nt"
        return SensorDeviceDescriptor(
            device_descriptor_id=stable_id("sensor_device_descriptor"),
            schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
            created_at=utc_now(),
            source_kind="screen",
            adapter_id=self.adapter_id,
            adapter_version=self.adapter_version,
            device_id="screen:windows_hwnd_client_area",
            device_index=None,
            device_display_name="Windows HWND client-area pixels",
            backend_name="windows_gdi_client_rect" if available else "missing",
            available=available,
            permission_status="unknown" if available else "not_applicable",
            supported_format_summary=("BGRA8",) if available else tuple(),
            read_only=True,
            external_control_allowed=False,
            real_device_capture=available,
        )

    def bind_by_title(self, *, experiment_run_id: str, window_title: str) -> BoundedWindowCaptureBinding:
        if os.name != "nt":
            return _binding(
                experiment_run_id=experiment_run_id,
                hwnd=0,
                title=window_title,
                process_id=0,
                left=0,
                top=0,
                width=0,
                height=0,
                status="window_not_found",
            )
        user32 = ctypes.windll.user32
        hwnd = int(user32.FindWindowW(None, window_title))
        if not hwnd:
            return _binding(experiment_run_id=experiment_run_id, hwnd=0, title=window_title, process_id=0, left=0, top=0, width=0, height=0, status="window_not_found")
        if user32.IsIconic(hwnd):
            return _binding(experiment_run_id=experiment_run_id, hwnd=hwnd, title=window_title, process_id=0, left=0, top=0, width=0, height=0, status="window_minimized")
        process_id = ctypes.c_ulong(0)
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
        rect = _RECT()
        if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
            return _binding(experiment_run_id=experiment_run_id, hwnd=hwnd, title=window_title, process_id=int(process_id.value), left=0, top=0, width=0, height=0, status="capture_failed")
        point = _POINT(0, 0)
        if not user32.ClientToScreen(hwnd, ctypes.byref(point)):
            return _binding(experiment_run_id=experiment_run_id, hwnd=hwnd, title=window_title, process_id=int(process_id.value), left=0, top=0, width=0, height=0, status="capture_failed")
        return _binding(
            experiment_run_id=experiment_run_id,
            hwnd=hwnd,
            title=window_title,
            process_id=int(process_id.value),
            left=int(point.x),
            top=int(point.y),
            width=int(rect.right - rect.left),
            height=int(rect.bottom - rect.top),
            status="bound",
        )

    def capture_sample(self, binding: BoundedWindowCaptureBinding) -> AdapterOutputSample:
        if binding.binding_status != "bound":
            raise SensorCaptureError("device_unavailable", f"window binding is not bound: {binding.binding_status}")
        if os.name != "nt":
            raise SensorCaptureError("backend_missing", "Windows HWND capture requires Windows")
        self._validate_geometry(binding)
        started = monotonic_ns()
        data = _capture_bgra8_windows_gdi(
            binding.client_left,
            binding.client_top,
            binding.client_width,
            binding.client_height,
        )
        ended = monotonic_ns()
        self._frame_index += 1
        return AdapterOutputSample(
            sample_id=stable_id("package_123_window_capture_sample"),
            source_kind="screen",
            adapter_id=self.adapter_id,
            adapter_version=self.adapter_version,
            device_descriptor_id=self._descriptor.device_descriptor_id,
            captured_at_utc=utc_now(),
            captured_at_monotonic_ns=ended,
            capture_duration_ns=ended - started,
            raw_level="adapter_output",
            media_type="image/raw",
            storage_format="BGRA8",
            data=data,
            metadata={
                "package_123_source_kind": "windows_window_capture",
                "target_hwnd": binding.target_hwnd,
                "target_window_title": binding.target_window_title,
                "client_rect": {
                    "left": binding.client_left,
                    "top": binding.client_top,
                    "width": binding.client_width,
                    "height": binding.client_height,
                },
                "pixel_format": "BGRA8",
                "actual_width": binding.client_width,
                "actual_height": binding.client_height,
                "row_stride_bytes": binding.client_width * 4,
                "frame_index": self._frame_index,
                "forbidden_screen_metadata_excluded": True,
            },
            real_device_capture=True,
        )

    def build_capture_config(self, *, state_dir: str, binding: BoundedWindowCaptureBinding, duration_ms: int = 12_000) -> SensorCaptureConfig:
        return build_sensor_capture_config(
            source_kind="screen",
            adapter_id=self.adapter_id,
            device_id="screen:windows_hwnd_client_area",
            explicit_state_dir=state_dir,
            source_specific_config={
                "left": binding.client_left,
                "top": binding.client_top,
                "width": binding.client_width,
                "height": binding.client_height,
            },
            capture_duration_ms=duration_ms,
            sample_interval_ms=100,
            maximum_artifact_count=128,
            maximum_total_bytes=536_870_912,
        )

    def descriptor(self) -> SensorDeviceDescriptor:
        return self._descriptor

    def _validate_geometry(self, binding: BoundedWindowCaptureBinding) -> None:
        current = self.bind_by_title(experiment_run_id=binding.experiment_run_id, window_title=binding.target_window_title)
        if current.binding_status != "bound":
            raise SensorCaptureError("device_unavailable", f"window is no longer bound: {current.binding_status}")
        expected = (binding.target_hwnd, binding.client_width, binding.client_height)
        actual = (current.target_hwnd, current.client_width, current.client_height)
        if expected != actual:
            raise SensorCaptureError("invalid_adapter_output", "window geometry changed during Package 123 capture")


def luminance_mean_from_bgra8(data: bytes) -> float:
    if not data:
        return 0.0
    pixels = len(data) // 4
    if pixels <= 0:
        return 0.0
    total = 0.0
    for index in range(0, pixels * 4, 4):
        b = data[index]
        g = data[index + 1]
        r = data[index + 2]
        total += 0.2126 * r + 0.7152 * g + 0.0722 * b
    return total / (pixels * 255.0)


def visual_contrast_distinguishable(sample_a: bytes, sample_b: bytes, *, threshold: float = 0.25) -> bool:
    return abs(luminance_mean_from_bgra8(sample_a) - luminance_mean_from_bgra8(sample_b)) >= threshold


def _binding(
    *,
    experiment_run_id: str,
    hwnd: int,
    title: str,
    process_id: int,
    left: int,
    top: int,
    width: int,
    height: int,
    status: str,
) -> BoundedWindowCaptureBinding:
    return BoundedWindowCaptureBinding(
        binding_id=stable_id("package_123_window_binding"),
        schema_version=WINDOW_BINDING_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_run_id=experiment_run_id,
        target_hwnd=int(hwnd),
        target_window_title=title,
        target_process_id=int(process_id),
        client_left=int(left),
        client_top=int(top),
        client_width=int(width),
        client_height=int(height),
        binding_status=status,
        source_trace_refs=tuple(),
    )
