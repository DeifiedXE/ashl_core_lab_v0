"""Sensor adapter protocol for bounded real host sensor ingress."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Protocol, runtime_checkable

from ashl_core_v1.runtime.host_sensor_types import SensorCaptureConfig, SensorDeviceDescriptor, plain


@dataclass(frozen=True)
class AdapterOutputSample:
    sample_id: str
    source_kind: str
    adapter_id: str
    adapter_version: str
    device_descriptor_id: str
    captured_at_utc: str
    captured_at_monotonic_ns: int
    capture_duration_ns: int | None
    raw_level: str
    media_type: str
    storage_format: str
    data: bytes
    metadata: dict[str, Any]
    real_device_capture: bool

    def to_dict(self) -> dict[str, object]:
        payload = {field.name: plain(getattr(self, field.name)) for field in fields(self)}
        payload.pop("data", None)
        payload["byte_length"] = len(self.data)
        return payload


@runtime_checkable
class SensorAdapter(Protocol):
    source_kind: str
    adapter_id: str
    adapter_version: str

    def enumerate_devices(self) -> tuple[SensorDeviceDescriptor, ...]:
        ...

    def open(self, config: SensorCaptureConfig) -> None:
        ...

    def read_sample(self) -> AdapterOutputSample:
        ...

    def pause(self) -> None:
        ...

    def resume(self) -> None:
        ...

    def close(self) -> None:
        ...
