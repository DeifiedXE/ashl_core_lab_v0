"""Read-only microphone PCM adapter for Package 120."""

from __future__ import annotations

import ctypes
import importlib.util
import os
import time
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


class _WAVEINCAPSW(ctypes.Structure):
    _fields_ = [
        ("wMid", ctypes.c_ushort),
        ("wPid", ctypes.c_ushort),
        ("vDriverVersion", ctypes.c_uint),
        ("szPname", ctypes.c_wchar * 32),
        ("dwFormats", ctypes.c_uint),
        ("wChannels", ctypes.c_ushort),
        ("wReserved1", ctypes.c_ushort),
    ]


class _WAVEFORMATEX(ctypes.Structure):
    _fields_ = [
        ("wFormatTag", ctypes.c_ushort),
        ("nChannels", ctypes.c_ushort),
        ("nSamplesPerSec", ctypes.c_uint),
        ("nAvgBytesPerSec", ctypes.c_uint),
        ("nBlockAlign", ctypes.c_ushort),
        ("wBitsPerSample", ctypes.c_ushort),
        ("cbSize", ctypes.c_ushort),
    ]


class _WAVEHDR(ctypes.Structure):
    _fields_ = [
        ("lpData", ctypes.c_void_p),
        ("dwBufferLength", ctypes.c_uint),
        ("dwBytesRecorded", ctypes.c_uint),
        ("dwUser", ctypes.c_void_p),
        ("dwFlags", ctypes.c_uint),
        ("dwLoops", ctypes.c_uint),
        ("lpNext", ctypes.c_void_p),
        ("reserved", ctypes.c_void_p),
    ]


class MicrophoneSensorAdapter:
    source_kind = "microphone"
    adapter_id = "microphone_pcm_s16le_local_v0"
    adapter_version = "v0"

    def __init__(self) -> None:
        self._config: SensorCaptureConfig | None = None
        self._descriptor: SensorDeviceDescriptor | None = None

    def enumerate_devices(self) -> tuple[SensorDeviceDescriptor, ...]:
        if importlib.util.find_spec("sounddevice") is not None:
            return _enumerate_sounddevice(self.adapter_id, self.adapter_version)
        if os.name == "nt":
            return _enumerate_winmm(self.adapter_id, self.adapter_version)
        return (
            _missing_descriptor(
                self.adapter_id,
                self.adapter_version,
                "microphone capture requires sounddevice/PortAudio or Windows winmm",
            ),
        )

    def open(self, config: SensorCaptureConfig) -> None:
        if config.source_kind != self.source_kind:
            raise SensorCaptureError("unsupported_format", "microphone adapter received non-microphone config")
        if "input_device_index" not in config.source_specific_config:
            raise SensorCaptureError("unsupported_format", "microphone capture requires explicit input_device_index")
        descriptors = [item for item in self.enumerate_devices() if item.available]
        if not descriptors:
            raise SensorCaptureError("backend_missing", "no microphone backend or input device available")
        requested = int(config.source_specific_config["input_device_index"])
        descriptor = next((item for item in descriptors if item.device_index == requested), None)
        if descriptor is None:
            raise SensorCaptureError("device_unavailable", f"microphone device unavailable: {requested}")
        self._config = config
        self._descriptor = descriptor

    def read_sample(self) -> AdapterOutputSample:
        if self._config is None or self._descriptor is None:
            raise SensorCaptureError("device_open_failed", "microphone adapter is not open")
        config = dict(self._config.source_specific_config)
        sample_rate = int(config.get("requested_sample_rate", 16000))
        channels = int(config.get("requested_channels", 1))
        sample_format = str(config.get("requested_sample_format", "int16"))
        duration_ms = int(config.get("capture_duration_ms", self._config.capture_duration_ms))
        chunk_duration_ms = int(config.get("chunk_duration_ms", 100))
        if sample_format not in {"int16", "pcm_s16le"}:
            raise SensorCaptureError("unsupported_format", "Package 120 microphone v0 supports int16 PCM only")
        started = monotonic_ns()
        if importlib.util.find_spec("sounddevice") is not None:
            data, overflow = _capture_sounddevice(self._descriptor.device_index or 0, sample_rate, channels, duration_ms)
            backend_name = "sounddevice"
        elif os.name == "nt":
            data, overflow = _capture_winmm(self._descriptor.device_index or 0, sample_rate, channels, duration_ms)
            backend_name = "winmm"
        else:
            raise SensorCaptureError("backend_missing", "no microphone backend available")
        ended = monotonic_ns()
        frame_count = len(data) // max(1, channels * 2)
        return AdapterOutputSample(
            sample_id=stable_id("microphone_sample"),
            source_kind=self.source_kind,
            adapter_id=self.adapter_id,
            adapter_version=self.adapter_version,
            device_descriptor_id=self._descriptor.device_descriptor_id,
            captured_at_utc=utc_now(),
            captured_at_monotonic_ns=ended,
            capture_duration_ns=ended - started,
            raw_level="adapter_output",
            media_type="audio/pcm",
            storage_format="pcm_s16le",
            data=data,
            metadata={
                "requested_sample_rate": sample_rate,
                "actual_sample_rate": sample_rate,
                "audio_channels": channels,
                "audio_sample_format": "int16",
                "audio_frame_count": frame_count,
                "chunk_duration_ms": chunk_duration_ms,
                "backend_name": backend_name,
                "device_name": self._descriptor.device_display_name,
                "overflow_status": overflow,
                "speech_to_text_created": False,
            },
            real_device_capture=True,
        )

    def pause(self) -> None:
        return None

    def resume(self) -> None:
        return None

    def close(self) -> None:
        self._config = None
        self._descriptor = None


def _missing_descriptor(adapter_id: str, adapter_version: str, message: str) -> SensorDeviceDescriptor:
    return SensorDeviceDescriptor(
        device_descriptor_id=stable_id("sensor_device_descriptor"),
        schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
        created_at=utc_now(),
        source_kind="microphone",
        adapter_id=adapter_id,
        adapter_version=adapter_version,
        device_id="microphone:missing_backend",
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


def _enumerate_sounddevice(adapter_id: str, adapter_version: str) -> tuple[SensorDeviceDescriptor, ...]:
    import sounddevice as sd  # type: ignore

    devices = []
    for index, device in enumerate(sd.query_devices()):
        if int(device.get("max_input_channels", 0)) <= 0:
            continue
        devices.append(
            SensorDeviceDescriptor(
                device_descriptor_id=stable_id("sensor_device_descriptor"),
                schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
                created_at=utc_now(),
                source_kind="microphone",
                adapter_id=adapter_id,
                adapter_version=adapter_version,
                device_id=f"microphone:sounddevice:{index}",
                device_index=index,
                device_display_name=str(device.get("name", f"input {index}")),
                backend_name="sounddevice",
                available=True,
                permission_status="unknown",
                supported_format_summary=("pcm_s16le",),
                read_only=True,
                external_control_allowed=False,
                real_device_capture=True,
            )
        )
    if not devices:
        return (_missing_descriptor(adapter_id, adapter_version, "sounddevice found no input devices"),)
    return tuple(devices)


def _capture_sounddevice(device_index: int, sample_rate: int, channels: int, duration_ms: int) -> tuple[bytes, bool]:
    import sounddevice as sd  # type: ignore

    frames = max(1, int(sample_rate * duration_ms / 1000))
    recording = sd.rec(frames, samplerate=sample_rate, channels=channels, dtype="int16", device=device_index)
    sd.wait()
    return bytes(recording.tobytes()), False


def _enumerate_winmm(adapter_id: str, adapter_version: str) -> tuple[SensorDeviceDescriptor, ...]:
    winmm = ctypes.windll.winmm
    count = int(winmm.waveInGetNumDevs())
    devices = []

    for index in range(count):
        caps = _WAVEINCAPSW()
        result = winmm.waveInGetDevCapsW(index, ctypes.byref(caps), ctypes.sizeof(caps))
        if result != 0:
            continue
        devices.append(
            SensorDeviceDescriptor(
                device_descriptor_id=stable_id("sensor_device_descriptor"),
                schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
                created_at=utc_now(),
                source_kind="microphone",
                adapter_id=adapter_id,
                adapter_version=adapter_version,
                device_id=f"microphone:winmm:{index}",
                device_index=index,
                device_display_name=str(caps.szPname),
                backend_name="winmm",
                available=True,
                permission_status="unknown",
                supported_format_summary=("pcm_s16le",),
                read_only=True,
                external_control_allowed=False,
                real_device_capture=True,
            )
        )
    if not devices:
        return (_missing_descriptor(adapter_id, adapter_version, "winmm found no input devices"),)
    return tuple(devices)


def _capture_winmm(device_index: int, sample_rate: int, channels: int, duration_ms: int) -> tuple[bytes, bool]:
    winmm = ctypes.windll.winmm
    WAVE_FORMAT_PCM = 1
    CALLBACK_NULL = 0

    bytes_per_sample = 2
    frame_count = max(1, int(sample_rate * duration_ms / 1000))
    buffer_length = frame_count * channels * bytes_per_sample
    fmt = _WAVEFORMATEX(
        WAVE_FORMAT_PCM,
        channels,
        sample_rate,
        sample_rate * channels * bytes_per_sample,
        channels * bytes_per_sample,
        16,
        0,
    )
    handle = ctypes.c_void_p()
    result = winmm.waveInOpen(ctypes.byref(handle), device_index, ctypes.byref(fmt), 0, 0, CALLBACK_NULL)
    if result != 0:
        raise SensorCaptureError("device_open_failed", f"waveInOpen failed: {result}")
    buffer = ctypes.create_string_buffer(buffer_length)
    header = _WAVEHDR(ctypes.cast(buffer, ctypes.c_void_p), buffer_length, 0, None, 0, 0, None, None)
    try:
        for fn, message in (
            (winmm.waveInPrepareHeader, "waveInPrepareHeader"),
            (winmm.waveInAddBuffer, "waveInAddBuffer"),
            (winmm.waveInStart, "waveInStart"),
        ):
            result = fn(handle, ctypes.byref(header), ctypes.sizeof(header))
            if result != 0:
                raise SensorCaptureError("device_open_failed", f"{message} failed: {result}")
        time.sleep(max(0.01, duration_ms / 1000.0))
        winmm.waveInStop(handle)
        winmm.waveInReset(handle)
        recorded = int(header.dwBytesRecorded)
        if recorded <= 0:
            raise SensorCaptureError("capture_timeout", "microphone captured no PCM frames")
        return bytes(buffer.raw[:recorded]), False
    finally:
        try:
            winmm.waveInUnprepareHeader(handle, ctypes.byref(header), ctypes.sizeof(header))
        finally:
            winmm.waveInClose(handle)
