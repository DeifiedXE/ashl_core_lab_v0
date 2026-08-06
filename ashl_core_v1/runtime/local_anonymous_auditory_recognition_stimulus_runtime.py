"""External in-memory stimulus for fresh Package 131 recognition probes."""

from __future__ import annotations

import math
import os
import struct
import threading
import time
import wave
from io import BytesIO
from typing import Any

from ashl_core_v1.runtime.auditory_predictive_recognition_types import (
    FIXTURE_MANIFEST_SCHEMA_VERSION,
    AuditoryRecognitionFixtureManifest,
)
from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, sha256_payload, utc_now


PROBE_FIXTURE_SPECS: dict[str, dict[str, Any]] = {
    "A": {
        "frequency_hz": 860,
        "amplitude": 0.19,
        "regions": ((235, 155), (675, 160), (1100, 380)),
    },
    "B": {
        "frequency_hz": 930,
        "amplitude": 0.17,
        "regions": ((260, 780), (1280, 180)),
    },
}


class LocalAnonymousAuditoryRecognitionStimulus:
    """Owns fixture truth so prediction components never receive its schedule."""

    def __init__(self, *, probe_slot: str, total_duration_ms: int = 1900) -> None:
        if probe_slot not in PROBE_FIXTURE_SPECS:
            raise ValueError("unknown Package 131 recognition probe slot")
        self.probe_slot = probe_slot
        self.total_duration_ms = int(total_duration_ms)
        self._thread: threading.Thread | None = None
        self._started_ns: int | None = None
        self._finished_ns: int | None = None
        self._error: BaseException | None = None

    @property
    def started_monotonic_ns(self) -> int:
        if self._started_ns is None:
            raise RuntimeError("recognition stimulus has not started")
        return self._started_ns

    @property
    def finished_monotonic_ns(self) -> int:
        if self._finished_ns is None:
            raise RuntimeError("recognition stimulus has not finished")
        return self._finished_ns

    def start(self, *, delay_ms: int = 80) -> None:
        if self._thread is not None:
            raise RuntimeError("recognition stimulus already started")

        def worker() -> None:
            try:
                time.sleep(max(0, delay_ms) / 1000.0)
                self._started_ns = monotonic_ns()
                spec = PROBE_FIXTURE_SPECS[self.probe_slot]
                if os.name == "nt":
                    import winsound

                    payload = _build_fixture_wav(
                        total_duration_ms=self.total_duration_ms,
                        frequency_hz=int(spec["frequency_hz"]),
                        amplitude=float(spec["amplitude"]),
                        regions=tuple(spec["regions"]),
                    )
                    winsound.PlaySound(payload, winsound.SND_MEMORY)
                    del payload
                else:
                    time.sleep(self.total_duration_ms / 1000.0)
                self._finished_ns = monotonic_ns()
            except BaseException as error:
                self._error = error

        self._thread = threading.Thread(
            target=worker,
            name=f"package_131_fixture_{self.probe_slot}",
            daemon=True,
        )
        self._thread.start()

    def join(self, timeout: float = 4.0) -> None:
        if self._thread is None:
            raise RuntimeError("recognition stimulus was not started")
        self._thread.join(timeout=timeout)
        if self._thread.is_alive():
            raise RuntimeError("recognition stimulus exceeded its bounded lifetime")
        if self._error is not None:
            raise self._error

    def build_audit_manifest(
        self,
        *,
        probe_id: str,
        frozen_source_record_refs: tuple[str, ...],
        result_frozen: bool,
    ) -> AuditoryRecognitionFixtureManifest:
        if not result_frozen:
            raise ValueError("prediction and cleanup must be frozen before fixture audit")
        spec = PROBE_FIXTURE_SPECS[self.probe_slot]
        identity = {
            "probe_id": probe_id,
            "probe_slot": self.probe_slot,
            "scheduled_frequency_hz": int(spec["frequency_hz"]),
            "scheduled_regions_ms": tuple(spec["regions"]),
            "stimulus_started_monotonic_ns": self.started_monotonic_ns,
            "stimulus_finished_monotonic_ns": self.finished_monotonic_ns,
            "source_record_refs": frozen_source_record_refs,
        }
        return AuditoryRecognitionFixtureManifest(
            fixture_manifest_id="package_131_fixture_manifest:" + sha256_payload(identity),
            schema_version=FIXTURE_MANIFEST_SCHEMA_VERSION,
            created_at=utc_now(),
            probe_id=probe_id,
            probe_slot=self.probe_slot,
            scheduled_frequency_hz=int(spec["frequency_hz"]),
            scheduled_regions_ms=tuple(spec["regions"]),
            stimulus_started_monotonic_ns=self.started_monotonic_ns,
            stimulus_finished_monotonic_ns=self.finished_monotonic_ns,
            result_frozen_before_manifest_creation=True,
            consumed_by_model_loader=False,
            consumed_by_audio_compiler=False,
            consumed_by_feature_extractor=False,
            consumed_by_prediction_comparator=False,
            consumed_by_prediction_result_builder=False,
            source_record_refs=frozen_source_record_refs,
        )


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
        active = next(
            (
                (start, duration)
                for start, duration in regions
                if start <= at_ms < start + duration
            ),
            None,
        )
        value = 0
        if active is not None:
            start, duration = active
            ramp = min(
                1.0,
                min((at_ms - start) / 8.0, (start + duration - at_ms) / 8.0),
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
        wav.writeframes(pcm)
    for index in range(len(pcm)):
        pcm[index] = 0
    return output.getvalue()
