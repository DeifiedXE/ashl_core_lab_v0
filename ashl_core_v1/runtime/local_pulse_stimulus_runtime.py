"""Native local black/white pulse stimulus for Package 123."""

from __future__ import annotations

import os
import threading
import time
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, utc_now
from ashl_core_v1.runtime.package_123_types import (
    EXPERIMENT_ID,
    STIMULUS_DURATION_MS,
    STIMULUS_MANIFEST_SCHEMA_VERSION,
    STIMULUS_SCHEDULE,
    WINDOW_CLIENT_HEIGHT,
    WINDOW_CLIENT_WIDTH,
    StimulusRunManifest,
    StimulusTransitionRecord,
    build_stimulus_transition,
)


TONE_FREQUENCY_HZ = 900
TONE_DURATION_MS = 350
TONE_AMPLITUDE = 0.20


class LocalPulseStimulusRuntime:
    """Foreground-only Tkinter stimulus.

    The scheduled transitions are ground truth for audit only. The runtime never
    passes these transition records into perception, learning, memory, or scoring.
    """

    def __init__(self, *, experiment_run_id: str, render_endpoint_id: str = "default") -> None:
        self.experiment_run_id = experiment_run_id
        self.render_endpoint_id = render_endpoint_id
        self.window_title = f"ASHL Package 123 Stimulus {experiment_run_id}"
        self._root: Any | None = None
        self._canvas: Any | None = None
        self._started_monotonic_ns: int | None = None
        self._finished_monotonic_ns: int | None = None
        self._transitions: list[StimulusTransitionRecord] = []
        self._next_transition_index = 0

    @property
    def window_handle(self) -> int:
        if self._root is None:
            return 0
        try:
            return int(self._root.winfo_id())
        except Exception:
            return 0

    def open(self) -> None:
        if self.render_endpoint_id != "default":
            raise ValueError("Package 123 v0 stimulus tone supports the default render endpoint only")
        import tkinter as tk

        root = tk.Tk()
        root.title(self.window_title)
        root.resizable(False, False)
        root.geometry(f"{WINDOW_CLIENT_WIDTH}x{WINDOW_CLIENT_HEIGHT}+80+80")
        try:
            root.attributes("-topmost", True)
            root.lift()
            root.focus_force()
        except Exception:
            pass
        canvas = tk.Canvas(root, width=WINDOW_CLIENT_WIDTH, height=WINDOW_CLIENT_HEIGHT, highlightthickness=0, bg="black")
        canvas.pack(fill="both", expand=True)
        root.update_idletasks()
        root.update()
        self._root = root
        self._canvas = canvas

    def tick(self) -> None:
        if self._root is None or self._canvas is None:
            raise RuntimeError("stimulus window is not open")
        if self._started_monotonic_ns is None:
            self._started_monotonic_ns = monotonic_ns()
        elapsed_ms = (monotonic_ns() - self._started_monotonic_ns) // 1_000_000
        while self._next_transition_index < len(STIMULUS_SCHEDULE):
            offset_ms, visual_state, audio_state = STIMULUS_SCHEDULE[self._next_transition_index]
            if elapsed_ms < offset_ms:
                break
            issued = monotonic_ns()
            self._canvas.configure(bg="white" if visual_state == "white" else "black")
            if audio_state == "tone":
                _play_tone_default_endpoint_nonblocking()
            self._transitions.append(
                build_stimulus_transition(
                    experiment_run_id=self.experiment_run_id,
                    transition_index=self._next_transition_index,
                    scheduled_offset_ms=offset_ms,
                    visual_state=visual_state,
                    audio_state=audio_state,
                    command_issued_monotonic_ns=issued,
                )
            )
            self._next_transition_index += 1
        self._root.update_idletasks()
        self._root.update()

    def run_until_complete(self, *, process_instance_id: str, duration_ms: int = STIMULUS_DURATION_MS) -> StimulusRunManifest:
        if self._root is None:
            self.open()
        started_utc = utc_now()
        self._started_monotonic_ns = monotonic_ns()
        deadline = self._started_monotonic_ns + int(duration_ms) * 1_000_000
        try:
            while monotonic_ns() < deadline:
                self.tick()
                time.sleep(0.005)
            self._finished_monotonic_ns = monotonic_ns()
            return self.manifest(process_instance_id=process_instance_id, stimulus_started_utc=started_utc)
        finally:
            self.close()

    def manifest(self, *, process_instance_id: str, stimulus_started_utc: str | None = None) -> StimulusRunManifest:
        if self._started_monotonic_ns is None:
            raise RuntimeError("stimulus has not started")
        return StimulusRunManifest(
            experiment_run_id=self.experiment_run_id,
            experiment_id=EXPERIMENT_ID,
            schema_version=STIMULUS_MANIFEST_SCHEMA_VERSION,
            process_instance_id=process_instance_id,
            window_title=self.window_title,
            window_handle=self.window_handle,
            client_width=WINDOW_CLIENT_WIDTH,
            client_height=WINDOW_CLIENT_HEIGHT,
            selected_render_endpoint_id=self.render_endpoint_id,
            stimulus_started_utc=stimulus_started_utc or utc_now(),
            stimulus_started_monotonic_ns=self._started_monotonic_ns,
            stimulus_finished_monotonic_ns=self._finished_monotonic_ns or monotonic_ns(),
            transitions=tuple(self._transitions),
            consumed_by_perception_runtime=False,
        )

    def close(self) -> None:
        if self._root is not None:
            try:
                self._root.destroy()
            except Exception:
                pass
        self._root = None
        self._canvas = None


def build_planned_stimulus_transitions(experiment_run_id: str) -> tuple[StimulusTransitionRecord, ...]:
    return tuple(
        build_stimulus_transition(
            experiment_run_id=experiment_run_id,
            transition_index=index,
            scheduled_offset_ms=offset_ms,
            visual_state=visual_state,
            audio_state=audio_state,
        )
        for index, (offset_ms, visual_state, audio_state) in enumerate(STIMULUS_SCHEDULE)
    )


def _play_tone_default_endpoint_nonblocking() -> None:
    if os.name != "nt":
        return

    def worker() -> None:
        try:
            from ashl_core_v1.runtime.windows_wasapi_loopback_source import play_default_endpoint_sine_tone

            play_default_endpoint_sine_tone()
        except Exception:
            return

    thread = threading.Thread(target=worker, name="package_123_stimulus_tone", daemon=True)
    thread.start()
