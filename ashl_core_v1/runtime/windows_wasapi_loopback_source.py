"""Bounded Windows WASAPI loopback source for Package 123."""

from __future__ import annotations

import ctypes
import math
import os
import struct
import time
import wave
from collections.abc import Callable
from io import BytesIO
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import (
    DEVICE_DESCRIPTOR_SCHEMA_VERSION,
    SensorCaptureConfig,
    SensorCaptureError,
    SensorDeviceDescriptor,
    build_sensor_capture_config,
    monotonic_ns,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.package_123_types import (
    LOOPBACK_CHUNK_DURATION_MS,
    LOOPBACK_DESCRIPTOR_SCHEMA_VERSION,
    MAX_CAPTURE_DURATION_MS,
    SystemAudioLoopbackSourceDescriptor,
)
from ashl_core_v1.runtime.sensor_adapter_protocol import AdapterOutputSample


LOOPBACK_ADAPTER_ID = "windows_wasapi_loopback_pcm_s16le_v0"
LOOPBACK_ADAPTER_VERSION = "v0"
DEFAULT_ENDPOINT_ID = "default"
DEFAULT_SAMPLE_RATE = 48_000
DEFAULT_CHANNELS = 2
AUDCLNT_STREAMFLAGS_LOOPBACK = 0x00020000
AUDCLNT_SHAREMODE_SHARED = 0
AUDCLNT_BUFFERFLAGS_SILENT = 0x00000002
CLSCTX_ALL = 23


class WindowsWasapiLoopbackSource:
    source_kind = "microphone"
    adapter_id = LOOPBACK_ADAPTER_ID
    adapter_version = LOOPBACK_ADAPTER_VERSION

    def __init__(self, *, endpoint_id: str = DEFAULT_ENDPOINT_ID) -> None:
        self.endpoint_id = endpoint_id
        self._endpoint_format = _probe_default_endpoint_format() if os.name == "nt" and endpoint_id == DEFAULT_ENDPOINT_ID else None
        self._descriptor = self.build_sensor_descriptor()
        self._source_descriptor = self.build_source_descriptor()

    def enumerate_sources(self) -> tuple[SystemAudioLoopbackSourceDescriptor, ...]:
        return (self._source_descriptor,)

    def build_source_descriptor(self) -> SystemAudioLoopbackSourceDescriptor:
        if self.endpoint_id != DEFAULT_ENDPOINT_ID:
            return SystemAudioLoopbackSourceDescriptor(
                source_descriptor_id=stable_id("package_123_loopback_descriptor"),
                schema_version=LOOPBACK_DESCRIPTOR_SCHEMA_VERSION,
                created_at=utc_now(),
                endpoint_id=self.endpoint_id,
                endpoint_name=self.endpoint_id,
                sample_rate_hz=0,
                channel_count=0,
                sample_format="unavailable",
                chunk_duration_ms=LOOPBACK_CHUNK_DURATION_MS,
                loopback_scope="selected_render_endpoint",
                bounded_capture_maximum_ms=MAX_CAPTURE_DURATION_MS,
                enabled_for_daily_runtime=False,
                available=False,
                failure_reason="non_default_render_endpoint_not_supported_in_v0",
            )
        if self._endpoint_format is None:
            return SystemAudioLoopbackSourceDescriptor(
                source_descriptor_id=stable_id("package_123_loopback_descriptor"),
                schema_version=LOOPBACK_DESCRIPTOR_SCHEMA_VERSION,
                created_at=utc_now(),
                endpoint_id=DEFAULT_ENDPOINT_ID,
                endpoint_name="Windows default render endpoint",
                sample_rate_hz=0,
                channel_count=0,
                sample_format="unavailable",
                chunk_duration_ms=LOOPBACK_CHUNK_DURATION_MS,
                loopback_scope="selected_render_endpoint",
                bounded_capture_maximum_ms=MAX_CAPTURE_DURATION_MS,
                enabled_for_daily_runtime=False,
                available=False,
                failure_reason="wasapi_default_render_endpoint_unavailable",
            )
        return SystemAudioLoopbackSourceDescriptor(
            source_descriptor_id=stable_id("package_123_loopback_descriptor"),
            schema_version=LOOPBACK_DESCRIPTOR_SCHEMA_VERSION,
            created_at=utc_now(),
            endpoint_id=DEFAULT_ENDPOINT_ID,
            endpoint_name=str(self._endpoint_format.get("endpoint_id") or "Windows default render endpoint"),
            sample_rate_hz=int(self._endpoint_format["sample_rate"]),
            channel_count=min(int(self._endpoint_format["channels"]), 2),
            sample_format="PCM_S16LE",
            chunk_duration_ms=LOOPBACK_CHUNK_DURATION_MS,
            loopback_scope="selected_render_endpoint",
            bounded_capture_maximum_ms=MAX_CAPTURE_DURATION_MS,
            enabled_for_daily_runtime=False,
            available=True,
        )

    def build_sensor_descriptor(self) -> SensorDeviceDescriptor:
        available = self._endpoint_format is not None and self.endpoint_id == DEFAULT_ENDPOINT_ID
        return SensorDeviceDescriptor(
            device_descriptor_id=stable_id("sensor_device_descriptor"),
            schema_version=DEVICE_DESCRIPTOR_SCHEMA_VERSION,
            created_at=utc_now(),
            source_kind="microphone",
            adapter_id=self.adapter_id,
            adapter_version=self.adapter_version,
            device_id=f"system_audio_loopback:{self.endpoint_id}",
            device_index=-1,
            device_display_name="Windows default render endpoint loopback",
            backend_name="windows_wasapi_loopback" if os.name == "nt" else "missing",
            available=available,
            permission_status="unknown" if available else "not_applicable",
            supported_format_summary=("PCM_S16LE",) if available else tuple(),
            read_only=True,
            external_control_allowed=False,
            real_device_capture=available,
        )

    def build_capture_config(self, *, state_dir: str, duration_ms: int = MAX_CAPTURE_DURATION_MS) -> SensorCaptureConfig:
        sample_rate = int(self._source_descriptor.sample_rate_hz or DEFAULT_SAMPLE_RATE)
        channels = int(self._source_descriptor.channel_count or DEFAULT_CHANNELS)
        return build_sensor_capture_config(
            source_kind="microphone",
            adapter_id=self.adapter_id,
            device_id=f"system_audio_loopback:{self.endpoint_id}",
            explicit_state_dir=state_dir,
            source_specific_config={
                "input_device_index": -1,
                "requested_sample_rate": sample_rate,
                "requested_channels": channels,
                "requested_sample_format": "int16",
                "chunk_duration_ms": LOOPBACK_CHUNK_DURATION_MS,
                "capture_duration_ms": int(duration_ms),
            },
            capture_duration_ms=int(duration_ms),
            sample_interval_ms=LOOPBACK_CHUNK_DURATION_MS,
            maximum_artifact_count=256,
            maximum_total_bytes=268_435_456,
        )

    def descriptor(self) -> SensorDeviceDescriptor:
        return self._descriptor

    def source_descriptor(self) -> SystemAudioLoopbackSourceDescriptor:
        return self._source_descriptor

    def capture_samples(self, *, duration_ms: int, chunk_duration_ms: int = LOOPBACK_CHUNK_DURATION_MS) -> tuple[AdapterOutputSample, ...]:
        if duration_ms <= 0 or duration_ms > MAX_CAPTURE_DURATION_MS:
            raise SensorCaptureError("unsupported_format", "Package 123 loopback duration exceeds bounds")
        if not self._source_descriptor.available:
            raise SensorCaptureError("backend_missing", self._source_descriptor.failure_reason or "WASAPI loopback unavailable")
        base_time = monotonic_ns()
        pcm, actual = _capture_wasapi_loopback_pcm_s16le(duration_ms=duration_ms)
        sample_rate = int(actual["sample_rate"])
        channels = int(actual["channels"])
        bytes_per_frame = 2 * channels
        frames_per_chunk = max(1, int(sample_rate * chunk_duration_ms / 1000))
        bytes_per_chunk = frames_per_chunk * bytes_per_frame
        samples: list[AdapterOutputSample] = []
        for index, start in enumerate(range(0, len(pcm), bytes_per_chunk)):
            chunk = pcm[start : start + bytes_per_chunk]
            if len(chunk) < bytes_per_chunk:
                continue
            frame_count = len(chunk) // bytes_per_frame
            samples.append(
                self._build_sample(
                    chunk=chunk,
                    actual=actual,
                    captured_at_monotonic_ns=base_time + int(index * chunk_duration_ms * 1_000_000),
                    chunk_duration_ms=chunk_duration_ms,
                )
            )
        return tuple(samples)

    def capture_samples_until_deadline(
        self,
        *,
        deadline_ns_getter: Callable[[], int],
        on_sample: Callable[[AdapterOutputSample], None] | None = None,
        chunk_duration_ms: int = LOOPBACK_CHUNK_DURATION_MS,
    ) -> tuple[AdapterOutputSample, ...]:
        """Capture through a shared mutable deadline without reopening WASAPI."""

        if not self._source_descriptor.available:
            raise SensorCaptureError(
                "backend_missing",
                self._source_descriptor.failure_reason or "WASAPI loopback unavailable",
            )
        started_ns = monotonic_ns()
        initial_deadline_ns = int(deadline_ns_getter())
        if initial_deadline_ns <= started_ns:
            raise SensorCaptureError("unsupported_format", "shared deadline must be in the future")
        if initial_deadline_ns - started_ns > MAX_CAPTURE_DURATION_MS * 1_000_000:
            raise SensorCaptureError("unsupported_format", "shared deadline exceeds Package 123 bounds")
        samples: list[AdapterOutputSample] = []

        def emit(pcm: bytes, actual: dict[str, object], captured_at_monotonic_ns: int) -> None:
            sample = self._build_sample(
                chunk=pcm,
                actual=actual,
                captured_at_monotonic_ns=captured_at_monotonic_ns,
                chunk_duration_ms=chunk_duration_ms,
            )
            samples.append(sample)
            if on_sample is not None:
                on_sample(sample)

        _capture_wasapi_loopback_pcm_s16le(
            duration_ms=None,
            deadline_ns_getter=deadline_ns_getter,
            pcm_chunk_callback=emit,
            chunk_duration_ms=chunk_duration_ms,
        )
        return tuple(samples)

    def _build_sample(
        self,
        *,
        chunk: bytes,
        actual: dict[str, object],
        captured_at_monotonic_ns: int,
        chunk_duration_ms: int,
    ) -> AdapterOutputSample:
        sample_rate = int(actual["sample_rate"])
        channels = int(actual["channels"])
        frame_count = len(chunk) // (2 * channels)
        return AdapterOutputSample(
            sample_id=stable_id("package_123_loopback_sample"),
            source_kind="microphone",
            adapter_id=self.adapter_id,
            adapter_version=self.adapter_version,
            device_descriptor_id=self._descriptor.device_descriptor_id,
            captured_at_utc=utc_now(),
            captured_at_monotonic_ns=int(captured_at_monotonic_ns),
            capture_duration_ns=int(frame_count / sample_rate * 1_000_000_000),
            raw_level="adapter_output",
            media_type="audio/pcm",
            storage_format="PCM_S16LE",
            data=chunk,
            metadata={
                "package_123_audio_lane": "system_audio_loopback",
                "capture_mode": "grounding_capture",
                "retention_classification": "bounded_package_123_experiment_evidence",
                "loopback_scope": "selected_render_endpoint",
                "endpoint_id": self.endpoint_id,
                "endpoint_name": self._source_descriptor.endpoint_name,
                "actual_sample_rate": sample_rate,
                "audio_channels": channels,
                "audio_sample_format": "int16",
                "audio_frame_count": frame_count,
                "chunk_duration_ms": chunk_duration_ms,
                "backend_name": "windows_wasapi_loopback",
                "original_format": actual.get("original_format"),
                "output_format": "PCM_S16LE",
                "channel_mapping": actual.get("channel_mapping"),
                "resampling_performed": False,
                "silence_fill_performed": bool(actual.get("silence_fill_performed")),
                "inserted_silence_frame_count": int(actual.get("inserted_silence_frame_count") or 0),
                "conversion_implementation": "ashl_core_v1.runtime.windows_wasapi_loopback_source",
                "speech_recognition_created": False,
                "speaker_recognition_created": False,
                "semantic_audio_model_used": False,
            },
            real_device_capture=True,
        )


def list_loopback_sources() -> tuple[SystemAudioLoopbackSourceDescriptor, ...]:
    return WindowsWasapiLoopbackSource(endpoint_id=DEFAULT_ENDPOINT_ID).enumerate_sources()


def pcm_s16le_rms_ratio(data: bytes) -> float:
    if len(data) < 2:
        return 0.0
    count = len(data) // 2
    total = 0.0
    for (sample,) in struct.iter_unpack("<h", data[: count * 2]):
        total += float(sample) * float(sample)
    return math.sqrt(total / count) / 32768.0


def generate_sine_wave_wav_bytes(
    *,
    frequency_hz: int = 900,
    duration_ms: int = 350,
    sample_rate: int = 48_000,
    channels: int = 2,
    amplitude: float = 0.20,
) -> bytes:
    frames = int(sample_rate * duration_ms / 1000)
    pcm = bytearray()
    for index in range(frames):
        value = int(max(-1.0, min(1.0, math.sin(2 * math.pi * frequency_hz * index / sample_rate) * amplitude)) * 32767)
        for _ in range(channels):
            pcm.extend(struct.pack("<h", value))
    output = BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(bytes(pcm))
    return output.getvalue()


def play_default_endpoint_sine_tone(*, duration_ms: int = 350) -> None:
    if os.name != "nt":
        return
    import winsound

    tone = generate_sine_wave_wav_bytes(duration_ms=duration_ms)
    winsound.PlaySound(tone, winsound.SND_MEMORY)


class _GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_ulong),
        ("Data2", ctypes.c_ushort),
        ("Data3", ctypes.c_ushort),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    def __init__(self, guid: str) -> None:
        import uuid

        value = uuid.UUID(guid)
        data = value.bytes_le
        super().__init__(
            int.from_bytes(data[0:4], "little"),
            int.from_bytes(data[4:6], "little"),
            int.from_bytes(data[6:8], "little"),
            (ctypes.c_ubyte * 8).from_buffer_copy(data[8:16]),
        )


class _WAVEFORMATEX(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("wFormatTag", ctypes.c_ushort),
        ("nChannels", ctypes.c_ushort),
        ("nSamplesPerSec", ctypes.c_ulong),
        ("nAvgBytesPerSec", ctypes.c_ulong),
        ("nBlockAlign", ctypes.c_ushort),
        ("wBitsPerSample", ctypes.c_ushort),
        ("cbSize", ctypes.c_ushort),
    ]


def _probe_default_endpoint_format() -> dict[str, object] | None:
    if os.name != "nt":
        return None
    try:
        handles = _open_default_audio_client()
        audio_client = handles["audio_client"]
        fmt_ptr = ctypes.c_void_p()
        _call(audio_client, 8, ctypes.c_long, [ctypes.POINTER(ctypes.c_void_p)])(audio_client, ctypes.byref(fmt_ptr))
        fmt = _format_from_waveformatex_pointer(fmt_ptr)
        fmt["endpoint_id"] = handles.get("endpoint_id") or DEFAULT_ENDPOINT_ID
        ctypes.oledll.ole32.CoTaskMemFree(fmt_ptr)
        _release_handles(handles)
        return fmt
    except Exception:
        try:
            if "handles" in locals():
                _release_handles(handles)
        except Exception:
            pass
        return None


def _capture_wasapi_loopback_pcm_s16le(
    *,
    duration_ms: int | None,
    deadline_ns_getter: Callable[[], int] | None = None,
    pcm_chunk_callback: Callable[[bytes, dict[str, object], int], None] | None = None,
    chunk_duration_ms: int = LOOPBACK_CHUNK_DURATION_MS,
) -> tuple[bytes, dict[str, object]]:
    if duration_ms is None and deadline_ns_getter is None:
        raise ValueError("duration_ms or deadline_ns_getter is required")
    handles: dict[str, Any] = {}
    fmt_ptr = ctypes.c_void_p()
    try:
        handles = _open_default_audio_client()
        audio_client = handles["audio_client"]
        hr = _call(audio_client, 8, ctypes.c_long, [ctypes.POINTER(ctypes.c_void_p)])(audio_client, ctypes.byref(fmt_ptr))
        _check_hr(hr, "IAudioClient.GetMixFormat")
        fmt = _format_from_waveformatex_pointer(fmt_ptr)
        hns_duration = int(max(1000, duration_ms or MAX_CAPTURE_DURATION_MS) * 10_000)
        hr = _call(
            audio_client,
            3,
            ctypes.c_long,
            [ctypes.c_int, ctypes.c_ulong, ctypes.c_longlong, ctypes.c_longlong, ctypes.c_void_p, ctypes.c_void_p],
        )(audio_client, AUDCLNT_SHAREMODE_SHARED, AUDCLNT_STREAMFLAGS_LOOPBACK, hns_duration, 0, fmt_ptr, None)
        _check_hr(hr, "IAudioClient.Initialize")
        capture_client = ctypes.c_void_p()
        iid_capture = _GUID("C8ADBD64-E71E-48A0-A4DE-185C395CD317")
        hr = _call(audio_client, 14, ctypes.c_long, [ctypes.POINTER(_GUID), ctypes.POINTER(ctypes.c_void_p)])(
            audio_client,
            ctypes.byref(iid_capture),
            ctypes.byref(capture_client),
        )
        _check_hr(hr, "IAudioClient.GetService(IAudioCaptureClient)")
        handles["capture_client"] = capture_client
        hr = _call(audio_client, 10, ctypes.c_long, [])(audio_client)
        _check_hr(hr, "IAudioClient.Start")
        started_ns = monotonic_ns()
        fixed_deadline_ns = (
            started_ns + int(duration_ms) * 1_000_000 if duration_ms is not None else None
        )
        raw = bytearray()
        packet = ctypes.c_uint32(0)
        sample_rate = int(fmt["sample_rate"])
        block_align = int(fmt["block_align"])
        inserted_silence_frames = 0
        emitted_frames = 0
        frames_per_chunk = max(1, int(sample_rate * int(chunk_duration_ms) / 1000))

        def current_deadline_ns() -> int:
            deadline = (
                int(deadline_ns_getter())
                if deadline_ns_getter is not None
                else int(fixed_deadline_ns or started_ns)
            )
            if deadline - started_ns > MAX_CAPTURE_DURATION_MS * 1_000_000:
                raise SensorCaptureError(
                    "unsupported_format",
                    "shared deadline exceeds Package 123 bounded maximum",
                )
            return deadline

        def expected_frames_at_deadline() -> int:
            return max(
                0,
                int((current_deadline_ns() - started_ns) * sample_rate / 1_000_000_000),
            )

        def pad_to_elapsed(pending_frames: int = 0) -> None:
            nonlocal inserted_silence_frames
            if sample_rate <= 0 or block_align <= 0:
                return
            elapsed_ns = max(0, min(monotonic_ns(), current_deadline_ns()) - started_ns)
            elapsed_frames = int(elapsed_ns * sample_rate / 1_000_000_000)
            current_frames = len(raw) // block_align
            missing_frames = elapsed_frames - current_frames - int(pending_frames)
            if missing_frames > 0:
                raw.extend(b"\x00" * missing_frames * block_align)
                inserted_silence_frames += missing_frames

        def emit_ready_chunks() -> None:
            nonlocal emitted_frames
            if pcm_chunk_callback is None:
                return
            available_frames = len(raw) // block_align
            while available_frames - emitted_frames >= frames_per_chunk:
                start = emitted_frames * block_align
                end = start + frames_per_chunk * block_align
                pcm_chunk, converted_chunk = _convert_to_pcm_s16le(bytes(raw[start:end]), fmt)
                converted_chunk["silence_fill_performed"] = inserted_silence_frames > 0
                converted_chunk["inserted_silence_frame_count"] = inserted_silence_frames
                pcm_chunk_callback(
                    pcm_chunk,
                    converted_chunk,
                    started_ns + int(emitted_frames * 1_000_000_000 / sample_rate),
                )
                emitted_frames += frames_per_chunk

        while monotonic_ns() < current_deadline_ns():
            hr = _call(capture_client, 5, ctypes.c_long, [ctypes.POINTER(ctypes.c_uint32)])(capture_client, ctypes.byref(packet))
            _check_hr(hr, "IAudioCaptureClient.GetNextPacketSize")
            if packet.value == 0:
                time.sleep(0.01)
                pad_to_elapsed()
                emit_ready_chunks()
                continue
            while packet.value:
                data_ptr = ctypes.POINTER(ctypes.c_ubyte)()
                frame_count = ctypes.c_uint32(0)
                flags = ctypes.c_uint32(0)
                device_position = ctypes.c_uint64(0)
                qpc_position = ctypes.c_uint64(0)
                hr = _call(
                    capture_client,
                    3,
                    ctypes.c_long,
                    [
                        ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)),
                        ctypes.POINTER(ctypes.c_uint32),
                        ctypes.POINTER(ctypes.c_uint32),
                        ctypes.POINTER(ctypes.c_uint64),
                        ctypes.POINTER(ctypes.c_uint64),
                    ],
                )(
                    capture_client,
                    ctypes.byref(data_ptr),
                    ctypes.byref(frame_count),
                    ctypes.byref(flags),
                    ctypes.byref(device_position),
                    ctypes.byref(qpc_position),
                )
                _check_hr(hr, "IAudioCaptureClient.GetBuffer")
                pad_to_elapsed(int(frame_count.value))
                byte_count = int(frame_count.value) * int(fmt["block_align"])
                if flags.value & AUDCLNT_BUFFERFLAGS_SILENT:
                    raw.extend(b"\x00" * byte_count)
                else:
                    raw.extend(ctypes.string_at(data_ptr, byte_count))
                emit_ready_chunks()
                hr = _call(capture_client, 4, ctypes.c_long, [ctypes.c_uint32])(capture_client, frame_count.value)
                _check_hr(hr, "IAudioCaptureClient.ReleaseBuffer")
                hr = _call(capture_client, 5, ctypes.c_long, [ctypes.POINTER(ctypes.c_uint32)])(capture_client, ctypes.byref(packet))
                _check_hr(hr, "IAudioCaptureClient.GetNextPacketSize")
        _call(audio_client, 11, ctypes.c_long, [])(audio_client)
        if block_align > 0:
            expected_frames = expected_frames_at_deadline()
            current_frames = len(raw) // block_align
            if current_frames < expected_frames:
                missing_frames = expected_frames - current_frames
                raw.extend(b"\x00" * missing_frames * block_align)
                inserted_silence_frames += missing_frames
            raw = raw[: expected_frames * block_align]
            emit_ready_chunks()
        pcm, converted = _convert_to_pcm_s16le(bytes(raw), fmt)
        converted["silence_fill_performed"] = inserted_silence_frames > 0
        converted["inserted_silence_frame_count"] = inserted_silence_frames
        return pcm, converted
    finally:
        if fmt_ptr:
            try:
                ctypes.oledll.ole32.CoTaskMemFree(fmt_ptr)
            except Exception:
                pass
        _release_handles(handles)


def _open_default_audio_client() -> dict[str, Any]:
    ole32 = ctypes.oledll.ole32
    ole32.CoInitializeEx(None, 0)
    clsid = _GUID("BCDE0395-E52F-467C-8E3D-C4579291692E")
    iid_enum = _GUID("A95664D2-9614-4F35-A746-DE8DB63617E6")
    enumerator = ctypes.c_void_p()
    hr = ole32.CoCreateInstance(ctypes.byref(clsid), None, CLSCTX_ALL, ctypes.byref(iid_enum), ctypes.byref(enumerator))
    _check_hr(hr, "CoCreateInstance(MMDeviceEnumerator)")
    device = ctypes.c_void_p()
    hr = _call(enumerator, 4, ctypes.c_long, [ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)])(
        enumerator,
        0,
        0,
        ctypes.byref(device),
    )
    _check_hr(hr, "IMMDeviceEnumerator.GetDefaultAudioEndpoint")
    endpoint_id = _device_id(device)
    iid_audio_client = _GUID("1CB9AD4C-DBFA-4C32-B178-C2F568A703B2")
    audio_client = ctypes.c_void_p()
    hr = _call(device, 3, ctypes.c_long, [ctypes.POINTER(_GUID), ctypes.c_ulong, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)])(
        device,
        ctypes.byref(iid_audio_client),
        CLSCTX_ALL,
        None,
        ctypes.byref(audio_client),
    )
    _check_hr(hr, "IMMDevice.Activate(IAudioClient)")
    return {"enumerator": enumerator, "device": device, "audio_client": audio_client, "endpoint_id": endpoint_id}


def _device_id(device: ctypes.c_void_p) -> str:
    try:
        endpoint = ctypes.c_wchar_p()
        hr = _call(device, 5, ctypes.c_long, [ctypes.POINTER(ctypes.c_wchar_p)])(device, ctypes.byref(endpoint))
        _check_hr(hr, "IMMDevice.GetId")
        value = endpoint.value or DEFAULT_ENDPOINT_ID
        ctypes.oledll.ole32.CoTaskMemFree(endpoint)
        return value
    except Exception:
        return DEFAULT_ENDPOINT_ID


def _format_from_waveformatex_pointer(ptr: ctypes.c_void_p) -> dict[str, object]:
    fmt = ctypes.cast(ptr, ctypes.POINTER(_WAVEFORMATEX)).contents
    sample_format = "unknown"
    if fmt.wFormatTag == 1:
        sample_format = f"pcm_{int(fmt.wBitsPerSample)}"
    elif fmt.wFormatTag == 3:
        sample_format = "float32"
    elif fmt.wFormatTag == 0xFFFE and fmt.cbSize >= 22:
        raw = ctypes.string_at(int(ptr.value) + ctypes.sizeof(_WAVEFORMATEX), int(fmt.cbSize))
        subformat_first = int.from_bytes(raw[6:10], "little") if len(raw) >= 10 else 0
        sample_format = "float32" if subformat_first == 3 else f"pcm_{int(fmt.wBitsPerSample)}"
    return {
        "sample_rate": int(fmt.nSamplesPerSec),
        "channels": int(fmt.nChannels),
        "bits_per_sample": int(fmt.wBitsPerSample),
        "block_align": int(fmt.nBlockAlign),
        "format_tag": int(fmt.wFormatTag),
        "sample_format": sample_format,
    }


def _convert_to_pcm_s16le(raw: bytes, fmt: dict[str, object]) -> tuple[bytes, dict[str, object]]:
    source_channels = int(fmt["channels"])
    output_channels = source_channels if source_channels in {1, 2} else 1
    sample_format = str(fmt["sample_format"])
    bits = int(fmt["bits_per_sample"])
    block_align = int(fmt["block_align"])
    frame_count = len(raw) // block_align if block_align else 0
    output = bytearray()
    for frame_index in range(frame_count):
        frame = raw[frame_index * block_align : (frame_index + 1) * block_align]
        values = _frame_values(frame, sample_format, bits, source_channels)
        if output_channels == 1 and len(values) > 1:
            values = (sum(values) / len(values),)
        elif output_channels == 2 and len(values) == 1:
            values = (values[0], values[0])
        for value in values[:output_channels]:
            output.extend(struct.pack("<h", int(max(-1.0, min(1.0, value)) * 32767)))
    converted = dict(fmt)
    converted.update(
        {
            "channels": output_channels,
            "original_format": dict(fmt),
            "channel_mapping": "preserve_mono_or_stereo" if source_channels in {1, 2} else "deterministic_average_to_mono",
        }
    )
    return bytes(output), converted


def _frame_values(frame: bytes, sample_format: str, bits: int, channels: int) -> tuple[float, ...]:
    values: list[float] = []
    if sample_format == "float32":
        for (value,) in struct.iter_unpack("<f", frame[: channels * 4]):
            values.append(float(value))
        return tuple(values)
    if bits == 16:
        for (value,) in struct.iter_unpack("<h", frame[: channels * 2]):
            values.append(float(value) / 32768.0)
        return tuple(values)
    if bits == 24:
        for channel in range(channels):
            start = channel * 3
            chunk = frame[start : start + 3]
            if len(chunk) == 3:
                signed = int.from_bytes(chunk + (b"\xff" if chunk[2] & 0x80 else b"\x00"), "little", signed=True)
                values.append(float(signed) / 8_388_608.0)
        return tuple(values)
    if bits == 32:
        for (value,) in struct.iter_unpack("<i", frame[: channels * 4]):
            values.append(float(value) / 2_147_483_648.0)
        return tuple(values)
    return tuple(0.0 for _ in range(channels))


def _call(ptr: ctypes.c_void_p, index: int, restype: Any, argtypes: list[Any]) -> Any:
    vtbl = ctypes.cast(ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    prototype = ctypes.WINFUNCTYPE(restype, ctypes.c_void_p, *argtypes)
    return prototype(vtbl[index])


def _check_hr(hr: int, label: str) -> None:
    if int(hr) < 0:
        raise SensorCaptureError("device_open_failed", f"{label} failed with HRESULT 0x{int(hr) & 0xFFFFFFFF:08x}")


def _release(ptr: ctypes.c_void_p | None) -> None:
    if ptr:
        try:
            _call(ptr, 2, ctypes.c_ulong, [])(ptr)
        except Exception:
            pass


def _release_handles(handles: dict[str, Any]) -> None:
    for name in ("capture_client", "audio_client", "device", "enumerator"):
        _release(handles.get(name))
    if os.name == "nt":
        try:
            ctypes.oledll.ole32.CoUninitialize()
        except Exception:
            pass
