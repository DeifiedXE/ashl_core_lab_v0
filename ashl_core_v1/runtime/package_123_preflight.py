"""Mandatory Package 123 preflight checks."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import (
    SensorCaptureError,
    build_sensor_capture_config,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.host_state_sensor_adapter import HostStateSensorAdapter
from ashl_core_v1.runtime.local_pulse_stimulus_runtime import LocalPulseStimulusRuntime
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    MultimodalPerceptionSessionMode,
    build_default_multimodal_session_config,
)
from ashl_core_v1.runtime.package_123_cycle_store import Package123CycleStore
from ashl_core_v1.runtime.package_123_types import (
    EXPERIMENT_ID,
    PREFLIGHT_SCHEMA_VERSION,
    WINDOW_CLIENT_HEIGHT,
    WINDOW_CLIENT_WIDTH,
    Package123PreflightRecord,
    build_source_profile,
    new_experiment_run_id,
)
from ashl_core_v1.runtime.package_123_transport_integrity import HOST_STATE_INTERVAL_MS
from ashl_core_v1.runtime.windows_bounded_window_capture_source import (
    WindowsBoundedWindowCaptureSource,
    visual_contrast_distinguishable,
)
from ashl_core_v1.runtime.windows_wasapi_loopback_source import (
    WindowsWasapiLoopbackSource,
    pcm_s16le_rms_ratio,
    play_default_endpoint_sine_tone,
)


BACKGROUND_AUDIO_RMS_THRESHOLD = 0.012
TONE_AUDIO_RMS_THRESHOLD = 0.02


def run_package_123_preflight(
    *,
    state_dir: str | Path,
    render_endpoint: str = "default",
    cycle_index: int = 1,
    experiment_run_id: str | None = None,
    allow_dirty_tree: bool = False,
    perform_real_checks: bool = True,
) -> Package123PreflightRecord:
    path = Path(state_dir)
    path.mkdir(parents=True, exist_ok=True)
    run_id = experiment_run_id or new_experiment_run_id()
    failures: list[str] = []
    window_capture_ready = False
    visual_contrast_verified = False
    loopback_source_ready = False
    loopback_tone_verified = False
    background_audio_silent = False
    host_state_ready = False
    compiler_compatibility_verified = False
    perception_profile_verified = False

    if not _state_dir_writable(path):
        failures.append("state_dir_not_writable")
    if not allow_dirty_tree and _git_metadata_present(Path.cwd()):
        # Git cleanliness is intentionally not checked through a subprocess in
        # the no-Codex runtime path. The CLI can pass an explicit override while
        # development files are dirty.
        failures.append("repository_clean_check_requires_explicit_allow_dirty_tree")

    if perform_real_checks:
        window_capture_ready, visual_contrast_verified, window_failures = _check_window_capture(run_id, render_endpoint)
        failures.extend(window_failures)
        loopback_source_ready, background_audio_silent, loopback_tone_verified, loopback_failures = _check_loopback(render_endpoint)
        failures.extend(loopback_failures)
        host_state_ready, host_failures = _check_host_state(path)
        failures.extend(host_failures)
    else:
        # Unit-test path: no devices, no windows, no sensors opened.
        window_capture_ready = True
        visual_contrast_verified = True
        loopback_source_ready = True
        loopback_tone_verified = True
        background_audio_silent = True
        host_state_ready = True

    try:
        config = build_package_123_multimodal_config(state_dir=path)
        perception_profile_verified = (
            set(config.required_source_kinds) == {"screen", "microphone", "host_state"}
            and "camera" not in set(config.required_source_kinds)
        )
    except Exception as error:
        failures.append(f"perception_profile_invalid:{type(error).__name__}")

    compiler_compatibility_verified = bool(window_capture_ready and loopback_source_ready and host_state_ready)
    status = "passed" if not failures and all(
        (
            window_capture_ready,
            visual_contrast_verified,
            loopback_source_ready,
            loopback_tone_verified,
            background_audio_silent,
            host_state_ready,
            compiler_compatibility_verified,
            perception_profile_verified,
        )
    ) else "blocked"
    record = Package123PreflightRecord(
        preflight_id=stable_id("package_123_preflight"),
        schema_version=PREFLIGHT_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_run_id=run_id,
        cycle_index=int(cycle_index),
        window_capture_ready=window_capture_ready,
        visual_contrast_verified=visual_contrast_verified,
        loopback_source_ready=loopback_source_ready,
        loopback_tone_verified=loopback_tone_verified,
        background_audio_silent=background_audio_silent,
        host_state_ready=host_state_ready,
        compiler_compatibility_verified=compiler_compatibility_verified,
        perception_profile_verified=perception_profile_verified,
        llm_runtime_available=False,
        network_required=False,
        preflight_status=status,
        failure_reasons=tuple(dict.fromkeys(failures)),
    )
    Package123CycleStore(path).append_preflight(record)
    return record


def build_package_123_multimodal_config(*, state_dir: str | Path):
    config = build_default_multimodal_session_config(
        state_dir=state_dir,
        mode=MultimodalPerceptionSessionMode.ARTIFACT_BACKED_ALIGNMENT_REPLAY.value,
        alignment_window_ms=500,
        maximum_window_count=24,
        maximum_session_duration_ms=12_000,
    )
    payload = config.to_dict()
    payload["enabled_source_kinds"] = ("screen", "microphone", "host_state")
    payload["required_source_kinds"] = ("screen", "microphone", "host_state")
    payload["optional_source_kinds"] = tuple()
    payload["config_id"] = stable_id("package_123_multimodal_session_config")
    payload["screen_queue_depth"] = 64
    payload["microphone_queue_depth"] = 32
    payload["host_state_queue_depth"] = 32
    payload["config_sha256"] = ""
    return type(config)(**payload)


def _check_window_capture(experiment_run_id: str, render_endpoint: str) -> tuple[bool, bool, list[str]]:
    failures: list[str] = []
    stimulus = LocalPulseStimulusRuntime(experiment_run_id=experiment_run_id, render_endpoint_id=render_endpoint)
    try:
        stimulus.open()
        source = WindowsBoundedWindowCaptureSource()
        binding = source.bind_by_title(experiment_run_id=experiment_run_id, window_title=stimulus.window_title)
        if binding.binding_status != "bound":
            return False, False, [f"window_binding_{binding.binding_status}"]
        if binding.client_width != WINDOW_CLIENT_WIDTH or binding.client_height != WINDOW_CLIENT_HEIGHT:
            failures.append("stimulus_window_client_geometry_invalid")
        if stimulus._root is not None:
            import time

            stimulus._root.update_idletasks()
            stimulus._root.update()
            time.sleep(0.1)
            stimulus._root.update_idletasks()
            stimulus._root.update()
        black = source.capture_sample(binding).data
        if stimulus._canvas is not None:
            stimulus._canvas.configure(bg="white")
            stimulus._root.update_idletasks()
            stimulus._root.update()

            time.sleep(0.1)
            stimulus._root.update_idletasks()
            stimulus._root.update()
        white = source.capture_sample(binding).data
        contrast = visual_contrast_distinguishable(black, white)
        return True, contrast, failures + ([] if contrast else ["black_white_visual_contrast_not_verified"])
    except Exception as error:
        return False, False, [f"window_capture_failed:{type(error).__name__}"]
    finally:
        stimulus.close()


def _check_loopback(render_endpoint: str) -> tuple[bool, bool, bool, list[str]]:
    source = WindowsWasapiLoopbackSource(endpoint_id=render_endpoint)
    descriptor = source.source_descriptor()
    if not descriptor.available:
        return False, False, False, [descriptor.failure_reason or "loopback_source_unavailable"]
    try:
        baseline_samples = source.capture_samples(duration_ms=1000)
        baseline_energy = _max_energy(baseline_samples)
        background_silent = baseline_energy <= BACKGROUND_AUDIO_RMS_THRESHOLD
        tone_thread = threading.Thread(target=play_default_endpoint_sine_tone, daemon=True)
        tone_thread.start()
        tone_samples = source.capture_samples(duration_ms=700)
        tone_thread.join(timeout=1.0)
        tone_energy = _max_energy(tone_samples)
        tone_verified = tone_energy >= TONE_AUDIO_RMS_THRESHOLD
        failures = []
        if not background_silent:
            failures.append("background_audio_not_silent")
        if not tone_verified:
            failures.append("loopback_tone_energy_not_verified")
        return True, background_silent, tone_verified, failures
    except Exception as error:
        return False, False, False, [f"loopback_capture_failed:{type(error).__name__}"]


def _check_host_state(state_dir: Path) -> tuple[bool, list[str]]:
    adapter = HostStateSensorAdapter()
    descriptor = adapter.enumerate_devices()[0]
    config = build_sensor_capture_config(
        source_kind="host_state",
        adapter_id=adapter.adapter_id,
        device_id=descriptor.device_id,
        explicit_state_dir=state_dir,
        source_specific_config={"host_state_fields": ("sample_monotonic_ns",)},
        capture_duration_ms=1000,
        sample_interval_ms=HOST_STATE_INTERVAL_MS,
        maximum_artifact_count=1,
        maximum_total_bytes=65536,
    )
    try:
        adapter.open(config)
        sample = adapter.read_sample()
        adapter.close()
        return bool(sample.data), [] if sample.data else ["host_state_empty_sample"]
    except Exception as error:
        return False, [f"host_state_failed:{type(error).__name__}"]


def _max_energy(samples: tuple[Any, ...]) -> float:
    return max((pcm_s16le_rms_ratio(sample.data) for sample in samples), default=0.0)


def _state_dir_writable(path: Path) -> bool:
    try:
        probe = path / ".package_123_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except Exception:
        return False


def _git_metadata_present(path: Path) -> bool:
    current = path.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return True
    return False
