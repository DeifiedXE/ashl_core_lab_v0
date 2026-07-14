"""Read-only screen pixel adapter for Package 120."""

from __future__ import annotations

import ctypes
import importlib.util
import os
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import (
    DEVICE_DESCRIPTOR_SCHEMA_VERSION,
    SensorCaptureConfig,
    SensorCaptureError,
    SensorDeviceDescriptor,
    monotonic_ns,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.sensor_adapter_protocol import AdapterOutputSample


class _BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.c_uint32),
        ("biWidth", ctypes.c_int32),
        ("biHeight", ctypes.c_int32),
        ("biPlanes", ctypes.c_uint16),
        ("biBitCount", ctypes.c_uint16),
        ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32),
        ("biXPelsPerMeter", ctypes.c_int32),
        ("biYPelsPerMeter", ctypes.c_int32),
        ("biClrUsed", ctypes.c_uint32),
        ("biClrImportant", ctypes.c_uint32),
    ]


class _BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", _BITMAPINFOHEADER), ("bmiColors", ctypes.c_uint32 * 3)]


class ScreenSensorAdapter:
    source_kind = "screen"
    adapter_id = "screen_bgra8_local_v0"
    adapter_version = "v0"

    def __init__(self) -> None:
        self._config: SensorCaptureConfig | None = None
        self._descriptor = self._build_descriptor()
        self._frame_index = 0

    def enumerate_devices(self) -> tuple[SensorDeviceDescriptor, ...]:
        return (self._descriptor,)

    def open(self, config: SensorCaptureConfig) -> None:
        if config.source_kind != self.source_kind:
            raise SensorCaptureError("unsupported_format", "screen adapter received non-screen config")
        source_config = dict(config.source_specific_config)
        has_region = all(key in source_config for key in ("left", "top", "width", "height"))
        has_monitor = "monitor_index" in source_config
        if not has_region and not has_monitor:
            raise SensorCaptureError("unsupported_format", "screen capture requires explicit monitor_index or region")
        if not self._descriptor.available:
            raise SensorCaptureError("backend_missing", "no screen capture backend available")
        self._config = config

    def read_sample(self) -> AdapterOutputSample:
        if self._config is None:
            raise SensorCaptureError("device_open_failed", "screen adapter is not open")
        source_config = dict(self._config.source_specific_config)
        left, top, width, height = _capture_rectangle(source_config)
        if width <= 0 or height <= 0:
            raise SensorCaptureError("unsupported_format", "screen capture rectangle must be positive")
        started = monotonic_ns()
        data = _capture_bgra8(left, top, width, height)
        ended = monotonic_ns()
        self._frame_index += 1
        return AdapterOutputSample(
            sample_id=stable_id("screen_sample"),
            source_kind=self.source_kind,
            adapter_id=self.adapter_id,
            adapter_version=self.adapter_version,
            device_descriptor_id=self._descriptor.device_descriptor_id,
            captured_at_utc=utc_now(),
            captured_at_monotonic_ns=ended,
            capture_duration_ns=ended - started,
            raw_level="adapter_output",
            media_type="application/octet-stream",
            storage_format="bgra8",
            data=data,
            metadata={
                "monitor_index": source_config.get("monitor_index"),
                "capture_rectangle": {"left": left, "top": top, "width": width, "height": height},
                "desktop_scale_metadata": None,
                "pixel_format": "BGRA8",
                "row_stride_bytes": width * 4,
                "frame_index": self._frame_index,
                "forbidden_screen_metadata_excluded": True,
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
        available = importlib.util.find_spec("mss") is not None or os.name == "nt"
        backend = "mss" if importlib.util.find_spec("mss") is not None else ("windows_gdi" if os.name == "nt" else "missing")
        return SensorDeviceDescriptor(
            device_descriptor_id=stable_id("sensor_device_descriptor"),
            schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
            created_at=utc_now(),
            source_kind=self.source_kind,
            adapter_id=self.adapter_id,
            adapter_version=self.adapter_version,
            device_id="screen:local-display",
            device_index=0,
            device_display_name="Local display pixels",
            backend_name=backend,
            available=available,
            permission_status="unknown" if available else "not_requested",
            supported_format_summary=("BGRA8",) if available else tuple(),
            read_only=True,
            external_control_allowed=False,
            real_device_capture=available,
        )


def _capture_rectangle(source_config: dict[str, Any]) -> tuple[int, int, int, int]:
    if all(key in source_config for key in ("left", "top", "width", "height")):
        return (
            int(source_config["left"]),
            int(source_config["top"]),
            int(source_config["width"]),
            int(source_config["height"]),
        )
    if "monitor_index" in source_config and os.name == "nt":
        return (
            0,
            0,
            int(ctypes.windll.user32.GetSystemMetrics(0)),
            int(ctypes.windll.user32.GetSystemMetrics(1)),
        )
    raise SensorCaptureError("unsupported_format", "screen capture requires explicit region or monitor")


def _capture_bgra8(left: int, top: int, width: int, height: int) -> bytes:
    if importlib.util.find_spec("mss") is not None:
        import mss  # type: ignore

        with mss.mss() as screen:
            shot = screen.grab({"left": left, "top": top, "width": width, "height": height})
            return bytes(shot.bgra)
    if os.name == "nt":
        return _capture_bgra8_windows_gdi(left, top, width, height)
    raise SensorCaptureError("backend_missing", "no screen capture backend available")


def _capture_bgra8_windows_gdi(left: int, top: int, width: int, height: int) -> bytes:
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    hdesktop = user32.GetDC(0)
    if not hdesktop:
        raise SensorCaptureError("device_unavailable", "GetDC failed")
    memdc = gdi32.CreateCompatibleDC(hdesktop)
    bitmap = gdi32.CreateCompatibleBitmap(hdesktop, width, height)
    old_obj = gdi32.SelectObject(memdc, bitmap)
    try:
        if not gdi32.BitBlt(memdc, 0, 0, width, height, hdesktop, left, top, 0x00CC0020):
            raise SensorCaptureError("capture_timeout", "BitBlt failed")

        info = _BITMAPINFO()
        info.bmiHeader.biSize = ctypes.sizeof(_BITMAPINFOHEADER)
        info.bmiHeader.biWidth = width
        info.bmiHeader.biHeight = -height
        info.bmiHeader.biPlanes = 1
        info.bmiHeader.biBitCount = 32
        info.bmiHeader.biCompression = 0
        buffer = ctypes.create_string_buffer(width * height * 4)
        copied = gdi32.GetDIBits(hdesktop, bitmap, 0, height, buffer, ctypes.byref(info), 0)
        if copied != height:
            raise SensorCaptureError("invalid_adapter_output", "GetDIBits did not return expected rows")
        return bytes(buffer)
    finally:
        gdi32.SelectObject(memdc, old_obj)
        gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(memdc)
        user32.ReleaseDC(0, hdesktop)
