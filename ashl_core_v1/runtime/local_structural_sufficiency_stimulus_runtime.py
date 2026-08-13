"""External visual onset/offset fixture for Package 128 real verification."""

from __future__ import annotations

from typing import Any

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, utc_now


class LocalStructuralSufficiencyStimulusRuntime:
    """Fixed fixture schedule that is exposed only after runtime freezes."""

    def __init__(
        self,
        *,
        experiment_run_id: str,
        client_width: int = 640,
        client_height: int = 360,
    ) -> None:
        self.experiment_run_id = experiment_run_id
        self.window_title = (
            "ASHL Package 128 Structural Stop "
            f"{experiment_run_id}"
        )
        self.client_width = int(client_width)
        self.client_height = int(client_height)
        self._root: Any | None = None
        self._canvas: Any | None = None
        self._started_ns: int | None = None
        self._finished_ns: int | None = None
        self._child_started_ns: int | None = None
        self._parent_phase_armed = False
        self._child_phase_armed = False
        self._stage = 0
        self._transitions: list[dict[str, Any]] = []

    def open(self) -> None:
        import tkinter as tk

        root = tk.Tk()
        root.title(self.window_title)
        root.resizable(False, False)
        root.geometry(
            f"{self.client_width}x{self.client_height}+80+80"
        )
        try:
            root.attributes("-topmost", True)
            root.lift()
            root.focus_force()
        except Exception:
            pass
        canvas = tk.Canvas(
            root,
            width=self.client_width,
            height=self.client_height,
            highlightthickness=0,
            bg="black",
        )
        canvas.pack(fill="both", expand=True)
        root.update_idletasks()
        root.update()
        self._root = root
        self._canvas = canvas

    def tick(self) -> None:
        if self._root is None or self._canvas is None:
            raise RuntimeError("Package 128 fixture is not open")
        now_ns = monotonic_ns()
        if self._parent_phase_armed:
            self._started_ns = now_ns
            self._parent_phase_armed = False
        elif self._started_ns is None:
            self._started_ns = now_ns
        elapsed_ms = (now_ns - self._started_ns) // 1_000_000
        if self._stage == 0 and elapsed_ms >= 400:
            self._draw_parent_changes()
            self._record_transition("parent_spatial_changes", now_ns)
            self._stage = 1
        if self._child_phase_armed:
            self._child_started_ns = now_ns
            self._child_phase_armed = False
        child_elapsed_ms = (
            (now_ns - self._child_started_ns) // 1_000_000
            if self._child_started_ns is not None
            else -1
        )
        if self._stage == 1 and child_elapsed_ms >= 400:
            self._draw_child_event_open()
            self._record_transition("child_visual_event_open", now_ns)
            self._stage = 2
        elif self._stage == 2 and child_elapsed_ms >= 1_000:
            self._draw_child_event_closed()
            self._record_transition("child_visual_event_closed", now_ns)
            self._stage = 3
        self._root.update_idletasks()
        self._root.update()

    def begin_child_phase(self) -> None:
        if self._stage != 1:
            raise RuntimeError(
                "Package 128 child phase requires parent changes"
            )
        if self._child_started_ns is not None or self._child_phase_armed:
            raise RuntimeError("Package 128 child phase already started")
        self._child_phase_armed = True

    def begin_parent_phase(self) -> None:
        if self._child_started_ns is not None or self._child_phase_armed:
            raise RuntimeError("Package 128 parent phase already ended")
        self._started_ns = None
        self._parent_phase_armed = True
        self._stage = 0

    def mark_finished(self) -> None:
        self._finished_ns = monotonic_ns()

    def manifest(self) -> dict[str, Any]:
        if self._started_ns is None:
            raise RuntimeError("Package 128 fixture has not started")
        return {
            "schema_version": (
                "ashl_package_128_external_visual_fixture_v0"
            ),
            "experiment_run_id": self.experiment_run_id,
            "created_at": utc_now(),
            "window_title": self.window_title,
            "client_width": self.client_width,
            "client_height": self.client_height,
            "started_monotonic_ns": self._started_ns,
            "finished_monotonic_ns": (
                self._finished_ns or monotonic_ns()
            ),
            "child_phase_started_monotonic_ns": self._child_started_ns,
            "transitions": tuple(self._transitions),
            "consumed_by_perception_runtime": False,
        }

    def close(self) -> None:
        if self._root is not None:
            try:
                self._root.destroy()
            except Exception:
                pass
        self._root = None
        self._canvas = None

    def _draw_parent_changes(self) -> None:
        assert self._canvas is not None
        self._canvas.delete("all")
        self._canvas.create_rectangle(
            160,
            90,
            239,
            134,
            fill="#ffffff",
            outline="#ffffff",
        )
        self._canvas.create_rectangle(
            400,
            180,
            479,
            224,
            fill="#707070",
            outline="#707070",
        )

    def _draw_child_event_open(self) -> None:
        assert self._canvas is not None
        self._canvas.create_rectangle(
            160,
            90,
            239,
            134,
            fill="#000000",
            outline="#000000",
        )
        self._canvas.create_rectangle(
            400,
            180,
            479,
            224,
            fill="#606060",
            outline="#606060",
        )

    def _draw_child_event_closed(self) -> None:
        self._draw_parent_changes()

    def _record_transition(self, stage: str, issued_ns: int) -> None:
        self._transitions.append(
            {
                "transition_index": len(self._transitions),
                "stage": stage,
                "issued_monotonic_ns": int(issued_ns),
                "consumed_by_perception_runtime": False,
            }
        )
