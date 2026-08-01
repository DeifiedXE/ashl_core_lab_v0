"""External in-memory audio fixture for the Package 130 real run."""

from __future__ import annotations

import math
import os
import struct
import threading
import time
import wave
from io import BytesIO
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, sha256_payload, utc_now


FIXTURE_SPECS: dict[str, dict[str, Any]] = {
    "P1": {"frequency_hz": 720, "amplitude": 0.18, "regions": ((220, 150), (650, 160), (1080, 360))},
    "P2": {"frequency_hz": 810, "amplitude": 0.24, "regions": ((250, 165), (690, 150), (1110, 390))},
    "P3": {"frequency_hz": 900, "amplitude": 0.15, "regions": ((210, 145), (640, 170), (1070, 370))},
    "P4": {"frequency_hz": 980, "amplitude": 0.21, "regions": ((270, 170), (710, 165), (1140, 410))},
    "C1": {"frequency_hz": 840, "amplitude": 0.20, "regions": ((350, 1050),)},
    "C2": {"frequency_hz": 880, "amplitude": 0.20, "regions": ((180, 420), (760, 120), (1440, 130))},
    "C3": {"frequency_hz": 0, "amplitude": 0.0, "regions": tuple()},
}


class LocalAnonymousAuditoryGroundingStimulus:
    """Plays an audit fixture without exposing its schedule to the compiler."""

    def __init__(self, *, fixture_slot: str, total_duration_ms: int = 1900) -> None:
        if fixture_slot not in FIXTURE_SPECS:
            raise ValueError("unknown Package 130 fixture slot")
        self.fixture_slot = fixture_slot
        self.total_duration_ms = int(total_duration_ms)
        self._thread: threading.Thread | None = None
        self._started_ns: int | None = None
        self._finished_ns: int | None = None
        self._error: BaseException | None = None

    def start(self, *, delay_ms: int = 120) -> None:
        if self._thread is not None:
            raise RuntimeError("grounding stimulus already started")

        def worker() -> None:
            try:
                time.sleep(max(0, delay_ms) / 1000.0)
                self._started_ns = monotonic_ns()
                spec = FIXTURE_SPECS[self.fixture_slot]
                if os.name == "nt" and spec["regions"]:
                    import winsound

                    payload = _build_fixture_wav(
                        total_duration_ms=self.total_duration_ms,
                        frequency_hz=int(spec["frequency_hz"]),
                        amplitude=float(spec["amplitude"]),
                        regions=tuple(spec["regions"]),
                    )
                    winsound.PlaySound(payload, winsound.SND_MEMORY)
                else:
                    time.sleep(self.total_duration_ms / 1000.0)
                self._finished_ns = monotonic_ns()
            except BaseException as error:
                self._error = error

        self._thread = threading.Thread(
            target=worker,
            name=f"package_130_fixture_{self.fixture_slot}",
            daemon=True,
        )
        self._thread.start()

    def join(self, timeout: float = 4.0) -> None:
        if self._thread is None:
            raise RuntimeError("grounding stimulus was not started")
        self._thread.join(timeout=timeout)
        if self._thread.is_alive():
            raise RuntimeError("grounding stimulus exceeded its bounded lifetime")
        if self._error is not None:
            raise self._error

    def audit_manifest(self, *, grounding_run_id: str, episode_id: str) -> dict[str, Any]:
        spec = FIXTURE_SPECS[self.fixture_slot]
        payload = {
            "schema_version": "ashl_package_130_external_audio_fixture_manifest_v0",
            "created_at": utc_now(),
            "grounding_run_id": grounding_run_id,
            "episode_id": episode_id,
            "fixture_slot": self.fixture_slot,
            "scheduled_frequency_hz": int(spec["frequency_hz"]),
            "scheduled_regions_ms": tuple(spec["regions"]),
            "fixture_started_monotonic_ns": self._started_ns,
            "fixture_finished_monotonic_ns": self._finished_ns,
            "loaded_after_episode_and_projection_frozen": True,
            "consumed_by_concept_compiler": False,
            "consumed_by_expected_primitive_generator": False,
            "consumed_by_predictive_validation": False,
        }
        payload["fixture_manifest_id"] = "package_130_fixture_manifest:" + sha256_payload(
            {key: value for key, value in payload.items() if key != "created_at"}
        )
        return payload


def _build_fixture_wav(
    *,
    total_duration_ms: int,
    frequency_hz: int,
    amplitude: float,
    regions: tuple[tuple[int, int], ...],
    sample_rate: int = 48_000,
    channels: int = 2,
) -> bytes:
    frame_count = int(sample_rate * total_duration_ms / 1000)
    pcm = bytearray()
    for frame in range(frame_count):
        at_ms = frame * 1000.0 / sample_rate
        value = 0
        active_region = next(
            (
                (start, duration)
                for start, duration in regions
                if start <= at_ms < start + duration
            ),
            None,
        )
        if active_region is not None:
            start, duration = active_region
            ramp = min(
                1.0,
                min(
                    (at_ms - start) / 8.0,
                    (start + duration - at_ms) / 8.0,
                ),
            )
            value = int(
                math.sin(2.0 * math.pi * frequency_hz * frame / sample_rate)
                * amplitude
                * max(0.0, ramp)
                * 32767
            )
        for _ in range(channels):
            pcm.extend(struct.pack("<h", value))
    output = BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(bytes(pcm))
    return output.getvalue()
