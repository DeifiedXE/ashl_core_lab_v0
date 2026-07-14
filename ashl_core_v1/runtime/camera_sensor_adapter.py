"""Read-only camera frame adapter for Package 120."""

from __future__ import annotations

import importlib.util
import time

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


class CameraSensorAdapter:
    source_kind = "camera"
    adapter_id = "camera_opencv_bgr8_local_v0"
    adapter_version = "v0"

    def __init__(self) -> None:
        self._config: SensorCaptureConfig | None = None
        self._descriptor: SensorDeviceDescriptor | None = None
        self._capture = None
        self._frame_index = 0

    def enumerate_devices(self) -> tuple[SensorDeviceDescriptor, ...]:
        if importlib.util.find_spec("cv2") is None:
            return (self._missing_descriptor(),)
        import cv2  # type: ignore

        devices: list[SensorDeviceDescriptor] = []
        for index in range(3):
            cap = cv2.VideoCapture(index)
            try:
                available = bool(cap is not None and cap.isOpened())
            finally:
                if cap is not None:
                    cap.release()
            if not available:
                continue
            devices.append(
                SensorDeviceDescriptor(
                    device_descriptor_id=stable_id("sensor_device_descriptor"),
                    schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
                    created_at=utc_now(),
                    source_kind=self.source_kind,
                    adapter_id=self.adapter_id,
                    adapter_version=self.adapter_version,
                    device_id=f"camera:opencv:{index}",
                    device_index=index,
                    device_display_name=f"OpenCV camera {index}",
                    backend_name="opencv",
                    available=True,
                    permission_status="unknown",
                    supported_format_summary=("BGR8",),
                    read_only=True,
                    external_control_allowed=False,
                    real_device_capture=True,
                )
            )
        return tuple(devices) if devices else (self._missing_descriptor("opencv found no available cameras"),)

    def open(self, config: SensorCaptureConfig) -> None:
        if config.source_kind != self.source_kind:
            raise SensorCaptureError("unsupported_format", "camera adapter received non-camera config")
        if "device_index" not in config.source_specific_config:
            raise SensorCaptureError("unsupported_format", "camera capture requires explicit device_index")
        if importlib.util.find_spec("cv2") is None:
            raise SensorCaptureError("backend_missing", "opencv-python is required for camera capture")
        import cv2  # type: ignore

        index = int(config.source_specific_config["device_index"])
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            cap.release()
            raise SensorCaptureError("device_open_failed", f"camera device could not be opened: {index}")
        requested_width = int(config.source_specific_config.get("requested_width", 640))
        requested_height = int(config.source_specific_config.get("requested_height", 480))
        requested_fps = float(config.source_specific_config.get("requested_fps", 1))
        if requested_width:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, requested_width)
        if requested_height:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, requested_height)
        if requested_fps:
            cap.set(cv2.CAP_PROP_FPS, requested_fps)
        self._capture = cap
        self._config = config
        self._descriptor = SensorDeviceDescriptor(
            device_descriptor_id=stable_id("sensor_device_descriptor"),
            schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
            created_at=utc_now(),
            source_kind=self.source_kind,
            adapter_id=self.adapter_id,
            adapter_version=self.adapter_version,
            device_id=f"camera:opencv:{index}",
            device_index=index,
            device_display_name=f"OpenCV camera {index}",
            backend_name="opencv",
            available=True,
            permission_status="unknown",
            supported_format_summary=("BGR8",),
            read_only=True,
            external_control_allowed=False,
            real_device_capture=True,
        )

    def read_sample(self) -> AdapterOutputSample:
        if self._capture is None or self._config is None or self._descriptor is None:
            raise SensorCaptureError("device_open_failed", "camera adapter is not open")
        read_timeout_ms = int(self._config.source_specific_config.get("read_timeout_ms", 1000))
        deadline = time.monotonic() + max(0.1, read_timeout_ms / 1000.0)
        started = monotonic_ns()
        frame = None
        while time.monotonic() <= deadline:
            ok, candidate = self._capture.read()
            if ok and candidate is not None:
                frame = candidate
                break
            time.sleep(0.02)
        if frame is None:
            raise SensorCaptureError("capture_timeout", "camera read timed out")
        ended = monotonic_ns()
        height, width = int(frame.shape[0]), int(frame.shape[1])
        if len(frame.shape) < 3 or int(frame.shape[2]) != 3:
            raise SensorCaptureError("invalid_adapter_output", "camera frame is not BGR8")
        data = bytes(frame.tobytes())
        self._frame_index += 1
        return AdapterOutputSample(
            sample_id=stable_id("camera_sample"),
            source_kind=self.source_kind,
            adapter_id=self.adapter_id,
            adapter_version=self.adapter_version,
            device_descriptor_id=self._descriptor.device_descriptor_id,
            captured_at_utc=utc_now(),
            captured_at_monotonic_ns=ended,
            capture_duration_ns=ended - started,
            raw_level="adapter_output",
            media_type="application/octet-stream",
            storage_format="bgr8",
            data=data,
            metadata={
                "requested_width": int(self._config.source_specific_config.get("requested_width", 640)),
                "requested_height": int(self._config.source_specific_config.get("requested_height", 480)),
                "actual_width": width,
                "actual_height": height,
                "requested_fps": float(self._config.source_specific_config.get("requested_fps", 1)),
                "reported_backend_fps": float(self._capture.get(5)),
                "pixel_format": "BGR8",
                "row_stride_bytes": width * 3,
                "frame_index": self._frame_index,
                "backend_name": "opencv",
                "device_index": self._descriptor.device_index,
                "adapter_transform_notes": ("opencv_backend_delivered_bgr8_array_bytes",),
                "semantic_processing_created": False,
            },
            real_device_capture=True,
        )

    def pause(self) -> None:
        return None

    def resume(self) -> None:
        return None

    def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
        self._capture = None
        self._config = None
        self._descriptor = None

    def _missing_descriptor(self, message: str = "opencv-python backend missing") -> SensorDeviceDescriptor:
        return SensorDeviceDescriptor(
            device_descriptor_id=stable_id("sensor_device_descriptor"),
            schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
            created_at=utc_now(),
            source_kind=self.source_kind,
            adapter_id=self.adapter_id,
            adapter_version=self.adapter_version,
            device_id="camera:missing_backend",
            device_index=None,
            device_display_name=message,
            backend_name="missing",
            available=False,
            permission_status="not_requested",
            supported_format_summary=tuple(),
            read_only=True,
            external_control_allowed=False,
            real_device_capture=False,
        )
